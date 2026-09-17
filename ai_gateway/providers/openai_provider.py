"""Adaptador para la API Chat Completions de OpenAI (también sirve para Azure/proxies compatibles)."""

from ..schemas import ChatCompletionRequest
from .base import BaseProvider, ProviderResult


class OpenAIProvider(BaseProvider):
    name = "openai"

    async def chat(self, request: ChatCompletionRequest, model: str) -> ProviderResult:
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.text()} for m in request.messages],
        }
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.stop is not None:
            payload["stop"] = request.stop
        if request.user:
            payload["user"] = request.user

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = await self._post(f"{self.base_url}/chat/completions", headers, payload)

        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        usage = data.get("usage") or {}
        return ProviderResult(
            content=message.get("content") or "",
            model=data.get("model", model),
            finish_reason=choice.get("finish_reason", "stop"),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            raw=data,
        )
