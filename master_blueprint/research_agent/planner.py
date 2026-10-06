"""
Planificador: convierte una pregunta en un plan de investigación.

Dos responsabilidades:

1. **Descomponer** la pregunta en cinco tipos de sub-pregunta. La lista fija es
   intencional: obliga a buscar evidencia en contra (CONTRASTE) y literatura
   reciente (NOVEDAD) aunque nadie lo pida, que es justo lo que una búsqueda
   improvisada suele omitir.

2. **Reformular** en las rondas siguientes. Las consultas de la ronda 2 en
   adelante no salen de plantillas, sino del vocabulario real de los documentos
   ya recuperados. Así el agente aprende la terminología del campo en lugar de
   repetir las palabras del usuario.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Dict, Iterable, List, Optional, Sequence

from .models import Source, SubQuestion, SubQuestionKind

STOPWORDS = {
    # español
    "como", "cual", "cuales", "cuando", "donde", "para", "porque", "pero", "este",
    "esta", "esto", "esos", "esas", "sobre", "entre", "desde", "hasta", "mas",
    "muy", "son", "con", "sin", "por", "los", "las", "del", "que", "una", "uno",
    "unos", "unas", "sus", "esa", "ese", "hay", "ser", "está", "están", "puede",
    "pueden", "debe", "deben", "cómo", "qué", "cuál", "cuáles", "según", "también",
    "tiene", "tienen", "hacer", "mejor", "forma", "caso", "casos", "tipo", "tipos",
    # inglés
    "about", "above", "after", "again", "against", "because", "been", "before",
    "being", "below", "between", "both", "could", "does", "doing", "down", "during",
    "each", "from", "further", "have", "having", "here", "how", "into", "itself",
    "more", "most", "once", "only", "other", "over", "same", "should", "some",
    "such", "than", "that", "their", "them", "then", "there", "these", "they",
    "this", "those", "through", "under", "until", "very", "were", "what", "when",
    "where", "which", "while", "will", "with", "would", "your",
}

# Modificadores en inglés a propósito: OpenAlex, Crossref y arXiv indexan
# mayoritariamente en inglés, así que una consulta en español recupera mucho menos.
QUERY_TEMPLATES: Dict[SubQuestionKind, Sequence[str]] = {
    SubQuestionKind.DEFINICION: ("{core} definition framework", "{core} concept review"),
    SubQuestionKind.EVIDENCIA: ("{core} case study empirical results", "{core} quantitative impact measured"),
    SubQuestionKind.METODO: ("{core} model formulation methodology", "{core} algorithm implementation"),
    SubQuestionKind.CONTRASTE: ("{core} limitations criticism", "{core} comparison alternative approach"),
    SubQuestionKind.NOVEDAD: ("{core} recent advances", "{core} state of the art"),
}

SUBQUESTION_TEMPLATES: Dict[SubQuestionKind, str] = {
    SubQuestionKind.DEFINICION: "¿Cómo se define y delimita «{core}» en la literatura?",
    SubQuestionKind.EVIDENCIA: "¿Qué evidencia empírica cuantificada existe sobre «{core}»?",
    SubQuestionKind.METODO: "¿Qué métodos y formulaciones se usan para abordar «{core}»?",
    SubQuestionKind.CONTRASTE: "¿Qué limitaciones, críticas o enfoques alternativos se reportan sobre «{core}»?",
    SubQuestionKind.NOVEDAD: "¿Qué hay de nuevo o en discusión activa sobre «{core}»?",
}


class ResearchPlanner:
    """Genera el plan inicial y las reformulaciones de cada ronda."""

    def __init__(self, question: str, max_core_terms: int = 6):
        self.question = question.strip()
        self.core_terms = extract_key_terms(self.question, limit=max_core_terms)
        self.core = " ".join(self.core_terms) if self.core_terms else self.question
        self._used_queries: set[str] = set()

    # ── plan inicial ─────────────────────────────────────────────────────────

    def initial_plan(self, kinds: Optional[Iterable[SubQuestionKind]] = None) -> List[SubQuestion]:
        """Crea una sub-pregunta por tipo, cada una con sus consultas de arranque."""
        selected = list(kinds) if kinds else list(SubQuestionKind)
        plan = []
        for kind in selected:
            queries = [
                template.format(core=self.core) for template in QUERY_TEMPLATES[kind]
            ]
            self._used_queries.update(queries)
            plan.append(
                SubQuestion(
                    text=SUBQUESTION_TEMPLATES[kind].format(core=self.core),
                    kind=kind,
                    queries=queries,
                )
            )
        return plan

    # ── reformulación ────────────────────────────────────────────────────────

    def refine_queries(
        self,
        sub_question: SubQuestion,
        harvested: Sequence[str],
        max_queries: int = 2,
    ) -> List[str]:
        """
        Construye consultas de seguimiento combinando el núcleo de la pregunta con
        términos aprendidos de los documentos recuperados.

        Devuelve sólo consultas nuevas: repetir una búsqueda ya hecha gastaría una
        ronda sin añadir información.
        """
        anchor = " ".join(self.core_terms[:3]) or self.core
        candidates = []
        for term in harvested:
            if term in self.core_terms:
                continue
            candidates.append(f"{anchor} {term}")
            if sub_question.kind == SubQuestionKind.CONTRASTE:
                candidates.append(f"{term} limitations drawbacks")

        fresh = []
        for candidate in candidates:
            normalized = candidate.lower().strip()
            if normalized in self._used_queries:
                continue
            self._used_queries.add(normalized)
            fresh.append(candidate)
            if len(fresh) >= max_queries:
                break
        return fresh


def extract_key_terms(text: str, limit: int = 6) -> List[str]:
    """
    Extrae los términos con más carga semántica de un texto.

    Heurística deliberadamente simple: tokens largos, sin stopwords ni números,
    ordenados por frecuencia y, a igualdad, por orden de aparición.
    """
    tokens = [
        token.lower()
        for token in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][\w\-]{2,}", text)
    ]
    meaningful = [t for t in tokens if t not in STOPWORDS and len(t) > 3]
    if not meaningful:
        return []

    counts = Counter(meaningful)
    first_seen = {term: index for index, term in enumerate(reversed(meaningful))}
    ranked = sorted(meaningful, key=lambda t: (-counts[t], -first_seen[t]))

    unique: List[str] = []
    for term in ranked:
        if term not in unique:
            unique.append(term)
        if len(unique) >= limit:
            break
    return unique


def harvest_terms(sources: Sequence[Source], exclude: Iterable[str] = (), limit: int = 8) -> List[str]:
    """
    Extrae el vocabulario dominante de un conjunto de fuentes.

    Un término cuenta una vez por documento, no una vez por aparición: así una
    sola fuente verbosa no secuestra la siguiente ronda de búsqueda.
    """
    excluded = {term.lower() for term in exclude}
    document_frequency: Counter[str] = Counter()

    for source in sources:
        text = f"{source.title} {source.abstract or ''}"
        terms = {
            token.lower()
            for token in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][\w\-]{3,}", text)
            if token.lower() not in STOPWORDS and len(token) > 4
        }
        document_frequency.update(terms - excluded)

    # Un término que aparece en una sola fuente es ruido, no señal del campo.
    return [term for term, count in document_frequency.most_common(limit * 3) if count >= 2][:limit]
