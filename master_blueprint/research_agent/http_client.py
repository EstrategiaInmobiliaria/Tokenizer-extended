"""
Cliente HTTP del agente: caché en disco, reintentos y control de ritmo.

Sólo usa la biblioteca estándar, a propósito. El agente tiene que poder
ejecutarse en un contenedor recién creado sin `pip install`, y la caché en disco
hace que una investigación repetida sea reproducible y no vuelva a golpear a los
servidores de terceros.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_USER_AGENT = (
    "master-blueprint-research-agent/1.0 "
    "(+https://github.com/; investigación académica; contacto: research@example.com)"
)


class HttpError(RuntimeError):
    """Fallo de red o respuesta no utilizable tras agotar los reintentos."""


@dataclass
class HttpResponse:
    url: str
    status: int
    body: str
    from_cache: bool = False


class HttpClient:
    """
    Cliente con caché opcional en disco y espaciado mínimo entre peticiones.

    El espaciado es por host: dos APIs distintas no se penalizan entre sí, pero
    nunca se martillea a la misma.
    """

    def __init__(
        self,
        cache_dir: Optional[str | Path] = None,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: float = 25.0,
        min_interval: float = 0.4,
        max_retries: int = 3,
        max_bytes: int = 4_000_000,
        offline: bool = False,
    ):
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.user_agent = user_agent
        self.timeout = timeout
        self.min_interval = min_interval
        self.max_retries = max_retries
        self.max_bytes = max_bytes
        self.offline = offline
        self._last_call: Dict[str, float] = {}
        self.request_count = 0
        self.cache_hits = 0

        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ── caché ────────────────────────────────────────────────────────────────

    def _cache_path(self, url: str, headers: Dict[str, str]) -> Optional[Path]:
        if not self.cache_dir:
            return None
        key = hashlib.sha256((url + json.dumps(headers, sort_keys=True)).encode()).hexdigest()
        return self.cache_dir / f"{key}.json"

    def _read_cache(self, path: Optional[Path]) -> Optional[HttpResponse]:
        if not path or not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        return HttpResponse(
            url=payload["url"],
            status=payload["status"],
            body=payload["body"],
            from_cache=True,
        )

    def _write_cache(self, path: Optional[Path], response: HttpResponse) -> None:
        if not path:
            return
        try:
            path.write_text(
                json.dumps(
                    {"url": response.url, "status": response.status, "body": response.body},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except OSError:
            pass  # una caché que no se puede escribir no debe tumbar la investigación

    # ── petición ─────────────────────────────────────────────────────────────

    def _throttle(self, url: str) -> None:
        host = url.split("/")[2] if "://" in url else url
        elapsed = time.monotonic() - self._last_call.get(host, 0.0)
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_call[host] = time.monotonic()

    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> HttpResponse:
        """Descarga una URL como texto. Lanza `HttpError` si no lo consigue."""
        extra_headers = dict(headers or {})
        cache_path = self._cache_path(url, extra_headers)

        cached = self._read_cache(cache_path)
        if cached:
            self.cache_hits += 1
            return cached

        if self.offline:
            raise HttpError(f"Modo offline activo; no hay caché para {url}")

        request_headers = {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip",
            **extra_headers,
        }

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries):
            self._throttle(url)
            try:
                request = urllib.request.Request(url, headers=request_headers)
                with urllib.request.urlopen(request, timeout=self.timeout) as raw:
                    data = raw.read(self.max_bytes)
                    if raw.headers.get("Content-Encoding") == "gzip":
                        data = gzip.decompress(data)
                    body = data.decode(raw.headers.get_content_charset() or "utf-8", "replace")
                    response = HttpResponse(url=url, status=raw.status, body=body)
                self.request_count += 1
                self._write_cache(cache_path, response)
                return response
            except urllib.error.HTTPError as exc:
                last_error = exc
                # 4xx distinto de 429 no mejora reintentando
                if exc.code != 429 and 400 <= exc.code < 500:
                    break
                time.sleep(1.5 * (2**attempt))
            except Exception as exc:  # timeouts, DNS, TLS, conexiones cortadas
                last_error = exc
                time.sleep(1.0 * (2**attempt))

        raise HttpError(f"No se pudo descargar {url}: {type(last_error).__name__}: {last_error}")

    def get_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
        """Igual que `get`, pero devuelve JSON ya parseado."""
        response = self.get(url, headers={"Accept": "application/json", **(headers or {})})
        try:
            return json.loads(response.body)
        except json.JSONDecodeError as exc:
            raise HttpError(f"Respuesta no es JSON válido desde {url}: {exc}") from exc


def default_cache_dir() -> Path:
    """Directorio de caché por defecto, configurable con `RESEARCH_AGENT_CACHE`."""
    return Path(os.environ.get("RESEARCH_AGENT_CACHE", Path.home() / ".cache" / "research_agent"))
