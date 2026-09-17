"""Tests del gateway: cada proveedor se simula con httpx.MockTransport (sin red ni llaves reales)."""

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from ai_gateway.config import Settings
from ai_gateway.main import create_app
from ai_gateway.router import infer_provider, resolve_model


class FakeUpstream:
    """Simula las tres APIs remotas y registra la última petición recibida por cada una."""

    def __init__(self):
        self.requests = {}
        self.fail_with = None  # (status_code, body) para forzar un error upstream

    def handler(self, request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content or b"{}")
        host = request.url.host
        path = request.url.path

        if self.fail_with:
            return httpx.Response(self.fail_with[0], json=self.fail_with[1])

        if host == "api.openai.com":
            self.requests["openai"] = (request, body)
            return httpx.Response(200, json={
                "id": "chatcmpl-abc", "model": body["model"],
                "choices": [{"index": 0, "message": {"role": "assistant", "content": "hola desde openai"}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
            })

        if host == "generativelanguage.googleapis.com":
            self.requests["gemini"] = (request, body)
            assert ":generateContent" in path
            return httpx.Response(200, json={
                "candidates": [{"content": {"role": "model", "parts": [{"text": "hola desde gemini"}]}, "finishReason": "MAX_TOKENS"}],
                "usageMetadata": {"promptTokenCount": 7, "candidatesTokenCount": 4},
                "modelVersion": "gemini-2.0-flash-001",
            })

        if host == "api.anthropic.com":
            self.requests["anthropic"] = (request, body)
            return httpx.Response(200, json={
                "id": "msg_1", "model": body["model"], "stop_reason": "end_turn",
                "content": [{"type": "text", "text": "hola desde claude"}],
                "usage": {"input_tokens": 9, "output_tokens": 2},
            })

        return httpx.Response(404, json={"error": f"host inesperado {host}"})


@pytest.fixture
def upstream():
    return FakeUpstream()


def make_client(upstream, **overrides):
    settings = Settings(
        _env_file=None,
        openai_api_key="sk-test",
        gemini_api_key="gm-test",
        anthropic_api_key="ant-test",
        **overrides,
    )
    app = create_app(settings=settings, transport=httpx.MockTransport(upstream.handler))
    return TestClient(app)


@pytest.fixture
def client(upstream):
    with make_client(upstream) as c:
        yield c


MESSAGES = [
    {"role": "system", "content": "Responde en español"},
    {"role": "user", "content": "Hola"},
]


# ----------------------------------------------------------------- routing

@pytest.mark.parametrize("name,expected", [
    ("gpt-4o", "openai"), ("o3-mini", "openai"),
    ("gemini-2.0-flash", "gemini"), ("claude-3-5-sonnet-latest", "anthropic"),
    ("llama-3", None),
])
def test_infer_provider(name, expected):
    assert infer_provider(name) == expected


def test_resolve_model_formats():
    providers = {"openai": type("P", (), {"default_model": "gpt-4o-mini"})(),
                 "gemini": type("P", (), {"default_model": "gemini-2.0-flash"})()}
    assert resolve_model("openai/gpt-4o", providers) == ("openai", "gpt-4o")
    assert resolve_model("google/gemini-1.5-pro", providers) == ("gemini", "gemini-1.5-pro")
    assert resolve_model("gpt-4o", providers) == ("openai", "gpt-4o")
    assert resolve_model("openai", providers) == ("openai", "gpt-4o-mini")
    with pytest.raises(LookupError):
        resolve_model("claude", providers)
    with pytest.raises(ValueError):
        resolve_model("mistral-large", providers)


# --------------------------------------------------------------- endpoints

def test_health_lists_providers(client):
    data = client.get("/health").json()
    assert data["status"] == "ok"
    assert {p["name"]: p["enabled"] for p in data["providers"]} == {"openai": True, "gemini": True, "anthropic": True}


def test_models_endpoint(client):
    ids = {m["id"] for m in client.get("/v1/models").json()["data"]}
    assert {"gpt-4o-mini", "openai/gpt-4o-mini", "gemini/gemini-2.0-flash", "anthropic/claude-3-5-sonnet-latest"} <= ids


def test_openai_passthrough(client, upstream):
    r = client.post("/v1/chat/completions", json={"model": "gpt-4o", "messages": MESSAGES, "temperature": 0.2, "max_tokens": 50})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["provider"] == "openai"
    assert data["choices"][0]["message"]["content"] == "hola desde openai"
    assert data["usage"]["total_tokens"] == 8

    request, body = upstream.requests["openai"]
    assert request.headers["authorization"] == "Bearer sk-test"
    assert body["model"] == "gpt-4o"
    assert body["messages"][0]["role"] == "system"
    assert body["temperature"] == 0.2 and body["max_tokens"] == 50


def test_gemini_translation(client, upstream):
    r = client.post("/v1/chat/completions", json={"model": "gemini/gemini-2.0-flash", "messages": MESSAGES + [
        {"role": "assistant", "content": "¡Hola!"}, {"role": "user", "content": "¿Qué tal?"}], "max_tokens": 20})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["provider"] == "gemini"
    assert data["choices"][0]["message"]["content"] == "hola desde gemini"
    assert data["choices"][0]["finish_reason"] == "length"
    assert data["model"] == "gemini-2.0-flash-001"
    assert data["usage"] == {"prompt_tokens": 7, "completion_tokens": 4, "total_tokens": 11}

    request, body = upstream.requests["gemini"]
    assert request.headers["x-goog-api-key"] == "gm-test"
    assert request.url.path.endswith("/models/gemini-2.0-flash:generateContent")
    assert body["systemInstruction"] == {"parts": [{"text": "Responde en español"}]}
    assert [c["role"] for c in body["contents"]] == ["user", "model", "user"]
    assert body["generationConfig"]["maxOutputTokens"] == 20


def test_anthropic_translation(client, upstream):
    r = client.post("/v1/chat/completions", json={"model": "claude-3-5-sonnet-latest", "messages": MESSAGES, "temperature": 1.5})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["provider"] == "anthropic"
    assert data["choices"][0]["message"]["content"] == "hola desde claude"
    assert data["usage"]["total_tokens"] == 11

    request, body = upstream.requests["anthropic"]
    assert request.headers["x-api-key"] == "ant-test"
    assert request.headers["anthropic-version"] == "2023-06-01"
    assert body["system"] == "Responde en español"
    assert body["messages"] == [{"role": "user", "content": "Hola"}]
    assert body["max_tokens"] == 1024
    assert body["temperature"] == 1.0  # recortada al máximo que acepta Anthropic


def test_simple_chat_endpoint(client, upstream):
    r = client.post("/v1/chat", json={"provider": "anthropic", "prompt": "Explica CAPM", "system": "Sé breve"})
    assert r.status_code == 200, r.text
    assert r.json()["choices"][0]["message"]["content"] == "hola desde claude"
    _, body = upstream.requests["anthropic"]
    assert body["model"] == "claude-3-5-sonnet-latest"
    assert body["system"] == "Sé breve"


def test_streaming_emits_openai_sse(client):
    with client.stream("POST", "/v1/chat/completions", json={"model": "openai", "messages": MESSAGES, "stream": True}) as r:
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/event-stream")
        lines = [line for line in r.iter_lines() if line]
    assert lines[-1] == "data: [DONE]"
    first = json.loads(lines[0][len("data: "):])
    assert first["object"] == "chat.completion.chunk"
    assert first["choices"][0]["delta"]["content"] == "hola desde openai"


def test_upstream_error_is_propagated(client, upstream):
    upstream.fail_with = (429, {"error": {"message": "Rate limit exceeded", "type": "rate_limit"}})
    r = client.post("/v1/chat/completions", json={"model": "gpt-4o", "messages": MESSAGES})
    assert r.status_code == 429
    assert r.json()["error"] == {"message": "Rate limit exceeded", "type": "provider_error", "provider": "openai"}


def test_unknown_model_returns_400(client):
    r = client.post("/v1/chat/completions", json={"model": "mistral-large", "messages": MESSAGES})
    assert r.status_code == 400


def test_disabled_provider_returns_503(upstream):
    settings = Settings(_env_file=None, openai_api_key="sk-test")
    app = create_app(settings=settings, transport=httpx.MockTransport(upstream.handler))
    with TestClient(app) as c:
        r = c.post("/v1/chat/completions", json={"model": "gemini", "messages": MESSAGES})
        assert r.status_code == 503
        assert "GEMINI_API_KEY" in r.json()["detail"]


def test_gateway_key_required_when_configured(upstream):
    with make_client(upstream, gateway_api_key="secreto") as c:
        assert c.get("/health").status_code == 200  # health siempre abierto
        assert c.post("/v1/chat/completions", json={"model": "openai", "messages": MESSAGES}).status_code == 401
        ok = c.post("/v1/chat/completions", json={"model": "openai", "messages": MESSAGES},
                    headers={"Authorization": "Bearer secreto"})
        assert ok.status_code == 200
