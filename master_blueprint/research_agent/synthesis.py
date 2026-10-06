"""
Síntesis: de un montón de documentos a un conjunto de afirmaciones citadas.

El recorrido es: deduplicar → puntuar relevancia → extraer la frase concreta que
respalda algo → agrupar frases que dicen lo mismo → comprobar si se contradicen →
asignar confianza.

El criterio que gobierna todo es la **triangulación por dominio**: dos documentos
del mismo sitio no son dos confirmaciones. Es la diferencia entre "lo dicen varias
fuentes" y "lo repite la misma fuente varias veces".
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .models import Claim, Confidence, Evidence, Source, SubQuestion, SubQuestionKind
from .planner import STOPWORDS

# Marcas de que un texto niega o matiza, usadas para detectar desacuerdos.
NEGATION_MARKERS = {
    "not", "no", "fails", "failed", "cannot", "unable", "contrary", "however",
    "although", "despite", "limitation", "limitations", "drawback", "unlike",
    "contradicts", "disputed", "inconclusive", "insufficient",
}

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ0-9])")
NUMBER_PATTERN = re.compile(r"(\d+(?:[.,]\d+)?)\s*(%|percent|per cent)")


# ═══════════════════════════════════════════════════════════════════════════
# 1. Deduplicación
# ═══════════════════════════════════════════════════════════════════════════


def dedupe_sources(sources: Iterable[Source]) -> List[Source]:
    """
    Funde duplicados conservando la versión mejor documentada.

    Dos pasadas, porque el mismo trabajo llega por caminos distintos: por DOI
    (OpenAlex y Crossref devuelven el mismo artículo) y por título normalizado
    (el preprint en arXiv y la versión publicada no comparten DOI).
    """
    by_key: Dict[str, Source] = {}

    for source in sources:
        if not source.url and not source.doi:
            continue
        key = source.source_id
        existing = by_key.get(key)
        by_key[key] = _merge(existing, source) if existing else source

    by_title: Dict[str, Source] = {}
    for source in by_key.values():
        title_key = _normalize_title(source.title)
        existing = by_title.get(title_key)
        by_title[title_key] = _merge(existing, source) if existing else source

    return _merge_near_duplicate_titles(list(by_title.values()))


def _merge_near_duplicate_titles(sources: List[Source], threshold: float = 0.85) -> List[Source]:
    """
    Funde trabajos cuyo título coincide casi del todo.

    Es el caso del preprint y su versión publicada: no comparten DOI y el título
    cambia en una palabra («…for Product Sequencing» frente a «…for Modeling
    Product Sequencing»), así que la comparación exacta los deja como dos. Si se
    cuelan los dos, el agente los toma por confirmación independiente y declara
    consenso donde sólo hay un trabajo contado dos veces.
    """
    survivors: List[Source] = []

    for source in sources:
        tokens = _title_tokens(source.title)
        duplicate_of = None

        if len(tokens) >= 4:
            for index, kept in enumerate(survivors):
                other = _title_tokens(kept.title)
                if len(other) < 4:
                    continue
                if len(tokens & other) / len(tokens | other) >= threshold:
                    duplicate_of = index
                    break

        if duplicate_of is None:
            survivors.append(source)
        else:
            survivors[duplicate_of] = _merge(survivors[duplicate_of], source)

    return survivors


def _title_tokens(title: str) -> Set[str]:
    return content_words(title)


def _merge(primary: Optional[Source], secondary: Source) -> Source:
    """Conserva la fuente de mayor autoridad y le completa los huecos con la otra."""
    if primary is None:
        return secondary

    winner, loser = (
        (primary, secondary)
        if primary.tier.weight >= secondary.tier.weight
        else (secondary, primary)
    )

    for attribute in ("doi", "abstract", "venue", "year", "cited_by_count", "is_open_access", "language"):
        if not getattr(winner, attribute) and getattr(loser, attribute):
            setattr(winner, attribute, getattr(loser, attribute))
    if not winner.authors and loser.authors:
        winner.authors = loser.authors

    providers = set(winner.extra.get("confirmed_by", [winner.provider]))
    providers.add(loser.provider)
    winner.extra["confirmed_by"] = sorted(providers)
    return winner


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (title or "").lower())[:120]


# ═══════════════════════════════════════════════════════════════════════════
# 2. Relevancia
# ═══════════════════════════════════════════════════════════════════════════


def content_words(text: str) -> Set[str]:
    """Palabras con carga semántica, en minúsculas y sin stopwords."""
    return {
        token.lower()
        for token in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][\w\-]{2,}", text or "")
        if token.lower() not in STOPWORDS and len(token) > 3
    }


def term_overlap_ratio(source: Source, question_terms: Set[str]) -> float:
    """
    Fracción de los términos núcleo de la pregunta que aparecen en la fuente.

    Es el filtro temático de entrada, separado de la puntuación compuesta a
    propósito: sin él, una fuente ajena al tema pero muy citada y reciente
    acumula puntos por autoridad y frescura hasta colarse en el informe. Aquí
    sólo cuenta si habla de lo que se preguntó.
    """
    if not question_terms:
        return 0.0
    haystack = content_words(f"{source.title} {source.abstract or ''}")
    return len(question_terms & haystack) / len(question_terms)


def is_on_topic(
    source: Source,
    question_terms: Set[str],
    min_ratio: float = 0.30,
    min_terms: int = 2,
) -> bool:
    """
    Decide si una fuente entra en el informe.

    Combina fracción y conteo absoluto a propósito. Sólo con la fracción, una
    pregunta formulada con términos muy específicos se vuelve casi imposible de
    satisfacer y el agente devuelve tres resultados; sólo con el conteo, una
    pregunta larga admitiría cualquier cosa que coincida en dos palabras. El
    doble criterio sostiene los dos extremos.
    """
    if not question_terms:
        return False
    haystack = content_words(f"{source.title} {source.abstract or ''}")
    matched = len(question_terms & haystack)
    required = min(min_terms, len(question_terms))
    return matched >= required and matched / len(question_terms) >= min_ratio


def score_relevance(source: Source, query_terms: Set[str], current_year: int = 2026) -> float:
    """
    Puntuación compuesta en [0, 1].

    Mezcla cuatro señales: solapamiento léxico con la consulta (lo que más pesa),
    autoridad del tipo de fuente, frescura y citas recibidas. Las citas entran en
    escala logarítmica suave para que un clásico muy citado no aplaste siempre a
    un trabajo reciente y pertinente.
    """
    if not query_terms:
        return 0.0

    haystack = content_words(f"{source.title} {source.abstract or ''}")
    overlap = len(query_terms & haystack) / len(query_terms)

    recency = 0.0
    if source.year:
        age = max(0, current_year - source.year)
        recency = max(0.0, 1.0 - age / 25.0)

    citations = 0.0
    if source.cited_by_count:
        citations = min(1.0, source.cited_by_count / 200.0)

    return round(
        0.55 * overlap + 0.25 * source.tier.weight + 0.12 * recency + 0.08 * citations,
        4,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 3. Extracción de evidencia
# ═══════════════════════════════════════════════════════════════════════════


def extract_evidence(
    source: Source,
    query_terms: Set[str],
    min_overlap: int = 2,
    prefer_numeric: bool = False,
) -> Optional[Evidence]:
    """
    Elige del resumen la frase que mejor respalda la sub-pregunta.

    Se cita una frase textual, no un parafraseo: un revisor tiene que poder buscar
    esa cadena en el documento original y encontrarla.
    """
    abstract = (source.abstract or "").strip()
    text = abstract or source.title
    if not text:
        return None

    # Un título no es evidencia del mismo rango que una frase del resumen; el
    # localizador lo deja explícito para quien revise.
    locator = "resumen" if abstract else "título"

    sentences = [s.strip() for s in SENTENCE_SPLIT.split(text) if len(s.strip()) > 40]
    if not sentences:
        sentences = [text]

    best_sentence, best_score = None, 0.0
    for sentence in sentences:
        overlap = len(query_terms & content_words(sentence))
        if overlap < min_overlap:
            continue
        score = float(overlap)
        if prefer_numeric and NUMBER_PATTERN.search(sentence):
            score += 2.0  # una cifra es más auditable que una afirmación cualitativa
        if score > best_score:
            best_sentence, best_score = sentence, score

    if best_sentence is None:
        return None

    return Evidence(
        source=source,
        quote=_truncate(best_sentence, 400),
        locator=locator,
        query=source.found_by_query,
        relevance=score_relevance(source, query_terms),
    )


def _truncate(text: str, limit: int) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"


# ═══════════════════════════════════════════════════════════════════════════
# 4. Agrupación en afirmaciones
# ═══════════════════════════════════════════════════════════════════════════


def build_claims(
    evidence: Sequence[Evidence],
    similarity_threshold: float = 0.33,
    min_distinctive_terms: int = 2,
) -> List[Claim]:
    """
    Agrupa en una sola afirmación las evidencias que dicen lo mismo.

    El agrupamiento es léxico, no semántico, y el criterio es **deliberadamente
    estricto**. Midiendo sobre resúmenes reales, los pares más "parecidos" sólo
    compartían vocabulario de redacción académica —`study`, `paper`, `research`,
    `planning`—, de modo que un umbral permisivo no produce triangulación: produce
    triangulación falsa, que es peor que ninguna, porque le pone un sello de
    confianza alta a dos trabajos que nunca hablaron del mismo resultado.

    Por eso se exige lo siguiente para fundir dos evidencias:

    1. Solapamiento ponderado por rareza: los términos frecuentes en el conjunto
       pesan poco, así que coincidir en palabras de relleno no acerca nada.
    2. Al menos `min_distinctive_terms` términos compartidos *poco frecuentes*,
       los que de verdad identifican un tema concreto.

    La consecuencia esperada es que muchas afirmaciones queden con una sola
    fuente. Eso no es un fallo del agente: es el estado real de la evidencia, y
    el informe lo declara en vez de disimularlo.
    """
    ordered = sorted(evidence, key=lambda item: item.relevance, reverse=True)
    weights, rare_terms = _term_statistics([item.quote for item in ordered])
    clusters: List[Tuple[Set[str], Claim]] = []

    for item in ordered:
        words = content_words(item.quote)
        if not words:
            continue

        attached = False
        for cluster_words, claim in clusters:
            shared = words & cluster_words
            if len(shared & rare_terms) < min_distinctive_terms:
                continue
            if _weighted_containment(words, cluster_words, weights) < similarity_threshold:
                continue
            if item.source.source_id not in {e.source.source_id for e in claim.evidence}:
                claim.evidence.append(item)
            cluster_words |= words
            attached = True
            break

        if not attached:
            clusters.append((set(words), Claim(text=item.quote, evidence=[item])))

    claims = [claim for _, claim in clusters]
    for claim in claims:
        claim.contradictions = detect_contradictions(claim)
        claim.confidence = assign_confidence(claim)
    return claims


def _term_statistics(quotes: Sequence[str]) -> Tuple[Dict[str, float], Set[str]]:
    """
    Calcula el peso de cada término y el subconjunto de términos distintivos.

    El peso es una IDF desplazada para que nunca sea negativa ni cero: con pocos
    documentos, una IDF cruda dejaría los términos universales en peso negativo
    y las similitudes dejarían de tener sentido.
    """
    import math
    from collections import Counter

    total = max(1, len(quotes))
    document_frequency: Counter[str] = Counter()
    for quote in quotes:
        document_frequency.update(content_words(quote))

    weights = {
        term: math.log((total + 1) / (1 + frequency)) + 1.0
        for term, frequency in document_frequency.items()
    }
    # "Poco frecuente" = presente en como mucho un cuarto del material recuperado.
    rarity_cutoff = max(2, total // 4)
    rare_terms = {
        term for term, frequency in document_frequency.items() if frequency <= rarity_cutoff
    }
    return weights, rare_terms


def _weighted_containment(left: Set[str], right: Set[str], weights: Dict[str, float]) -> float:
    """
    Solapamiento ponderado respecto al texto más corto.

    Se normaliza por el menor de los dos y no por la unión (Jaccard) porque una
    frase breve y precisa contenida en otra más larga sí es la misma afirmación,
    y Jaccard la penalizaría sólo por la diferencia de longitud.
    """
    if not left or not right:
        return 0.0
    shared = sum(weights.get(term, 1.0) for term in left & right)
    smaller = min(
        sum(weights.get(term, 1.0) for term in left),
        sum(weights.get(term, 1.0) for term in right),
    )
    return shared / smaller if smaller else 0.0


# ═══════════════════════════════════════════════════════════════════════════
# 5. Contradicciones y confianza
# ═══════════════════════════════════════════════════════════════════════════


def detect_contradictions(claim: Claim) -> List[str]:
    """
    Señala desacuerdos dentro de una misma afirmación.

    Detecta dos patrones: cifras porcentuales incompatibles entre fuentes que
    hablan de lo mismo, y mezcla de evidencia afirmativa con evidencia que niega
    o matiza. No resuelve el conflicto: lo deja marcado para revisión humana,
    que es lo correcto cuando el desacuerdo puede venir de contextos distintos.
    """
    notes: List[str] = []
    if len(claim.evidence) < 2:
        return notes

    measurements: List[Tuple[float, str]] = []
    for item in claim.evidence:
        for value, _unit in NUMBER_PATTERN.findall(item.quote):
            measurements.append((float(value.replace(",", ".")), item.source.source_id))

    if len(measurements) >= 2:
        values = [value for value, _ in measurements]
        low, high = min(values), max(values)
        # Tolerancia del 20%: por debajo son redondeos o métricas levemente distintas.
        if high > 0 and (high - low) / high > 0.20:
            detail = ", ".join(f"{value:g}% ({sid})" for value, sid in measurements)
            notes.append(f"Cifras divergentes entre fuentes: {detail}")

    with_negation = {
        item.source.source_id
        for item in claim.evidence
        if content_words(item.quote) & NEGATION_MARKERS
    }
    if with_negation and len(with_negation) < len(claim.evidence):
        notes.append(
            "Evidencia mixta: "
            + ", ".join(sorted(with_negation))
            + " introduce negación o salvedad frente al resto."
        )

    return notes


def assign_confidence(claim: Claim) -> Confidence:
    """
    Traduce la estructura de la evidencia a un nivel de confianza.

    - DISPUTADA: hay contradicciones sin resolver, gane quien gane en número.
    - BAJA, siempre, si toda la evidencia sale de títulos: un título anuncia un
      tema, no demuestra un resultado. Tres títulos que comparten palabras son
      una coincidencia léxica, no una confirmación, y dejar que escalen a ALTA
      es la vía más rápida a un informe que parece sólido y no lo es.
    - ALTA: confirmada por dos o más grupos independientes, con al menos uno
      revisado por pares.
    - MEDIA: confirmada por dos grupos sin respaldo académico, o bien una sola
      fuente revisada por pares.
    """
    if claim.contradictions:
        return Confidence.DISPUTADA

    if not any(item.locator == "resumen" for item in claim.evidence):
        return Confidence.BAJA

    groups = len(claim.independent_groups)
    if groups >= 2 and claim.has_peer_review:
        return Confidence.ALTA
    if groups >= 2 or claim.has_peer_review:
        return Confidence.MEDIA
    return Confidence.BAJA


# ═══════════════════════════════════════════════════════════════════════════
# 6. Redacción del resumen por hallazgo
# ═══════════════════════════════════════════════════════════════════════════

_KIND_OPENERS: Dict[SubQuestionKind, str] = {
    SubQuestionKind.DEFINICION: "Sobre la delimitación del concepto",
    SubQuestionKind.EVIDENCIA: "Sobre la evidencia cuantificada",
    SubQuestionKind.METODO: "Sobre los métodos empleados",
    SubQuestionKind.CONTRASTE: "Sobre limitaciones y alternativas",
    SubQuestionKind.NOVEDAD: "Sobre los desarrollos recientes",
}


def summarize_finding(sub_question: SubQuestion, claims: Sequence[Claim]) -> str:
    """
    Redacta el resumen de un hallazgo describiendo el *estado de la evidencia*.

    No intenta parafrasear el contenido —eso lo hacen las citas literales— sino
    decir cuánto respaldo hay y de qué calidad, que es lo que el lector necesita
    para saber cuánto fiarse del bloque que viene a continuación.
    """
    opener = _KIND_OPENERS[sub_question.kind]

    if not claims:
        return (
            f"{opener}: no se recuperó evidencia utilizable con las consultas "
            f"{_format_list(sub_question.queries)}. Queda como brecha abierta."
        )

    triangulated = [c for c in claims if c.is_triangulated]
    disputed = [c for c in claims if c.confidence is Confidence.DISPUTADA]
    groups = sorted({key for claim in claims for key in claim.independent_groups})
    peer_reviewed = sum(
        1
        for claim in claims
        for item in claim.evidence
        if item.source.tier.weight >= 1.0
    )

    parts = [
        f"{opener}, se consolidaron {len(claims)} afirmación(es) a partir de "
        f"{len(groups)} grupo(s) independiente(s), con {peer_reviewed} respaldo(s) "
        f"de literatura revisada por pares."
    ]
    if triangulated:
        parts.append(
            f"{len(triangulated)} están trianguladas, es decir, confirmadas por más "
            "de un grupo autoral."
        )
    else:
        parts.append(
            "Ninguna está triangulada: cada afirmación descansa en un solo grupo "
            "autoral, así que son indicios, no consenso."
        )
    if disputed:
        parts.append(
            f"{len(disputed)} quedan marcadas como disputadas y requieren revisión "
            "humana antes de citarse."
        )
    if not sub_question.is_covered:
        parts.append(
            "La cobertura es insuficiente (menos de dos fuentes), así que conviene "
            "tratar este bloque como provisional."
        )
    return " ".join(parts)


def _format_list(items: Sequence[str]) -> str:
    return ", ".join(f"«{item}»" for item in items) if items else "(ninguna)"
