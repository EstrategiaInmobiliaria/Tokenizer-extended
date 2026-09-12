"""
Sistema de Alertas Inteligentes
Monitorea predicciones y métricas para enviar notificaciones proactivas
"""

from typing import List, Dict, Callable
from enum import Enum
from dataclasses import dataclass
import json
from pathlib import Path
from datetime import datetime, timedelta

class AlertType(Enum):
    ACCURACY_DROP = "accuracy_drop"
    HIGH_OPPORTUNITY = "high_opportunity"
    GOAL_ACHIEVED = "goal_achieved"
    MODEL_DRIFT = "model_drift"
    ENGAGEMENT_SPIKE = "engagement_spike"
    ROI_MILESTONE = "roi_milestone"

class AlertPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Alert:
    type: AlertType
    priority: AlertPriority
    title: str
    message: str
    data: Dict
    timestamp: datetime
    
    def to_whatsapp_message(self) -> str:
        """Formatea alerta para WhatsApp"""
        emoji_map = {
            AlertType.ACCURACY_DROP: "⚠️",
            AlertType.HIGH_OPPORTUNITY: "🎯",
            AlertType.GOAL_ACHIEVED: "🎉",
            AlertType.MODEL_DRIFT: "📊",
            AlertType.ENGAGEMENT_SPIKE: "🚀",
            AlertType.ROI_MILESTONE: "💰"
        }
        
        emoji = emoji_map.get(self.type, "📢")
        priority_text = "🔴 CRÍTICO" if self.priority == AlertPriority.CRITICAL else ""
        
        return f"""{emoji} *{self.title}* {priority_text}

{self.message}

📅 {self.timestamp.strftime('%d/%m/%Y %H:%M')}"""


class SmartAlertSystem:
    """Sistema de alertas inteligentes con reglas configurables"""
    
    def __init__(self, alerts_dir: str = "backend/data/alerts"):
        self.alerts_dir = Path(alerts_dir)
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
        self.alerts_file = self.alerts_dir / "alerts.jsonl"
        self.config_file = self.alerts_dir / "alert_config.json"
        
        # Configuración por defecto
        self.config = {
            "accuracy_threshold": 0.75,  # Alertar si accuracy < 75%
            "high_opportunity_threshold": 0.85,  # Alertar si prob > 85%
            "roi_milestones": [10000, 50000, 100000],  # Alertar al alcanzar estos valores
            "engagement_spike_threshold": 1.5,  # Alertar si engagement > 150% del promedio
            "enabled": True,
            "notification_channels": ["log", "whatsapp"]
        }
        
        self.load_config()
    
    def load_config(self):
        """Carga configuración de alertas"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config.update(json.load(f))
    
    def save_config(self):
        """Guarda configuración"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def check_accuracy_drop(self, metrics) -> List[Alert]:
        """Verifica si la accuracy ha caído por debajo del umbral"""
        alerts = []
        
        if metrics.accuracy < self.config["accuracy_threshold"]:
            alert = Alert(
                type=AlertType.ACCURACY_DROP,
                priority=AlertPriority.HIGH,
                title="Precisión del Modelo Baja",
                message=f"La precisión actual es {metrics.accuracy:.1%}, por debajo del umbral de {self.config['accuracy_threshold']:.1%}.\n\nRecomendación: Considera re-entrenar los modelos con datos más recientes.",
                data={
                    "accuracy": metrics.accuracy,
                    "threshold": self.config["accuracy_threshold"],
                    "total_predictions": metrics.total_predictions
                },
                timestamp=datetime.now()
            )
            alerts.append(alert)
        
        return alerts
    
    def check_high_opportunity(self, prediction_data: Dict) -> List[Alert]:
        """Verifica si hay una oportunidad de alta prioridad"""
        alerts = []
        
        if prediction_data.get('probabilidad_venta_12m', 0) >= self.config["high_opportunity_threshold"]:
            alert = Alert(
                type=AlertType.HIGH_OPPORTUNITY,
                priority=AlertPriority.HIGH,
                title="🎯 Oportunidad de Alta Prioridad Detectada",
                message=f"Desarrollo con {prediction_data['probabilidad_venta_12m']:.1%} de probabilidad de venta.\n\nPrecio estimado: ${prediction_data['precio_estimado']:,.0f}\nDías estimados: {prediction_data['dias_estimados']}\n\n¡Acción recomendada ahora!",
                data=prediction_data,
                timestamp=datetime.now()
            )
            alerts.append(alert)
        
        return alerts
    
    def check_roi_milestone(self, total_roi: float, previous_roi: float = 0) -> List[Alert]:
        """Verifica si se alcanzó un milestone de ROI"""
        alerts = []
        
        for milestone in self.config["roi_milestones"]:
            if previous_roi < milestone <= total_roi:
                alert = Alert(
                    type=AlertType.ROI_MILESTONE,
                    priority=AlertPriority.MEDIUM,
                    title=f"🎉 Milestone de ROI Alcanzado: ${milestone:,}",
                    message=f"El sistema ha generado un ROI total de ${total_roi:,.0f}!\n\nMilestone: ${milestone:,}\n\n¡Excelente progreso!",
                    data={
                        "milestone": milestone,
                        "total_roi": total_roi,
                        "previous_roi": previous_roi
                    },
                    timestamp=datetime.now()
                )
                alerts.append(alert)
        
        return alerts
    
    def check_engagement_spike(self, actual_engagement: float, predicted_engagement: float, avg_engagement: float) -> List[Alert]:
        """Verifica si hubo un spike significativo de engagement"""
        alerts = []
        
        if actual_engagement > avg_engagement * self.config["engagement_spike_threshold"]:
            improvement = ((actual_engagement - predicted_engagement) / predicted_engagement) * 100
            
            alert = Alert(
                type=AlertType.ENGAGEMENT_SPIKE,
                priority=AlertPriority.MEDIUM,
                title="🚀 Spike de Engagement Detectado",
                message=f"Post superó expectativas en {improvement:+.1f}%!\n\nEngagement real: {actual_engagement:.1f}\nEngagement predicho: {predicted_engagement:.1f}\n\nAnálisis recomendado para replicar éxito.",
                data={
                    "actual": actual_engagement,
                    "predicted": predicted_engagement,
                    "improvement": improvement
                },
                timestamp=datetime.now()
            )
            alerts.append(alert)
        
        return alerts
    
    def log_alert(self, alert: Alert):
        """Guarda alerta en el log"""
        alert_dict = {
            "type": alert.type.value,
            "priority": alert.priority.value,
            "title": alert.title,
            "message": alert.message,
            "data": alert.data,
            "timestamp": alert.timestamp.isoformat()
        }
        
        with open(self.alerts_file, 'a') as f:
            f.write(json.dumps(alert_dict) + '\n')
    
    def send_alert(self, alert: Alert):
        """Envía alerta a los canales configurados"""
        if not self.config["enabled"]:
            return
        
        # Log
        if "log" in self.config["notification_channels"]:
            self.log_alert(alert)
            print(f"\n{alert.to_whatsapp_message()}\n")
        
        # WhatsApp (requiere integración externa)
        if "whatsapp" in self.config["notification_channels"]:
            # Aquí iría la integración con WhatsApp Business API
            pass
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Obtiene alertas recientes"""
        if not self.alerts_file.exists():
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = []
        
        with open(self.alerts_file, 'r') as f:
            for line in f:
                alert = json.loads(line)
                alert_time = datetime.fromisoformat(alert['timestamp'])
                if alert_time >= cutoff_time:
                    recent_alerts.append(alert)
        
        return sorted(recent_alerts, key=lambda x: x['timestamp'], reverse=True)


# Instancia global
alert_system = SmartAlertSystem()


# Funciones helper
def check_and_alert_prediction(prediction_data: Dict, category: str = "real_estate"):
    """Verifica y envía alertas para una predicción"""
    alerts = []
    
    if category == "real_estate":
        alerts.extend(alert_system.check_high_opportunity(prediction_data))
    
    for alert in alerts:
        alert_system.send_alert(alert)
    
    return alerts


def check_and_alert_metrics(metrics):
    """Verifica y envía alertas para métricas del sistema"""
    alerts = []
    
    alerts.extend(alert_system.check_accuracy_drop(metrics))
    
    for alert in alerts:
        alert_system.send_alert(alert)
    
    return alerts


if __name__ == "__main__":
    # Demo
    print("🔔 Sistema de Alertas Inteligentes\n")
    
    # Simular alerta de alta oportunidad
    pred_data = {
        'probabilidad_venta_12m': 0.92,
        'precio_estimado': 18500000,
        'dias_estimados': 142,
        'ubicacion': 'Querétaro'
    }
    
    alerts = alert_system.check_high_opportunity(pred_data)
    
    if alerts:
        print("Alertas generadas:")
        for alert in alerts:
            alert_system.send_alert(alert)
    
    # Simular alerta de milestone ROI
    alerts = alert_system.check_roi_milestone(52000, 48000)
    
    if alerts:
        for alert in alerts:
            alert_system.send_alert(alert)
    
    # Mostrar alertas recientes
    recent = alert_system.get_recent_alerts(hours=24)
    print(f"\n📋 Alertas recientes (últimas 24h): {len(recent)}")
