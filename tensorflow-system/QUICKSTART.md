# Guía de Uso Rápido - Sistema TensorFlow Intelligence

## 🚀 Quick Start (5 minutos)

### 1. Instalación

```bash
cd tensorflow-system
./install.sh
```

Esto instalará todas las dependencias y entrenará los modelos iniciales.

### 2. Iniciar API

```bash
./start_api.sh
```

La API estará disponible en `http://localhost:3001`

### 3. Probar el Sistema

```bash
./run_examples.sh
```

Esto ejecutará ejemplos de los 3 módulos.

---

## 📊 Casos de Uso

### Caso 1: Análisis Inmobiliario Semanal

**Objetivo**: Cada lunes a las 7am, analizar 50 desarrollos y recibir Top 3 por WhatsApp

**Setup**:

1. Crear hoja de Google Sheets con desarrollos:
   - Columnas: `nombre, precio_m2, ubicacion, amenidades, velocidad_ventas, cap_rate`

2. Importar workflow de n8n:
   ```bash
   n8n import:workflow --input=workflows/real_estate_scanner.json
   ```

3. Configurar credenciales en n8n:
   - Google Sheets
   - WhatsApp Business API

4. Activar workflow

**Resultado**: Recibirás mensaje como:

```
🏗️ REPORTE SEMANAL INMOBILIARIO

📊 Analizados: 50 desarrollos
✅ Alta prioridad: 12

TOP 3 OPORTUNIDADES

1. Proyecto Querétaro Centro
   Probabilidad: 87.3%
   Precio estimado: $14.2M
   Días: 156
   🎯 ALTA PRIORIDAD

2. Desarrollo Monterrey Sur
   Probabilidad: 82.1%
   Precio estimado: $21.5M
   Días: 203
   🎯 ALTA PRIORIDAD

3. Torre CDMX Polanco
   Probabilidad: 78.9%
   Precio estimado: $45.8M
   Días: 287
   🎯 ALTA PRIORIDAD
```

---

### Caso 2: Calendario de Contenido Automático

**Objetivo**: Generar plan semanal de contenido optimizado para Instagram

**Setup**:

1. Definir temas en `temas_maestros.json`:

```json
{
  "temas": [
    "Cap Rate",
    "Estrategia Inmobiliaria",
    "Caso UIA",
    "ExO",
    "Productividad",
    "Tenis",
    "Familia"
  ]
}
```

2. API Call:

```bash
curl -X POST http://localhost:3001/api/generate/weekly-content-schedule \
  -H "Content-Type: application/json" \
  -d '{
    "temas_disponibles": ["Cap Rate", "Estrategia Inmobiliaria", "ExO", "Tenis"]
  }'
```

**Resultado**: JSON con 14 posts optimizados (2 por día) con:
- Mejor horario
- Tipo de contenido (Carrusel, Reel, Story)
- Tema a cubrir
- Engagement esperado
- Probabilidad de viralidad

**Integración con n8n**: El workflow `instagram_collector.json` automáticamente:
1. Recoge métricas de tus posts actuales (diario 2am)
2. Las guarda en Google Sheets
3. Genera nuevo calendario semanal
4. Te lo envía por WhatsApp

---

### Caso 3: Decisión de Compra de Auto

**Objetivo**: Comparar TCO entre Geely EX5 EM-i y Toyota RAV4

**Script Python**:

```python
import requests

geely = {
    "precio_inicial": 650000,
    "gasolina_mensual": 800,
    "seguro_anual": 12000,
    "mantenimiento_anual": 8000,
    "depreciacion_anual": 65000,
    "km_anuales": 20000,
    "rendimiento_km_l": 25,
    "es_electrico": 1
}

rav4 = {
    "precio_inicial": 720000,
    "gasolina_mensual": 2500,
    "seguro_anual": 15000,
    "mantenimiento_anual": 12000,
    "depreciacion_anual": 70000,
    "km_anuales": 20000,
    "rendimiento_km_l": 14,
    "es_electrico": 0
}

response = requests.post(
    "http://localhost:3001/api/compare/vehicles",
    json={
        "vehicle1": geely,
        "vehicle2": rav4,
        "vehicle1_name": "Geely EX5 EM-i",
        "vehicle2_name": "Toyota RAV4"
    }
)

print(response.json())
```

**Resultado**:

```json
{
  "Geely EX5 EM-i": {
    "tco_total_3_anos": 258400,
    "costo_mensual_promedio": 7177
  },
  "Toyota RAV4": {
    "tco_total_3_anos": 312000,
    "costo_mensual_promedio": 8666
  },
  "diferencia_3_anos": 53600,
  "ahorro_mensual": 1489,
  "recomendacion": "Geely EX5 EM-i ahorra $53,600 en 3 años"
}
```

**Guardar en Obsidian**:
El plugin automáticamente crea una nota con la decisión.

---

### Caso 4: Optimización de Tenis

**Objetivo**: Encontrar mejor setup para partido del martes

**API Call**:

```bash
curl -X POST http://localhost:3001/api/optimize/tennis-setup \
  -H "Content-Type: application/json" \
  -d '{
    "temperatura": 24,
    "rival_nivel": 6,
    "dia_semana": 1,
    "horas_descanso": 2
  }'
```

**Resultado**:

```json
{
  "tension_kg": 24,
  "pelota": "Wilson US Open",
  "probabilidad_victoria": 0.73,
  "mejora_vs_promedio": 18.2
}
```

**Interpretación**: 
- Usar 24kg de tensión (no 25kg como usas actualmente)
- Wilson US Open (la que ya usas) ✅
- Con este setup: 73% probabilidad de ganar
- +18.2% mejor que tu promedio actual

---

## 🔌 Integraciones

### A. n8n Workflows

**Instalación**:

```bash
# Instalar n8n (si no lo tienes)
npm install -g n8n

# Iniciar n8n
n8n start
```

**Importar workflows**:

1. Ir a `http://localhost:5678`
2. Click en "Workflows" → "Import from File"
3. Seleccionar:
   - `workflows/instagram_collector.json`
   - `workflows/real_estate_scanner.json`

**Configurar credenciales**:
- Instagram Graph API
- Google Sheets
- WhatsApp Business API

---

### B. Power BI

**Conectar a API**:

1. Abrir Power BI Desktop
2. Obtener datos → Web
3. URL: `http://localhost:3001/api/integrations/powerbi-data`
4. Configurar actualización automática cada hora

**Dashboards recomendados**:
- Desarrollos por ubicación (mapa)
- Engagement por tipo de contenido (barras)
- TCO comparativo (líneas de tiempo)

---

### C. Obsidian Plugin

**Instalación**:

1. Copiar plugin:
   ```bash
   cp -r obsidian-plugin ~/.obsidian/plugins/tensorflow-intelligence-sync/
   ```

2. En Obsidian:
   - Settings → Community Plugins
   - Enable "TensorFlow Intelligence Sync"

3. Configurar:
   - API URL: `http://localhost:3001`
   - Auto-sync: ✅ Enabled
   - Intervalo: 60 minutos

**Comandos disponibles**:
- `Ctrl+P` → "Sincronizar con TensorFlow API"
- `Ctrl+P` → "Crear Reporte Semanal"
- `Ctrl+P` → "Registrar Decisión Personal"

---

## 📈 Re-entrenamiento de Modelos

### Con Tus Datos Reales

**1. Preparar CSV**:

Inmobiliario (`data/real_estate/training_data.csv`):
```csv
desarrollo,precio_m2,ubicacion,amenidades,velocidad_ventas,cap_rate,vendido_12_meses,precio_venta_real,dias_venta
Torre Central,45000,Querétaro,12,0.85,7.2,1,18500000,156
```

Instagram (`data/social_media/instagram_posts.csv`):
```csv
fecha,tipo_contenido,tema_categoria,hora_publicacion,num_hashtags,longitud_caption,likes,guardados,comentarios,shares,alcance
2024-01-15 09:00:00,Reel,Cap Rate,9,5,150,847,89,34,12,4235
```

**2. Re-entrenar**:

```bash
cd backend
source venv/bin/activate
python scripts/train_all_models.py
```

**3. Frecuencia recomendada**:
- Mensual (mínimo)
- Cuando tengas +50 nuevos datos

---

## 🎯 Consejos de Uso

### 1. Empieza con un módulo

No intentes implementar los 3 módulos al mismo tiempo. Orden recomendado:

1. **Personal** (TCO + Tenis): Más fácil, datos controlados
2. **Redes Sociales**: Impacto visible rápido
3. **Inmobiliario**: Más complejo, mayor ROI

### 2. Valida predicciones

Durante el primer mes, compara:
- Predicción del modelo vs realidad
- Ajusta pesos si es necesario

### 3. Integra con tu flujo actual

- Power BI: Ya lo usas, solo conecta nuevo endpoint
- WhatsApp: Recibe reportes donde ya trabajas
- Obsidian: Centraliza aprendizajes en tu Índice Maestro

### 4. Automatiza gradualmente

Semana 1: Ejecuta ejemplos manualmente
Semana 2: Configura 1 workflow de n8n
Semana 3: Habilita auto-sync de Obsidian
Semana 4: 100% automático

---

## 🔧 Troubleshooting

### API no inicia

```bash
# Verificar puerto disponible
lsof -i :3001

# Si está ocupado, cambiar puerto en api.py
uvicorn.run(..., port=3002)
```

### Modelo no predice correctamente

```bash
# Verificar que existan los .tflite
ls -lh backend/models/*.tflite

# Re-entrenar específico
cd backend
python models/real_estate_opportunity.py
```

### n8n no conecta a API

- Verificar firewall
- Usar `http://host.docker.internal:3001` si n8n está en Docker

---

## 📞 Soporte

Para problemas o mejoras:
1. Ver logs: `backend/api/logs/`
2. Revisar documentación completa: `README.md`
3. Ejecutar tests: `pytest backend/tests/`

---

**¡Listo! Ahora tienes Jeff Dean trabajando para ti 24/7** 🚀
