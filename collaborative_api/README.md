# Gemini & Claude Collaborative API

Servicio FastAPI que encadena dos modelos: Gemini analiza el requerimiento y
produce un plan estructurado; Claude toma ese plan y genera la solución final.

## Requisitos

- Python 3.10+
- `GEMINI_API_KEY` y `ANTHROPIC_API_KEY` en el entorno o en un archivo `.env`

## Instalación y ejecución

```bash
cd collaborative_api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export GEMINI_API_KEY="..."
export ANTHROPIC_API_KEY="..."

python main.py
# o: uvicorn main:app --reload
```

La documentación interactiva queda en `http://127.0.0.1:8000/docs`.

## Uso

```bash
curl -X POST http://127.0.0.1:8000/api/collaborate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Crea un script en Python que descargue un CSV y calcule promedios por columna"}'
```

Respuesta:

```json
{
  "status": "success",
  "step_1_gemini_analysis": "...",
  "step_2_claude_execution": "..."
}
```

## Configuración opcional

| Variable            | Default             | Descripción                         |
| ------------------- | ------------------- | ----------------------------------- |
| `GEMINI_MODEL`      | `gemini-2.5-flash`  | Modelo de Gemini para el análisis   |
| `CLAUDE_MODEL`      | `claude-sonnet-4-6` | Modelo de Claude para la ejecución  |
| `CLAUDE_MAX_TOKENS` | `2048`              | Límite de tokens de salida de Claude |

`claude-3-5-sonnet-20241022` fue retirado de la API el 28 de octubre de 2025;
por eso el default es `claude-sonnet-4-6`, el reemplazo recomendado por Anthropic.
