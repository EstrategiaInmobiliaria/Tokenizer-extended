"""
Sistema de Métricas y Tracking de Impacto
Mide el valor real generado por las predicciones del sistema
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from dataclasses import dataclass, asdict
from enum import Enum

class MetricCategory(Enum):
    REAL_ESTATE = "real_estate"
    SOCIAL_MEDIA = "social_media"
    PERSONAL = "personal"

class PredictionOutcome(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"

@dataclass
class PredictionRecord:
    """Registro de una predicción con su outcome real"""
    id: str
    timestamp: datetime
    category: MetricCategory
    model: str
    input_data: Dict
    prediction: Dict
    actual_outcome: Optional[Dict] = None
    outcome_status: PredictionOutcome = PredictionOutcome.PENDING
    confidence_score: float = 0.0
    notes: str = ""
    
    def to_dict(self):
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat(),
            'category': self.category.value,
            'outcome_status': self.outcome_status.value
        }

@dataclass
class ImpactMetrics:
    """Métricas de impacto del sistema"""
    # Tiempo ahorrado
    time_saved_hours: float = 0.0
    
    # Precisión
    total_predictions: int = 0
    correct_predictions: int = 0
    accuracy: float = 0.0
    
    # Valor monetario
    money_saved: float = 0.0
    revenue_generated: float = 0.0
    
    # Engagement (redes sociales)
    predicted_engagement: float = 0.0
    actual_engagement: float = 0.0
    engagement_improvement: float = 0.0
    
    # Inmobiliario
    deals_predicted_success: int = 0
    deals_actual_success: int = 0
    avg_time_to_close: float = 0.0
    
    # Personal
    decisions_optimized: int = 0
    avg_confidence: float = 0.0


class ImpactTracker:
    """Sistema de tracking de impacto y métricas"""
    
    def __init__(self, data_dir: str = "backend/data/metrics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.predictions_file = self.data_dir / "predictions.jsonl"
        self.metrics_file = self.data_dir / "impact_metrics.json"
        
    def log_prediction(self, 
                      category: MetricCategory,
                      model: str,
                      input_data: Dict,
                      prediction: Dict,
                      confidence_score: float = 0.0) -> str:
        """Registra una nueva predicción"""
        
        pred_id = f"{category.value}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        record = PredictionRecord(
            id=pred_id,
            timestamp=datetime.now(),
            category=category,
            model=model,
            input_data=input_data,
            prediction=prediction,
            confidence_score=confidence_score
        )
        
        # Guardar en JSONL
        with open(self.predictions_file, 'a') as f:
            f.write(json.dumps(record.to_dict()) + '\n')
        
        print(f"✅ Predicción registrada: {pred_id}")
        return pred_id
    
    def update_outcome(self, 
                      pred_id: str,
                      actual_outcome: Dict,
                      outcome_status: PredictionOutcome,
                      notes: str = ""):
        """Actualiza el outcome real de una predicción"""
        
        # Leer todas las predicciones
        predictions = []
        if self.predictions_file.exists():
            with open(self.predictions_file, 'r') as f:
                predictions = [json.loads(line) for line in f]
        
        # Encontrar y actualizar
        updated = False
        for pred in predictions:
            if pred['id'] == pred_id:
                pred['actual_outcome'] = actual_outcome
                pred['outcome_status'] = outcome_status.value
                pred['notes'] = notes
                updated = True
                break
        
        if updated:
            # Re-escribir archivo
            with open(self.predictions_file, 'w') as f:
                for pred in predictions:
                    f.write(json.dumps(pred) + '\n')
            
            print(f"✅ Outcome actualizado: {pred_id}")
            
            # Re-calcular métricas
            self.calculate_metrics()
        else:
            print(f"❌ Predicción no encontrada: {pred_id}")
    
    def calculate_metrics(self) -> ImpactMetrics:
        """Calcula métricas de impacto agregadas"""
        
        if not self.predictions_file.exists():
            return ImpactMetrics()
        
        # Cargar predicciones
        predictions = []
        with open(self.predictions_file, 'r') as f:
            predictions = [json.loads(line) for line in f]
        
        metrics = ImpactMetrics()
        metrics.total_predictions = len(predictions)
        
        # Predicciones con outcome
        completed = [p for p in predictions if p['outcome_status'] != 'pending']
        
        if completed:
            # Precisión general
            success = [p for p in completed if p['outcome_status'] == 'success']
            metrics.correct_predictions = len(success)
            metrics.accuracy = len(success) / len(completed) if completed else 0.0
        
        # Métricas por categoría
        for category in MetricCategory:
            cat_preds = [p for p in predictions if p['category'] == category.value]
            
            if category == MetricCategory.REAL_ESTATE:
                metrics = self._calculate_real_estate_metrics(cat_preds, metrics)
            elif category == MetricCategory.SOCIAL_MEDIA:
                metrics = self._calculate_social_media_metrics(cat_preds, metrics)
            elif category == MetricCategory.PERSONAL:
                metrics = self._calculate_personal_metrics(cat_preds, metrics)
        
        # Guardar métricas
        with open(self.metrics_file, 'w') as f:
            json.dump(asdict(metrics), f, indent=2)
        
        return metrics
    
    def _calculate_real_estate_metrics(self, predictions: List[Dict], metrics: ImpactMetrics) -> ImpactMetrics:
        """Calcula métricas específicas de inmobiliario"""
        
        completed = [p for p in predictions if p['outcome_status'] != 'pending']
        
        # Deals predichos como exitosos
        high_prob = [p for p in predictions 
                    if p['prediction'].get('probabilidad_venta_12m', 0) > 0.7]
        metrics.deals_predicted_success = len(high_prob)
        
        # Deals realmente exitosos
        actual_success = [p for p in completed 
                         if p.get('actual_outcome', {}).get('vendido', False)]
        metrics.deals_actual_success = len(actual_success)
        
        # Tiempo promedio de cierre
        if actual_success:
            dias_reales = [p['actual_outcome'].get('dias_venta', 0) for p in actual_success]
            metrics.avg_time_to_close = sum(dias_reales) / len(dias_reales)
        
        # Tiempo ahorrado (6 horas por análisis manual vs 2 segundos)
        metrics.time_saved_hours += len(predictions) * 6.0
        
        return metrics
    
    def _calculate_social_media_metrics(self, predictions: List[Dict], metrics: ImpactMetrics) -> ImpactMetrics:
        """Calcula métricas específicas de redes sociales"""
        
        completed = [p for p in predictions if p['outcome_status'] != 'pending']
        
        if completed:
            # Engagement predicho vs real
            predicted_eng = [p['prediction'].get('engagement_score', 0) for p in completed]
            actual_eng = [p.get('actual_outcome', {}).get('engagement_real', 0) for p in completed]
            
            if predicted_eng and actual_eng:
                metrics.predicted_engagement = sum(predicted_eng) / len(predicted_eng)
                metrics.actual_engagement = sum(actual_eng) / len(actual_eng)
                
                # Mejora vs baseline (baseline = 50)
                baseline = 50
                metrics.engagement_improvement = ((metrics.actual_engagement - baseline) / baseline) * 100
        
        # Tiempo ahorrado (4 horas de planificación semanal vs 5 min)
        weeks = len(predictions) / 14  # Asumiendo 2 posts por día
        metrics.time_saved_hours += weeks * 4.0
        
        return metrics
    
    def _calculate_personal_metrics(self, predictions: List[Dict], metrics: ImpactMetrics) -> ImpactMetrics:
        """Calcula métricas específicas de decisiones personales"""
        
        completed = [p for p in predictions if p['outcome_status'] != 'pending']
        
        metrics.decisions_optimized = len(predictions)
        
        # Confianza promedio
        if predictions:
            confidences = [p.get('confidence_score', 0) for p in predictions]
            metrics.avg_confidence = sum(confidences) / len(confidences)
        
        # Dinero ahorrado (de decisiones TCO)
        tco_decisions = [p for p in completed 
                        if p['model'] == 'tco_calculator' 
                        and p.get('actual_outcome', {}).get('ahorro_real')]
        
        if tco_decisions:
            ahorros = [p['actual_outcome']['ahorro_real'] for p in tco_decisions]
            metrics.money_saved = sum(ahorros)
        
        # Tiempo ahorrado (2 horas por decisión importante)
        metrics.time_saved_hours += len(predictions) * 2.0
        
        return metrics
    
    def generate_impact_report(self, days: int = 30) -> str:
        """Genera reporte de impacto en formato texto"""
        
        metrics = self.calculate_metrics()
        
        # Calcular ROI
        hours_saved = metrics.time_saved_hours
        hourly_rate = 1000  # MXN por hora (ajustable)
        time_value = hours_saved * hourly_rate
        total_value = time_value + metrics.money_saved + (metrics.revenue_generated or 0)
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   📊 REPORTE DE IMPACTO - ÚLTIMOS {days} DÍAS                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

📈 MÉTRICAS GENERALES
{'─' * 78}
Total de predicciones:          {metrics.total_predictions:>10,}
Predicciones verificadas:       {metrics.correct_predictions:>10,}
Precisión del sistema:          {metrics.accuracy:>10.1%}
Confianza promedio:             {metrics.avg_confidence:>10.1%}

⏱️  AHORRO DE TIEMPO
{'─' * 78}
Horas ahorradas:                {metrics.time_saved_hours:>10.1f} h
Valor del tiempo ($1,000/h):   ${time_value:>10,.0f}

💰 IMPACTO ECONÓMICO
{'─' * 78}
Dinero ahorrado directo:        ${metrics.money_saved:>10,.0f}
Ingresos generados:             ${metrics.revenue_generated:>10,.0f}
Valor total generado:           ${total_value:>10,.0f}

🏗️  INMOBILIARIO
{'─' * 78}
Desarrollos analizados:         {metrics.deals_predicted_success:>10,}
Predicciones exitosas:          {metrics.deals_actual_success:>10,}
Tiempo promedio cierre:         {metrics.avg_time_to_close:>10.0f} días

📱 REDES SOCIALES
{'─' * 78}
Engagement predicho:            {metrics.predicted_engagement:>10.1f}/100
Engagement real:                {metrics.actual_engagement:>10.1f}/100
Mejora vs baseline:             {metrics.engagement_improvement:>10.1f}%

🎯 DECISIONES PERSONALES
{'─' * 78}
Decisiones optimizadas:         {metrics.decisions_optimized:>10,}

╔══════════════════════════════════════════════════════════════════════════════╗
║  💎 ROI TOTAL: ${total_value:,.0f} en {days} días                                    ║
║  📈 ROI mensual proyectado: ${total_value * (30/days):,.0f}                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return report
    
    def get_predictions_df(self) -> pd.DataFrame:
        """Retorna DataFrame con todas las predicciones para análisis"""
        
        if not self.predictions_file.exists():
            return pd.DataFrame()
        
        predictions = []
        with open(self.predictions_file, 'r') as f:
            predictions = [json.loads(line) for line in f]
        
        return pd.DataFrame(predictions)
    
    def export_to_powerbi(self, output_file: str = None, to_sql: bool = True):
        """
        Exporta predicciones a Power BI.

        Preferido: repositorio SQL (to_sql=True) vía PowerBIExportPipeline.
        Fallback: CSV plano para Import manual.
        """
        if output_file is None:
            output_file = self.data_dir / "powerbi_export.csv"

        df = self.get_predictions_df()

        if df.empty:
            print("⚠️  No hay datos para exportar")
            return None

        # CSV legacy (opcional / auditoría)
        df_flat = pd.json_normalize(df.to_dict("records"))
        df_flat.to_csv(output_file, index=False)
        print(f"✅ CSV exportado: {output_file}")

        result = None
        if to_sql:
            try:
                import sys
                from pathlib import Path

                backend = Path(__file__).resolve().parent.parent
                sys.path.insert(0, str(backend / "integrations"))
                from powerbi_exporter import PowerBIExportPipeline

                pipeline = PowerBIExportPipeline()
                result = pipeline.export_batch_file(
                    self.predictions_file, write_mode="append"
                )
                print(f"✅ SQL/Push export: {result}")
            except Exception as e:
                print(f"⚠️  Export SQL/Push falló (CSV disponible): {e}")

        return result


# Función helper para uso fácil
tracker = ImpactTracker()

def log_prediction(category: str, model: str, input_data: Dict, prediction: Dict, confidence: float = 0.0) -> str:
    """Helper function para logging rápido"""
    cat = MetricCategory(category)
    return tracker.log_prediction(cat, model, input_data, prediction, confidence)

def update_outcome(pred_id: str, actual_outcome: Dict, success: bool, notes: str = ""):
    """Helper function para actualizar outcomes"""
    status = PredictionOutcome.SUCCESS if success else PredictionOutcome.FAILURE
    tracker.update_outcome(pred_id, actual_outcome, status, notes)

def show_impact_report(days: int = 30):
    """Helper function para mostrar reporte"""
    print(tracker.generate_impact_report(days))


if __name__ == "__main__":
    # Demo
    print("📊 Sistema de Tracking de Impacto\n")
    
    # Simular algunas predicciones
    pred1 = tracker.log_prediction(
        MetricCategory.REAL_ESTATE,
        "real_estate_opportunity",
        {"precio_m2": 45000, "ubicacion": "Querétaro"},
        {"probabilidad_venta_12m": 0.87, "precio_estimado": 14200000},
        confidence_score=0.87
    )
    
    pred2 = tracker.log_prediction(
        MetricCategory.SOCIAL_MEDIA,
        "social_content_optimizer",
        {"tipo": "Reel", "hora": 9},
        {"engagement_score": 78.5},
        confidence_score=0.82
    )
    
    # Simular outcomes
    tracker.update_outcome(
        pred1,
        {"vendido": True, "dias_venta": 158, "precio_real": 14100000},
        PredictionOutcome.SUCCESS,
        "Vendido en tiempo estimado"
    )
    
    tracker.update_outcome(
        pred2,
        {"engagement_real": 82.3},
        PredictionOutcome.SUCCESS,
        "Superó expectativas"
    )
    
    # Mostrar reporte
    print("\n" + tracker.generate_impact_report(30))
    
    # Exportar para Power BI
    tracker.export_to_powerbi()
