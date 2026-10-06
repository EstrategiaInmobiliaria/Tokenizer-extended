"""
Modelos de datos del agente de investigación.

El diseño gira alrededor de una regla: **ninguna afirmación existe sin evidencia
rastreable**. Por eso `Claim` no guarda texto suelto, sino una lista de `Evidence`,
y cada `Evidence` apunta a una `Source` identificable (DOI o URL) junto con la
consulta exacta que la encontró y la fecha de acceso.

Jerarquía:

    ResearchReport
    └── Finding (un hallazgo por sub-pregunta)
        └── Claim (afirmación verificable)
            └── Evidence (cita textual + localizador)
                └── Source (documento con metadatos bibliográficos)
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SourceTier(Enum):
    """
    Nivel de autoridad de una fuente.

    El orden importa: se usa para ponderar la confianza y para desempatar
    cuando dos fuentes se contradicen.
    """

    PEER_REVIEWED = ("peer_reviewed", "Artículo con revisión por pares", 1.00)
    PREPRINT = ("preprint", "Preprint o working paper", 0.70)
    INSTITUTIONAL = ("institutional", "Norma, organismo o institución", 0.85)
    REFERENCE = ("reference", "Obra de referencia (enciclopedia)", 0.50)
    WEB = ("web", "Página web general", 0.35)
    UNKNOWN = ("unknown", "Origen no determinado", 0.20)

    def __init__(self, code: str, label: str, weight: float):
        self.code = code
        self.label = label
        self.weight = weight


class SubQuestionKind(Enum):
    """
    Tipos de sub-pregunta que genera el planificador.

    Cubrir los cinco tipos es lo que convierte una búsqueda en una investigación:
    sin CONTRASTE el informe sólo confirma lo que ya se creía, y sin NOVEDAD
    se queda anclado en la literatura vieja.
    """

    DEFINICION = "definicion"
    EVIDENCIA = "evidencia"
    METODO = "metodo"
    CONTRASTE = "contraste"
    NOVEDAD = "novedad"


class Confidence(Enum):
    """Nivel de confianza asignado a una afirmación tras la triangulación."""

    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"
    DISPUTADA = "disputada"


@dataclass
class Source:
    """Un documento recuperado, con los metadatos mínimos para poder citarlo."""

    title: str
    url: str
    provider: str
    tier: SourceTier = SourceTier.UNKNOWN
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None
    cited_by_count: Optional[int] = None
    is_open_access: Optional[bool] = None
    language: Optional[str] = None
    retrieved_at: str = field(default_factory=_utc_now)
    found_by_query: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def source_id(self) -> str:
        """Identificador estable: DOI normalizado si existe, si no un hash de la URL."""
        if self.doi:
            return "doi:" + normalize_doi(self.doi)
        return "url:" + hashlib.sha1(self.url.encode("utf-8")).hexdigest()[:12]

    @property
    def domain(self) -> str:
        """Host de la URL, normalizado sin `www.`."""
        match = re.match(r"https?://([^/]+)", self.url or "")
        host = match.group(1).lower() if match else "desconocido"
        return host[4:] if host.startswith("www.") else host

    @property
    def independence_key(self) -> str:
        """
        Clave que decide si dos fuentes cuentan como confirmación independiente.

        El dominio no sirve para literatura académica: casi todos los artículos
        resuelven por `doi.org`, así que usarlo haría que veinte papers de veinte
        equipos distintos parecieran una sola fuente. Para trabajos académicos la
        unidad de independencia es el **grupo autoral** —confirmar algo significa
        que otro equipo llegó a lo mismo—, y para el resto de la web sigue siendo
        el dominio.
        """
        if self.tier in (SourceTier.PEER_REVIEWED, SourceTier.PREPRINT) and self.authors:
            return f"autores:{self.first_author_surname.lower()}"
        return f"dominio:{self.domain}"

    @property
    def first_author_surname(self) -> str:
        if not self.authors:
            return "Anónimo"
        return self.authors[0].strip().split()[-1]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["tier"] = self.tier.code
        data["source_id"] = self.source_id
        data["domain"] = self.domain
        return data


@dataclass
class Evidence:
    """
    Fragmento textual que respalda una afirmación.

    `locator` indica dónde dentro del documento se encontró (p. ej. "resumen",
    "sección 4"), para que un revisor humano pueda ir al punto exacto.
    """

    source: Source
    quote: str
    locator: str = "resumen"
    query: Optional[str] = None
    relevance: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source.source_id,
            "quote": self.quote,
            "locator": self.locator,
            "query": self.query,
            "relevance": round(self.relevance, 4),
        }


@dataclass
class Claim:
    """Afirmación verificable con su evidencia, confianza y contradicciones."""

    text: str
    evidence: List[Evidence] = field(default_factory=list)
    confidence: Confidence = Confidence.BAJA
    contradictions: List[str] = field(default_factory=list)

    @property
    def independent_groups(self) -> List[str]:
        """Grupos independientes que respaldan la afirmación (orden de aparición)."""
        seen: List[str] = []
        for item in self.evidence:
            if item.source.independence_key not in seen:
                seen.append(item.source.independence_key)
        return seen

    @property
    def is_triangulated(self) -> bool:
        return len(self.independent_groups) >= 2

    @property
    def has_peer_review(self) -> bool:
        return any(item.source.tier is SourceTier.PEER_REVIEWED for item in self.evidence)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": self.confidence.value,
            "triangulated": self.is_triangulated,
            "independent_groups": self.independent_groups,
            "contradictions": self.contradictions,
            "evidence": [e.to_dict() for e in self.evidence],
        }


@dataclass
class SubQuestion:
    """Una sub-pregunta del plan, con las consultas que se lanzaron para resolverla."""

    text: str
    kind: SubQuestionKind
    queries: List[str] = field(default_factory=list)
    sources_found: int = 0

    @property
    def is_covered(self) -> bool:
        """Se considera cubierta con al menos dos fuentes; con menos queda como brecha."""
        return self.sources_found >= 2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "kind": self.kind.value,
            "queries": self.queries,
            "sources_found": self.sources_found,
            "covered": self.is_covered,
        }


@dataclass
class Finding:
    """Hallazgo: la síntesis de lo encontrado para una sub-pregunta."""

    sub_question: SubQuestion
    summary: str
    claims: List[Claim] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sub_question": self.sub_question.to_dict(),
            "summary": self.summary,
            "claims": [c.to_dict() for c in self.claims],
        }


@dataclass
class SearchStep:
    """Un paso del registro de auditoría: qué se buscó, dónde y con qué resultado."""

    round_number: int
    provider: str
    query: str
    results: int
    timestamp: str = field(default_factory=_utc_now)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchReport:
    """Resultado completo de una investigación, listo para exportar o auditar."""

    question: str
    sub_questions: List[SubQuestion] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)
    sources: List[Source] = field(default_factory=list)
    audit_trail: List[SearchStep] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    started_at: str = field(default_factory=_utc_now)
    finished_at: Optional[str] = None

    @property
    def all_claims(self) -> List[Claim]:
        return [claim for finding in self.findings for claim in finding.claims]

    @property
    def coverage_ratio(self) -> float:
        """Fracción de sub-preguntas que alcanzaron el umbral de cobertura."""
        if not self.sub_questions:
            return 0.0
        covered = sum(1 for sq in self.sub_questions if sq.is_covered)
        return covered / len(self.sub_questions)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "coverage_ratio": round(self.coverage_ratio, 3),
            "sub_questions": [sq.to_dict() for sq in self.sub_questions],
            "findings": [f.to_dict() for f in self.findings],
            "sources": [s.to_dict() for s in self.sources],
            "audit_trail": [step.to_dict() for step in self.audit_trail],
            "open_questions": self.open_questions,
        }


def normalize_doi(doi: str) -> str:
    """Reduce un DOI a su forma canónica en minúsculas, sin prefijo de resolución."""
    value = (doi or "").strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.startswith(prefix):
            value = value[len(prefix) :]
    return value.strip("/")
