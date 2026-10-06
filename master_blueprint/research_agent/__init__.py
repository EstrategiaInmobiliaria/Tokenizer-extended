"""
Agente de investigación web multi-paso con síntesis de fuentes y citas.

Pensado para preguntas que no se resuelven con una sola búsqueda: descompone la
pregunta, busca en varias rondas cerrando las brechas que detecta, deduplica y
tritura las fuentes, y devuelve un informe donde cada afirmación lleva su cita
literal y su nivel de confianza.

Ejemplo:

    from master_blueprint.research_agent import ResearchAgent, render_markdown

    agent = ResearchAgent()
    report = agent.research(
        "reducción de tiempos de setup mediante secuenciación en líneas de empaque"
    )
    print(render_markdown(report))

Funciona sin ninguna API key: los proveedores por defecto (OpenAlex, Crossref,
arXiv, Wikipedia) son abiertos. Si existen `TAVILY_API_KEY` o `BRAVE_API_KEY`
en el entorno, se añade además búsqueda web general.
"""

from .agent import AgentConfig, ResearchAgent
from .citations import CitationRegistry, format_reference
from .http_client import HttpClient
from .models import (
    Claim,
    Confidence,
    Evidence,
    Finding,
    ResearchReport,
    Source,
    SourceTier,
    SubQuestion,
    SubQuestionKind,
)
from .planner import ResearchPlanner
from .providers import (
    ArxivProvider,
    BraveProvider,
    CrossrefProvider,
    OpenAlexProvider,
    SearchProvider,
    StaticProvider,
    TavilyProvider,
    WikipediaProvider,
    build_default_providers,
)
from .report import render_json, render_markdown

__version__ = "1.0.0"

__all__ = [
    "AgentConfig",
    "ArxivProvider",
    "BraveProvider",
    "CitationRegistry",
    "Claim",
    "Confidence",
    "CrossrefProvider",
    "Evidence",
    "Finding",
    "HttpClient",
    "OpenAlexProvider",
    "ResearchAgent",
    "ResearchPlanner",
    "ResearchReport",
    "SearchProvider",
    "Source",
    "SourceTier",
    "StaticProvider",
    "SubQuestion",
    "SubQuestionKind",
    "TavilyProvider",
    "WikipediaProvider",
    "build_default_providers",
    "format_reference",
    "render_json",
    "render_markdown",
]
