"""Resolución de 'modelo solicitado' -> (proveedor, modelo real)."""

from typing import Dict, Optional, Tuple

import httpx

from .config import Settings
from .providers import AnthropicProvider, BaseProvider, GeminiProvider, OpenAIProvider

PROVIDER_ALIASES = {
    "openai": "openai",
    "gpt": "openai",
    "chatgpt": "openai",
    "gemini": "gemini",
    "google": "gemini",
    "anthropic": "anthropic",
    "claude": "anthropic",
}


def build_providers(settings: Settings, client: httpx.AsyncClient) -> Dict[str, BaseProvider]:
    """Instancia solo los proveedores que tienen llave configurada."""
    providers: Dict[str, BaseProvider] = {}
    if settings.openai_api_key:
        providers["openai"] = OpenAIProvider(
            settings.openai_api_key, settings.openai_base_url, client, settings.default_openai_model
        )
    if settings.gemini_api_key:
        providers["gemini"] = GeminiProvider(
            settings.gemini_api_key, settings.gemini_base_url, client, settings.default_gemini_model
        )
    if settings.anthropic_api_key:
        providers["anthropic"] = AnthropicProvider(
            settings.anthropic_api_key,
            settings.anthropic_base_url,
            client,
            settings.default_anthropic_model,
            anthropic_version=settings.anthropic_version,
        )
    return providers


def infer_provider(model_name: str) -> Optional[str]:
    """Deduce el proveedor a partir del nombre del modelo cuando no viene prefijado."""
    lower = model_name.lower()
    if lower.startswith(("gpt-", "o1", "o3", "o4", "chatgpt", "text-", "davinci")):
        return "openai"
    if lower.startswith("gemini"):
        return "gemini"
    if lower.startswith("claude"):
        return "anthropic"
    return None


def resolve_model(requested: str, providers: Dict[str, BaseProvider]) -> Tuple[str, str]:
    """
    Formatos aceptados:
      - "openai/gpt-4o", "gemini/gemini-2.0-flash", "anthropic/claude-3-5-sonnet-latest"
      - "gpt-4o", "gemini-2.0-flash", "claude-3-5-sonnet-latest"  (proveedor inferido)
      - "openai", "gemini", "claude"                               (modelo por defecto)
    """
    requested = requested.strip()
    if not requested:
        raise ValueError("El campo 'model' no puede estar vacío")

    if "/" in requested:
        prefix, _, model = requested.partition("/")
        provider_name = PROVIDER_ALIASES.get(prefix.lower())
        if provider_name is None:
            raise ValueError(f"Proveedor desconocido '{prefix}'. Usa openai, gemini o anthropic")
    elif requested.lower() in PROVIDER_ALIASES:
        provider_name = PROVIDER_ALIASES[requested.lower()]
        model = ""
    else:
        provider_name = infer_provider(requested)
        if provider_name is None:
            raise ValueError(
                f"No se pudo inferir el proveedor para '{requested}'. "
                "Usa el formato 'proveedor/modelo', por ejemplo 'gemini/gemini-2.0-flash'"
            )
        model = requested

    provider = providers.get(provider_name)
    if provider is None:
        raise LookupError(
            f"El proveedor '{provider_name}' no está habilitado. "
            f"Define {provider_name.upper()}_API_KEY en el .env"
        )
    return provider_name, (model or provider.default_model)
