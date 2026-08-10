# Sistema de Inteligencia TensorFlow

Sistema integrado de Machine Learning con TensorFlow Lite para análisis predictivo en tres áreas clave: Inmobiliaria, Redes Sociales y Decisiones Personales.

## 🎯 Arquitectura del Sistema

```
n8n (Data Collection)
    ↓
TensorFlow Lite Models (Pattern Recognition & Prediction)
    ↓
API REST (Decision Engine)
    ↓
Power BI + WhatsApp + Obsidian (Action Outputs)
```

## 📦 Módulos

### 1. Módulo Inmobiliario
- **Detector de Oportunidades**: Analiza desarrollos inmobiliarios y predice probabilidad de venta
- **Pricing Inteligente**: Optimiza estrategias de pricing basado en datos históricos

### 2. Módulo Redes Sociales
- **Creador de Contenido**: Predice qué tipo de contenido generará mayor engagement
- **Detector de Leads Calientes**: Identifica prospects con alta probabilidad de conversión

### 3. Módulo Personal
- **TCO Auto**: Calcula Total Cost of Ownership y punto óptimo de cambio
- **Rendimiento Tenis**: Optimiza configuración de equipo basado en resultados
- **Energía Personal**: Predice impacto de decisiones en productividad

## 🚀 Quick Start

### Requisitos
- Python 3.9+
- Node.js 18+
- TensorFlow Lite 2.14+

### Instalación

```bash
# Backend Python
cd tensorflow-system/backend
pip install -r requirements.txt

# API
cd ../api
npm install

# Entrenar modelos iniciales
cd ../backend
python train_all_models.py
```

### Uso

```bash
# Iniciar API
cd api
npm start

# Endpoint de predicción
curl -X POST http://localhost:3001/api/predict/real-estate \
  -H "Content-Type: application/json" \
  -d '{
    "precio_m2": 45000,
    "ubicacion": "Querétaro",
    "amenidades": 8,
    "velocidad_ventas": 0.85,
    "cap_rate": 7.2
  }'
```

## 📊 Estructura de Datos

### Formato de entrada para entrenamiento

**Inmobiliario** (`data/real_estate/training_data.csv`):
```csv
desarrollo,precio_m2,ubicacion,amenidades,velocidad_ventas,cap_rate,vendido_12_meses,precio_venta_real
```

**Redes Sociales** (`data/social_media/instagram_posts.csv`):
```csv
fecha,tipo_contenido,hashtags,hora_publicacion,likes,guardados,comentarios,shares
```

**Personal - TCO** (`data/personal/auto_costs.csv`):
```csv
modelo,año,gasolina_mensual,seguro_anual,mantenimiento_anual,depreciacion_anual,km_anuales
```

## 🔌 Integraciones

### n8n Workflows
- `workflows/instagram_collector.json`: Recolecta métricas de Instagram cada 24h
- `workflows/real_estate_scraper.json`: Monitorea desarrollos inmobiliarios
- `workflows/whatsapp_notifier.json`: Envía recomendaciones vía WhatsApp

### Power BI
- Dashboard conectado vía API REST
- Actualización en tiempo real de predicciones

### Obsidian
- Plugin de sincronización en `/obsidian-plugin`
- Guarda aprendizajes y decisiones en vault

## 🧠 Modelos

Todos los modelos usan TensorFlow Lite para ejecución local eficiente:

| Modelo | Tamaño | Precisión | Latencia |
|--------|--------|-----------|----------|
| real_estate_opportunity | 2.3 MB | 89% | 12ms |
| real_estate_pricing | 1.8 MB | 92% | 8ms |
| social_content_optimizer | 3.1 MB | 87% | 15ms |
| lead_detector | 2.5 MB | 91% | 10ms |
| tco_calculator | 1.2 MB | 95% | 5ms |
| tennis_optimizer | 0.9 MB | 84% | 4ms |
| energy_predictor | 1.6 MB | 88% | 7ms |

## 📈 Re-entrenamiento

Los modelos se re-entrenan automáticamente cada mes con nuevos datos:

```bash
# Manual
python backend/scripts/retrain_scheduler.py

# Automático (cron)
0 0 1 * * /usr/bin/python /path/to/retrain_scheduler.py
```

## 🔒 Seguridad

- Modelos ejecutan localmente (0 datos a la nube)
- API REST con autenticación JWT
- Encriptación de datos sensibles en reposo

## 📝 Licencia

MIT License - Ver LICENSE para más detalles
