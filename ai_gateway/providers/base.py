"""Contrato común que implementa cada proveedor (OpenAI, Gemini, Anthropic)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

import httpx

from ..schemas import ChatCompletionRequest, ChatMessage


class ProviderError(Exception):
    """Error devuelto por el proveedor upstream, con el código HTTP original."""

    def __init__(self, provider: str, status_code: int, detail: str):
        self.provider = provider
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"[{provider}] HTTP {status_code}: {detail}")


@dataclass
class ProviderResult:
    """Respuesta normalizada, independiente del proveedor."""

    content: str
    model: str
    finish_reason: Optional[str] = "stop"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    raw: dict = field(default_factory=dict)


def split_system_messages(messages: List[ChatMessage]):
    """Separa los mensajes 'system' del resto (Gemini y Anthropic los reciben aparte)."""
    system_parts = [m.text() for m in messages if m.role == "system"]
    conversation = [m for m in messages if m.role != "system"]
    system = "\n\n".join(p for p in system_parts if p) or None
    return system, conversation


class BaseProvider(ABC):
    name: str = "base"

    def __init__(self, api_key: str, base_url: str, client: httpx.AsyncClient, default_model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = client
        self.default_model = default_model

    @abstractmethod
    async def chat(self, request: ChatCompletionRequest, model: str) -> ProviderResult:
        """Envía la conversación al proveedor y devuelve un resultado normalizado."""

    async def _post(self, url: str, headers: dict, payload: dict) -> dict:
        try:
            response = await self.client.post(url, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise ProviderError(self.name, 504, f"Timeout al contactar {self.name}: {exc}") from exc
        except httpx.HTTPError as exc:
            raise ProviderError(self.name, 502, f"Error de red hacia {self.name}: {exc}") from exc

        if response.status_code >= 400:
            raise ProviderError(self.name, response.status_code, _extract_error(response))
        return response.json()


def _extract_error(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return response.text[:500]
    err = body.get("error", body)
    if isinstance(err, dict):
        return str(err.get("message") or err)
    return str(err)
