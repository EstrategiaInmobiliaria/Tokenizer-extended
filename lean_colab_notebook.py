"""
MVP de Análisis Lean Manufacturing - Versión Google Colab
═══════════════════════════════════════════════════════════════════════════

Este archivo está diseñado para ejecutarse en Google Colab.
Usa pyngrok para exponer Streamlit a través de un túnel público.

**Instrucciones de Uso:**

1. Abre Google Colab: https://colab.research.google.com/
2. Crea un nuevo notebook
3. Copia y pega este código completo en UNA celda
4. Ejecuta la celda (Shift + Enter)
5. Espera ~30 segundos
6. Copia el link público que aparece (https://xxxx.ngrok.io)
7. Abre el link en tu navegador

**Tiempo total: 2 minutos desde cero hasta app funcionando**
"""

# ═══════════════════════════════════════════════════════════════════════════
# PASO 1: Instalar dependencias (automático)
# ═══════════════════════════════════════════════════════════════════════════

print("📦 Instalando dependencias...")
print("=" * 80)

get_ipython().system('pip install -q streamlit pandas numpy networkx matplotlib pyngrok')

print("✅ Dependencias instaladas\n")

# ═══════════════════════════════════════════════════════════════════════════
# PASO 2: Guardar app de Streamlit en archivo temporal
# ═══════════════════════════════════════════════════════════════════════════

print("📝 Creando aplicación Streamlit...")

streamlit_code = '''
import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from dataclasses import dataclass

st.set_page_config(
    page_title="Lean Manufacturing Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
                "⚠️ EFICIENCIA CRÍTICA (<40%): Revisar todos los pasos no-operativos. "
                "Aplicar 5 Porqués para identificar causas raíz."
            )
        elif self.metrics["efficiency_percentage"] < 60:
            recommendations.append(
                "⚡ EFICIENCIA MEJORABLE (40-60%): Priorizar eliminación de demoras "
                "y reducción de transportes."
            )
        
        type_durations = {}
        for step in self.steps:
            if not step.is_value_added:
                type_durations[step.step_type] = type_durations.get(step.step_type, 0) + step.duration_minutes
        
        for step_type, total_time in sorted(type_durations.items(), key=lambda x: x[1], reverse=True):
            if step_type == "Demora" and total_time > 10:
                recommendations.append(
                    f"🔴 DEMORAS: {total_time:.1f} min detectados. "
                    "Acciones: (1) Paralelizar tareas, (2) Eliminar esperas innecesarias, "
                    "(3) Implementar flujo continuo."
                )
            elif step_type == "Transporte" and total_time > 5:
                recommendations.append(
                    f"🚚 TRANSPORTE: {total_time:.1f} min detectados. "
                    "Acciones: (1) Acercar estaciones de trabajo, (2) Rediseñar layout, "
                    "(3) Implementar células de manufactura."
                )
            elif step_type == "Inspección" and total_time > 8:
                recommendations.append(
                    f"🔍 INSPECCIÓN: {total_time:.1f} min detectados. "
                    "Acciones: (1) Poka-Yoke (a prueba de errores), (2) Inspección en línea, "
                    "(3) Control estadístico de procesos."
                )
            elif step_type == "Almacenamiento" and total_time > 60:
                recommendations.append(
                    f"📦 ALMACENAMIENTO: {total_time:.1f} min detectados. "
                    "Acciones: (1) Sistema Pull (Kanban), (2) Reducir lotes, "
                    "(3) Just-In-Time (JIT)."
                )
        
        if self.metrics["lead_time_minutes"] > 480:
            recommendations.append(
                f"⏰ LEAD TIME ALTO ({self.metrics['lead_time_minutes']/60:.1f} horas): "
                "Considerar mapeo de flujo de valor (VSM) completo."
            )
        
        if not recommendations:
            recommendations.append("✅ Proceso en buen estado. Continuar monitoreando métricas.")
        
        return recommendations
    
    def build_process_graph(self) -> nx.DiGraph:
        G = nx.DiGraph()
        
        for i, step in enumerate(self.steps):
            color = "#2ecc71" if step.is_value_added else "#e74c3c"
            
            G.add_node(
                i,
                label=f"{step.name}\\n{step.duration_minutes} min",
                color=color,
                step_type=step.step_type
            )
            
            if i > 0:
                G.add_edge(i - 1, i)
        
        return G


def plot_process_graph(G: nx.DiGraph, analyzer: LeanAnalyzer):
    fig, ax = plt.subplots(figsize=(14, 8))
    
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    node_colors = [G.nodes[node].get("color", "#95a5a6") for node in G.nodes()]
    
    nx.draw_networkx_nodes(
        G, pos, node_color=node_colors, node_size=2000, 
        alpha=0.9, ax=ax
    )
    
    nx.draw_networkx_edges(
        G, pos, edge_color="#34495e", arrows=True, 
        arrowsize=20, width=2, alpha=0.6, ax=ax
    )
    
    labels = {node: G.nodes[node].get("label", str(node)) for node in G.nodes()}
    nx.draw_networkx_labels(
        G, pos, labels, font_size=8, font_weight="bold", ax=ax
    )
    
    bottlenecks = analyzer.get_bottlenecks()
    bottleneck_indices = [
        i for i, step in enumerate(analyzer.steps)
        if any(step == b[0] for b in bottlenecks)
    ]
    
    if bottleneck_indices:
        nx.draw_networkx_nodes(
            G, pos, nodelist=bottleneck_indices, 
            node_color="#e74c3c", node_size=2500, 
            alpha=0.5, ax=ax
        )
    
    ax.set_title(
        "Flujo de Proceso\\n🟢 Verde = Valor Agregado | 🔴 Rojo = Desperdicio (MUDA)",
        fontsize=14, fontweight="bold", pad=20
    )
    ax.axis("off")
    
    plt.tight_layout()
    return fig


def plot_metrics_dashboard(metrics: Dict[str, float]):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("Dashboard de Métricas Lean", fontsize=16, fontweight="bold")
    
    ax1 = axes[0, 0]
    ax1.barh(["Lead Time"], [metrics["lead_time_minutes"]], color="#3498db")
    ax1.set_xlabel("Minutos", fontweight="bold")
    ax1.set_title(f"Lead Time Total\\n{metrics['lead_time_minutes']:.1f} min", fontweight="bold")
    ax1.grid(axis="x", alpha=0.3)
    
    ax2 = axes[0, 1]
    sizes = [metrics["value_added_time"], metrics["non_value_added_time"]]
    colors = ["#2ecc71", "#e74c3c"]
    labels = [
        f"Valor Agregado\\n{metrics['value_added_time']:.1f} min",
        f"Desperdicio\\n{metrics['non_value_added_time']:.1f} min"
    ]
    ax2.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
    ax2.set_title("Composición del Tiempo", fontweight="bold")
    
    ax3 = axes[1, 0]
    efficiency = metrics["efficiency_percentage"]
    color = "#2ecc71" if efficiency >= 60 else "#e67e22" if efficiency >= 40 else "#e74c3c"
    ax3.barh(["Eficiencia"], [efficiency], color=color)
    ax3.set_xlim(0, 100)
    ax3.set_xlabel("Porcentaje", fontweight="bold")
    ax3.set_title(f"Eficiencia del Proceso\\n{efficiency:.1f}%", fontweight="bold")
    ax3.grid(axis="x", alpha=0.3)
    
    ax4 = axes[1, 1]
    step_counts = [metrics["value_added_steps"], metrics["total_steps"] - metrics["value_added_steps"]]
    colors = ["#2ecc71", "#e74c3c"]
    labels = ["Valor Agregado", "Desperdicio"]
    ax4.bar(labels, step_counts, color=colors)
    ax4.set_ylabel("Cantidad de Pasos", fontweight="bold")
    ax4.set_title("Distribución de Pasos", fontweight="bold")
    ax4.grid(axis="y", alpha=0.3)
    
    plt.tight_layout()
    return fig


def main():
    st.title("📊 Lean Manufacturing Analyzer MVP")
    st.markdown("""
    **Prototipo para análisis de procesos y detección de desperdicios (MUDA)**
    
    🚀 **Ejecutándose en Google Colab vía ngrok**
    
    ---
    
    ### 📖 Conceptos Clave
    
    **Lead Time (Tiempo de Ciclo)**
    - Tiempo real que tarda algo de inicio a fin en tu proceso
    - Ejemplo: orden → materia prima → producción → entrega = 12 días
    - **Es una métrica operativa** que ves en planta
    
    **Complejidad Computacional (NO es lo mismo)**
    - Concepto de ciencias de la computación
    - Mide cómo crece el tiempo de cálculo cuando aumenta el tamaño del problema
    - Este MVP tiene complejidad O(n) en análisis → escala bien hasta 100k registros
    
    ---
    """)
    
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        st.markdown("### 📌 Umbrales de Alerta (minutos)")
        threshold_demora = st.number_input(
            "Demora", value=10.0, min_value=0.0, step=1.0
        )
        threshold_transporte = st.number_input(
            "Transporte", value=3.0, min_value=0.0, step=0.5
        )
        threshold_inspeccion = st.number_input(
            "Inspección", value=5.0, min_value=0.0, step=1.0
        )
        threshold_almacenamiento = st.number_input(
            "Almacenamiento", value=60.0, min_value=0.0, step=5.0
        )
        
        LeanAnalyzer.THRESHOLDS = {
            "Demora": threshold_demora,
            "Transporte": threshold_transporte,
            "Inspección": threshold_inspeccion,
            "Almacenamiento": threshold_almacenamiento
        }
        
        st.markdown("---")
        st.markdown("### 🎯 Información")
        st.info("""
        **Tipos de Paso:**
        - 🟢 **Operación**: Valor agregado
        - 🔴 **Inspección**: No agrega valor
        - 🔴 **Transporte**: Desperdicio
        - 🔴 **Demora**: Desperdicio
        - 🔴 **Almacenamiento**: Desperdicio
        """)
    
    st.header("1️⃣ Editor de Procesos")
    st.markdown("Edita la tabla directamente en el navegador (como Excel):")
    
    if "process_data" not in st.session_state:
        st.session_state.process_data = pd.DataFrame({
            "Paso": [
                "Recepción Materia Prima",
                "Transporte a Almacén",
                "Espera en Almacén",
                "Transporte a Producción",
                "Setup Máquina",
                "Corte",
                "Inspección Visual",
                "Ensamblaje",
                "Transporte a Calidad",
                "Control de Calidad",
                "Empaque"
            ],
            "Tipo": [
                "Operación", "Transporte", "Demora", "Transporte", "Operación",
                "Operación", "Inspección", "Operación", "Transporte", 
                "Inspección", "Operación"
            ],
            "Tiempo (min)": [5.0, 3.0, 15.0, 4.0, 10.0, 20.0, 8.0, 30.0, 2.0, 12.0, 8.0],
            "Recurso": [
                "Operador 1", "Montacargas", "Almacén", "Montacargas", "Operador 2",
                "CNC", "Inspector", "Operador 3", "Montacargas", "Inspector", "Operador 4"
            ]
        })
    
    edited_df = st.data_editor(
        st.session_state.process_data,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Tipo": st.column_config.SelectboxColumn(
                "Tipo",
                options=LeanAnalyzer.STEP_TYPES,
                required=True
            ),
            "Tiempo (min)": st.column_config.NumberColumn(
                "Tiempo (min)",
                min_value=0.0,
                step=0.5,
                format="%.1f"
            )
        }
    )
    
    st.session_state.process_data = edited_df
    
    st.header("2️⃣ Análisis Automático")
    
    if st.button("🚀 Analizar Proceso", type="primary"):
        if edited_df.empty or len(edited_df) == 0:
            st.error("❌ Agrega al menos un paso al proceso")
        else:
            with st.spinner("Analizando proceso..."):
                steps = []
                for _, row in edited_df.iterrows():
                    step = ProcessStep(
                        name=row["Paso"],
                        step_type=row["Tipo"],
                        duration_minutes=row["Tiempo (min)"],
                        resource=row["Recurso"]
                    )
                    steps.append(step)
                
                analyzer = LeanAnalyzer(steps)
                
                st.subheader("📊 Métricas Clave")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="⏰ Lead Time Total",
                        value=f"{analyzer.metrics['lead_time_minutes']:.1f} min",
                        delta=f"{analyzer.metrics['lead_time_minutes']/60:.2f} horas"
                    )
                
                with col2:
                    st.metric(
                        label="✅ Tiempo de Valor Agregado",
                        value=f"{analyzer.metrics['value_added_time']:.1f} min",
                        delta=f"{analyzer.metrics['efficiency_percentage']:.1f}% eficiencia"
                    )
                
                with col3:
                    st.metric(
                        label="🚫 Tiempo de Desperdicio (MUDA)",
                        value=f"{analyzer.metrics['non_value_added_time']:.1f} min",
                        delta=f"{100 - analyzer.metrics['efficiency_percentage']:.1f}% del total",
                        delta_color="inverse"
                    )
                
                st.subheader("📈 Dashboard Visual")
                fig_dashboard = plot_metrics_dashboard(analyzer.metrics)
                st.pyplot(fig_dashboard)
                
                st.subheader("🔴 Cuellos de Botella Detectados")
                bottlenecks = analyzer.get_bottlenecks()
                
                if bottlenecks:
                    for step, reason in bottlenecks:
                        st.warning(f"**{step.name}** ({step.step_type}): {reason}")
                else:
                    st.success("✅ No se detectaron cuellos de botella críticos")
                
                st.subheader("🗺️ Mapa de Flujo del Proceso")
                G = analyzer.build_process_graph()
                fig_graph = plot_process_graph(G, analyzer)
                st.pyplot(fig_graph)
                
                st.subheader("💡 Recomendaciones de Mejora")
                recommendations = analyzer.get_recommendations()
                
                for i, rec in enumerate(recommendations, 1):
                    st.info(f"**{i}.** {rec}")
                
                st.subheader("📋 Detalle por Paso")
                
                detail_df = pd.DataFrame([
                    {
                        "Paso": s.name,
                        "Tipo": s.step_type,
                        "Tiempo (min)": s.duration_minutes,
                        "Valor Agregado": "✅ Sí" if s.is_value_added else "🚫 No",
                        "Recurso": s.resource
                    }
                    for s in steps
                ])
                
                st.dataframe(detail_df, use_container_width=True)
    
    st.markdown("---")
    st.markdown("""
    ### 📚 Referencias
    
    **Lean Manufacturing:**
    - **Lead Time**: Tiempo total de proceso (métrica operativa)
    - **MUDA**: Desperdicio (todo lo que no agrega valor al cliente)
    - **VSM**: Value Stream Mapping (mapeo de flujo de valor)
    
    **Complejidad Computacional (diferente de Lead Time):**
    - **O(n)**: Lineal → Este MVP analiza en tiempo lineal
    - **O(n²)**: Cuadrático → NetworkX grafo (solo para <1000 nodos)
    - **O(2ⁿ)**: Exponencial → Inviable para n>30
    
    ---
    
    🚀 **MVP creado para análisis rápido sin código pesado**
    """)


if __name__ == "__main__":
    main()
'''

# Guardar en archivo
with open('/content/lean_app.py', 'w', encoding='utf-8') as f:
    f.write(streamlit_code)

print("✅ Aplicación creada en /content/lean_app.py\n")

# ═══════════════════════════════════════════════════════════════════════════
# PASO 3: Configurar ngrok
# ═══════════════════════════════════════════════════════════════════════════

print("🌐 Configurando túnel ngrok...")

from pyngrok import ngrok

# Terminar túneles previos si existen
ngrok.kill()

# Crear túnel en puerto 8501 (puerto por defecto de Streamlit)
public_url = ngrok.connect(addr="8501", proto="http")

print("=" * 80)
print("✅ TÚNEL CREADO EXITOSAMENTE")
print("=" * 80)
print(f"\n🚀 ABRE ESTA URL EN TU NAVEGADOR:\n\n   {public_url}\n")
print("=" * 80)
print("\n⚠️  IMPORTANTE: NO CIERRES ESTE NOTEBOOK")
print("La app dejará de funcionar si cierras esta celda.\n")

# ═══════════════════════════════════════════════════════════════════════════
# PASO 4: Lanzar Streamlit
# ═══════════════════════════════════════════════════════════════════════════

print("🚀 Iniciando Streamlit...\n")
print("Esto puede tomar 10-15 segundos...")
print("=" * 80)

get_ipython().system('streamlit run /content/lean_app.py --server.port 8501 --server.headless true')
