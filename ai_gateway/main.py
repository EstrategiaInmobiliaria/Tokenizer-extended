"""
AI Gateway - API unificada hacia OpenAI, Google Gemini y Anthropic Claude.

Expone un endpoint compatible con la API de OpenAI (POST /v1/chat/completions)
para que herramientas como Cursor puedan usarlo como "OpenAI Base URL", más un
endpoint simplificado (POST /v1/chat) para integraciones propias.

Ejecutar:
    uvicorn ai_gateway.main:app --reload --port 8080
"""

import json
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Optional

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from . import __version__
from .config import Settings, get_settings
from .providers import BaseProvider, ProviderError, ProviderResult
from .router import build_providers, resolve_model
from .schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    Choice,
    ModelInfo,
    ModelList,
    ProviderStatus,
    SimpleChatRequest,
    Usage,
)

logger = logging.getLogger("ai_gateway")


def create_app(settings: Optional[Settings] = None, transport: Optional[httpx.AsyncBaseTransport] = None) -> FastAPI:
    """Fábrica de la aplicación. `transport` permite inyectar un mock en tests."""
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        client = httpx.AsyncClient(timeout=settings.request_timeout, transport=transport)
        app.state.providers = build_providers(settings, client)
        if not app.state.providers:
            logger.warning("Ningún proveedor habilitado: define OPENAI_API_KEY, GEMINI_API_KEY o ANTHROPIC_API_KEY")
        else:
            logger.info("Proveedores habilitados: %s", ", ".join(app.state.providers))
        try:
            yield
        finally:
            await client.aclose()

    app = FastAPI(
        title="AI Gateway",
        description="API unificada para OpenAI (ChatGPT), Google Gemini y Anthropic Claude. Compatible con clientes OpenAI.",
        version=__version__,
        lifespan=lifespan,
    )
    app.state.settings = settings

    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()] or ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=origins != ["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------ auth
    async def require_gateway_key(authorization: Optional[str] = Header(default=None)) -> None:
        expected = settings.gateway_api_key
        if not expected:
            return
        token = ""
        if authorization and authorization.lower().startswith("bearer "):
            token = authorization[7:].strip()
        if token != expected:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Llave de gateway inválida. Envía 'Authorization: Bearer <GATEWAY_API_KEY>'",
            )

    def get_providers(request: Request) -> Dict[str, BaseProvider]:
        return request.app.state.providers

    # -------------------------------------------------------------- helpers
    def to_response(result: ProviderResult, provider_name: str) -> ChatCompletionResponse:
        return ChatCompletionResponse(
            model=result.model,
            provider=provider_name,
            choices=[
                Choice(
                    index=0,
                    message={"role": "assistant", "content": result.content},
                    finish_reason=result.finish_reason,
                )
            ],
            usage=Usage(
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                total_tokens=result.prompt_tokens + result.completion_tokens,
            ),
        )

    def sse_stream(response: ChatCompletionResponse):
        """Emite la respuesta como chunks SSE con el formato de OpenAI.

        Los proveedores se consultan sin streaming, así que se envía el contenido
        completo en un solo chunk seguido del marcador de fin. Esto basta para
        clientes que exigen `stream: true` (como Cursor).
        """
        base = {
            "id": response.id,
            "object": "chat.completion.chunk",
            "created": response.created,
            "model": response.model,
        }
        content = response.choices[0].message["content"]
        first = {**base, "choices": [{"index": 0, "delta": {"role": "assistant", "content": content}, "finish_reason": None}]}
        last = {**base, "choices": [{"index": 0, "delta": {}, "finish_reason": response.choices[0].finish_reason}],
                "usage": response.usage.model_dump()}
        yield f"data: {json.dumps(first, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps(last, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    async def run_chat(body: ChatCompletionRequest, providers: Dict[str, BaseProvider]) -> ChatCompletionResponse:
        try:
            provider_name, model = resolve_model(body.model, providers)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except LookupError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        started = time.perf_counter()
        result = await providers[provider_name].chat(body, model)
        logger.info("%s/%s respondió en %.2fs", provider_name, model, time.perf_counter() - started)
        return to_response(result, provider_name)

    # ------------------------------------------------------------ endpoints
    @app.exception_handler(ProviderError)
    async def provider_error_handler(_: Request, exc: ProviderError):
        return JSONResponse(
            status_code=exc.status_code if 400 <= exc.status_code < 600 else 502,
            content={"error": {"message": exc.detail, "type": "provider_error", "provider": exc.provider}},
        )

    @app.get("/", tags=["info"])
    async def root():
        return {
            "service": "AI Gateway",
            "version": __version__,
            "docs": "/docs",
            "endpoints": ["/health", "/v1/models", "/v1/chat", "/v1/chat/completions"],
        }

    @app.get("/health", tags=["info"])
    async def health(providers: Dict[str, BaseProvider] = Depends(get_providers)):
        return {
            "status": "ok" if providers else "degraded",
            "providers": [
                ProviderStatus(name=name, enabled=name in providers, default_model=_default_model(settings, name))
                for name in ("openai", "gemini", "anthropic")
            ],
        }

    @app.get("/v1/models", response_model=ModelList, tags=["openai-compatible"], dependencies=[Depends(require_gateway_key)])
    async def list_models(providers: Dict[str, BaseProvider] = Depends(get_providers)):
        data = []
        for name, provider in providers.items():
            data.append(ModelInfo(id=provider.default_model, owned_by=name))
            data.append(ModelInfo(id=f"{name}/{provider.default_model}", owned_by=name))
        return ModelList(data=data)

    @app.post("/v1/chat/completions", tags=["openai-compatible"], dependencies=[Depends(require_gateway_key)])
    async def chat_completions(body: ChatCompletionRequest, providers: Dict[str, BaseProvider] = Depends(get_providers)):
        response = await run_chat(body, providers)
        if body.stream:
            return StreamingResponse(sse_stream(response), media_type="text/event-stream")
        return response

    @app.post("/v1/chat", response_model=ChatCompletionResponse, tags=["simple"], dependencies=[Depends(require_gateway_key)])
    async def simple_chat(body: SimpleChatRequest, providers: Dict[str, BaseProvider] = Depends(get_providers)):
        messages = []
        if body.system:
            messages.append(ChatMessage(role="system", content=body.system))
        messages.append(ChatMessage(role="user", content=body.prompt))
        model = f"{body.provider}/{body.model}" if body.model else body.provider
        request = ChatCompletionRequest(
            model=model, messages=messages, temperature=body.temperature, max_tokens=body.max_tokens
        )
        return await run_chat(request, providers)

    return app


def _default_model(settings: Settings, name: str) -> str:
    return {
        "openai": settings.default_openai_model,
        "gemini": settings.default_gemini_model,
        "anthropic": settings.default_anthropic_model,
    }[name]


app = create_app()
