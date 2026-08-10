# Configurar Streaming Dataset en Power BI Service (nube Microsoft)

Guía para crear el punto de entrada que recibe el JSON de TensorFlow vía **Push URL**.

> Objetivo: cada predicción del modelo impacta directamente el modelo semántico en `app.powerbi.com`, con histórico retenido.

---

## Paso a paso

### 1. Ir a tu Área de Trabajo

1. Inicia sesión en [app.powerbi.com](https://app.powerbi.com)
2. Panel izquierdo → **Áreas de trabajo**
3. Entra a la que alojará el dashboard (o **Mi área de trabajo**)

### 2. Iniciar un nuevo conjunto de datos

1. Esquina superior izquierda → **Nuevo**
2. Selecciona **Conjunto de datos de streaming** (*Streaming dataset*)

### 3. Seleccionar la fuente de datos

1. En el panel lateral, elige **API**
2. Clic en **Siguiente**

### 4. Definir el esquema de predicciones

Nombre del conjunto: **`Predicciones_TensorFlow`**

Añade estos valores **exactamente** (mayúsculas/minúsculas importan):

| Nombre del valor   | Tipo de dato |
|--------------------|--------------|
| `ID_Registro`      | Number       |
| `ID_Negocio`       | Text         |
| `Categoria`        | Text         |
| `Modelo`           | Text         |
| `Probabilidad`     | Number       |
| `Confianza`        | Number       |
| `Recomendacion`    | Text         |
| `Fecha_Prediccion` | DateTime     |
| `Batch_ID`         | Text         |
| `Ubicacion`        | Text         |
| `Precio_Estimado`  | Number       |

> Schema mínimo (si prefieres empezar simple):  
> `ID_Registro` (Number) · `Probabilidad` (Number) · `Fecha_Prediccion` (DateTime)  
> Luego usa `POWERBI_STREAMING_SCHEMA=minimal` en `.env`.

### 5. Activar Análisis de datos históricos ⚠️ CRÍTICO

En la parte inferior de la misma ventana, **enciende**:

**Análisis de datos históricos** (*Historic data analysis*)

| Interruptor | Efecto |
|-------------|--------|
| **OFF** | Solo caché temporal para tiles en tiempo real (se pierde el histórico) |
| **ON** | Power BI crea base en segundo plano → puedes analizar tendencias y reportes |

No avances sin activarlo si quieres histórico de predicciones.

### 6. Generar y copiar la URL

1. Clic en **Crear**
2. Aparece la confirmación con la **Push URL**
3. Abre la pestaña **Raw** (no uses el bloque completo de cURL/PowerShell)
4. Copia solo la URL del cuadro de texto

Formato típico:

```
https://api.powerbi.com/beta/<workspace-id>/datasets/<dataset-id>/rows?key=<key>
```

---

## Conectar con TensorFlow

### Opción A — Variable de entorno (recomendado)

```bash
# En tensorflow-system/.env
POWERBI_PUSH_URL=https://api.powerbi.com/beta/.../rows?key=...
POWERBI_STREAMING_SCHEMA=full
POWERBI_EXPORT_MODE=hybrid
POWERBI_AUTO_EXPORT_ON_PREDICT=true
```

### Opción B — Probar la URL de inmediato

```bash
cd tensorflow-system/backend
export POWERBI_PUSH_URL="https://api.powerbi.com/beta/.../rows?key=..."

# Ver schema + payload de muestra
python scripts/test_powerbi_push.py --dry-run

# Enviar 1 fila de prueba al dataset
python scripts/test_powerbi_push.py
```

Si responde **HTTP 200**, abre el dataset en Power BI: ya deberías ver la fila `TEST_CONNECTION`.

### Opción C — Desde código (como en tu snippet)

```python
from datetime import datetime, timezone
from integrations.powerbi_exporter import PowerBIPushClient

client = PowerBIPushClient()  # lee POWERBI_PUSH_URL

# El cliente transforma al schema PascalCase de Power BI
result = client.push_rows([{
    "id_registro": "any-uuid",          # → ID_Registro numérico
    "id_negocio": "DEV-QRO-001",
    "categoria": "real_estate",
    "modelo": "real_estate_opportunity",
    "probabilidad": 0.873,
    "confianza": 0.873,
    "recomendacion": "ALTA PRIORIDAD",
    "fecha_prediccion": datetime.now(timezone.utc).isoformat(),
    "batch_id": "manual_01",
    "input_ubicacion": "Querétaro",
    "precio_estimado": 14200000,
}])

print(f"Status de actualización: {result['status_code']}")
```

Payload real enviado (pestaña Raw):

```json
[
  {
    "ID_Registro": 482910375,
    "ID_Negocio": "DEV-QRO-001",
    "Categoria": "real_estate",
    "Modelo": "real_estate_opportunity",
    "Probabilidad": 0.873,
    "Confianza": 0.873,
    "Recomendacion": "ALTA PRIORIDAD",
    "Fecha_Prediccion": "2026-08-10T06:45:00+00:00",
    "Batch_ID": "manual_01",
    "Ubicacion": "Querétaro",
    "Precio_Estimado": 14200000.0
  }
]
```

---

## Automatización después del setup

| Trigger | Qué hace |
|---------|----------|
| Predicción vía API | Auto-push si `POWERBI_AUTO_EXPORT_ON_PREDICT=true` |
| `python scripts/export_to_powerbi.py --mode hybrid` | SQL + Push en lote |
| GitHub Action diaria | Export programado a las 7am CDMX |
| `POST /api/integrations/powerbi/push` | Push manual de filas |

```bash
# Estado
curl http://localhost:3001/api/integrations/powerbi/status

# Ver schema esperado por el backend
curl http://localhost:3001/api/integrations/powerbi/streaming-schema
```

---

## Crear un tile / reporte

1. En el Área de trabajo → dataset **Predicciones_TensorFlow**
2. Para tiempo real: crea un **dashboard** → **Agregar tile** → **Datos de streaming en tiempo real**
3. Para histórico (con el interruptor ON): **Crear informe** sobre el dataset y usa:
   - Línea: `Probabilidad` por `Fecha_Prediccion`
   - Tarjeta: promedio de `Probabilidad`
   - Tabla: top por `Recomendacion` / `Ubicacion`

---

## Checklist

- [ ] Dataset creado como **API** (no PubNub / Azure)
- [ ] Campos con nombres **exactos** de la tabla de arriba
- [ ] **Análisis de datos históricos** = ON
- [ ] Push URL copiada desde pestaña **Raw**
- [ ] `POWERBI_PUSH_URL` en `.env`
- [ ] `python scripts/test_powerbi_push.py` → HTTP 200
- [ ] Tile o informe muestra la fila de prueba

---

## Troubleshooting

| Error | Causa | Solución |
|-------|-------|----------|
| HTTP 400 | Nombre/tipo de campo distinto | Recrea dataset o alinea schema |
| HTTP 401/403 | Key inválida | Copia de nuevo la URL Raw |
| Sin histórico | Interruptor OFF | Recrea dataset con histórico ON |
| No aparece en informe | Solo miras tile cache | Usa informe sobre dataset histórico |
| Schema minimal vs full | Modo distinto | `POWERBI_STREAMING_SCHEMA=minimal` o `full` |

---

**Siguiente paso:** pega tu Push URL en `.env` y ejecuta `python scripts/test_powerbi_push.py`.
