"""Adaptador para la API Messages de Anthropic (Claude)."""

from ..schemas import ChatCompletionRequest
from .base import BaseProvider, ProviderResult, split_system_messages

# Anthropic exige max_tokens; este es el valor cuando el cliente no lo indica.
DEFAULT_MAX_TOKENS = 1024

_FINISH_MAP = {
    "end_turn": "stop",
    "stop_sequence": "stop",
    "max_tokens": "length",
    "tool_use": "tool_calls",
}


class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def __init__(self, *args, anthropic_version: str = "2023-06-01", **kwargs):
        super().__init__(*args, **kwargs)
        self.anthropic_version = anthropic_version

    async def chat(self, request: ChatCompletionRequest, model: str) -> ProviderResult:
        system, conversation = split_system_messages(request.messages)

        payload = {
            "model": model,
            "max_tokens": request.max_tokens or DEFAULT_MAX_TOKENS,
            "messages": [{"role": m.role, "content": m.text()} for m in conversation],
        }
        if system:
            payload["system"] = system
        if request.temperature is not None:
            # Anthropic acepta 0..1; OpenAI permite hasta 2.
            payload["temperature"] = min(request.temperature, 1.0)
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.stop is not None:
            payload["stop_sequences"] = [request.stop] if isinstance(request.stop, str) else request.stop
        if request.user:
            payload["metadata"] = {"user_id": request.user}

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.anthropic_version,
            "Content-Type": "application/json",
        }
        data = await self._post(f"{self.base_url}/messages", headers, payload)

        blocks = data.get("content") or []
        content = "".join(block.get("text", "") for block in blocks if block.get("type") == "text")
        usage = data.get("usage") or {}
        return ProviderResult(
            content=content,
            model=data.get("model", model),
            finish_reason=_FINISH_MAP.get(data.get("stop_reason") or "end_turn", "stop"),
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            raw=data,
        )
