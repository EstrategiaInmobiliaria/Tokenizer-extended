"""
Tests del agente de investigación.

Todos corren offline con `StaticProvider` y un corpus fijo: la suite no debe
depender de que una API pública esté arriba ni de que devuelva hoy lo mismo que
ayer. Lo que se verifica aquí es la lógica de síntesis, que es donde el agente
puede equivocarse en silencio.

Ejecutar desde `master_blueprint/`:

    pytest tests/test_research_agent.py -v
"""

import pytest

from research_agent import (
    AgentConfig,
    CitationRegistry,
    HttpClient,
    Confidence,
    ResearchAgent,
    ResearchPlanner,
    Source,
    SourceTier,
    StaticProvider,
    SubQuestionKind,
    build_default_providers,
    format_reference,
    render_json,
    render_markdown,
)
from research_agent.providers import _crossref_tier, _decode_inverted_abstract
from research_agent.planner import extract_key_terms, harvest_terms
from research_agent.synthesis import (
    assign_confidence,
    build_claims,
    dedupe_sources,
    detect_contradictions,
    extract_evidence,
    is_on_topic,
    term_overlap_ratio,
)
from research_agent.models import Claim, Evidence


# ═══════════════════════════════════════════════════════════════════════════
# Corpus de prueba
# ═══════════════════════════════════════════════════════════════════════════


def make_source(
    title="Setup time reduction in packaging lines",
    url="https://doi.org/10.1000/a",
    doi="10.1000/a",
    tier=SourceTier.PEER_REVIEWED,
    authors=("Ada Lovelace", "Alan Turing"),
    year=2024,
    abstract=None,
    provider="openalex",
    **kwargs,
):
    return Source(
        title=title,
        url=url,
        doi=doi,
        tier=tier,
        authors=list(authors),
        year=year,
        abstract=abstract,
        provider=provider,
        **kwargs,
    )


@pytest.fixture
def corpus():
    """Corpus mínimo pero realista: temas solapados, un duplicado y una web."""
    return [
        make_source(
            title="Product sequencing in pharmaceutical packaging lines",
            doi="10.1000/seq1",
            url="https://doi.org/10.1000/seq1",
            authors=("Esbeydi Villicaña", "Isidro Soria"),
            year=2026,
            abstract=(
                "This study models product sequencing on pharmaceutical packaging lines. "
                "A Traveling Salesman Problem formulation with Miller-Tucker-Zemlin constraints "
                "minimizes setup times. The framework reduces setup times by 13.6% compared to "
                "manual scheduling practices across four production lines."
            ),
            cited_by_count=12,
        ),
        make_source(
            title="Clustering and sequencing for setup reduction in packaging",
            doi="10.1000/seq2",
            url="https://doi.org/10.1000/seq2",
            authors=("Marta Ruiz", "Peter Chen"),
            year=2023,
            abstract=(
                "We apply similarity clustering before sequencing products on packaging lines. "
                "Setup times decrease by 12.9% relative to the manual baseline, confirming that "
                "grouping by active substance avoids major changeovers."
            ),
            cited_by_count=40,
        ),
        make_source(
            title="Limits of metaheuristics for packaging line sequencing",
            doi="10.1000/lim1",
            url="https://doi.org/10.1000/lim1",
            authors=("Hiroshi Tanaka",),
            year=2025,
            abstract=(
                "Although ant colony methods are widely used for sequencing, this paper shows that "
                "they do not guarantee optimality and fail on large packaging instances. "
                "Reported setup reductions of 40% could not be reproduced."
            ),
        ),
        Source(
            title="Single-Minute Exchange of Die",
            url="https://en.wikipedia.org/wiki/SMED",
            provider="wikipedia",
            tier=SourceTier.REFERENCE,
            venue="Wikipedia (en)",
            abstract=(
                "SMED is a lean method for reducing setup times on production lines by converting "
                "internal setup operations into external ones."
            ),
        ),
    ]


@pytest.fixture
def agent(corpus):
    config = AgentConfig(rounds=1, results_per_query=5, offline=True, min_term_overlap=0.1)
    return ResearchAgent(providers=[StaticProvider(None, corpus)], config=config)


# ═══════════════════════════════════════════════════════════════════════════
# Planificador
# ═══════════════════════════════════════════════════════════════════════════


class TestPlanner:
    def test_plan_covers_all_kinds(self):
        plan = ResearchPlanner("setup time reduction in packaging lines").initial_plan()
        assert {sub.kind for sub in plan} == set(SubQuestionKind)
        assert all(sub.queries for sub in plan)

    def test_contrast_subquestion_is_always_planned(self):
        """Buscar evidencia en contra no puede quedar a criterio del usuario."""
        plan = ResearchPlanner("¿funciona la secuenciación TSP?").initial_plan()
        assert any(sub.kind is SubQuestionKind.CONTRASTE for sub in plan)

    def test_key_terms_drop_stopwords(self):
        terms = extract_key_terms("¿Cómo se reduce el tiempo de setup en las líneas de empaque?")
        assert "como" not in terms
        assert "setup" in terms

    def test_refined_queries_are_never_repeated(self):
        planner = ResearchPlanner("packaging line sequencing")
        first = planner.refine_queries(planner.initial_plan()[0], ["changeover", "clustering"])
        second = planner.refine_queries(planner.initial_plan()[0], ["changeover", "clustering"])
        assert first
        assert not set(first) & set(second)

    def test_core_terms_can_be_overridden_to_search_in_another_language(self):
        planner = ResearchPlanner(
            "¿Cómo se reducen los tiempos de preparación en líneas de empaque?",
            core_terms=["setup", "time", "packaging", "lines"],
        )
        assert planner.core_terms == ["setup", "time", "packaging", "lines"]
        assert all("setup" in query for query in planner.initial_plan()[0].queries)

    def test_harvest_requires_term_in_two_sources(self, corpus):
        """Un término de un único documento es ruido, no vocabulario del campo."""
        harvested = harvest_terms(corpus, exclude=["packaging"], limit=10)
        assert "miller-tucker-zemlin" not in harvested
        assert "sequencing" in harvested


# ═══════════════════════════════════════════════════════════════════════════
# Deduplicación e independencia
# ═══════════════════════════════════════════════════════════════════════════


class TestDeduplication:
    def test_same_doi_collapses(self):
        duplicates = [make_source(provider="openalex"), make_source(provider="crossref")]
        assert len(dedupe_sources(duplicates)) == 1

    def test_merge_records_confirming_providers(self):
        merged = dedupe_sources([make_source(provider="openalex"), make_source(provider="crossref")])[0]
        assert merged.extra["confirmed_by"] == ["crossref", "openalex"]

    def test_preprint_and_published_version_collapse_by_title(self):
        published = make_source(doi="10.1000/x", url="https://doi.org/10.1000/x")
        preprint = make_source(
            doi=None, url="https://arxiv.org/abs/1", tier=SourceTier.PREPRINT, abstract="Texto."
        )
        merged = dedupe_sources([published, preprint])
        assert len(merged) == 1
        assert merged[0].tier is SourceTier.PEER_REVIEWED  # gana la versión de mayor autoridad
        assert merged[0].abstract == "Texto."  # pero hereda lo que le faltaba

    def test_near_identical_titles_collapse(self):
        """Preprint y versión publicada: distinto DOI, un título casi igual."""
        published = make_source(
            title="A prescriptive analytics framework for product sequencing in packaging lines",
            doi="10.1016/j.health.1",
        )
        preprint = make_source(
            title="A Prescriptive Analytics Framework for Modeling Product Sequencing in Packaging Lines",
            doi="10.2139/ssrn.1",
            tier=SourceTier.PREPRINT,
        )
        assert len(dedupe_sources([published, preprint])) == 1

    def test_unrelated_titles_are_not_collapsed(self):
        one = make_source(title="Sequencing products on pharmaceutical packaging lines", doi="10.1000/a")
        two = make_source(title="Thermal degradation of polymer films in storage", doi="10.1000/b")
        assert len(dedupe_sources([one, two])) == 2

    def test_academic_independence_is_by_author_not_domain(self):
        """Dos papers distintos resuelven ambos por doi.org y aun así son independientes."""
        one = make_source(doi="10.1000/a", url="https://doi.org/10.1000/a", authors=("Ada Lovelace",))
        two = make_source(doi="10.1000/b", url="https://doi.org/10.1000/b", authors=("Grace Hopper",))
        claim = Claim(text="x", evidence=[Evidence(one, "q"), Evidence(two, "q")])
        assert len(claim.independent_groups) == 2

    def test_shared_author_in_any_position_breaks_independence(self):
        """
        El caso real que motivó esto: preprint y artículo del mismo equipo listan
        a los mismos investigadores en distinto orden. Mirar sólo al primer autor
        los daría por confirmaciones independientes.
        """
        journal = make_source(doi="10.1000/a", authors=("Esbeydi Villicaña", "Isidro Soria"))
        preprint = make_source(
            doi="10.1000/b", authors=("Isidro Soria", "Esbeydi Villicaña"), tier=SourceTier.PREPRINT
        )
        claim = Claim(text="x", evidence=[Evidence(journal, "q"), Evidence(preprint, "q")])
        assert len(claim.independent_groups) == 1
        assert not claim.is_triangulated

    def test_shared_coauthor_chains_groups_transitively(self):
        a = make_source(doi="10.1000/a", authors=("Ada Lovelace", "Shared Person"))
        b = make_source(doi="10.1000/b", authors=("Shared Person", "Grace Hopper"))
        c = make_source(doi="10.1000/c", authors=("Grace Hopper",))
        claim = Claim(text="x", evidence=[Evidence(s, "q") for s in (a, b, c)])
        assert len(claim.independent_groups) == 1

    def test_web_independence_falls_back_to_domain(self):
        page = Source(title="t", url="https://example.org/a", provider="brave", tier=SourceTier.WEB)
        assert page.identity_keys == {"dominio:example.org"}


# ═══════════════════════════════════════════════════════════════════════════
# Relevancia y evidencia
# ═══════════════════════════════════════════════════════════════════════════


class TestEvidence:
    def test_off_topic_source_is_rejected(self):
        """Un paper que sólo comparte la palabra «pharmaceutical» no es del tema."""
        question_terms = {"setup", "sequencing", "packaging", "pharmaceutical"}
        off_topic = make_source(
            title="Removal of pharmaceutical products from wastewater using microalgae",
            abstract="This review covers wastewater treatment with microalgae.",
        )
        assert term_overlap_ratio(off_topic, question_terms) < 0.30
        assert not is_on_topic(off_topic, question_terms)

    def test_specific_question_still_admits_two_term_matches(self):
        """
        Con términos muy específicos, exigir una fracción alta deja al agente sin
        material. El piso absoluto de dos términos evita ese colapso.
        """
        question_terms = {"setup", "sequencing", "packaging", "pharmaceutical", "clustering", "changeover"}
        relevant = make_source(
            title="Sequencing products on packaging lines",
            abstract="A model that orders jobs to cut transition effort.",
        )
        assert term_overlap_ratio(relevant, question_terms) < 0.34
        assert is_on_topic(relevant, question_terms)

    def test_numeric_sentence_is_preferred_as_evidence(self, corpus):
        evidence = extract_evidence(
            corpus[0], {"setup", "times", "reduces", "framework"}, prefer_numeric=True
        )
        assert evidence is not None
        assert "13.6%" in evidence.quote

    def test_evidence_from_title_is_labelled_as_such(self):
        source = make_source(title="Setup time reduction in packaging lines", abstract=None)
        evidence = extract_evidence(source, {"setup", "time", "reduction", "packaging"}, min_overlap=2)
        assert evidence is not None
        assert evidence.locator == "título"

    def test_no_evidence_when_nothing_matches(self):
        assert extract_evidence(make_source(abstract="Unrelated text."), {"quantum", "entanglement"}) is None


# ═══════════════════════════════════════════════════════════════════════════
# Afirmaciones, contradicciones y confianza
# ═══════════════════════════════════════════════════════════════════════════


class TestClaims:
    def test_quotes_saying_the_same_thing_cluster_into_one_claim(self):
        evidence = [
            Evidence(
                make_source(doi="10.1000/a", authors=("Ada Lovelace",)),
                "The framework reduces setup times on packaging lines versus manual scheduling.",
            ),
            Evidence(
                make_source(doi="10.1000/b", authors=("Grace Hopper",)),
                "Setup times on packaging lines fall against the manual scheduling baseline.",
            ),
        ]
        claims = build_claims(evidence)
        assert len(claims) == 1
        assert claims[0].is_triangulated

    def test_boilerplate_overlap_does_not_fabricate_triangulation(self):
        """
        El modo de fallo que de verdad importa: tres resúmenes distintos comparten
        palabras de redacción académica. Si eso los fundiera, el informe declararía
        confianza alta sobre un consenso que no existe.
        """
        evidence = [
            Evidence(
                make_source(doi="10.1000/a", authors=("Ada Lovelace",)),
                "The purpose of this study is to evaluate the proposed research approach.",
            ),
            Evidence(
                make_source(doi="10.1000/b", authors=("Grace Hopper",)),
                "The objective of this study is to evaluate a research framework for turbines.",
            ),
            Evidence(
                make_source(doi="10.1000/c", authors=("Alan Turing",)),
                "This study presents research evaluating soil permeability in cold climates.",
            ),
        ]
        claims = build_claims(evidence)
        assert len(claims) == 3
        assert not any(claim.is_triangulated for claim in claims)

    def test_quotes_about_different_things_stay_separate(self):
        evidence = [
            Evidence(make_source(doi="10.1000/a"), "Setup times fall when products are clustered."),
            Evidence(
                make_source(doi="10.1000/b", authors=("Other",)),
                "Microalgae remove contaminants from municipal wastewater streams.",
            ),
        ]
        assert len(build_claims(evidence)) == 2

    def test_divergent_percentages_are_flagged(self):
        claim = Claim(
            text="setup reduction",
            evidence=[
                Evidence(make_source(doi="10.1000/a"), "Setup times fell by 13.6% overall."),
                Evidence(
                    make_source(doi="10.1000/b", authors=("Other Person",)),
                    "Setup times fell by 40% overall.",
                ),
            ],
        )
        notes = detect_contradictions(claim)
        assert any("divergentes" in note for note in notes)

    def test_close_percentages_are_not_flagged(self):
        """13.6% vs 12.9% es variación de contexto, no contradicción."""
        claim = Claim(
            text="setup reduction",
            evidence=[
                Evidence(make_source(doi="10.1000/a"), "Setup times fell by 13.6%."),
                Evidence(make_source(doi="10.1000/b", authors=("Other",)), "Setup times fell by 12.9%."),
            ],
        )
        assert not detect_contradictions(claim)

    def test_contradiction_forces_disputed_confidence(self):
        claim = Claim(
            text="x",
            evidence=[
                Evidence(make_source(doi="10.1000/a"), "Reduction of 10%."),
                Evidence(make_source(doi="10.1000/b", authors=("Other",)), "Reduction of 90%."),
            ],
        )
        claim.contradictions = detect_contradictions(claim)
        assert assign_confidence(claim) is Confidence.DISPUTADA

    def test_two_independent_peer_reviewed_groups_reach_high(self):
        claim = Claim(
            text="x",
            evidence=[
                Evidence(make_source(doi="10.1000/a", authors=("Ada Lovelace",)), "Long abstract sentence."),
                Evidence(make_source(doi="10.1000/b", authors=("Grace Hopper",)), "Another abstract sentence."),
            ],
        )
        assert assign_confidence(claim) is Confidence.ALTA

    def test_title_only_evidence_never_reaches_high(self):
        """Tres títulos que comparten palabras son coincidencia léxica, no consenso."""
        claim = Claim(
            text="SETUP TIME REDUCTION",
            evidence=[
                Evidence(make_source(doi=f"10.1000/{n}", authors=(f"Author {n}",)), "SETUP TIME REDUCTION", locator="título")
                for n in "abc"
            ],
        )
        assert claim.is_triangulated
        assert assign_confidence(claim) is Confidence.BAJA

    def test_single_source_is_not_triangulated(self):
        claim = Claim(text="x", evidence=[Evidence(make_source(), "A sentence from the abstract.")])
        assert not claim.is_triangulated
        assert assign_confidence(claim) is Confidence.MEDIA


# ═══════════════════════════════════════════════════════════════════════════
# Proveedores
# ═══════════════════════════════════════════════════════════════════════════


class TestProviders:
    def test_crossref_preprints_are_not_labelled_peer_reviewed(self):
        """
        Crossref asigna DOI a preprints, tesis e informes. Darlos por revisados
        por pares inflaría el nivel de confianza de todo el informe.
        """
        assert _crossref_tier("posted-content") is SourceTier.PREPRINT
        assert _crossref_tier("journal-article") is SourceTier.PEER_REVIEWED
        assert _crossref_tier("dissertation") is SourceTier.INSTITUTIONAL
        assert _crossref_tier(None) is SourceTier.UNKNOWN

    def test_openalex_inverted_abstract_is_reconstructed(self):
        """OpenAlex entrega los resúmenes como índice invertido, por licencia."""
        assert (
            _decode_inverted_abstract({"Setup": [0], "times": [1], "fell": [2]})
            == "Setup times fell"
        )
        assert _decode_inverted_abstract(None) is None

    def test_providers_without_api_key_are_not_offered(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        monkeypatch.delenv("BRAVE_API_KEY", raising=False)
        names = {p.name for p in build_default_providers(HttpClient(offline=True))}
        assert names == {"openalex", "crossref", "arxiv", "wikipedia"}

    def test_provider_failure_does_not_abort_the_research(self, corpus):
        """Un proveedor caído degrada el informe; no puede tumbar la ejecución."""

        class BrokenProvider(StaticProvider):
            name = "broken"

            def search(self, query, limit=8, since_year=None):
                raise ConnectionError("servicio no disponible")

        agent = ResearchAgent(
            providers=[BrokenProvider(None, []), StaticProvider(None, corpus)],
            config=AgentConfig(rounds=1, offline=True, min_term_overlap=0.1),
        )
        report = agent.research("product sequencing setup times packaging lines")
        assert report.sources
        assert any("ConnectionError" in step.note for step in report.audit_trail)


# ═══════════════════════════════════════════════════════════════════════════
# Citas
# ═══════════════════════════════════════════════════════════════════════════


class TestCitations:
    def test_numbering_is_stable_across_calls(self):
        registry = CitationRegistry()
        first, second = make_source(doi="10.1000/a"), make_source(doi="10.1000/b", authors=("Other",))
        assert registry.marker(first) == "[1]"
        assert registry.marker(second) == "[2]"
        assert registry.marker(first) == "[1]"

    def test_markers_are_sorted_and_deduplicated(self):
        registry = CitationRegistry()
        a = make_source(doi="10.1000/a")
        b = make_source(doi="10.1000/b", authors=("Other",))
        registry.register(a)
        registry.register(b)
        markers = registry.markers([Evidence(b, "q"), Evidence(a, "q"), Evidence(a, "q")])
        assert markers == "[1][2]"

    def test_bibliography_matches_citation_numbers(self):
        registry = CitationRegistry()
        registry.register(make_source(doi="10.1000/a"))
        registry.register(make_source(doi="10.1000/b", authors=("Other",)))
        bibliography = registry.bibliography()
        assert bibliography[0].startswith("[1]")
        assert bibliography[1].startswith("[2]")

    def test_reference_includes_doi_and_access_date(self):
        reference = format_reference(make_source(doi="10.1000/a", year=2024))
        assert "https://doi.org/10.1000/a" in reference
        assert "consultado" in reference

    def test_single_author_does_not_get_a_double_period(self):
        assert format_reference(make_source(authors=("Fatemeh Tanhaie",))).startswith("Tanhaie, F. (")

    def test_many_authors_are_abbreviated(self):
        reference = format_reference(
            make_source(authors=("A One", "B Two", "C Three", "D Four"))
        )
        assert "et al." in reference


# ═══════════════════════════════════════════════════════════════════════════
# Integración
# ═══════════════════════════════════════════════════════════════════════════


class TestAgentEndToEnd:
    def test_report_has_findings_for_every_subquestion(self, agent):
        report = agent.research("product sequencing setup times packaging lines")
        assert len(report.findings) == len(report.sub_questions) == len(SubQuestionKind)

    def test_audit_trail_records_every_query(self, agent):
        report = agent.research("product sequencing setup times packaging lines")
        assert report.audit_trail
        assert all(step.provider == "static" for step in report.audit_trail)

    def test_open_questions_flag_untriangulated_claims(self, agent):
        report = agent.research("product sequencing setup times packaging lines")
        assert any("trianguladas" in item for item in report.open_questions)

    def test_subquestion_reopens_when_sources_share_one_author_group(self, agent):
        """
        Tener fuentes de sobra no basta si todas son del mismo equipo: sin varios
        grupos la triangulación es imposible, así que la sub-pregunta se reabre.
        """
        plan = ResearchPlanner("x").initial_plan()
        plan[0].sources_found = 50

        same_team = {
            f"doi:10.1000/{n}": make_source(doi=f"10.1000/{n}", authors=("Ada Lovelace", "X"))
            for n in range(5)
        }
        assert 0 in agent._pending_subquestions(plan, 2, same_team, {0: set(same_team)})

        many_teams = {
            f"doi:10.2000/{n}": make_source(doi=f"10.2000/{n}", authors=(f"Author {n}",))
            for n in range(5)
        }
        assert 0 not in agent._pending_subquestions(plan, 2, many_teams, {0: set(many_teams)})

    def test_agent_without_providers_fails_loudly(self):
        with pytest.raises(RuntimeError, match="proveedores"):
            ResearchAgent(providers=[], config=AgentConfig(offline=True)).research("x")

    def test_markdown_has_all_sections(self, agent):
        markdown = render_markdown(agent.research("product sequencing setup times packaging lines"))
        for heading in ("Resumen ejecutivo", "Hallazgos", "Matriz de evidencia", "Bibliografía", "auditoría"):
            assert heading in markdown

    def test_every_inline_marker_resolves_to_a_reference(self, agent):
        """Garantía clave: ninguna cita del cuerpo puede quedar sin entrada bibliográfica."""
        import re

        registry = CitationRegistry()
        markdown = render_markdown(agent.research("product sequencing setup times packaging lines"), registry)

        body = markdown.split("## 5. Bibliografía")[0]
        cited = {int(n) for n in re.findall(r"\[(\d+)\]", body)}
        listed = {number for number, _ in registry.entries}
        assert cited <= listed
        assert cited  # y el informe cita algo, no está vacío

    def test_json_export_is_valid_and_complete(self, agent):
        import json

        payload = json.loads(render_json(agent.research("product sequencing setup times packaging lines")))
        assert payload["question"]
        assert payload["audit_trail"]
        assert payload["sources"]
        assert 0.0 <= payload["coverage_ratio"] <= 1.0
