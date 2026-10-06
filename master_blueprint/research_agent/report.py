"""
Renderizado del informe.

El Markdown resultante está pensado para que un tercero pueda **auditarlo sin
volver a ejecutar el agente**: cada afirmación lleva su cita literal, la
bibliografía da el identificador persistente y la fecha de acceso, y el registro
final lista todas las consultas lanzadas con su número de resultados.
"""

from __future__ import annotations

import json
from typing import List, Optional, Sequence

from .citations import CitationRegistry, inline_quote
from .models import Claim, Confidence, Finding, ResearchReport

CONFIDENCE_BADGE = {
    Confidence.ALTA: "🟢 Alta",
    Confidence.MEDIA: "🟡 Media",
    Confidence.BAJA: "🔴 Baja",
    Confidence.DISPUTADA: "⚠️ Disputada",
}


def render_markdown(
    report: ResearchReport,
    registry: Optional[CitationRegistry] = None,
    title: Optional[str] = None,
    max_claims_per_finding: int = 4,
    include_audit: bool = True,
) -> str:
    """Genera el informe completo en Markdown."""
    # `registry is None` y no `registry or ...`: un registro recién creado tiene
    # longitud cero y por tanto es falsy, así que el atajo descartaría en
    # silencio el registro que pasó quien llama y la numeración se perdería.
    registry = CitationRegistry() if registry is None else registry
    lines: List[str] = []

    lines += _header(report, title)
    lines += _executive_summary(report, registry)
    lines += _findings(report, registry, max_claims_per_finding)
    lines += _evidence_matrix(report, registry)
    lines += _open_questions(report)
    lines += _bibliography(registry)
    if include_audit:
        lines += _audit_trail(report)

    return "\n".join(lines).rstrip() + "\n"


def render_json(report: ResearchReport, indent: int = 2) -> str:
    """Exporta el informe como JSON, para diffs entre ejecuciones o análisis posterior."""
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=indent)


# ═══════════════════════════════════════════════════════════════════════════
# Secciones
# ═══════════════════════════════════════════════════════════════════════════


def _header(report: ResearchReport, title: Optional[str]) -> List[str]:
    peer_reviewed = sum(1 for s in report.sources if s.tier.weight >= 1.0)
    groups = len({source.independence_key for source in report.sources})
    triangulated = sum(1 for claim in report.all_claims if claim.is_triangulated)

    return [
        f"# {title or 'Informe de investigación'}",
        "",
        f"**Pregunta:** {report.question}",
        "",
        "| Métrica | Valor |",
        "| :--- | :--- |",
        f"| Sub-preguntas investigadas | {len(report.sub_questions)} |",
        f"| Cobertura alcanzada | {report.coverage_ratio:.0%} |",
        f"| Fuentes únicas | {len(report.sources)} |",
        f"| Grupos autorales independientes | {groups} |",
        f"| Fuentes revisadas por pares | {peer_reviewed} |",
        f"| Afirmaciones sintetizadas | {len(report.all_claims)} |",
        f"| Afirmaciones trianguladas | {triangulated} |",
        f"| Consultas ejecutadas | {len(report.audit_trail)} |",
        f"| Inicio / fin (UTC) | {report.started_at} → {report.finished_at or '—'} |",
        "",
        "> Informe generado automáticamente. Las afirmaciones marcadas como "
        "**disputadas** o no trianguladas requieren verificación humana antes de "
        "usarse como base de decisión.",
        "",
    ]


def _executive_summary(report: ResearchReport, registry: CitationRegistry) -> List[str]:
    solid = [
        claim
        for claim in report.all_claims
        if claim.confidence in (Confidence.ALTA, Confidence.MEDIA)
    ]
    solid.sort(key=_claim_strength, reverse=True)

    lines = ["## 1. Resumen ejecutivo", ""]
    if not solid:
        lines += [
            "No se consolidó ninguna afirmación con confianza media o superior. "
            "Revisa las brechas abiertas en la sección 4 antes de sacar conclusiones.",
            "",
        ]
        return lines

    lines.append(
        f"De {len(report.all_claims)} afirmaciones sintetizadas, {len(solid)} alcanzan "
        "confianza media o alta. Las más respaldadas son:"
    )
    lines.append("")

    # Una misma afirmación puede emerger desde varias sub-preguntas; en el
    # resumen se lista una sola vez para no simular más respaldo del que hay.
    seen: set = set()
    shown = 0
    for claim in solid:
        fingerprint = _shorten(claim.text, 120).lower()
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        lines.append(
            f"- {CONFIDENCE_BADGE[claim.confidence]} — {_shorten(claim.text, 260)} "
            f"{registry.markers(claim.evidence)}"
        )
        shown += 1
        if shown >= 5:
            break

    lines.append("")
    return lines


def _findings(report: ResearchReport, registry: CitationRegistry, max_claims: int) -> List[str]:
    lines = ["## 2. Hallazgos por sub-pregunta", ""]

    for index, finding in enumerate(report.findings, start=1):
        sub_question = finding.sub_question
        status = "✅ cubierta" if sub_question.is_covered else "⚠️ brecha"
        lines += [
            f"### 2.{index} {sub_question.text}",
            "",
            f"*Tipo:* `{sub_question.kind.value}` · *Fuentes:* {sub_question.sources_found} ({status})",
            "",
            finding.summary,
            "",
        ]

        if not finding.claims:
            lines += ["_Sin evidencia utilizable para esta sub-pregunta._", ""]
            continue

        for claim in sorted(finding.claims, key=_claim_strength, reverse=True)[:max_claims]:
            lines += _render_claim(claim, registry)

        lines += ["<details>", "<summary>Consultas lanzadas</summary>", ""]
        lines += [f"- `{query}`" for query in sub_question.queries]
        lines += ["", "</details>", ""]

    return lines


def _render_claim(claim: Claim, registry: CitationRegistry) -> List[str]:
    lines = [
        f"**{CONFIDENCE_BADGE[claim.confidence]}** · "
        f"{len(claim.evidence)} evidencia(s) en {len(claim.independent_groups)} grupo(s) independiente(s)",
        "",
    ]
    for item in claim.evidence:
        lines.append(f"> {inline_quote(item, registry)}")
        lines.append(">")
    if lines[-1] == ">":
        lines.pop()

    if claim.contradictions:
        lines.append("")
        for note in claim.contradictions:
            lines.append(f"⚠️ **Conflicto detectado:** {note}")
    lines.append("")
    return lines


def _evidence_matrix(report: ResearchReport, registry: CitationRegistry) -> List[str]:
    """
    Tabla afirmación → confianza → fuentes.

    Es la pieza que convierte el informe en algo revisable: permite repartir la
    verificación entre varias personas, una fila cada una.
    """
    lines = [
        "## 3. Matriz de evidencia",
        "",
        "Cada fila es una afirmación verificable con sus fuentes de respaldo. "
        "Úsala como lista de verificación: una fila, un revisor.",
        "",
        "| # | Afirmación (extracto) | Confianza | Grupos | Referencias | Verificado por |",
        "| :-- | :--- | :--- | :-- | :--- | :--- |",
    ]

    # La misma afirmación puede surgir desde varias sub-preguntas. En una lista
    # de verificación eso sería trabajo duplicado para el revisor.
    seen: set = set()
    number = 0
    for claim in sorted(report.all_claims, key=_claim_strength, reverse=True):
        fingerprint = _shorten(claim.text, 120).lower()
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        number += 1
        lines.append(
            f"| {number} "
            f"| {_shorten(claim.text, 150).replace('|', '/')} "
            f"| {CONFIDENCE_BADGE[claim.confidence]} "
            f"| {len(claim.independent_groups)} "
            f"| {registry.markers(claim.evidence)} "
            f"| _(pendiente)_ |"
        )

    lines.append("")
    return lines


def _open_questions(report: ResearchReport) -> List[str]:
    lines = ["## 4. Brechas y preguntas abiertas", ""]
    if not report.open_questions:
        lines += ["No se detectaron brechas de cobertura ni afirmaciones disputadas.", ""]
        return lines

    for item in report.open_questions:
        lines.append(f"- {item}")
    lines.append("")
    return lines


def _bibliography(registry: CitationRegistry) -> List[str]:
    lines = ["## 5. Bibliografía", ""]
    if not len(registry):
        lines += ["_No se citó ninguna fuente._", ""]
        return lines

    for entry in registry.bibliography():
        lines.append(f"{entry}")
        lines.append("")
    return lines


def _audit_trail(report: ResearchReport) -> List[str]:
    """Registro completo de consultas, para que la ejecución sea reproducible."""
    lines = [
        "## 6. Registro de auditoría",
        "",
        "Toda consulta lanzada, en orden. Permite reproducir la investigación y "
        "detectar si una conclusión depende de una única búsqueda afortunada.",
        "",
        "<details>",
        "<summary>Ver las "
        f"{len(report.audit_trail)} consultas</summary>",
        "",
        "| Ronda | Proveedor | Consulta | Resultados | Nota |",
        "| :-- | :--- | :--- | :-- | :--- |",
    ]
    for step in report.audit_trail:
        lines.append(
            f"| {step.round_number} | {step.provider} | `{step.query}` "
            f"| {step.results} | {step.note or '—'} |"
        )
    lines += ["", "</details>", ""]
    return lines


# ═══════════════════════════════════════════════════════════════════════════
# Utilidades
# ═══════════════════════════════════════════════════════════════════════════


def _claim_strength(claim: Claim) -> tuple:
    """Ordena por confianza, luego triangulación, luego relevancia máxima."""
    confidence_rank = {
        Confidence.ALTA: 3,
        Confidence.MEDIA: 2,
        Confidence.DISPUTADA: 1,
        Confidence.BAJA: 0,
    }
    return (
        confidence_rank[claim.confidence],
        len(claim.independent_groups),
        max((item.relevance for item in claim.evidence), default=0.0),
    )


def _shorten(text: str, limit: int) -> str:
    clean = " ".join(text.split())
    return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"
