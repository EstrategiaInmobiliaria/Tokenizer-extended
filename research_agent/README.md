# Agente de investigación web (síntesis + citas)

Kit para un agente que hace investigación de varios pasos, audita claims y deja un briefing que el equipo puede re-ejecutar. El primer corrido está en [`briefings/2026-packaging-tsp-lfi/`](briefings/2026-packaging-tsp-lfi/).

## Qué entorno usar

| Decisión | Recomendación | Por qué |
|---|---|---|
| Tipo de entorno | **Uno nuevo y dedicado** a investigación, no el de la app (tokenizer, CRM, etc.) | El agente solo necesita Python + red; no debe arrastrar `install` de Node/Docker de otro producto |
| Acceso a internet | **Efectivamente irrestricto** (`allow-all` / unrestricted egress) | Deep research tiene que abrir editoriales, preprints, docs y páginas arbitrarias. Una allowlist de “solo buscadores” se queda corta |
| Gestores de paquetes | No hace falta abrir PyPI/npm **en el egress de runtime** si las deps van en el snapshot | El runtime busca y lee; instalar `numpy`/`matplotlib` pertenece al `install` del entorno |
| MCP con credenciales | Ninguno obligatorio | Búsqueda + fetch bastan. Granola/Drive son fuentes extra, no dependencias |

Este repositorio ya corre en el entorno personal **Tokenizer-extended**, con egress unrestricted. Sirve para **probar** el agente. Para producción, crea un entorno aparte con el mismo egress y un `install` mínimo:

```json
{
  "name": "web-research-agent",
  "install": "pip install -r research_agent/requirements.txt"
}
```

No scopes hosts de antemano: el conjunto de dominios de un paper (SSRN, Springer, IBERO, Lean Construction Institute, PyPI, SimPy docs) no es estable ni completo.

## Cómo usarlo

1. Pega [`AGENT_PROMPT.md`](AGENT_PROMPT.md) como system prompt del agente (Cursor custom agent / Cloud Agent).
2. Activa el skill [`.cursor/skills/web-research-agent/SKILL.md`](../.cursor/skills/web-research-agent/SKILL.md).
3. Pide el tema. El agente debe dejar archivos con las [plantillas](templates/), no un monólogo.
4. Revisa `CLAIM_AUDIT.md` **antes** de usar cifras en clase o con un cliente.

## Primer briefing (paper de empaque + MUDA + LPS/LFI)

Tema: secuenciación en líneas de empaque farmacéutico (Soria-Arguello et al.), 7 MUDA, Last Planner System, “LFI” como capa de decisión didáctica, y herramientas de simulación.

```bash
pip install -r research_agent/requirements.txt
python3 research_agent/briefings/2026-packaging-tsp-lfi/simulations/run_lab.py
python3 -m unittest discover -s research_agent/tests -v
```

Salidas: gráficos PNG, CSV de 30 días con patrón oculto, y la clave del instructor.

## Cómo documentar hallazgos (más allá del aprendizaje personal)

El método está en [`methodology/como-documentar-hallazgos.md`](methodology/como-documentar-hallazgos.md). En corto: cada cifra vive en una ficha de fuente; cada afirmación vive en un claim audit; los conflictos no se promedian; lo didáctico no se cita como paper.
