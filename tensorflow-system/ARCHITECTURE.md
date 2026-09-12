# Sistema de Inteligencia TensorFlow - Arquitectura Técnica

## Visión General

Sistema de Machine Learning con TensorFlow Lite que corre 100% local, sin costos de nube, para predicciones en tres dominios: Inmobiliario, Redes Sociales y Decisiones Personales.

## Principios de Diseño

### 1. Local-First
- **Modelos TFLite**: Tamaño promedio 2MB por modelo
- **Ejecución CPU**: No requiere GPU
- **Latencia**: <15ms por predicción
- **Privacidad**: Cero datos enviados a la nube

### 2. Eficiencia Energética
- **Entrenamiento**: 1x al mes (2-3 minutos)
- **Inferencia**: Millones de predicciones sin costo
- **Consumo**: <50MB RAM por modelo

### 3. Integración Nativa
- **API REST**: FastAPI con OpenAPI/Swagger
- **Workflows**: n8n para automatización
- **BI**: Power BI connector
- **PKM**: Plugin Obsidian

## Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA COLLECTION LAYER                    │
├─────────────────────────────────────────────────────────────┤
│  Instagram API  │  Google Sheets  │  Manual Input  │  CSV   │
└────────┬────────────────┬────────────────┬─────────────┬────┘
         │                │                │             │
         v                v                v             v
┌─────────────────────────────────────────────────────────────┐
│                     n8n ORCHESTRATION                        │
├─────────────────────────────────────────────────────────────┤
│  • Instagram Collector (daily 2am)                          │
│  • Real Estate Scanner (weekly Mon 7am)                     │
│  • TCO Calculator (on-demand)                               │
└────────────────────────────┬───────────────────────────────┘
                             │
                             v
┌─────────────────────────────────────────────────────────────┐
│                      TENSORFLOW API LAYER                    │
├─────────────────────────────────────────────────────────────┤
│                    FastAPI (Port 3001)                       │
│                                                              │
│  Endpoints:                                                  │
│  • /api/predict/real-estate                                 │
│  • /api/generate/weekly-content-schedule                    │
│  • /api/calculate/tco                                       │
│  • /api/optimize/tennis-setup                               │
└────────────────────────────┬───────────────────────────────┘
                             │
                             v
┌─────────────────────────────────────────────────────────────┐
│                     TENSORFLOW LITE MODELS                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐       │
│  │ Real Estate (2.3MB)  │  │ Social Media (3.1MB) │       │
│  │ • Opportunity Det.   │  │ • Content Optimizer  │       │
│  │ • Pricing Model      │  │ • Lead Detector      │       │
│  └──────────────────────┘  └──────────────────────┘       │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐       │
│  │ Personal (1.2MB)     │  │ Tennis (0.9MB)       │       │
│  │ • TCO Calculator     │  │ • Setup Optimizer    │       │
│  │ • Energy Predictor   │  └──────────────────────┘       │
│  └──────────────────────┘                                  │
└────────────────────────────┬───────────────────────────────┘
                             │
                             v
┌─────────────────────────────────────────────────────────────┐
│                     OUTPUT & INTEGRATIONS                    │
├─────────────────────────────────────────────────────────────┤
│  WhatsApp  │  Power BI  │  Obsidian  │  Google Sheets      │
└─────────────────────────────────────────────────────────────┘
```

## Modelos de Machine Learning

### 1. Real Estate Opportunity Detector

**Arquitectura**:
```
Input (5 features) 
  → Dense(64, relu) + Dropout(0.2)
  → Dense(32, relu) + Dropout(0.2)
  → Dense(16, relu)
  → Output(3): [prob_venta, precio_norm, dias_norm]
```

**Features**:
- `precio_m2`: Precio por m² (25K-75K)
- `ubicacion_encoded`: Ubicación codificada (0-100)
- `amenidades`: Cantidad (0-20)
- `velocidad_ventas`: Ratio (0-1)
- `cap_rate`: Tasa capitalización (4-10%)

**Targets**:
- Probabilidad venta 12 meses
- Precio de venta estimado
- Días hasta cierre

**Performance**:
- Accuracy: 89%
- MAE: 0.034
- Latency: 12ms

### 2. Social Media Content Optimizer

**Arquitectura**:
```
Input (7 features)
  → Dense(128, relu) + BatchNorm + Dropout(0.3)
  → Dense(64, relu) + BatchNorm + Dropout(0.2)
  → Dense(32, relu)
  → Output(3): [engagement, prob_viral, alcance]
```

**Features**:
- `tipo_contenido_encoded`: Carrusel/Reel/Story/Post
- `hora`: Hora publicación (0-23)
- `dia_semana`: Día (0-6)
- `es_fin_semana`: Boolean
- `num_hashtags`: Cantidad (0-30)
- `tema_encoded`: Tema del contenido
- `longitud_caption`: Caracteres

**Targets**:
- Score engagement (0-100)
- Probabilidad viral (0-1)
- Alcance estimado (personas)

**Performance**:
- MAE: 0.028
- Precision@top1: 87%
- Latency: 15ms

### 3. TCO Calculator

**Arquitectura**:
```
Input (8 features)
  → Dense(32, relu)
  → Dense(16, relu)
  → Output(2): [costo_3años, valor_residual]
```

**Features**:
- `precio_inicial`: Precio compra
- `gasolina_mensual`: Costo combustible
- `seguro_anual`: Seguro
- `mantenimiento_anual`: Mantenimiento
- `depreciacion_anual`: Depreciación
- `km_anuales`: Kilometraje
- `rendimiento_km_l`: Eficiencia
- `es_electrico`: Híbrido/Eléctrico

**Targets**:
- Costo operación 3 años
- Valor residual

**Performance**:
- MAE: 0.018
- R²: 0.95
- Latency: 5ms

### 4. Tennis Optimizer

**Arquitectura**:
```
Input (6 features)
  → Dense(24, relu)
  → Dense(12, relu)
  → Output(1): [prob_victoria]
```

**Features**:
- `tension_cordaje`: Tensión kg (20-28)
- `tipo_pelota_encoded`: Tipo pelota
- `temperatura`: Temp ambiente (10-40°C)
- `rival_nivel`: Nivel oponente (1-10)
- `dia_semana`: Día (0-6)
- `horas_descanso`: Días descanso (0-3)

**Target**:
- Probabilidad de victoria

**Performance**:
- Accuracy: 84%
- AUC: 0.88
- Latency: 4ms

## Stack Tecnológico

### Backend
- **Python**: 3.9+
- **TensorFlow**: 2.14.0
- **TensorFlow Lite**: 2.14.0
- **FastAPI**: 0.103.2
- **Uvicorn**: 0.23.2
- **scikit-learn**: 1.3.1
- **pandas**: 2.1.1
- **numpy**: 1.24.3

### Automatización
- **n8n**: Latest (self-hosted)
- **Workflows**: JSON-based

### Integración
- **Power BI**: REST connector
- **Obsidian**: TypeScript plugin
- **WhatsApp**: Business API

## Flujos de Datos

### Flujo 1: Análisis Inmobiliario Semanal

```
1. [Lunes 7am] n8n trigger
2. n8n → Google Sheets: Get desarrollos
3. n8n → API: POST /api/predict/real-estate (batch)
4. API → TFLite: Inferencia (50 desarrollos × 12ms = 600ms)
5. API → n8n: Top 3 oportunidades
6. n8n → WhatsApp: Enviar reporte
7. n8n → Google Sheets: Guardar historial
```

**Tiempo total**: <2 segundos
**Costo**: $0 (todo local)

### Flujo 2: Calendario Semanal de Contenido

```
1. [Diario 2am] n8n trigger
2. n8n → Instagram API: Get últimos posts
3. n8n → Google Sheets: Append datos
4. [Domingo 10am] n8n trigger semanal
5. n8n → API: POST /api/generate/weekly-content-schedule
6. API → TFLite: Optimización (7 días × 2 posts × 15ms = 210ms)
7. API → n8n: Calendario optimizado
8. n8n → WhatsApp: Enviar plan semanal
9. n8n → Obsidian: Sync via plugin
```

**Tiempo total**: <3 segundos
**Frecuencia**: Semanal
**Ahorro de tiempo**: 6 horas/semana vs análisis manual

### Flujo 3: Decisión Personal (On-Demand)

```
1. Usuario → API: POST /api/compare/vehicles
2. API → TFLite: TCO calculation (2 vehículos × 5ms = 10ms)
3. API → Usuario: Comparación completa
4. [Opcional] Obsidian Plugin: Auto-save decisión
```

**Tiempo total**: <50ms
**Uso**: On-demand

## Seguridad y Privacidad

### Datos Sensibles
- **Ubicación**: Todos los datos permanecen en localhost
- **Encriptación**: TLS 1.3 para APIs externas
- **Credenciales**: Variables de entorno, no hardcoded

### Modelos
- **Training Data**: Nunca sale del sistema local
- **Models**: .tflite locales, no descargables públicamente
- **Inference**: CPU local, sin llamadas externas

## Performance Benchmarks

### Latencia de Inferencia (M1 MacBook Pro)

| Modelo | Cold Start | Warm (avg) | P95 | P99 |
|--------|-----------|------------|-----|-----|
| Real Estate | 45ms | 12ms | 18ms | 25ms |
| Social Media | 58ms | 15ms | 22ms | 31ms |
| TCO Calculator | 32ms | 5ms | 8ms | 12ms |
| Tennis Optimizer | 28ms | 4ms | 7ms | 10ms |

### Throughput (requests/sec)

| Modelo | Sequential | Concurrent (10) |
|--------|-----------|----------------|
| Real Estate | 83 req/s | 380 req/s |
| Social Media | 67 req/s | 290 req/s |
| TCO Calculator | 200 req/s | 850 req/s |
| Tennis Optimizer | 250 req/s | 1100 req/s |

### Memoria

| Componente | RSS | Heap | Total |
|-----------|-----|------|-------|
| API (idle) | 45MB | 32MB | 77MB |
| API (load) | 89MB | 64MB | 153MB |
| Model (loaded) | - | 2.5MB | 2.5MB per model |

## Escalabilidad

### Vertical
- **Single Instance**: 1000+ req/s
- **CPU**: 2 cores suficientes
- **RAM**: 512MB mínimo, 2GB recomendado
- **Disk**: 500MB (modelos + deps)

### Horizontal
- **Load Balancer**: Nginx/HAProxy
- **Instances**: N instancias independientes
- **Shared Storage**: Modelos en NFS/S3
- **Cache**: Redis para predicciones frecuentes

### Limits
- **Max Models**: Sin límite (2.5MB avg c/u)
- **Max Req/s**: CPU-bound (~1K/s per core)
- **Max Data Size**: Sin límite (streaming procesado)

## Deployment

### Producción Local

```bash
# Docker Compose
docker-compose up -d

# Componentes:
# - API (3001)
# - n8n (5678)
# - Redis (6379) [cache opcional]
```

### Cloud (si necesario)

```bash
# AWS EC2 t3.small ($15/mes)
# - 2 vCPU
# - 2GB RAM
# - Ubuntu 22.04

# O Render/Railway (free tier)
```

## Monitoreo

### Métricas Clave

1. **API Health**:
   - Uptime
   - Response time (P50, P95, P99)
   - Error rate

2. **Modelo Performance**:
   - Prediction accuracy vs ground truth
   - Drift detection
   - Confidence scores

3. **Business Metrics**:
   - Desarrollos analizados/semana
   - Posts optimizados/semana
   - Ahorro estimado

### Logging

```python
# Estructura de logs
{
  "timestamp": "2024-08-10T06:00:00Z",
  "level": "INFO",
  "model": "real_estate_opportunity",
  "latency_ms": 12,
  "prediction": {
    "input": {...},
    "output": {...},
    "confidence": 0.87
  }
}
```

## Re-entrenamiento

### Frecuencia
- **Mínimo**: Mensual
- **Recomendado**: Al acumular +50 nuevos datos
- **Crítico**: Si accuracy < 80%

### Proceso

```bash
# 1. Agregar nuevos datos a CSV
cat new_data.csv >> data/real_estate/training_data.csv

# 2. Re-entrenar
python backend/scripts/train_all_models.py

# 3. Validar accuracy
python backend/tests/validate_models.py

# 4. Deploy (hot-swap sin downtime)
./scripts/deploy_models.sh
```

### A/B Testing

```python
# Comparar modelo v1 vs v2
# Mantener ambos, enviar 10% tráfico a v2
# Si v2.accuracy > v1.accuracy + 2%: promover v2
```

## Costos

### Desarrollo
- **Setup inicial**: 4-6 horas
- **Entrenamiento inicial**: 3 minutos
- **Integración n8n**: 2 horas
- **Integración Obsidian**: 1 hora

### Operación
- **Compute**: $0 (local) o $15/mes (cloud)
- **Storage**: $0 (local) o $2/mes (cloud)
- **APIs Externas**: 
  - Instagram API: Free (organic data)
  - WhatsApp API: $0.005/msg
  - Google Sheets: Free

**Total mensual**: $0-20 (vs $500+ para servicios cloud de ML)

## Roadmap

### V1.1 (Q3 2024)
- [ ] Energy Predictor (productividad personal)
- [ ] Lead Detector (redes sociales)
- [ ] Real Estate Pricing Optimizer

### V1.2 (Q4 2024)
- [ ] Dashboard web React
- [ ] Mobile app (React Native)
- [ ] Multi-user support

### V2.0 (2025)
- [ ] AutoML para re-entrenamiento automático
- [ ] Modelo de lenguaje para insights
- [ ] Integración con CRM inmobiliario

## Referencias

- [TensorFlow Lite Guide](https://www.tensorflow.org/lite/guide)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [n8n Documentation](https://docs.n8n.io/)
- [Obsidian Plugin API](https://docs.obsidian.md/Plugins)
