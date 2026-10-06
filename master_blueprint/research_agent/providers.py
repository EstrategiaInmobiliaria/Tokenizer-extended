"""
Proveedores de búsqueda.

Cada proveedor traduce una consulta en una lista de `Source` ya normalizadas.
La prioridad del diseño es que el agente **funcione sin ninguna API key**: los
cuatro proveedores académicos y enciclopédicos (OpenAlex, Crossref, arXiv,
Wikipedia) son abiertos. Los proveedores de web general requieren clave y se
activan solos si la variable de entorno correspondiente está presente.
"""

from __future__ import annotations

import os
import re
import urllib.parse
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .http_client import HttpClient, HttpError
from .models import Source, SourceTier


class SearchProvider(ABC):
    """Contrato común: un nombre, una comprobación de disponibilidad y una búsqueda."""

    name: str = "abstracto"

    def __init__(self, client: HttpClient):
        self.client = client

    def available(self) -> bool:
        return True

    @abstractmethod
    def search(self, query: str, limit: int = 8, since_year: Optional[int] = None) -> List[Source]:
        """Devuelve fuentes para `query`. Nunca lanza: ante error devuelve lista vacía."""


def _clean(text: Optional[str]) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


# ═══════════════════════════════════════════════════════════════════════════
# Proveedores académicos abiertos (sin API key)
# ═══════════════════════════════════════════════════════════════════════════


class OpenAlexProvider(SearchProvider):
    """
    OpenAlex: catálogo abierto de literatura académica.

    Es el proveedor principal del agente porque entrega en una sola llamada todo
    lo que hace falta para citar (autores, año, revista, DOI, acceso abierto) más
    el número de citas, que alimenta la puntuación de relevancia.
    """

    name = "openalex"
    BASE = "https://api.openalex.org/works"

    def __init__(self, client: HttpClient, mailto: Optional[str] = None):
        super().__init__(client)
        self.mailto = mailto or os.environ.get("OPENALEX_MAILTO", "")

    def search(self, query: str, limit: int = 8, since_year: Optional[int] = None) -> List[Source]:
        params: Dict[str, Any] = {"search": query, "per-page": min(limit, 25)}
        if since_year:
            params["filter"] = f"from_publication_date:{since_year}-01-01"
        if self.mailto:
            params["mailto"] = self.mailto

        try:
            payload = self.client.get_json(f"{self.BASE}?{urllib.parse.urlencode(params)}")
        except HttpError:
            return []

        return [self._to_source(work, query) for work in payload.get("results", [])]

    def _to_source(self, work: Dict[str, Any], query: str) -> Source:
        location = work.get("primary_location") or {}
        venue = (location.get("source") or {}).get("display_name")
        open_access = work.get("open_access") or {}
        is_preprint = (work.get("type") or "").lower() in {"preprint", "posted-content"}

        return Source(
            title=_clean(work.get("title")) or "(sin título)",
            url=location.get("landing_page_url") or work.get("doi") or work.get("id") or "",
            provider=self.name,
            tier=SourceTier.PREPRINT if is_preprint else SourceTier.PEER_REVIEWED,
            authors=[
                _clean(a.get("author", {}).get("display_name"))
                for a in work.get("authorships", [])
                if a.get("author", {}).get("display_name")
            ],
            year=work.get("publication_year"),
            venue=_clean(venue) or None,
            doi=work.get("doi"),
            abstract=_decode_inverted_abstract(work.get("abstract_inverted_index")),
            cited_by_count=work.get("cited_by_count"),
            is_open_access=open_access.get("is_oa"),
            language=work.get("language"),
            found_by_query=query,
            extra={
                "openalex_id": work.get("id"),
                "type": work.get("type"),
                "topics": [t.get("display_name") for t in (work.get("topics") or [])][:3],
            },
        )


class CrossrefProvider(SearchProvider):
    """
    Crossref: registro oficial de DOIs.

    Se usa como contraste de OpenAlex. Que un trabajo aparezca en ambos con el
    mismo DOI es la verificación más barata de que la referencia existe de verdad.
    """

    name = "crossref"
    BASE = "https://api.crossref.org/works"

    def search(self, query: str, limit: int = 8, since_year: Optional[int] = None) -> List[Source]:
        params: Dict[str, Any] = {"query": query, "rows": min(limit, 20)}
        if since_year:
            params["filter"] = f"from-pub-date:{since_year}-01-01"

        try:
            payload = self.client.get_json(f"{self.BASE}?{urllib.parse.urlencode(params)}")
        except HttpError:
            return []

        sources = []
        for item in payload.get("message", {}).get("items", []):
            titles = item.get("title") or []
            if not titles:
                continue
            sources.append(
                Source(
                    title=_clean(titles[0]),
                    url=item.get("URL") or "",
                    provider=self.name,
                    tier=SourceTier.PEER_REVIEWED,
                    authors=[
                        _clean(f"{a.get('given', '')} {a.get('family', '')}")
                        for a in item.get("author", [])
                        if a.get("family")
                    ],
                    year=_crossref_year(item),
                    venue=_clean((item.get("container-title") or [None])[0]),
                    doi=item.get("DOI"),
                    abstract=_strip_tags(item.get("abstract")),
                    cited_by_count=item.get("is-referenced-by-count"),
                    found_by_query=query,
                    extra={"publisher": item.get("publisher"), "type": item.get("type")},
                )
            )
        return sources


class ArxivProvider(SearchProvider):
    """arXiv: preprints, útil sobre todo para métodos computacionales recientes."""

    name = "arxiv"
    BASE = "https://export.arxiv.org/api/query"

    NS = {"atom": "http://www.w3.org/2005/Atom"}

    def search(self, query: str, limit: int = 8, since_year: Optional[int] = None) -> List[Source]:
        params = {
            "search_query": f"all:{query}",
            "max_results": min(limit, 20),
            "sortBy": "relevance",
        }
        try:
            response = self.client.get(f"{self.BASE}?{urllib.parse.urlencode(params)}")
            root = ET.fromstring(response.body)
        except (HttpError, ET.ParseError):
            return []

        sources = []
        for entry in root.findall("atom:entry", self.NS):
            published = (entry.findtext("atom:published", default="", namespaces=self.NS) or "")[:4]
            year = int(published) if published.isdigit() else None
            if since_year and year and year < since_year:
                continue
            sources.append(
                Source(
                    title=_clean(entry.findtext("atom:title", default="", namespaces=self.NS)),
                    url=entry.findtext("atom:id", default="", namespaces=self.NS),
                    provider=self.name,
                    tier=SourceTier.PREPRINT,
                    authors=[
                        _clean(a.findtext("atom:name", default="", namespaces=self.NS))
                        for a in entry.findall("atom:author", self.NS)
                    ],
                    year=year,
                    venue="arXiv",
                    abstract=_clean(entry.findtext("atom:summary", default="", namespaces=self.NS)),
                    found_by_query=query,
                )
            )
        return sources


class WikipediaProvider(SearchProvider):
    """
    Wikipedia: sólo para definiciones y contexto.

    Se clasifica como `REFERENCE`, un escalón por debajo de la literatura
    revisada, para que nunca sostenga por sí sola una afirmación cuantitativa.
    """

    name = "wikipedia"

    def __init__(self, client: HttpClient, lang: str = "en"):
        super().__init__(client)
        self.lang = lang

    def search(self, query: str, limit: int = 5, since_year: Optional[int] = None) -> List[Source]:
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": min(limit, 10),
        }
        base = f"https://{self.lang}.wikipedia.org/w/api.php"
        try:
            payload = self.client.get_json(f"{base}?{urllib.parse.urlencode(params)}")
        except HttpError:
            return []

        sources = []
        for result in payload.get("query", {}).get("search", []):
            title = result.get("title", "")
            sources.append(
                Source(
                    title=title,
                    url=f"https://{self.lang}.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
                    provider=self.name,
                    tier=SourceTier.REFERENCE,
                    venue=f"Wikipedia ({self.lang})",
                    abstract=_strip_tags(result.get("snippet")),
                    language=self.lang,
                    found_by_query=query,
                )
            )
        return sources


# ═══════════════════════════════════════════════════════════════════════════
# Proveedores de web general (requieren API key)
# ═══════════════════════════════════════════════════════════════════════════


class TavilyProvider(SearchProvider):
    """Búsqueda web orientada a agentes. Requiere `TAVILY_API_KEY`."""

    name = "tavily"

    def available(self) -> bool:
        return bool(os.environ.get("TAVILY_API_KEY"))

    def search(self, query: str, limit: int = 8, since_year: Optional[int] = None) -> List[Source]:
        if not self.available():
            return []
        import json
        import urllib.request

        body = json.dumps(
            {
                "api_key": os.environ["TAVILY_API_KEY"],
                "query": query,
                "max_results": min(limit, 10),
                "search_depth": "advanced",
            }
        ).encode()
        request = urllib.request.Request(
            "https://api.tavily.com/search",
            data=body,
            headers={"Content-Type": "application/json", "User-Agent": self.client.user_agent},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.client.timeout) as raw:
                payload = json.loads(raw.read().decode())
        except Exception:
            return []

        return [
            Source(
                title=_clean(item.get("title")),
                url=item.get("url", ""),
                provider=self.name,
                tier=SourceTier.WEB,
                abstract=_clean(item.get("content")),
                found_by_query=query,
                extra={"score": item.get("score")},
            )
            for item in payload.get("results", [])
        ]


class BraveProvider(SearchProvider):
    """Brave Search API. Requiere `BRAVE_API_KEY`."""

    name = "brave"
    BASE = "https://api.search.brave.com/res/v1/web/search"

    def available(self) -> bool:
        return bool(os.environ.get("BRAVE_API_KEY"))

    def search(self, query: str, limit: int = 8, since_year: Optional[int] = None) -> List[Source]:
        if not self.available():
            return []
        params = {"q": query, "count": min(limit, 20)}
        try:
            payload = self.client.get_json(
                f"{self.BASE}?{urllib.parse.urlencode(params)}",
                headers={
                    "X-Subscription-Token": os.environ["BRAVE_API_KEY"],
                    "Accept": "application/json",
                },
            )
        except HttpError:
            return []

        return [
            Source(
                title=_clean(item.get("title")),
                url=item.get("url", ""),
                provider=self.name,
                tier=SourceTier.WEB,
                abstract=_strip_tags(item.get("description")),
                found_by_query=query,
            )
            for item in payload.get("web", {}).get("results", [])
        ]


class StaticProvider(SearchProvider):
    """
    Proveedor en memoria para pruebas y ejecuciones offline deterministas.

    Hace coincidir la consulta con el título y el resumen de un corpus fijo.
    """

    name = "static"

    def __init__(self, client: Optional[HttpClient], corpus: List[Source]):
        self.client = client  # type: ignore[assignment]
        self.corpus = corpus

    def search(self, query: str, limit: int = 8, since_year: Optional[int] = None) -> List[Source]:
        terms = {t for t in re.findall(r"\w+", query.lower()) if len(t) > 3}
        scored = []
        for source in self.corpus:
            if since_year and source.year and source.year < since_year:
                continue
            haystack = f"{source.title} {source.abstract or ''}".lower()
            overlap = sum(1 for term in terms if term in haystack)
            if overlap:
                copy = Source(**{**source.__dict__, "found_by_query": query})
                scored.append((overlap, copy))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [source for _, source in scored[:limit]]


# ═══════════════════════════════════════════════════════════════════════════
# Utilidades
# ═══════════════════════════════════════════════════════════════════════════


def _decode_inverted_abstract(inverted: Optional[Dict[str, List[int]]]) -> Optional[str]:
    """
    OpenAlex entrega los resúmenes como índice invertido (palabra → posiciones)
    por motivos de licencia. Esto los reconstruye en texto corrido.
    """
    if not inverted:
        return None
    positions: Dict[int, str] = {}
    for word, indexes in inverted.items():
        for index in indexes:
            positions[index] = word
    return " ".join(positions[i] for i in sorted(positions)) or None


def _strip_tags(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    return _clean(re.sub(r"<[^>]+>", " ", text)) or None


def _crossref_year(item: Dict[str, Any]) -> Optional[int]:
    for key in ("published-print", "published-online", "issued", "created"):
        parts = (item.get(key) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            return int(parts[0][0])
    return None


def build_default_providers(client: HttpClient, lang: str = "en") -> List[SearchProvider]:
    """
    Construye el conjunto estándar de proveedores y descarta los no disponibles.

    El orden es deliberado: primero lo académico (citable), luego la web general
    (contexto). La síntesis procesa las fuentes en el orden en que llegan.
    """
    candidates: List[SearchProvider] = [
        OpenAlexProvider(client),
        CrossrefProvider(client),
        ArxivProvider(client),
        WikipediaProvider(client, lang=lang),
        TavilyProvider(client),
        BraveProvider(client),
    ]
    return [provider for provider in candidates if provider.available()]
