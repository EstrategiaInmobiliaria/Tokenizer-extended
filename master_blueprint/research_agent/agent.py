"""
Orquestador del agente de investigación.

El bucle es el siguiente:

    plan → buscar → deduplicar → medir cobertura → reformular sobre las brechas
         → (repetir) → extraer evidencia → sintetizar → citar

Lo que lo hace multi-paso de verdad no es que busque varias veces, sino que la
ronda N+1 **depende** del resultado de la ronda N: sólo se reabren las
sub-preguntas mal cubiertas y las nuevas consultas se construyen con el
vocabulario aprendido de los documentos ya recuperados.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set

from .citations import CitationRegistry
from .http_client import HttpClient, default_cache_dir
from .models import (
    Confidence,
    Evidence,
    Finding,
    ResearchReport,
    SearchStep,
    Source,
    SubQuestion,
    SubQuestionKind,
)
from .planner import ResearchPlanner, harvest_terms
from .providers import SearchProvider, build_default_providers
from .synthesis import (
    build_claims,
    content_words,
    dedupe_sources,
    extract_evidence,
    is_on_topic,
    score_relevance,
    summarize_finding,
)

ProgressCallback = Callable[[str], None]


@dataclass
class AgentConfig:
    """Parámetros de ejecución. Los valores por defecto buscan un equilibrio
    entre profundidad y número de peticiones a APIs públicas."""

    rounds: int = 2
    results_per_query: int = 8
    max_sources_per_subquestion: int = 12
    min_sources_per_subquestion: int = 2
    target_sources_per_subquestion: int = 6
    min_groups_per_subquestion: int = 3
    # Filtro temático de entrada. Sin él el informe se llena de trabajos que
    # comparten una palabra con la pregunta y nada más.
    min_term_overlap: float = 0.30
    min_matched_terms: int = 2
    novelty_window_years: int = 3
    evidence_per_subquestion: int = 8
    lang: str = "en"
    cache_dir: Optional[str] = None
    offline: bool = False
    kinds: Optional[Sequence[SubQuestionKind]] = None
    # Términos de búsqueda explícitos; útil para preguntar en un idioma y
    # buscar en otro.
    core_terms: Optional[Sequence[str]] = None
    current_year: int = field(default_factory=lambda: datetime.now(timezone.utc).year)


class ResearchAgent:
    """
    Agente de investigación web multi-paso con síntesis y citas.

    Uso mínimo:

        agent = ResearchAgent()
        report = agent.research("reducción de tiempos de setup en líneas de empaque")
        print(render_markdown(report))
    """

    def __init__(
        self,
        providers: Optional[Sequence[SearchProvider]] = None,
        config: Optional[AgentConfig] = None,
        client: Optional[HttpClient] = None,
    ):
        self.config = config or AgentConfig()
        self.client = client or HttpClient(
            cache_dir=self.config.cache_dir or default_cache_dir(),
            offline=self.config.offline,
        )
        self.providers = list(
            providers if providers is not None else build_default_providers(self.client, self.config.lang)
        )
        self.registry = CitationRegistry()
        self._question_terms: Set[str] = set()

    # ── API pública ──────────────────────────────────────────────────────────

    def research(
        self,
        question: str,
        on_progress: Optional[ProgressCallback] = None,
    ) -> ResearchReport:
        """Ejecuta la investigación completa y devuelve el informe estructurado."""
        emit = on_progress or (lambda _message: None)

        if not self.providers:
            raise RuntimeError(
                "No hay proveedores de búsqueda disponibles. Revisa la conectividad "
                "de red o define al menos uno (TAVILY_API_KEY, BRAVE_API_KEY…)."
            )

        planner = ResearchPlanner(question, core_terms=self.config.core_terms)
        plan = planner.initial_plan(self.config.kinds)
        report = ResearchReport(question=question, sub_questions=plan)
        self._question_terms = set(planner.core_terms)

        emit(f"Plan: {len(plan)} sub-preguntas; proveedores: {', '.join(p.name for p in self.providers)}")

        catalog: Dict[str, Source] = {}
        assignments: Dict[int, Set[str]] = {index: set() for index in range(len(plan))}

        for round_number in range(1, self.config.rounds + 1):
            pending = self._pending_subquestions(plan, round_number, catalog, assignments)
            if not pending:
                emit(f"Ronda {round_number}: cobertura completa, no hace falta seguir buscando.")
                break

            emit(f"Ronda {round_number}: {len(pending)} sub-pregunta(s) por reforzar.")

            for index in pending:
                sub_question = plan[index]
                queries = self._queries_for_round(planner, sub_question, catalog, assignments[index], round_number)

                for query in queries:
                    if round_number > 1:
                        sub_question.queries.append(query)
                    found = self._run_query(query, sub_question, round_number, report)
                    for source in found:
                        if not is_on_topic(
                            source,
                            self._question_terms,
                            self.config.min_term_overlap,
                            self.config.min_matched_terms,
                        ):
                            continue
                        catalog[source.source_id] = source
                        assignments[index].add(source.source_id)

                self._consolidate(catalog, assignments)
                sub_question.sources_found = len(assignments[index])
                emit(
                    f"  · {sub_question.kind.value}: {sub_question.sources_found} fuente(s) "
                    f"{'✓' if sub_question.is_covered else '— brecha'}"
                )

        report.sources = sorted(catalog.values(), key=lambda s: (-(s.year or 0), s.title))
        report.findings = [
            self._build_finding(plan[index], [catalog[sid] for sid in assignments[index] if sid in catalog])
            for index in range(len(plan))
        ]
        report.open_questions = self._collect_open_questions(report)
        report.finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

        emit(
            f"Listo: {len(report.sources)} fuentes únicas, "
            f"{len(report.all_claims)} afirmaciones, "
            f"cobertura {report.coverage_ratio:.0%}."
        )
        return report

    # ── pasos internos ───────────────────────────────────────────────────────

    def _pending_subquestions(
        self,
        plan: Sequence[SubQuestion],
        round_number: int,
        catalog: Dict[str, Source],
        assignments: Dict[int, Set[str]],
    ) -> List[int]:
        """
        En la primera ronda se atienden todas; después, sólo las que siguen flojas.

        Una sub-pregunta se reabre por dos motivos distintos:

        - **Volumen**: no llegó al objetivo de fuentes pertinentes. El umbral se
          mide sobre fuentes que pasaron el filtro temático, no sobre resultados
          brutos; cualquier consulta devuelve decenas de títulos y contarlos daría
          por cubierta una sub-pregunta sin material utilizable.
        - **Diversidad**: tiene fuentes de sobra pero casi todas del mismo grupo
          autoral. Buscar más de lo mismo no ayuda, pero seguir con el vocabulario
          aprendido sí puede alcanzar a otros equipos, y sin varios grupos la
          triangulación es imposible por construcción.
        """
        if round_number == 1:
            return list(range(len(plan)))

        pending = []
        for index, sub_question in enumerate(plan):
            groups = {
                catalog[sid].independence_key
                for sid in assignments.get(index, set())
                if sid in catalog
            }
            too_few = sub_question.sources_found < self.config.target_sources_per_subquestion
            too_uniform = len(groups) < self.config.min_groups_per_subquestion
            if too_few or too_uniform:
                pending.append(index)
        return pending

    def _queries_for_round(
        self,
        planner: ResearchPlanner,
        sub_question: SubQuestion,
        catalog: Dict[str, Source],
        assigned: Set[str],
        round_number: int,
    ) -> List[str]:
        if round_number == 1:
            return list(sub_question.queries)

        # El vocabulario se aprende de lo ya recuperado para esta sub-pregunta;
        # si todavía no hay nada, se recurre al catálogo global.
        pool = [catalog[sid] for sid in assigned if sid in catalog] or list(catalog.values())
        harvested = harvest_terms(pool, exclude=planner.core_terms, limit=6)
        return planner.refine_queries(sub_question, harvested)

    def _run_query(
        self,
        query: str,
        sub_question: SubQuestion,
        round_number: int,
        report: ResearchReport,
    ) -> List[Source]:
        """Lanza una consulta contra todos los proveedores y registra la auditoría."""
        since_year = (
            self.config.current_year - self.config.novelty_window_years
            if sub_question.kind is SubQuestionKind.NOVEDAD
            else None
        )

        collected: List[Source] = []
        for provider in self.providers:
            try:
                results = provider.search(
                    query, limit=self.config.results_per_query, since_year=since_year
                )
                note = ""
            except Exception as exc:  # un proveedor caído no puede abortar la investigación
                results = []
                note = f"error: {type(exc).__name__}: {exc}"

            report.audit_trail.append(
                SearchStep(
                    round_number=round_number,
                    provider=provider.name,
                    query=query,
                    results=len(results),
                    note=note,
                )
            )
            collected.extend(results)

        return dedupe_sources(collected)

    def _consolidate(self, catalog: Dict[str, Source], assignments: Dict[int, Set[str]]) -> None:
        """
        Deduplica el catálogo global y reescribe las asignaciones.

        Hace falta porque la fusión por título puede colapsar dos entradas que ya
        estaban asignadas a distintas sub-preguntas; sin esto, los identificadores
        viejos quedarían colgando.
        """
        merged = dedupe_sources(catalog.values())
        survivors = {source.source_id: source for source in merged}

        title_index = {_title_key(source): source.source_id for source in merged}
        remap = {
            old_id: title_index.get(_title_key(source), old_id)
            for old_id, source in catalog.items()
        }

        catalog.clear()
        catalog.update(survivors)

        for index, ids in assignments.items():
            assignments[index] = {
                remap.get(sid, sid) for sid in ids if remap.get(sid, sid) in survivors
            }

    def _build_finding(self, sub_question: SubQuestion, sources: Sequence[Source]) -> Finding:
        """Convierte las fuentes de una sub-pregunta en afirmaciones citadas."""
        query_terms = content_words(sub_question.text) | content_words(" ".join(sub_question.queries))
        prefer_numeric = sub_question.kind is SubQuestionKind.EVIDENCIA

        ranked = sorted(
            sources,
            key=lambda source: score_relevance(source, query_terms, self.config.current_year),
            reverse=True,
        )[: self.config.max_sources_per_subquestion]

        evidence: List[Evidence] = []
        for source in ranked:
            item = extract_evidence(source, query_terms, prefer_numeric=prefer_numeric)
            if item:
                evidence.append(item)
            if len(evidence) >= self.config.evidence_per_subquestion:
                break

        claims = build_claims(evidence)
        return Finding(
            sub_question=sub_question,
            summary=summarize_finding(sub_question, claims),
            claims=claims,
        )

    def _collect_open_questions(self, report: ResearchReport) -> List[str]:
        """
        Lo que el informe *no* resolvió.

        Se declara explícitamente porque una brecha silenciada se lee como
        ausencia de evidencia, y no es lo mismo que evidencia de ausencia.
        """
        open_questions: List[str] = []

        for sub_question in report.sub_questions:
            if not sub_question.is_covered:
                open_questions.append(
                    f"Cobertura insuficiente ({sub_question.sources_found} fuente/s) para: "
                    f"{sub_question.text}"
                )

        for claim in report.all_claims:
            if claim.confidence is Confidence.DISPUTADA:
                open_questions.append(
                    f"Afirmación disputada que requiere verificación manual: "
                    f"«{claim.text[:120]}…» — {'; '.join(claim.contradictions)}"
                )

        single_source = [c for c in report.all_claims if not c.is_triangulated]
        if single_source:
            open_questions.append(
                f"{len(single_source)} afirmación(es) dependen de una sola fuente y no "
                "están trianguladas; no deberían presentarse como conclusión firme."
            )

        return open_questions


def _title_key(source: Source) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "", (source.title or "").lower())[:120]
