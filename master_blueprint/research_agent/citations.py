"""
Registro de citas.

Asigna a cada fuente un número estable en el orden en que se cita por primera
vez y produce la bibliografía final. La numeración se lleva aquí y en ningún otro
sitio, para que sea imposible que el cuerpo del informe diga `[4]` y la
bibliografía liste otra cosa en esa posición.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

from .models import Evidence, Source, normalize_doi


class CitationRegistry:
    """Numera fuentes bajo demanda y construye la bibliografía."""

    def __init__(self) -> None:
        self._numbers: Dict[str, int] = {}
        self._sources: Dict[str, Source] = {}

    def register(self, source: Source) -> int:
        """Devuelve el número de la fuente, asignándole uno nuevo si es la primera vez."""
        key = source.source_id
        if key not in self._numbers:
            self._numbers[key] = len(self._numbers) + 1
            self._sources[key] = source
        return self._numbers[key]

    def marker(self, source: Source) -> str:
        """Marca de cita en línea, p. ej. `[3]`."""
        return f"[{self.register(source)}]"

    def markers(self, evidence: Iterable[Evidence]) -> str:
        """Marca combinada para varias evidencias, ordenada y sin repetir: `[1][4]`."""
        numbers = sorted({self.register(item.source) for item in evidence})
        return "".join(f"[{number}]" for number in numbers)

    @property
    def entries(self) -> List[Tuple[int, Source]]:
        return sorted(
            ((number, self._sources[key]) for key, number in self._numbers.items()),
            key=lambda pair: pair[0],
        )

    def bibliography(self) -> List[str]:
        """Bibliografía numerada, en el orden en que aparecen las citas."""
        return [f"[{number}] {format_reference(source)}" for number, source in self.entries]

    def __len__(self) -> int:
        return len(self._numbers)


def format_reference(source: Source) -> str:
    """
    Formatea una referencia en estilo tipo APA, con la trazabilidad que necesita
    una auditoría: identificador persistente (DOI si lo hay) y fecha de acceso.
    """
    pieces = [format_authors(source.authors)]
    pieces.append(f"({source.year})" if source.year else "(s.f.)")
    pieces.append(f"{source.title.rstrip('.')}.")

    if source.venue:
        pieces.append(f"*{source.venue}*.")

    identifier = (
        f"https://doi.org/{normalize_doi(source.doi)}" if source.doi else source.url
    )
    if identifier:
        pieces.append(identifier)

    tags = [f"vía {source.provider}", f"consultado {source.retrieved_at[:10]}"]
    if source.is_open_access:
        tags.append("acceso abierto")
    confirmed = source.extra.get("confirmed_by") or []
    if len(confirmed) > 1:
        tags.append("confirmado en " + "/".join(confirmed))
    pieces.append(f"[{'; '.join(tags)}]")

    return " ".join(piece for piece in pieces if piece)


def format_authors(authors: Sequence[str], max_listed: int = 3) -> str:
    """`Apellido, N.` con `et al.` a partir del cuarto autor."""
    if not authors:
        return "Autoría no identificada."

    formatted = [_initialize(author) for author in authors[:max_listed]]
    if len(authors) > max_listed:
        return ", ".join(formatted) + ", et al."
    joined = (
        formatted[0] if len(formatted) == 1
        else ", ".join(formatted[:-1]) + f", & {formatted[-1]}"
    )
    # Las iniciales ya terminan en punto; añadir otro produce «Lovelace, A..».
    return joined if joined.endswith(".") else joined + "."


def _initialize(author: str) -> str:
    parts = [part for part in author.replace(",", " ").split() if part]
    if not parts:
        return author
    if len(parts) == 1:
        return parts[0]
    surname = parts[-1]
    initials = " ".join(f"{part[0].upper()}." for part in parts[:-1])
    return f"{surname}, {initials}"


def inline_quote(evidence: Evidence, registry: CitationRegistry, max_length: int = 240) -> str:
    """Cita textual entrecomillada con su localizador y su número de referencia."""
    quote = evidence.quote
    if len(quote) > max_length:
        quote = quote[: max_length - 1].rstrip() + "…"
    return f'«{quote}» ({evidence.locator}) {registry.marker(evidence.source)}'
