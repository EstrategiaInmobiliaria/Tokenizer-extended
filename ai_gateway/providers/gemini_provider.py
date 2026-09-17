"""Adaptador para la API generateContent de Google Gemini."""

from ..schemas import ChatCompletionRequest
from .base import BaseProvider, ProviderResult, split_system_messages

# Gemini usa "model" en lugar de "assistant" para los turnos del modelo.
_ROLE_MAP = {"user": "user", "assistant": "model"}

_FINISH_MAP = {
    "STOP": "stop",
    "MAX_TOKENS": "length",
    "SAFETY": "content_filter",
    "RECITATION": "content_filter",
}


class GeminiProvider(BaseProvider):
    name = "gemini"

    async def chat(self, request: ChatCompletionRequest, model: str) -> ProviderResult:
        system, conversation = split_system_messages(request.messages)

        payload = {
            "contents": [
                {"role": _ROLE_MAP[m.role], "parts": [{"text": m.text()}]} for m in conversation
            ]
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        generation_config = {}
        if request.temperature is not None:
            generation_config["temperature"] = request.temperature
        if request.max_tokens is not None:
            generation_config["maxOutputTokens"] = request.max_tokens
        if request.top_p is not None:
            generation_config["topP"] = request.top_p
        if request.stop is not None:
            generation_config["stopSequences"] = (
                [request.stop] if isinstance(request.stop, str) else request.stop
            )
        if generation_config:
            payload["generationConfig"] = generation_config

        url = f"{self.base_url}/models/{model}:generateContent"
        headers = {"x-goog-api-key": self.api_key, "Content-Type": "application/json"}
        data = await self._post(url, headers, payload)

        candidate = (data.get("candidates") or [{}])[0]
        parts = (candidate.get("content") or {}).get("parts") or []
        content = "".join(part.get("text", "") for part in parts)
        usage = data.get("usageMetadata") or {}
        return ProviderResult(
            content=content,
            model=data.get("modelVersion", model),
            finish_reason=_FINISH_MAP.get(candidate.get("finishReason", "STOP"), "stop"),
            prompt_tokens=usage.get("promptTokenCount", 0),
            completion_tokens=usage.get("candidatesTokenCount", 0),
            raw=data,
        )
