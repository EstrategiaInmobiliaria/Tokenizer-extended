#!/usr/bin/env python3
"""
Demo visual del MVP Lean - Genera gráfico de ejemplo sin necesidad de Streamlit
"""

import matplotlib
matplotlib.use('Agg')  # Backend no-GUI
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from typing import List

@dataclass
class ProcessStep:
    name: str
    step_type: str
    duration_minutes: float
    is_value_added: bool = False
    
    def __post_init__(self):
        self.is_value_added = (self.step_type == "Operación")


def create_demo_visualization():
    """Crea visualización de demostración"""
    
    # Proceso de ejemplo
    steps = [
        ProcessStep("Recepción MP", "Operación", 5.0),
        ProcessStep("Transporte→Almacén", "Transporte", 3.0),
        ProcessStep("Espera Almacén", "Demora", 15.0),
        ProcessStep("Transporte→Prod", "Transporte", 4.0),
        ProcessStep("Setup Máquina", "Operación", 10.0),
        ProcessStep("Corte", "Operación", 20.0),
        ProcessStep("Inspección Visual", "Inspección", 8.0),
        ProcessStep("Ensamblaje", "Operación", 30.0),
        ProcessStep("Transporte→QA", "Transporte", 2.0),
        ProcessStep("Control Calidad", "Inspección", 12.0),
        ProcessStep("Empaque", "Operación", 8.0),
    ]
    
    # Calcular métricas
    lead_time = sum(s.duration_minutes for s in steps)
    value_added = sum(s.duration_minutes for s in steps if s.is_value_added)
    waste = lead_time - value_added
    efficiency = (value_added / lead_time * 100)
    
    # Crear figura con 4 subplots
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('MVP Lean Manufacturing Analyzer - Demo Visual', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    # ========================================================================
    # Panel 1: Timeline del Proceso
    # ========================================================================
    ax1 = plt.subplot(2, 2, 1)
    
    y_pos = 0
    cumulative = 0
    colors = {
        'Operación': '#2ecc71',
        'Transporte': '#e74c3c',
        'Demora': '#e67e22',
        'Inspección': '#f39c12',
        'Almacenamiento': '#95a5a6'
    }
    
    for i, step in enumerate(steps):
        color = colors.get(step.step_type, '#95a5a6')
        ax1.barh(y_pos, step.duration_minutes, left=cumulative, 
                color=color, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Label en el centro de la barra
        center = cumulative + step.duration_minutes / 2
        label = f"{step.name}\n{step.duration_minutes:.0f}m"
        ax1.text(center, y_pos, label, ha='center', va='center',
                fontsize=7, fontweight='bold')
        
        cumulative += step.duration_minutes
    
    ax1.set_ylim(-0.5, 0.5)
    ax1.set_xlim(0, lead_time)
    ax1.set_xlabel('Tiempo (minutos)', fontweight='bold', fontsize=11)
    ax1.set_title('Timeline del Proceso\n🟢 Verde=Valor | 🔴 Rojo=Desperdicio', 
                  fontweight='bold', fontsize=12, pad=10)
    ax1.set_yticks([])
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Leyenda
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, fc=colors['Operación'], label='Operación (Valor)'),
        plt.Rectangle((0, 0), 1, 1, fc=colors['Transporte'], label='Transporte (Desperdicio)'),
        plt.Rectangle((0, 0), 1, 1, fc=colors['Demora'], label='Demora (Desperdicio)'),
        plt.Rectangle((0, 0), 1, 1, fc=colors['Inspección'], label='Inspección (Desperdicio)')
    ]
    ax1.legend(handles=legend_elements, loc='upper right', fontsize=8)
    
    # ========================================================================
    # Panel 2: Métricas Clave
    # ========================================================================
    ax2 = plt.subplot(2, 2, 2)
    ax2.axis('off')
    
    metrics_text = f"""
    📊 MÉTRICAS LEAN
    
    ⏰ Lead Time Total
       {lead_time:.1f} minutos ({lead_time/60:.2f} horas)
    
    ✅ Tiempo de Valor Agregado
       {value_added:.1f} minutos ({value_added/lead_time*100:.1f}%)
    
    🚫 Tiempo de Desperdicio (MUDA)
       {waste:.1f} minutos ({waste/lead_time*100:.1f}%)
    
    📈 Eficiencia del Proceso
       {efficiency:.1f}%
    
    📋 Pasos del Proceso
       Total: {len(steps)}
       Valor Agregado: {sum(1 for s in steps if s.is_value_added)}
       Desperdicio: {sum(1 for s in steps if not s.is_value_added)}
    """
    
    ax2.text(0.1, 0.95, metrics_text, transform=ax2.transAxes,
            fontsize=11, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # ========================================================================
    # Panel 3: Composición del Tiempo (Pie Chart)
    # ========================================================================
    ax3 = plt.subplot(2, 2, 3)
    
    sizes = [value_added, waste]
    colors_pie = ['#2ecc71', '#e74c3c']
    labels_pie = [
        f'Valor Agregado\n{value_added:.0f} min\n({value_added/lead_time*100:.1f}%)',
        f'Desperdicio\n{waste:.0f} min\n({waste/lead_time*100:.1f}%)'
    ]
    
    wedges, texts, autotexts = ax3.pie(
        sizes, labels=labels_pie, colors=colors_pie, 
        autopct='%1.1f%%', startangle=90,
        textprops={'fontsize': 10, 'fontweight': 'bold'}
    )
    
    ax3.set_title('Composición del Tiempo', fontweight='bold', fontsize=12, pad=15)
    
    # ========================================================================
    # Panel 4: Análisis de Cuellos de Botella
    # ========================================================================
    ax4 = plt.subplot(2, 2, 4)
    
    # Identificar top 5 pasos más largos
    sorted_steps = sorted(steps, key=lambda s: s.duration_minutes, reverse=True)[:5]
    
    names = [s.name for s in sorted_steps]
    durations = [s.duration_minutes for s in sorted_steps]
    colors_bar = [colors.get(s.step_type, '#95a5a6') for s in sorted_steps]
    
    bars = ax4.barh(names, durations, color=colors_bar, alpha=0.8, edgecolor='black')
    
    # Agregar valores en las barras
    for i, (bar, duration) in enumerate(zip(bars, durations)):
        ax4.text(duration + 1, i, f'{duration:.0f} min', 
                va='center', fontsize=9, fontweight='bold')
    
    ax4.set_xlabel('Tiempo (minutos)', fontweight='bold', fontsize=11)
    ax4.set_title('Top 5 Pasos más Largos\n(Potenciales Cuellos de Botella)', 
                  fontweight='bold', fontsize=12, pad=10)
    ax4.grid(axis='x', alpha=0.3, linestyle='--')
    ax4.set_xlim(0, max(durations) * 1.15)
    
    # ========================================================================
    # Información adicional
    # ========================================================================
    fig.text(0.5, 0.01, 
             'MVP Lean Manufacturing Analyzer | Complejidad O(n) | '
             'Lead Time: Métrica operativa real (minutos/horas en planta)',
             ha='center', fontsize=9, style='italic', color='gray')
    
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    
    # Guardar
    output_path = '/workspace/lean_mvp_demo_visual.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ Demo visual guardado en: {output_path}")
    
    return output_path


if __name__ == "__main__":
    print("=" * 80)
    print("GENERANDO VISUALIZACIÓN DE DEMO DEL MVP LEAN")
    print("=" * 80)
    
    output_file = create_demo_visualization()
    
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETADO")
    print("=" * 80)
    print(f"\nAbre el archivo: {output_file}")
    print("\nPara usar la app completa:")
    print("  streamlit run lean_streamlit_mvp.py")
