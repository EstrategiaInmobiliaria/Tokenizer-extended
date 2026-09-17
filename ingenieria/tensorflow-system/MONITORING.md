# 📊 Guía de Monitoreo y Métricas

## 🎯 Visión General

El sistema incluye un **framework completo de monitoreo** que permite medir el impacto real de las predicciones y calcular ROI cuantificable.

---

## 🔧 Componentes del Sistema

### 1. Impact Tracker

Registra todas las predicciones y sus outcomes reales para calcular métricas precisas.

**Funcionalidades:**
- ✅ Log automático de todas las predicciones
- ✅ Tracking de outcomes reales vs predichos
- ✅ Cálculo de accuracy por categoría y modelo
- ✅ Medición de tiempo ahorrado
- ✅ Cálculo de ROI (dinero + tiempo)
- ✅ Exportación a Power BI

### 2. Smart Alert System

Sistema de alertas inteligentes con reglas configurables.

**Tipos de alertas:**
- ⚠️ **Accuracy Drop**: Cuando precisión cae <75%
- 🎯 **High Opportunity**: Oportunidades con >85% probabilidad
- 🎉 **ROI Milestone**: Al alcanzar $10K, $50K, $100K
- 📊 **Model Drift**: Cambios significativos en patrones
- 🚀 **Engagement Spike**: Posts que superan 150% del promedio

### 3. Dashboard en Tiempo Real

Dashboard web responsivo con visualizaciones interactivas.

**Acceso:** http://localhost:3001/static/dashboard.html

**Características:**
- 📈 ROI total y desglosado
- 🎯 Precisión del sistema por categoría
- ⏱️ Tiempo ahorrado en horas
- 💰 Valor monetario generado
- 📊 Gráficos de tendencias
- 🔄 Auto-refresh cada 60 segundos

---

## 📡 Endpoints de Monitoreo

### Tracking de Outcomes

```bash
# Actualizar outcome de una predicción
POST /api/tracking/update-outcome

{
  "prediction_id": "real_estate_20240810_123456_789",
  "actual_outcome": {
    "vendido": true,
    "dias_venta": 158,
    "precio_real": 14100000
  },
  "success": true,
  "notes": "Vendido en tiempo estimado"
}
```

### Reporte de Impacto

```bash
# Generar reporte de los últimos 30 días
GET /api/metrics/impact-report?days=30

Response:
{
  "report_text": "Reporte formateado",
  "metrics": {
    "total_predictions": 45,
    "correct_predictions": 39,
    "accuracy": 0.867,
    "time_saved_hours": 270,
    "money_saved": 48000,
    "deals_predicted_success": 12,
    "deals_actual_success": 10
  },
  "period_days": 30
}
```

### Calculadora de ROI

```bash
# Calcular ROI detallado
GET /api/metrics/roi-calculator?days=30

Response:
{
  "period_days": 30,
  "breakdown": {
    "time_saved_hours": 270,
    "time_value_mxn": 270000,
    "direct_savings_mxn": 48000,
    "cloud_costs_avoided_mxn": 11400,
    "total_value_mxn": 329400
  },
  "projections": {
    "monthly_value_mxn": 329400,
    "annual_value_mxn": 3952800
  }
}
```

### Alertas Recientes

```bash
# Obtener alertas de las últimas 24 horas
GET /api/alerts/recent?hours=24

Response:
{
  "alerts": [
    {
      "type": "high_opportunity",
      "priority": "high",
      "title": "Oportunidad de Alta Prioridad Detectada",
      "message": "Desarrollo con 92% de probabilidad...",
      "timestamp": "2024-08-10T14:30:00"
    }
  ],
  "total": 3,
  "period_hours": 24
}
```

### Configuración de Alertas

```bash
# Ver configuración actual
GET /api/alerts/config

Response:
{
  "accuracy_threshold": 0.75,
  "high_opportunity_threshold": 0.85,
  "roi_milestones": [10000, 50000, 100000],
  "engagement_spike_threshold": 1.5,
  "enabled": true,
  "notification_channels": ["log", "whatsapp"]
}

# Actualizar configuración
POST /api/alerts/config

{
  "accuracy_threshold": 0.80,
  "high_opportunity_threshold": 0.90
}
```

---

## 💡 Uso en Código Python

### Logging de Predicciones

```python
from monitoring.impact_tracker import ImpactTracker, MetricCategory

tracker = ImpactTracker()

# Log predicción
pred_id = tracker.log_prediction(
    MetricCategory.REAL_ESTATE,
    "real_estate_opportunity",
    input_data={"precio_m2": 45000, "ubicacion": "Querétaro"},
    prediction={"probabilidad_venta_12m": 0.87},
    confidence_score=0.87
)

print(f"Predicción registrada: {pred_id}")
```

### Actualizar Outcomes

```python
from monitoring.impact_tracker import PredictionOutcome

# Después de verificar resultado real
tracker.update_outcome(
    pred_id="real_estate_20240810_123456_789",
    actual_outcome={
        "vendido": True,
        "dias_venta": 158,
        "precio_real": 14100000
    },
    outcome_status=PredictionOutcome.SUCCESS,
    notes="Vendido cerca del tiempo predicho"
)
```

### Generar Reportes

```python
# Reporte de impacto
print(tracker.generate_impact_report(days=30))

# Métricas programáticas
metrics = tracker.calculate_metrics()
print(f"Accuracy: {metrics.accuracy:.2%}")
print(f"ROI: ${metrics.money_saved + (metrics.time_saved_hours * 1000):,.0f}")
```

### Exportar a Power BI

```python
# Exportar todas las predicciones a CSV
tracker.export_to_powerbi("data/powerbi_export.csv")
```

---

## 🔔 Sistema de Alertas

### Configurar Alertas

```python
from monitoring.alert_system import SmartAlertSystem

alert_system = SmartAlertSystem()

# Configurar umbrales
alert_system.config["accuracy_threshold"] = 0.80
alert_system.config["high_opportunity_threshold"] = 0.90
alert_system.config["roi_milestones"] = [25000, 75000, 150000]
alert_system.save_config()
```

### Verificar Alertas Manualmente

```python
from monitoring.alert_system import check_and_alert_prediction

# Después de una predicción
prediction_data = {
    'probabilidad_venta_12m': 0.92,
    'precio_estimado': 18500000,
    'dias_estimados': 142
}

alerts = check_and_alert_prediction(prediction_data, "real_estate")

for alert in alerts:
    print(alert.to_whatsapp_message())
```

---

## 📊 KPIs Clave

### Generales

| KPI | Descripción | Meta |
|-----|-------------|------|
| **Accuracy** | % de predicciones correctas | >85% |
| **Total Predictions** | Predicciones realizadas | 100+/mes |
| **Time Saved** | Horas ahorradas | 50+h/mes |
| **ROI Total** | Valor generado (MXN) | $100K+/mes |

### Por Categoría

**Inmobiliario:**
- Deals analizados vs vendidos
- Tiempo promedio de cierre (predicho vs real)
- Accuracy de pricing

**Redes Sociales:**
- Engagement predicho vs real
- Posts virales identificados
- Mejora % vs baseline

**Personal:**
- Decisiones optimizadas
- Dinero ahorrado en TCO
- Mejora en win rate (tenis)

---

## 📈 Dashboards Recomendados

### Dashboard Power BI

**Visualizaciones sugeridas:**

1. **ROI Overview**
   - Card: ROI Total
   - Line Chart: ROI Trend (últimos 6 meses)
   - Bar Chart: ROI Breakdown (tiempo, ahorros, cloud)

2. **Accuracy Monitoring**
   - Gauge: Accuracy General
   - Bar Chart: Accuracy por Modelo
   - Line Chart: Accuracy Trend

3. **Real Estate Intelligence**
   - Map: Desarrollos por ubicación
   - Scatter: Precio vs Probabilidad
   - Table: Top Oportunidades

4. **Social Media Performance**
   - Line Chart: Engagement Trend
   - Bar Chart: Best Performing Content Types
   - Heatmap: Mejor hora/día para publicar

### Dashboard Web (Incluido)

**Acceso:** http://localhost:3001/static/dashboard.html

**Secciones:**
- 💰 Métricas de ROI (tarjetas grandes)
- 📊 Gráficos de tendencias
- 🎯 Precisión por categoría
- 📋 Lista de predicciones recientes

---

## 🔍 Análisis de Datos

### Explorar Predicciones

```python
import pandas as pd

# Obtener DataFrame con todas las predicciones
df = tracker.get_predictions_df()

# Filtrar por categoría
df_re = df[df['category'] == 'real_estate']

# Analizar accuracy por ubicación
accuracy_by_location = df_re.groupby('input_data.ubicacion').apply(
    lambda x: (x['outcome_status'] == 'success').mean()
)

print(accuracy_by_location)
```

### Identificar Patrones

```python
# Desarrollos que superaron expectativas
df_surprise = df_re[
    (df_re['actual_outcome'].apply(lambda x: x.get('dias_venta', 999))) < 
    (df_re['prediction'].apply(lambda x: x.get('dias_estimados', 0)))
]

print(f"Ventas más rápidas de lo esperado: {len(df_surprise)}")
```

---

## 🎯 Mejora Continua

### Proceso de Re-entrenamiento

1. **Recolectar outcomes** reales (actualizar via API)
2. **Analizar accuracy** por categoría/modelo
3. **Re-entrenar** si accuracy <80%
4. **Validar** con datos recientes
5. **Deploy** nuevo modelo

### Script de Re-entrenamiento con Validación

```python
# 1. Verificar accuracy actual
metrics = tracker.calculate_metrics()

if metrics.accuracy < 0.80:
    print("⚠️ Accuracy baja, re-entrenando...")
    
    # 2. Exportar datos recientes
    df = tracker.get_predictions_df()
    df_with_outcomes = df[df['outcome_status'] != 'pending']
    
    # 3. Preparar dataset
    # (código de preparación)
    
    # 4. Re-entrenar
    # python backend/scripts/train_all_models.py
    
    # 5. Validar
    # Probar con datos recientes
```

---

## 📞 Soporte

### Troubleshooting

**Dashboard no carga:**
```bash
# Verificar API está corriendo
curl http://localhost:3001/health

# Verificar archivos estáticos
ls backend/api/static/dashboard.html
```

**Predicciones no se registran:**
```bash
# Verificar directorio de datos
ls backend/data/metrics/

# Ver logs
tail -f backend/data/metrics/predictions.jsonl
```

**Alertas no se envían:**
```bash
# Verificar configuración
curl http://localhost:3001/api/alerts/config

# Ver alertas recientes
curl http://localhost:3001/api/alerts/recent
```

---

## 🎓 Best Practices

1. **Actualiza outcomes regularmente** (semanal o mensual)
2. **Revisa dashboard diariamente** para detectar anomalías
3. **Configura alertas personalizadas** según tus necesidades
4. **Exporta a Power BI mensualmente** para análisis profundo
5. **Re-entrena modelos trimestralmente** o cuando accuracy <80%
6. **Documenta decisiones importantes** en el campo `notes`

---

## 📚 Recursos

- **Dashboard**: http://localhost:3001/static/dashboard.html
- **API Docs**: http://localhost:3001/docs
- **Métricas**: http://localhost:3001/api/metrics/impact-report
- **ROI**: http://localhost:3001/api/metrics/roi-calculator

---

**¡El sistema está diseñado para mejorar continuamente con tus datos!** 📈
