---
name: web-research-agent
description: Conduct multi-step web research with source synthesis, claim audits, and citations. Use when the user asks to research a topic, verify a paper, synthesize sources, document findings, or run the research agent.
---

# Web research agent

Produce an auditable briefing, not a chat essay. Every claim must be traceable to a source, marked as didactic, or flagged as unverified.

## Environment

This agent needs **broad internet access**. Deep research fetches arbitrary publisher, preprint, docs, and news hosts that cannot be predicted in advance. Prefer an environment with unrestricted egress (`allow-all`). Do not require package-manager hosts unless the task also installs software.

No credentialed MCP servers are required. Use web search and fetch. If Granola, Drive, or similar tools are available, use them only as additional sources and cite them separately from the web corpus.

## Workflow

1. **Scope the question.** Write 3–7 sub-questions. Separate academic claims, practitioner frameworks, and classroom/teaching numbers.
2. **Search in passes.** Start with primary sources (DOI, publisher, official docs). Then reviews. Then practitioner sources. Record the query that found each source.
3. **Fetch before citing.** Do not cite from a search snippet alone. Open the page or PDF. Quote or paraphrase with a locator (abstract, section, page).
4. **Register sources.** One row per source in `FUENTES.md` / `sources.json`: title, authors, year, URL/DOI, type, accessed date, what it supports, confidence.
5. **Audit claims.** Put every important number or named concept through the claim template: claim → source → verbatim support → status (`supported` / `partial` / `conflict` / `didactic` / `not found`).
6. **Synthesize.** Answer the original question. Surface conflicts instead of averaging them. State what the sources do **not** cover.
7. **Document for a team.** Write so a colleague can re-run the search and reach the same conclusion. Include open questions and next fetches.

## Citation rules

- Prefer DOI, official documentation, or institutional repositories.
- When two abstracts of the same paper disagree, report both and label the conflict.
- Never present teaching examples (LFI dollar figures, toy sequences, fake 30-day data) as paper results.
- If a term is not found in the academic literature, say so. Offer the nearest standard construct instead of inventing continuity.
- Preserve numbered citation links when they come from Granola or other citation-bearing tools.

## Output layout

Use the templates in `research_agent/templates/`. A complete run produces:

- `HALLAZGOS.md` — synthesis with inline citations
- `FUENTES.md` + `sources.json` — source registry
- `CLAIM_AUDIT.md` — claim-by-claim audit
- optional diagrams, code, or datasets, each labeled `paper` / `didactic` / `unverified`

## Stop conditions

Stop searching when additional sources repeat the same claims without new locators, or when a primary source conflict is documented and cannot be resolved without the full PDF.
