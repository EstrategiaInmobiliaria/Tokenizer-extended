# AI Gateway — una sola API para ChatGPT (OpenAI), Gemini y Claude

Servicio FastAPI que recibe peticiones en **formato OpenAI** y las traduce a la API
nativa de cada proveedor. Sirve para:

- Conectar **Cursor** a Gemini o Claude a través de la opción *Override OpenAI Base URL*.
- Tener **una sola URL y una sola llave** en tus propias apps (Streamlit, bots, n8n, etc.).
- Cambiar de modelo/proveedor sin tocar código: basta con cambiar el campo `model`.

> Importante: `https://chat.openai.com` es la interfaz web de ChatGPT y **no es una API**.
> La API real de OpenAI vive en `https://api.openai.com/v1` y requiere una llave de
> `platform.openai.com`. Lo mismo aplica a Gemini (`aistudio.google.com`) y Claude
> (`console.anthropic.com`). Este gateway usa esas tres APIs oficiales.

---

## 1. Consigue las llaves

| Proveedor | Dónde obtener la llave | Variable |
|---|---|---|
| OpenAI (ChatGPT) | https://platform.openai.com/api-keys | `OPENAI_API_KEY` |
| Google Gemini | https://aistudio.google.com/app/apikey | `GEMINI_API_KEY` |
| Anthropic Claude | https://console.anthropic.com/settings/keys | `ANTHROPIC_API_KEY` |

Puedes configurar una, dos o las tres. El proveedor sin llave queda deshabilitado.

## 2. Instala y arranca

```bash
# desde la raíz del repositorio
pip install -r ai_gateway/requirements.txt

cp ai_gateway/.env.example ai_gateway/.env
# edita ai_gateway/.env con tus llaves y define GATEWAY_API_KEY

uvicorn ai_gateway.main:app --reload --port 8080
```

O con Docker:

```bash
docker build -f ai_gateway/Dockerfile -t ai-gateway .
docker run --rm -p 8080:8080 --env-file ai_gateway/.env ai-gateway
```

Documentación interactiva: http://localhost:8080/docs

## 3. Pruébalo

```bash
# Estado de los proveedores
curl http://localhost:8080/health

# Endpoint simple
curl http://localhost:8080/v1/chat \
  -H "Authorization: Bearer $GATEWAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"provider": "gemini", "prompt": "Explica el WACC en dos líneas"}'

# Endpoint compatible con OpenAI (mismo cuerpo que la API de OpenAI)
curl http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer $GATEWAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-latest",
    "messages": [
      {"role": "system", "content": "Eres un analista financiero"},
      {"role": "user", "content": "¿Qué es el CAPM?"}
    ]
  }'
```

### Cómo se elige el proveedor

El campo `model` acepta tres formas:

| Forma | Ejemplo | Resultado |
|---|---|---|
| `proveedor/modelo` | `gemini/gemini-1.5-pro`, `anthropic/claude-3-opus-latest`, `openai/gpt-4o` | Exacto |
| Solo el modelo | `gpt-4o`, `gemini-2.0-flash`, `claude-3-5-sonnet-latest` | Proveedor inferido por el prefijo |
| Solo el proveedor | `openai`, `gemini`, `claude` | Modelo por defecto del `.env` |

## 4. Conectar Cursor al gateway

Cursor habla el protocolo de OpenAI, así que puede usar este gateway para llegar a
Gemini o Claude:

1. Publica el gateway en una URL HTTPS (Railway, Render, Fly.io, un VPS con Caddy, o
   `ngrok http 8080` para probar).
2. En Cursor: **Settings → Models**.
3. Activa **OpenAI API Key** y pega el valor de tu `GATEWAY_API_KEY`.
4. Activa **Override OpenAI Base URL** y escribe `https://tu-dominio/v1`.
5. En **Add model** agrega los nombres que quieras usar, por ejemplo
   `gemini/gemini-2.0-flash` o `anthropic/claude-3-5-sonnet-latest`.
6. Selecciona ese modelo en el chat. Cursor envía `stream: true`; el gateway responde
   en formato SSE de OpenAI.

Si prefieres no pasar por el gateway, Cursor también acepta directamente llaves de
OpenAI, Anthropic y Google en la misma pantalla de *Models*; el gateway aporta valor
cuando quieres una única llave, registrar uso, o reutilizar la misma URL desde otras
aplicaciones.

## 5. Usarlo desde Python (cualquier SDK de OpenAI funciona)

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8080/v1", api_key="tu-GATEWAY_API_KEY")

for model in ["openai/gpt-4o-mini", "gemini/gemini-2.0-flash", "anthropic/claude-3-5-sonnet-latest"]:
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Resume el modelo DCF en una frase"}],
    )
    print(model, "->", r.choices[0].message.content)
```

## 6. Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Estado y proveedores habilitados (sin autenticación) |
| `GET` | `/v1/models` | Lista de modelos por defecto, formato OpenAI |
| `POST` | `/v1/chat/completions` | Compatible con OpenAI; soporta `stream: true` |
| `POST` | `/v1/chat` | Forma corta: `{provider, prompt, system?, model?}` |
| `GET` | `/docs` | Swagger UI |

Respuesta normalizada (idéntica para los tres proveedores):

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "model": "gemini-2.0-flash-001",
  "provider": "gemini",
  "choices": [{"index": 0, "message": {"role": "assistant", "content": "..."}, "finish_reason": "stop"}],
  "usage": {"prompt_tokens": 12, "completion_tokens": 40, "total_tokens": 52}
}
```

Los errores del proveedor se devuelven con su código HTTP original
(`401` llave inválida, `429` límite de uso, `404` modelo inexistente):

```json
{"error": {"message": "API key not valid...", "type": "provider_error", "provider": "gemini"}}
```

## 7. Tests

```bash
python -m pytest ai_gateway/tests -q
```

Los tests simulan las tres APIs remotas con `httpx.MockTransport`: no gastan crédito
ni necesitan llaves reales.

## 8. Estructura

```
ai_gateway/
├── main.py                  FastAPI: endpoints, auth, streaming SSE
├── router.py                resolución "model" -> (proveedor, modelo)
├── config.py                variables de entorno (.env)
├── schemas.py               modelos Pydantic compatibles con OpenAI
├── providers/
│   ├── base.py              contrato común + manejo de errores HTTP
│   ├── openai_provider.py   /v1/chat/completions
│   ├── gemini_provider.py   /v1beta/models/{m}:generateContent
│   └── anthropic_provider.py /v1/messages
├── tests/test_gateway.py    17 tests con mocks
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Limitaciones actuales

- El streaming es "pseudo-stream": se consulta al proveedor sin streaming y se emite
  la respuesta completa en un solo chunk SSE. Suficiente para Cursor y SDKs, pero no
  muestra tokens uno a uno.
- Solo texto: no se traducen imágenes, `tools`/function calling ni embeddings.
- Sin persistencia ni límites de uso por cliente; añade un proxy (Caddy, nginx) o
  extiende `require_gateway_key` si lo expones públicamente.
