# Palm Diamante - Router Comercial de Primer Contacto

Script de enrutamiento en **Python / FastAPI** que conecta el **inventario maestro JSON** de
Palm Diamante (Agartha Bienes Raices) con el **clasificador de intención** (Comprador Real /
Lead Frío / Coyote), para que la automatización filtre el tráfico entrante antes de
comprometer tiempo humano o comercial.

```
palm_diamante_router/
├── data/inventario_maestro.json     # Parte 1: inventario normalizado (única fuente de verdad)
├── prompts/reglas_clasificacion.md  # Parte 2: reglas de negocio en prosa (prompt para LLM)
├── prompts/guia_respuestas_whatsapp.md  # Guía de respuestas (27-sep-2026): reglas y textos aprobados
├── router/
│   ├── inventory.py                 # Carga y consulta del inventario (filtros, por id)
│   ├── classifier.py                # Clasificador determinista por reglas + extracción de filtros
│   ├── policy.py                    # Política de comunicación: borrador, precios, canales, prohibidos
│   ├── plantillas.py                # Textos de la guía (aprobados / derivados / pendientes)
│   ├── orchestrator.py              # Categoría -> acción de negocio -> borrador de respuesta
│   └── review_queue.py              # Bandeja de revisión manual (alerta roja)
├── main.py                          # API FastAPI
├── tests/                           # pytest (clasificador, inventario, API)
└── requirements.txt
```

## Inicio rápido

```bash
cd palm_diamante_router
pip install -r requirements.txt
uvicorn main:app --reload --port 8010
# Swagger: http://localhost:8010/docs
```

Tests:

```bash
pytest -q
```

## Flujo de decisión

```
mensaje entrante
      │
      ▼
RuleBasedClassifier  ──►  COYOTE          ──►  ticket alerta ROJA + bloqueo de inventario
 (precedencia:       ──►  COMPRADOR_REAL  ──►  consulta inventario + respuesta exacta + siguiente paso
  COYOTE > COMPRADOR ──►  LEAD_FRIO       ──►  menú rápido (Prototipos / Ubicación / Agendar cita)
  > LEAD_FRIO)
```

| Categoría        | Señales típicas                                                                 | Acción                                   |
|------------------|----------------------------------------------------------------------------------|------------------------------------------|
| `COMPRADOR_REAL` | precio, m², torre, prototipo, recámaras, enganche/mensualidades, cita/visita     | `RESPONDER_CON_INVENTARIO`               |
| `LEAD_FRIO`      | "hola", "info", saludos sin contexto                                             | `DESPLEGAR_MENU`                         |
| `COYOTE`         | comisión, broker, "soy asesor", lista de precios para terceros, referir clientes | `ESCALAR_REVISION_MANUAL` (alerta roja)  |

El clasificador además extrae parámetros explícitos del mensaje (`torre`, `prototipo`,
`recamaras`, `precio_max_mxn`) para consultar el inventario con precisión.

## Endpoints

| Método | Ruta                                        | Descripción                                             |
|--------|---------------------------------------------|---------------------------------------------------------|
| POST   | `/api/v1/router/route`                      | Clasifica **y ejecuta** la acción; devuelve respuesta lista para enviar |
| POST   | `/api/v1/router/classify`                   | Solo clasifica (auditoría / pruebas)                    |
| GET    | `/api/v1/router/prompt`                     | Reglas de negocio en prosa (para un clasificador LLM)   |
| GET    | `/api/v1/inventario`                        | Inventario con filtros `torre`, `prototipo`, `recamaras`, `precio_min_mxn`, `precio_max_mxn` |
| GET    | `/api/v1/inventario/{id_unidad}`            | Detalle de una unidad                                   |
| GET    | `/api/v1/revision-manual`                   | Bandeja de tickets escalados                            |
| POST   | `/api/v1/revision-manual/{id}/resolver`     | Cierra un ticket                                        |
| GET    | `/health`                                   | Health check                                            |

### Ejemplo: comprador real

```bash
curl -s -X POST localhost:8010/api/v1/router/route \
  -H 'Content-Type: application/json' \
  -d '{"mensaje":"¿Cuánto cuesta el de 3 recámaras en la Torre 2?","canal":"whatsapp"}'
```

```json
{
  "categoria": "COMPRADOR_REAL",
  "accion": "RESPONDER_CON_INVENTARIO",
  "respuesta": "Con gusto. Estas son las unidades disponibles en Palm Diamante que coinciden con lo que buscas:\n- PD-T2-204 · Torre 2 · Prototipo B · 3 recámaras · 165 m² · $6,500,000 MXN\n¿Te gustaría agendar una visita o que te comparta el esquema de pago de alguna unidad?",
  "unidades": [{ "id_unidad": "PD-T2-204", "precio_lista_mxn": 6500000, "...": "..." }],
  "asesor_sugerido": "CA",
  "filtros_aplicados": { "torre": 2, "recamaras": 3 },
  "bloqueo_datos_confidenciales": false
}
```

### Ejemplo: coyote

```bash
curl -s -X POST localhost:8010/api/v1/router/route \
  -H 'Content-Type: application/json' \
  -d '{"mensaje":"Soy broker, ¿qué comisión manejan y me pasan la lista para terceros?","conversacion_id":"wa-123"}'
```

```json
{
  "categoria": "COYOTE",
  "accion": "ESCALAR_REVISION_MANUAL",
  "respuesta": "Gracias por tu mensaje. Un ejecutivo de Agartha Bienes Raices revisará tu solicitud y se pondrá en contacto contigo.",
  "bloqueo_datos_confidenciales": true,
  "unidades": [],
  "ticket_revision": { "id_ticket": "REV-1A2B3C4D", "alerta": "ROJA", "estado": "PENDIENTE", "...": "..." }
}
```

## Integración

- **Inventario**: sustituye `data/inventario_maestro.json` (o apunta `PALM_INVENTORY_PATH` a otro
  archivo) manteniendo el mismo esquema. El servicio nunca inventa precios ni metrajes: todo
  sale de este archivo.
- **Clasificador LLM**: cualquier objeto con `clasificar(mensaje) -> Clasificacion` puede pasarse
  a `Orquestador(...)`. `router.SYSTEM_PROMPT` (o `GET /api/v1/router/prompt`) contiene las reglas
  en prosa listas para inyectarse como *system prompt*; el formato de salida esperado está en
  `prompts/reglas_clasificacion.md`.
- **Bandeja de revisión**: `ColaRevisionManual` es en memoria. Para producción, implementa la misma
  interfaz (`registrar` / `pendientes` / `resolver`) sobre PostgreSQL, Redis o el CRM.
