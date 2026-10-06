# Agente de investigación web multi-paso

Agente que convierte una pregunta en un informe con citas verificables. Descompone
la pregunta, busca en rondas sucesivas cerrando las brechas que detecta, deduplica
y sintetiza las fuentes, y entrega cada afirmación con su cita literal, su nivel
de confianza y el registro completo de cómo se llegó a ella.

Sólo biblioteca estándar. Funciona sin ninguna API key.

---

## Inicio rápido

```bash
cd master_blueprint

# Informe por stdout
python -m research_agent "optimización de secuencias en líneas de producción"

# Informe a archivo, con auditoría JSON
python -m research_agent "Last Planner System y fiabilidad de la planificación" \
  --rounds 3 --out informe.md --json auditoria.json
```

Desde Python:

```python
from research_agent import ResearchAgent, AgentConfig, render_markdown

agent = ResearchAgent(config=AgentConfig(rounds=3))
report = agent.research("reducción de tiempos de setup en líneas de empaque")

print(render_markdown(report, title="Estado de la evidencia"))
print(f"Cobertura: {report.coverage_ratio:.0%}")
```

### Preguntar en español, buscar en inglés

OpenAlex, Crossref y arXiv indexan mayoritariamente en inglés, así que una pregunta
en español recupera mucho menos de lo que debería. `--terms` separa el idioma de la
pregunta del idioma de la búsqueda:

```bash
python -m research_agent \
  "¿Qué evidencia hay sobre reducir tiempos de setup secuenciando productos?" \
  --terms setup sequencing packaging changeover scheduling
```

---

## Proveedores

| Proveedor | API key | Nivel asignado | Para qué sirve |
| :--- | :--- | :--- | :--- |
| OpenAlex | no | revisado por pares / preprint | Fuente principal: metadatos completos y recuento de citas |
| Crossref | no | según el tipo de registro | Contraste de DOI; confirma que la referencia existe |
| arXiv | no | preprint | Métodos computacionales recientes |
| Wikipedia | no | referencia | Definiciones y contexto, nunca cifras |
| Tavily | `TAVILY_API_KEY` | web | Web general |
| Brave | `BRAVE_API_KEY` | web | Web general |

Los de web general se activan solos si la variable de entorno existe. Un proveedor
caído degrada el informe y queda anotado en la auditoría, pero no interrumpe la
ejecución.

---

## Opciones principales

| Opción | Por defecto | Qué hace |
| :--- | :--- | :--- |
| `--rounds` | 2 | Rondas de búsqueda. Las posteriores a la primera sólo atienden brechas |
| `--results` | 8 | Resultados por consulta y proveedor |
| `--terms` | — | Términos de búsqueda explícitos |
| `--kinds` | los cinco | Limita los tipos de sub-pregunta |
| `--cache-dir` | `~/.cache/research_agent` | Caché HTTP en disco |
| `--offline` | no | Usa sólo la caché; útil para re-generar un informe sin red |
| `--json` | — | Vuelca la auditoría completa |

---

## Qué produce

El informe en Markdown tiene seis secciones: resumen ejecutivo, hallazgos por
sub-pregunta con citas literales, **matriz de evidencia** (una fila por afirmación,
pensada como lista de verificación para repartir entre revisores), brechas
declaradas, bibliografía con DOI y fecha de acceso, y el registro de auditoría con
todas las consultas lanzadas.

El JSON contiene lo mismo en forma estructurada. Guardarlo permite comparar dos
ejecuciones de la misma pregunta y ver qué cambió en la literatura.

---

## Lo que el agente no hace

No lee el texto completo de los artículos: trabaja con títulos y resúmenes, así que
un resultado enterrado en la sección 5 de un paper se le escapa.

No entiende el significado de las frases. Agrupa afirmaciones por coincidencia
léxica ponderada, y el criterio es estricto a propósito, de modo que **lo normal es
que la mayoría de afirmaciones queden con una sola fuente**. Eso no es un fallo: es
el estado real de la evidencia, y el informe lo dice en vez de disimularlo.

No sustituye la revisión humana. Produce material ordenado y trazable para que
revisarlo sea rápido; el protocolo está en
[`docs/AGENTE_INVESTIGACION.md`](../docs/AGENTE_INVESTIGACION.md).

---

## Tests

```bash
cd master_blueprint
pytest tests/test_research_agent.py -v
```

Corren offline con un corpus fijo. Cubren sobre todo los modos de fallo silencioso:
triangulación fabricada a partir de vocabulario genérico, preprints etiquetados como
literatura revisada, y citas del cuerpo sin entrada en la bibliografía.
