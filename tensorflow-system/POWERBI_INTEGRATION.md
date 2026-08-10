# Power BI Integration — Arquitectura Desacoplada

## Por qué NO ejecutar Python en Power Query

Ejecutar el script de TensorFlow **dentro de Power Query** fuerza un **Personal Gateway** siempre encendido y rompe la automatización en la nube.

**Estrategia correcta:** desacoplar el modelo de la visualización.

```
TensorFlow Lite (predice)
        ↓
DataFrame estructurado (id + timestamp + probabilidad)
        ↓
    ┌───┴───┐
    ▼       ▼
  SQL DB   Push Dataset API
    │       │
    ▼       ▼
 Power BI  Power BI (streaming)
 Import / DirectQuery
```

---

## Arquitectura A — Repositorio Central (recomendada)

Ideal para históricos, análisis cruzado y refresh programado.

### 1. Estructurar predicciones

Cada fila incluye:

| Campo | Tipo | Uso en Power BI |
|-------|------|-----------------|
| `id_registro` | Text | Clave única |
| `id_negocio` | Text | Join con CRM / desarrollos |
| `categoria` | Text | Filtros (real_estate, social_media…) |
| `modelo` | Text | Comparar modelos |
| `probabilidad` | Number | KPI / gauges |
| `confianza` | Number | Calidad de predicción |
| `recomendacion` | Text | Acción sugerida |
| `fecha_prediccion` | DateTime | Tendencias |
| `batch_id` | Text | Auditoría de corridas |
| `input_*` | mixto | Dimensiones (ubicación, hora…) |

### 2. Exportar a SQL

```bash
cd tensorflow-system/backend
source venv/bin/activate

# SQLite local (default)
python scripts/export_to_powerbi.py --source live --mode repository

# PostgreSQL
export DATABASE_URL="postgresql+psycopg2://tensorflow:tensorflow@localhost:5432/tensorflow_bi"
python scripts/export_to_powerbi.py --source tracker --write-mode append
```

Código equivalente:

```python
from integrations.powerbi_exporter import PowerBIExportPipeline, PredictionRowBuilder

pipeline = PowerBIExportPipeline(mode="repository")
row = PredictionRowBuilder.build_row(
    category="real_estate",
    model="real_estate_opportunity",
    prediction=modelo.predict(datos),
    input_data=datos,
    id_negocio="DEV-QRO-001",
    confidence_score=0.87,
)
pipeline.export_predictions([row], write_mode="append")  # df.to_sql(..., if_exists='append')
```

### 3. Conectar Power BI Desktop

1. **Obtener datos** → PostgreSQL (o SQLite)
2. Servidor: `localhost:5432` / DB: `tensorflow_bi`
3. Tabla: `predicciones_tensorflow`
4. Modo:
   - **DirectQuery** → dashboard casi en tiempo real cuando el modelo inserta
   - **Importación** → refresh programado (lote diario)

### 4. Orquestar sin intervención manual

| Opción | Cuándo usarla |
|--------|----------------|
| **GitHub Actions** | `.github/workflows/export-predictions.yml` — cron diario 7am CDMX |
| **cron local** | `0 7 * * * cd ... && python scripts/export_to_powerbi.py --source live` |
| **API** | `POST /api/integrations/powerbi/export?source=live` |
| **n8n** | HTTP Request al endpoint de export después del scanner inmobiliario |
| **Docker Compose** | Postgres + API con `DATABASE_URL` ya cableado |

#### Secrets de GitHub Actions

- `DATABASE_URL` — connection string de Postgres/SQL
- `POWERBI_PUSH_URL` — (opcional) URL del streaming dataset
- `POWERBI_API_KEY` — (opcional) si el push requiere auth

---

## Arquitectura B — Push Dataset (streaming)

Ideal para tableros en tiempo real sin base de datos intermedia.

### Setup en Power BI Service

1. Área de trabajo → **Nuevo** → **Conjunto de datos de streaming** → **API**
2. Definir campos:

```
id_registro        Text
id_negocio         Text
categoria          Text
modelo             Text
probabilidad       Number
confianza          Number
recomendacion      Text
fecha_prediccion   DateTime
batch_id           Text
```

3. Copiar la **URL de inserción** → `POWERBI_PUSH_URL` en `.env`

### Enviar desde Python

```python
import os
from integrations.powerbi_exporter import PowerBIPushClient, PredictionRowBuilder

client = PowerBIPushClient(push_url=os.environ["POWERBI_PUSH_URL"])
row = PredictionRowBuilder.build_row(
    category="real_estate",
    model="real_estate_opportunity",
    prediction={"probabilidad_venta_12m": 0.87, "recomendacion": "ALTA PRIORIDAD"},
    id_negocio="1042",
)
print(client.push_rows([row]))
# Status de actualización: 200
```

### Vía API

```bash
curl -X POST http://localhost:3001/api/integrations/powerbi/push \
  -H "Content-Type: application/json" \
  -d '[{
    "id_registro": "abc-123",
    "categoria": "real_estate",
    "modelo": "real_estate_opportunity",
    "probabilidad": 0.87,
    "confianza": 0.87,
    "recomendacion": "ALTA PRIORIDAD",
    "fecha_prediccion": "2026-08-10T12:00:00Z",
    "id_negocio": "DEV-QRO-001",
    "batch_id": "stream_01"
  }]'
```

---

## Modo Hybrid (recomendado en producción)

```bash
export POWERBI_EXPORT_MODE=hybrid
export DATABASE_URL="postgresql+psycopg2://..."
export POWERBI_PUSH_URL="https://api.powerbi.com/beta/.../rows?key=..."

python scripts/export_to_powerbi.py --source live --mode hybrid
```

- **SQL** → histórico + DirectQuery/Import
- **Push** → tiles en tiempo real

Cada predicción de la API (si `POWERBI_AUTO_EXPORT_ON_PREDICT=true`) también escribe al repositorio.

---

## Endpoints API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/integrations/powerbi/status` | Estado DB + Push |
| GET | `/api/integrations/powerbi-data?limit=500` | Filas JSON (dev / Get Data → Web) |
| POST | `/api/integrations/powerbi/export` | Disparar export batch |
| POST | `/api/integrations/powerbi/push` | Push streaming manual |

```bash
# Estado
curl http://localhost:3001/api/integrations/powerbi/status

# Exportar lote
curl -X POST "http://localhost:3001/api/integrations/powerbi/export?source=live&write_mode=append"
```

---

## Docker Compose (Postgres listo)

```bash
cd tensorflow-system
docker-compose up -d postgres tensorflow-api
```

Power BI Desktop → PostgreSQL:

- Host: `localhost`
- Port: `5432`
- Database: `tensorflow_bi`
- User/Pass: `tensorflow` / `tensorflow` (override con `.env`)
- Table: `predicciones_tensorflow`
- Mode: **DirectQuery** o **Import**

---

## Medición de impacto en Power BI

Visualizaciones sugeridas sobre `predicciones_tensorflow`:

1. **Line chart** — `probabilidad` by `fecha_prediccion` (tendencia)
2. **Card** — Average `probabilidad` (últimos 7 días)
3. **Bar** — Count by `recomendacion` / `ubicacion`
4. **Table** — Top oportunidades (`probabilidad` DESC)
5. **Gauge** — % ALTA PRIORIDAD vs total

Une `id_negocio` con tu modelo dimensional de Softec / CRM para análisis cruzado (Cap Rate real vs probabilidad predicha).

---

## Checklist de producción

- [ ] `DATABASE_URL` apunta a Postgres (no SQLite) en prod
- [ ] Power BI conectado con **Import** + refresh o **DirectQuery**
- [ ] GitHub Action secrets configurados **o** cron en servidor
- [ ] (Opcional) Streaming Dataset + `POWERBI_PUSH_URL`
- [ ] `POWERBI_AUTO_EXPORT_ON_PREDICT=true` en la API
- [ ] **No** usar script Python dentro de Power Query

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| Tabla vacía en Power BI | `python scripts/export_to_powerbi.py --source live` |
| Push 404/401 | Regenerar URL del Streaming Dataset; verificar campos |
| Personal Gateway pedido | Estás usando Python en Power Query → migrar a SQL/Push |
| Postgres connection refused | `docker-compose up -d postgres` |
| Tipos incompatibles en Push | `probabilidad`/`confianza` deben ser Number; fechas ISO |

---

**Resumen:** el modelo escribe a un repositorio; Power BI solo lee. Cero gateway Python, 100% automatizable.
