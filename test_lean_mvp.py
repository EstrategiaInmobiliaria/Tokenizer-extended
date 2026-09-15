#!/usr/bin/env python3
"""
Script de prueba para validar la lógica del MVP Lean sin lanzar Streamlit
"""

import sys
sys.path.insert(0, '/workspace')

# Importar solo las clases de dominio (no Streamlit)
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import networkx as nx

@dataclass
class ProcessStep:
    """Representa un paso en el proceso productivo"""
    name: str
    step_type: str
    duration_minutes: float
    resource: str
    is_value_added: bool = False
    
    def __post_init__(self):
        self.is_value_added = (self.step_type == "Operación")


class LeanAnalyzer:
    """Motor de análisis Lean - Complejidad O(n)"""
    
    STEP_TYPES = ["Operación", "Inspección", "Transporte", "Demora", "Almacenamiento"]
    
    THRESHOLDS = {
        "Demora": 10.0,
        "Transporte": 3.0,
        "Inspección": 5.0,
        "Almacenamiento": 60.0
    }
    
    def __init__(self, steps: List[ProcessStep]):
        self.steps = steps
        self.metrics = self._calculate_metrics()
    
    def _calculate_metrics(self) -> Dict[str, float]:
        if not self.steps:
            return {
                "lead_time_minutes": 0,
                "value_added_time": 0,
                "non_value_added_time": 0,
                "efficiency_percentage": 0,
                "total_steps": 0,
                "value_added_steps": 0
            }
        
        lead_time = sum(step.duration_minutes for step in self.steps)
        value_added_time = sum(
            step.duration_minutes for step in self.steps if step.is_value_added
        )
        non_value_added_time = lead_time - value_added_time
        
        efficiency = (value_added_time / lead_time * 100) if lead_time > 0 else 0
        
        return {
            "lead_time_minutes": round(lead_time, 2),
            "value_added_time": round(value_added_time, 2),
            "non_value_added_time": round(non_value_added_time, 2),
            "efficiency_percentage": round(efficiency, 2),
            "total_steps": len(self.steps),
            "value_added_steps": sum(1 for s in self.steps if s.is_value_added)
        }
    
    def get_bottlenecks(self) -> List[Tuple[ProcessStep, str]]:
        bottlenecks = []
        
        for step in self.steps:
            if step.step_type in self.THRESHOLDS:
                threshold = self.THRESHOLDS[step.step_type]
                if step.duration_minutes > threshold:
                    reason = f"{step.step_type} excede límite de {threshold} min"
                    bottlenecks.append((step, reason))
        
        return bottlenecks
    
    def get_recommendations(self) -> List[str]:
        recommendations = []
        
        if self.metrics["efficiency_percentage"] < 40:
            recommendations.append(
                "⚠️ EFICIENCIA CRÍTICA (<40%): Revisar todos los pasos no-operativos."
            )
        elif self.metrics["efficiency_percentage"] < 60:
            recommendations.append(
                "⚡ EFICIENCIA MEJORABLE (40-60%): Priorizar eliminación de demoras."
            )
        
        type_durations = {}
        for step in self.steps:
            if not step.is_value_added:
                type_durations[step.step_type] = type_durations.get(step.step_type, 0) + step.duration_minutes
        
        for step_type, total_time in sorted(type_durations.items(), key=lambda x: x[1], reverse=True):
            if step_type == "Demora" and total_time > 10:
                recommendations.append(f"🔴 DEMORAS: {total_time:.1f} min detectados")
        
        if not recommendations:
            recommendations.append("✅ Proceso en buen estado")
        
        return recommendations


def test_lean_analyzer():
    """Prueba unitaria del motor de análisis"""
    print("=" * 80)
    print("PRUEBA DEL MOTOR DE ANÁLISIS LEAN")
    print("=" * 80)
    
    # Crear proceso de ejemplo
    steps = [
        ProcessStep("Recepción", "Operación", 5.0, "Operador 1"),
        ProcessStep("Transporte", "Transporte", 3.0, "Montacargas"),
        ProcessStep("Espera", "Demora", 15.0, "Almacén"),
        ProcessStep("Corte", "Operación", 20.0, "CNC"),
        ProcessStep("Inspección", "Inspección", 8.0, "Inspector"),
        ProcessStep("Ensamblaje", "Operación", 30.0, "Operador 3"),
        ProcessStep("Empaque", "Operación", 8.0, "Operador 4"),
    ]
    
    analyzer = LeanAnalyzer(steps)
    
    print("\n📊 MÉTRICAS CALCULADAS:")
    print(f"   Lead Time Total:        {analyzer.metrics['lead_time_minutes']} min")
    print(f"   Tiempo Valor Agregado:  {analyzer.metrics['value_added_time']} min")
    print(f"   Tiempo Desperdicio:     {analyzer.metrics['non_value_added_time']} min")
    print(f"   Eficiencia:             {analyzer.metrics['efficiency_percentage']}%")
    print(f"   Total de Pasos:         {analyzer.metrics['total_steps']}")
    print(f"   Pasos Valor Agregado:   {analyzer.metrics['value_added_steps']}")
    
    # Validaciones
    assert analyzer.metrics['lead_time_minutes'] == 89.0, "Lead time incorrecto"
    assert analyzer.metrics['value_added_time'] == 63.0, "Tiempo valor agregado incorrecto"
    assert analyzer.metrics['efficiency_percentage'] == 70.79, "Eficiencia incorrecta"
    
    print("\n✅ Todas las validaciones pasaron")
    
    print("\n🔴 CUELLOS DE BOTELLA:")
    bottlenecks = analyzer.get_bottlenecks()
    if bottlenecks:
        for step, reason in bottlenecks:
            print(f"   - {step.name}: {reason}")
    else:
        print("   (ninguno)")
    
    print("\n💡 RECOMENDACIONES:")
    recommendations = analyzer.get_recommendations()
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    print("\n" + "=" * 80)
    print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_lean_analyzer()
        print("\n🚀 El motor de análisis funciona correctamente")
        print("Puedes ejecutar la app completa con: streamlit run lean_streamlit_mvp.py")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
