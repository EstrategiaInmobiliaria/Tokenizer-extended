"""
API REST para el Sistema de Inteligencia TensorFlow
FastAPI backend que expone endpoints para todos los modelos
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import sys
from pathlib import Path
import uvicorn

# Agregar path de modelos
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from models.real_estate_opportunity import RealEstateOpportunityDetector
from models.social_media_optimizer import SocialMediaContentOptimizer
from models.personal_decision_models import TCOCalculator, TennisOptimizer

# Importar sistema de tracking
sys.path.insert(0, str(backend_path / "monitoring"))
from impact_tracker import ImpactTracker, MetricCategory, PredictionOutcome
from alert_system import SmartAlertSystem, check_and_alert_prediction, check_and_alert_metrics

# Power BI export (repositorio central + Push Dataset)
sys.path.insert(0, str(backend_path / "integrations"))
from powerbi_exporter import PowerBIExportPipeline, PredictionRowBuilder
import os

# Inicializar FastAPI
app = FastAPI(
    title="Sistema de Inteligencia TensorFlow",
    description="API para predicciones de ML en Inmobiliario, Redes Sociales y Decisiones Personales",
    version="1.0.0"
)

# Inicializar tracker de impacto
impact_tracker = ImpactTracker()
alert_system = SmartAlertSystem()
powerbi_pipeline = PowerBIExportPipeline()
POWERBI_AUTO_EXPORT = os.getenv("POWERBI_AUTO_EXPORT_ON_PREDICT", "true").lower() == "true"

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos globales (se cargan al inicio)
re_detector = RealEstateOpportunityDetector()
sm_optimizer = SocialMediaContentOptimizer()
tco_calculator = TCOCalculator()
tennis_optimizer = TennisOptimizer()

# Montar archivos estáticos (dashboard)
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# ==================== SCHEMAS ====================

class RealEstateInput(BaseModel):
    precio_m2: float = Field(..., description="Precio por metro cuadrado")
    ubicacion: str = Field(..., description="Ubicación del desarrollo")
    amenidades: int = Field(..., ge=0, le=20, description="Cantidad de amenidades")
    velocidad_ventas: float = Field(..., ge=0, le=1, description="Velocidad de ventas (0-1)")
    cap_rate: float = Field(..., description="Tasa de capitalización (%)")

class RealEstateOutput(BaseModel):
    probabilidad_venta_12m: float
    precio_estimado: float
    dias_estimados: int
    recomendacion: str
    certeza: str

class SocialMediaPostInput(BaseModel):
    tipo_contenido: str = Field(..., description="Carrusel, Reel, Story, Post")
    hora: int = Field(..., ge=0, le=23)
    dia_semana: int = Field(..., ge=0, le=6)
    num_hashtags: int = Field(..., ge=0, le=30)
    tema_categoria: str
    longitud_caption: int = Field(..., ge=0)

class SocialMediaPostOutput(BaseModel):
    engagement_score: float
    probabilidad_viral: float
    alcance_estimado: int
    recomendacion: str
    confianza: str

class WeeklyScheduleInput(BaseModel):
    temas_disponibles: List[str] = Field(..., description="Lista de temas del Índice Maestro")

class AutoTCOInput(BaseModel):
    precio_inicial: float
    gasolina_mensual: float
    seguro_anual: float
    mantenimiento_anual: float
    depreciacion_anual: float
    km_anuales: int
    rendimiento_km_l: float
    es_electrico: int = Field(..., ge=0, le=1)

class AutoTCOOutput(BaseModel):
    costo_operacion_3_anos: float
    valor_residual_3_anos: float
    tco_total_3_anos: float
    costo_mensual_promedio: float
    recomendacion: str

class VehicleComparisonInput(BaseModel):
    vehicle1: AutoTCOInput
    vehicle2: AutoTCOInput
    vehicle1_name: str
    vehicle2_name: str

class TennisConditionsInput(BaseModel):
    temperatura: int = Field(..., ge=10, le=40)
    rival_nivel: int = Field(..., ge=1, le=10)
    dia_semana: int = Field(..., ge=0, le=6)
    horas_descanso: int = Field(..., ge=0, le=3)

class TennisSetupOutput(BaseModel):
    tension_kg: int
    pelota: str
    probabilidad_victoria: float
    mejora_vs_promedio: float


# Schemas para tracking
class OutcomeUpdate(BaseModel):
    prediction_id: str
    actual_outcome: Dict[str, Any]
    success: bool
    notes: str = ""


# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "Sistema de Inteligencia TensorFlow",
        "version": "1.0.0",
        "modelos_disponibles": [
            "real_estate_opportunity",
            "social_content_optimizer",
            "tco_calculator",
            "tennis_optimizer"
        ],
        "dashboard": "/static/dashboard.html",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Status de modelos"""
    models_path = backend_path / "models"
    
    return {
        "status": "healthy",
        "models": {
            "real_estate_opportunity": (models_path / "real_estate_opportunity.tflite").exists(),
            "social_content_optimizer": (models_path / "social_content_optimizer.tflite").exists(),
            "tco_calculator": (models_path / "tco_calculator.tflite").exists(),
            "tennis_optimizer": (models_path / "tennis_optimizer.tflite").exists(),
        }
    }


# ==================== INMOBILIARIO ====================

@app.post("/api/predict/real-estate", response_model=RealEstateOutput)
async def predict_real_estate(data: RealEstateInput):
    """
    Predice oportunidad de venta para un desarrollo inmobiliario
    
    Retorna:
    - Probabilidad de venta en 12 meses
    - Precio estimado de venta
    - Días estimados para cerrar
    - Recomendación (ALTA PRIORIDAD, ANALIZAR, BAJA PRIORIDAD)
    """
    try:
        resultado = re_detector.predict(data.dict())
        
        # Log predicción para tracking de impacto
        pred_id = impact_tracker.log_prediction(
            MetricCategory.REAL_ESTATE,
            "real_estate_opportunity",
            data.dict(),
            resultado,
            confidence_score=resultado['probabilidad_venta_12m']
        )
        
        # Verificar alertas
        check_and_alert_prediction(resultado, "real_estate")

        # Export automático a Power BI (SQL + Push Dataset si está configurado)
        if POWERBI_AUTO_EXPORT:
            try:
                powerbi_pipeline.export_from_model_output(
                    category="real_estate",
                    model="real_estate_opportunity",
                    prediction=resultado,
                    input_data=data.dict(),
                    id_negocio=pred_id,
                    confidence_score=resultado.get("probabilidad_venta_12m"),
                )
            except Exception:
                pass  # No bloquear predicción si falla el export
        
        # Agregar ID a respuesta
        resultado['prediction_id'] = pred_id
        
        return RealEstateOutput(**resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")


@app.post("/api/analyze/real-estate-batch")
async def analyze_real_estate_batch(desarrollos: List[RealEstateInput]):
    """
    Analiza múltiples desarrollos y retorna Top 3 oportunidades
    Útil para el análisis semanal automatizado
    """
    try:
        resultados = []
        for desarrollo in desarrollos:
            pred = re_detector.predict(desarrollo.dict())
            resultados.append({
                "desarrollo": desarrollo.dict(),
                "prediccion": pred
            })
        
        # Ordenar por probabilidad
        resultados.sort(key=lambda x: x['prediccion']['probabilidad_venta_12m'], reverse=True)
        
        return {
            "total_analizados": len(resultados),
            "top_3_oportunidades": resultados[:3],
            "resumen": f"De {len(resultados)} desarrollos, {sum(1 for r in resultados if r['prediccion']['probabilidad_venta_12m'] > 0.7)} son ALTA PRIORIDAD"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== REDES SOCIALES ====================

@app.post("/api/predict/social-media-post", response_model=SocialMediaPostOutput)
async def predict_social_media_post(data: SocialMediaPostInput):
    """
    Predice performance de un post específico
    """
    try:
        resultado = sm_optimizer.predict(data.dict())
        return SocialMediaPostOutput(**resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")


@app.post("/api/generate/weekly-content-schedule")
async def generate_weekly_schedule(data: WeeklyScheduleInput):
    """
    Genera calendario semanal optimizado de contenido
    
    Retorna plan de 7 días con:
    - Mejor horario de publicación
    - Tipo de contenido recomendado
    - Tema a cubrir
    - Engagement esperado
    """
    try:
        schedule = sm_optimizer.predict_week_schedule(data.temas_disponibles)
        
        return {
            "semana": schedule,
            "resumen": {
                "total_posts_recomendados": sum(len(dia['posts']) for dia in schedule),
                "mejor_dia": max(schedule, key=lambda d: d['posts'][0]['engagement_esperado'])['dia'],
                "temas_cubiertos": len(set(post['tema'] for dia in schedule for post in dia['posts']))
            },
            "recomendacion_n8n": "Configurar workflow para publicar automáticamente estos posts"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PERSONAL ====================

@app.post("/api/calculate/tco", response_model=AutoTCOOutput)
async def calculate_tco(data: AutoTCOInput):
    """
    Calcula Total Cost of Ownership para un vehículo
    """
    try:
        resultado = tco_calculator.calculate_tco(data.dict())
        return AutoTCOOutput(**resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en cálculo: {str(e)}")


@app.post("/api/compare/vehicles")
async def compare_vehicles(data: VehicleComparisonInput):
    """
    Compara TCO entre dos vehículos
    Ejemplo: Geely EX5 EM-i vs Toyota RAV4
    """
    try:
        comparacion = tco_calculator.compare_vehicles(
            data.vehicle1.dict(),
            data.vehicle2.dict(),
            data.vehicle1_name,
            data.vehicle2_name
        )
        return comparacion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize/tennis-setup", response_model=TennisSetupOutput)
async def optimize_tennis_setup(data: TennisConditionsInput):
    """
    Encuentra la configuración óptima de cordaje y pelota
    basado en condiciones del partido
    """
    try:
        resultado = tennis_optimizer.optimize_setup(data.dict())
        return TennisSetupOutput(**resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en optimización: {str(e)}")


# ==================== TRACKING & METRICS ====================

@app.post("/api/tracking/update-outcome")
async def update_prediction_outcome(data: OutcomeUpdate):
    """
    Actualiza el outcome real de una predicción para medir precisión y ROI
    """
    try:
        status = PredictionOutcome.SUCCESS if data.success else PredictionOutcome.FAILURE
        impact_tracker.update_outcome(
            data.prediction_id,
            data.actual_outcome,
            status,
            data.notes
        )
        return {"status": "ok", "message": "Outcome actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/impact-report")
async def get_impact_report(days: int = 30):
    """
    Genera reporte de impacto con ROI, precisión, tiempo ahorrado
    """
    try:
        report_text = impact_tracker.generate_impact_report(days)
        metrics = impact_tracker.calculate_metrics()
        
        from dataclasses import asdict
        return {
            "report_text": report_text,
            "metrics": asdict(metrics),
            "period_days": days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/roi-calculator")
async def calculate_roi(days: int = 30):
    """
    Calcula ROI detallado del sistema
    """
    try:
        metrics = impact_tracker.calculate_metrics()
        
        hourly_rate = 1000  # MXN/hora
        cloud_ml_cost_monthly = 570  # USD/mes evitado
        cloud_ml_cost_daily = cloud_ml_cost_monthly / 30
        
        time_value = metrics.time_saved_hours * hourly_rate
        cloud_savings = cloud_ml_cost_daily * days * 20
        total_value = time_value + metrics.money_saved + cloud_savings
        
        monthly_value = total_value * (30 / days) if days > 0 else 0
        annual_value = monthly_value * 12
        
        return {
            "period_days": days,
            "breakdown": {
                "time_saved_hours": metrics.time_saved_hours,
                "time_value_mxn": time_value,
                "direct_savings_mxn": metrics.money_saved,
                "cloud_costs_avoided_mxn": cloud_savings,
                "total_value_mxn": total_value
            },
            "projections": {
                "monthly_value_mxn": monthly_value,
                "annual_value_mxn": annual_value
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ALERTAS ====================

@app.get("/api/alerts/recent")
async def get_recent_alerts(hours: int = 24):
    """
    Obtiene alertas recientes del sistema
    """
    try:
        alerts = alert_system.get_recent_alerts(hours)
        return {
            "alerts": alerts,
            "total": len(alerts),
            "period_hours": hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts/config")
async def get_alert_config():
    """
    Obtiene configuración actual de alertas
    """
    return alert_system.config


@app.post("/api/alerts/config")
async def update_alert_config(config: Dict[str, Any]):
    """
    Actualiza configuración de alertas
    """
    try:
        alert_system.config.update(config)
        alert_system.save_config()
        return {"status": "ok", "config": alert_system.config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== INTEGRACIONES ====================

@app.post("/api/integrations/whatsapp-report")
async def generate_whatsapp_report(tipo: str = "inmobiliario"):
    """
    Genera reporte formateado para enviar por WhatsApp
    Tipos: inmobiliario, social_media, personal
    """
    try:
        if tipo == "inmobiliario":
            # Ejemplo: analizar 3 desarrollos ficticios
            desarrollos = [
                {"precio_m2": 45000, "ubicacion": "Querétaro", "amenidades": 12, 
                 "velocidad_ventas": 0.85, "cap_rate": 7.2},
                {"precio_m2": 52000, "ubicacion": "CDMX", "amenidades": 15, 
                 "velocidad_ventas": 0.72, "cap_rate": 6.8},
                {"precio_m2": 38000, "ubicacion": "Monterrey", "amenidades": 10, 
                 "velocidad_ventas": 0.90, "cap_rate": 7.5}
            ]
            
            resultados = [re_detector.predict(d) for d in desarrollos]
            mejor = max(resultados, key=lambda x: x['probabilidad_venta_12m'])
            
            mensaje = f"""🏗️ *REPORTE SEMANAL INMOBILIARIO*

📊 Analizados: 3 nuevos desarrollos

🎯 *OPORTUNIDAD DESTACADA*
Probabilidad de venta: {mejor['certeza']}
Precio estimado: ${mejor['precio_estimado']:,.0f}
Días estimados: {mejor['dias_estimados']}
*Recomendación: {mejor['recomendacion']}*

¿Quieres el pitch completo?"""
            
            return {"mensaje_whatsapp": mensaje, "formato": "markdown"}
        
        else:
            return {"error": "Tipo no soportado"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/integrations/powerbi-data")
async def get_powerbi_data(limit: int = 500):
    """
    Endpoint REST para Power BI (Get Data → Web).

    Preferible para pruebas. En producción usa el repositorio SQL
    (DirectQuery/Import) vía DATABASE_URL — sin Personal Gateway Python.
    """
    try:
        df = powerbi_pipeline.db.fetch_recent(limit=limit)
        if df.empty:
            # Fallback: métricas agregadas si aún no hay filas exportadas
            return {
                "mode": "aggregate_fallback",
                "hint": "Ejecuta POST /api/integrations/powerbi/export o el script export_to_powerbi.py",
                "real_estate": {
                    "desarrollos_analizados": 0,
                    "oportunidades_alta_prioridad": 0,
                    "tasa_exito_predicciones": 0.0,
                },
                "rows": [],
            }

        records = json.loads(df.to_json(orient="records", date_format="iso"))
        return {
            "mode": "repository",
            "table": powerbi_pipeline.db.table_name,
            "total_in_db": powerbi_pipeline.db.count_rows(),
            "returned": len(records),
            "rows": records,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/integrations/powerbi/export")
async def export_to_powerbi(
    source: str = "tracker",
    write_mode: str = "append",
    mode: Optional[str] = None,
):
    """
    Dispara exportación TensorFlow → Power BI.

    - source: tracker | live
    - write_mode: append | replace | upsert
    - mode: repository | streaming | hybrid

    Arquitectura recomendada: repository/hybrid → SQL → Power BI Import/DirectQuery.
    Evita ejecutar Python dentro de Power Query (Personal Gateway).
    """
    try:
        pipeline = PowerBIExportPipeline(mode=mode) if mode else powerbi_pipeline

        if source == "live":
            # Generar predicciones frescas de muestra y exportar
            rows = []
            builder = PredictionRowBuilder()
            sample = {
                "precio_m2": 45000,
                "ubicacion": "Querétaro",
                "amenidades": 12,
                "velocidad_ventas": 0.85,
                "cap_rate": 7.2,
            }
            pred = re_detector.predict(sample)
            rows.append(
                builder.build_row(
                    category="real_estate",
                    model="real_estate_opportunity",
                    prediction=pred,
                    input_data=sample,
                    id_negocio="LIVE-API-EXPORT",
                    confidence_score=pred.get("probabilidad_venta_12m"),
                )
            )
            result = pipeline.export_predictions(rows, write_mode=write_mode)
        else:
            metrics_file = backend_path / "data" / "metrics" / "predictions.jsonl"
            if metrics_file.exists():
                result = pipeline.export_batch_file(
                    metrics_file, write_mode=write_mode
                )
            else:
                # Bootstrap: una predicción live si no hay historial
                source = "live"
                sample = {
                    "precio_m2": 45000,
                    "ubicacion": "Querétaro",
                    "amenidades": 12,
                    "velocidad_ventas": 0.85,
                    "cap_rate": 7.2,
                }
                pred = re_detector.predict(sample)
                result = pipeline.export_predictions(
                    [
                        PredictionRowBuilder.build_row(
                            category="real_estate",
                            model="real_estate_opportunity",
                            prediction=pred,
                            input_data=sample,
                            id_negocio="BOOTSTRAP-EXPORT",
                            confidence_score=pred.get("probabilidad_venta_12m"),
                        )
                    ],
                    write_mode=write_mode,
                )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/integrations/powerbi/push")
async def push_to_powerbi_streaming(rows: List[Dict[str, Any]]):
    """
    Envía filas directamente al Push Dataset de Power BI (streaming).
    Requiere POWERBI_PUSH_URL en el entorno.
    """
    try:
        if not powerbi_pipeline.push.enabled:
            raise HTTPException(
                status_code=400,
                detail="POWERBI_PUSH_URL no configurada. Crea un Streaming Dataset en Power BI Service y pega la URL.",
            )
        result = powerbi_pipeline.push.push_rows(rows)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/integrations/powerbi/status")
async def powerbi_export_status():
    """Estado de la integración Power BI (DB + Push)."""
    return {
        "export_mode": powerbi_pipeline.mode,
        "auto_export_on_predict": POWERBI_AUTO_EXPORT,
        "database": {
            "scheme": powerbi_pipeline.db.database_url.split("://", 1)[0],
            "table": powerbi_pipeline.db.table_name,
            "row_count": powerbi_pipeline.db.count_rows(),
        },
        "push_dataset": {
            "configured": powerbi_pipeline.push.enabled,
            "url_set": bool(powerbi_pipeline.push.push_url),
            "schema_mode": powerbi_pipeline.push.schema_mode,
        },
        "recommended_powerbi_connection": {
            "production": "SQL DirectQuery/Import sobre DATABASE_URL",
            "dev_web": "GET /api/integrations/powerbi-data",
            "realtime": "Push Dataset via POWERBI_PUSH_URL (app.powerbi.com streaming API)",
            "setup_guide": "POWERBI_STREAMING_SETUP.md",
            "avoid": "Python script dentro de Power Query (requiere Personal Gateway)",
        },
    }


@app.get("/api/integrations/powerbi/streaming-schema")
async def powerbi_streaming_schema(mode: str = "full"):
    """
    Schema exacto a crear en Power BI Service
    (Nuevo → Conjunto de datos de streaming → API).

    Incluye payload de muestra (equivalente al que muestra Power BI)
    y recuerda activar 'Análisis de datos históricos'.
    """
    schema_mode = mode if mode in ("full", "minimal") else "full"
    return {
        "dataset_name_suggested": "Predicciones_TensorFlow",
        "source": "API",
        "historic_data_analysis": "REQUIRED — activar interruptor antes de Crear",
        "fields": [
            {"name": name, "type": pbi_type}
            for name, pbi_type in PowerBIPushClient.schema_definition(schema_mode).items()
        ],
        "sample_payload": PowerBIPushClient.sample_payload(schema_mode),
        "env": {
            "POWERBI_PUSH_URL": "Pegar URL de la pestaña Raw tras Crear",
            "POWERBI_STREAMING_SCHEMA": schema_mode,
        },
        "test_command": "python scripts/test_powerbi_push.py",
    }


@app.post("/api/integrations/powerbi/test-push")
async def powerbi_test_push():
    """
    Envía 1 fila de prueba a la Push URL configurada.
    Útil justo después de crear el Streaming Dataset en app.powerbi.com.
    """
    if not powerbi_pipeline.push.enabled:
        raise HTTPException(
            status_code=400,
            detail=(
                "POWERBI_PUSH_URL no configurada. "
                "Crea el dataset en app.powerbi.com → copia URL Raw → .env"
            ),
        )
    return powerbi_pipeline.push.test_connection()


# ==================== MAIN ====================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Iniciando API de Inteligencia TensorFlow")
    print("=" * 60)
    print("\n📡 Servidor: http://localhost:3001")
    print("📚 Docs: http://localhost:3001/docs")
    print("🔍 Health: http://localhost:3001/health")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=3001,
        reload=True,
        log_level="info"
    )
