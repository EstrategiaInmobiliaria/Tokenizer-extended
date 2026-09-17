"""Modelos Pydantic: formato de entrada/salida compatible con la API de OpenAI."""

import time
import uuid
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

Role = Literal["system", "user", "assistant"]


class ContentPart(BaseModel):
    type: str
    text: Optional[str] = None


class ChatMessage(BaseModel):
    role: Role
    # OpenAI acepta string o lista de partes; el gateway normaliza a texto plano.
    content: Union[str, List[ContentPart]]

    def text(self) -> str:
        if isinstance(self.content, str):
            return self.content
        return "".join(part.text or "" for part in self.content if part.type == "text")


class ChatCompletionRequest(BaseModel):
    """Cuerpo de POST /v1/chat/completions (subconjunto de la API de OpenAI)."""

    model: str = Field(..., description="Ej: gpt-4o, gemini-2.0-flash, claude-3-5-sonnet-latest, o 'proveedor/modelo'")
    messages: List[ChatMessage] = Field(..., min_length=1)
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    stop: Optional[Union[str, List[str]]] = None
    stream: bool = False
    user: Optional[str] = None

    model_config = {"extra": "allow"}


class SimpleChatRequest(BaseModel):
    """Cuerpo de POST /v1/chat: la forma más corta de hablar con un proveedor."""

    provider: Literal["openai", "gemini", "anthropic"]
    prompt: str = Field(..., min_length=1)
    system: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class Choice(BaseModel):
    index: int = 0
    message: Dict[str, Any]
    finish_reason: Optional[str] = "stop"


class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:24]}")
    object: Literal["chat.completion"] = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    provider: str
    choices: List[Choice]
    usage: Usage = Field(default_factory=Usage)


class ModelInfo(BaseModel):
    id: str
    object: Literal["model"] = "model"
    owned_by: str
    created: int = Field(default_factory=lambda: int(time.time()))


class ModelList(BaseModel):
    object: Literal["list"] = "list"
    data: List[ModelInfo]


class ProviderStatus(BaseModel):
    name: str
    enabled: bool
    default_model: str
