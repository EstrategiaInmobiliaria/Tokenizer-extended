"""Configuración del gateway leída desde variables de entorno / archivo .env."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

# Se busca ai_gateway/.env y, además, un .env en el directorio actual (este último gana).
_PACKAGE_ENV = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(_PACKAGE_ENV), ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    # Llaves de los proveedores (cualquiera puede omitirse; el proveedor queda deshabilitado)
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # URLs base (permiten apuntar a Azure OpenAI, proxies, etc.)
    openai_base_url: str = "https://api.openai.com/v1"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    anthropic_base_url: str = "https://api.anthropic.com/v1"
    anthropic_version: str = "2023-06-01"

    # Llave propia del gateway. Si se define, los clientes deben enviar
    # "Authorization: Bearer <GATEWAY_API_KEY>". Si está vacía, no hay autenticación.
    gateway_api_key: Optional[str] = None

    # Modelos por defecto cuando el cliente solo indica el proveedor
    default_openai_model: str = "gpt-4o-mini"
    default_gemini_model: str = "gemini-2.0-flash"
    default_anthropic_model: str = "claude-3-5-sonnet-latest"

    # Timeout hacia los proveedores (segundos)
    request_timeout: float = 120.0

    # Orígenes permitidos para CORS, separados por coma
    cors_origins: str = "*"


@lru_cache
def get_settings() -> Settings:
    return Settings()
