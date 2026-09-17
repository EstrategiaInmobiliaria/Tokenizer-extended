"""
Ejemplos Avanzados - Análisis Financiero e Ingeniería Económica
Casos de uso profesionales con cálculos reales
"""

import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# EJEMPLO 1: Análisis de Break-even (Punto de Equilibrio)
# =============================================================================
def break_even_analysis():
    unidades = np.arange(0, 1001, 50)
    costos_fijos = 50000
    costo_variable_unitario = 25
    precio_venta = 75
    
    costo_total = costos_fijos + costo_variable_unitario * unidades
    ingreso_total = precio_venta * unidades
    utilidad = ingreso_total - costo_total
    
    # Calcular punto de equilibrio exacto
    break_even = costos_fijos / (precio_venta - costo_variable_unitario)
    
    plt.figure(figsize=(11, 6))
    
    # Gráficos principales
    plt.plot(unidades, costo_total, label='Costo Total', linewidth=2.5, color='#d62728')
    plt.plot(unidades, ingreso_total, label='Ingreso Total', linewidth=2.5, color='#2ca02c')
    
    # Líneas de referencia
    plt.axhline(costos_fijos, linestyle='--', alpha=0.5, color='gray', label='Costos Fijos')
    plt.axvline(break_even, color='#ff7f0e', linestyle=':', linewidth=2.5, 
                label=f'Break-even: {break_even:.0f} unidades')
    
    # Zonas de pérdida y ganancia
    plt.fill_between(unidades, costo_total, ingreso_total, 
                     where=(ingreso_total >= costo_total), 
                     alpha=0.2, color='green', label='Zona de Ganancia')
    plt.fill_between(unidades, costo_total, ingreso_total, 
                     where=(ingreso_total < costo_total), 
                     alpha=0.2, color='red', label='Zona de Pérdida')
    
    plt.title('Análisis de Punto de Equilibrio (Break-even)', fontsize=13, fontweight='bold')
    plt.xlabel('Unidades Producidas/Vendidas', fontsize=11, fontweight='bold')
    plt.ylabel('$ (USD)', fontsize=11, fontweight='bold')
    plt.legend(loc='upper left', framealpha=0.95)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig('break_even_analysis.png', dpi=150, bbox_inches='tight')
    print(f"✓ Break-even Analysis: {break_even:.0f} unidades | ${break_even * precio_venta:,.0f} en ventas")


# =============================================================================
# EJEMPLO 2: Diagrama de Pareto (Análisis 80/20)
# =============================================================================
def pareto_chart():
    categorias = ['Defecto A', 'Defecto B', 'Defecto C', 'Defecto D', 
                  'Defecto E', 'Defecto F', 'Otros']
    frecuencias = np.array([145, 89, 67, 45, 23, 18, 13])
    
    # Ordenar de mayor a menor
    indices = np.argsort(frecuencias)[::-1]
    categorias_ord = [categorias[i] for i in indices]
    frecuencias_ord = frecuencias[indices]
    
    # Calcular porcentaje acumulado
    porcentaje_acum = np.cumsum(frecuencias_ord) / np.sum(frecuencias_ord) * 100
    
    fig, ax1 = plt.subplots(figsize=(11, 6))
    
    # Barras de frecuencia
    bars = ax1.bar(range(len(categorias_ord)), frecuencias_ord, 
                   color='#1f77b4', alpha=0.7, edgecolor='black', linewidth=0.5)
    ax1.set_xlabel('Causas de Defectos', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Frecuencia (Número de Casos)', fontsize=11, fontweight='bold', color='#1f77b4')
    ax1.tick_params(axis='y', labelcolor='#1f77b4')
    ax1.set_xticks(range(len(categorias_ord)))
    ax1.set_xticklabels(categorias_ord, rotation=30, ha='right')
    
    # Eje secundario para porcentaje acumulado
    ax2 = ax1.twinx()
    line = ax2.plot(range(len(categorias_ord)), porcentaje_acum, 
                    color='#d62728', marker='o', linewidth=2.5, markersize=8, 
                    label='% Acumulado')
    ax2.set_ylabel('Porcentaje Acumulado (%)', fontsize=11, fontweight='bold', color='#d62728')
    ax2.tick_params(axis='y', labelcolor='#d62728')
    ax2.axhline(80, color='green', linestyle='--', linewidth=2, alpha=0.7, label='80% (Pareto)')
    
    # Agregar valores en las barras
    for i, (bar, freq) in enumerate(zip(bars, frecuencias_ord)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{freq}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.title('Diagrama de Pareto - Análisis de Causas Principales', fontsize=13, fontweight='bold')
    ax1.grid(True, axis='y', linestyle=':', alpha=0.5)
    
    # Leyenda combinada
    lines, labels = ax2.get_legend_handles_labels()
    ax2.legend(lines, labels, loc='upper right', framealpha=0.95)
    
    plt.tight_layout()
    plt.savefig('pareto_chart.png', dpi=150, bbox_inches='tight')
    print(f"✓ Pareto Chart: {np.where(porcentaje_acum >= 80)[0][0] + 1} causas representan el 80%")


# =============================================================================
# EJEMPLO 3: Flujo de Caja Descontado (DCF - Discounted Cash Flow)
# =============================================================================
def dcf_analysis():
    anios = np.arange(0, 11)
    flujos_libres = np.array([-500, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260])
    tasa_descuento = 0.12
    
    # Calcular valor presente de cada flujo
    factores_descuento = 1 / (1 + tasa_descuento) ** anios
    flujos_descontados = flujos_libres * factores_descuento
    vpn = np.sum(flujos_descontados)
    flujos_acumulados = np.cumsum(flujos_descontados)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Gráfico 1: Flujos por año
    colors = ['#d62728' if f < 0 else '#2ca02c' for f in flujos_descontados]
    bars = ax1.bar(anios, flujos_descontados, color=colors, alpha=0.7, edgecolor='black', linewidth=0.8)
    ax1.axhline(0, color='black', linewidth=1)
    ax1.set_title('Flujo de Caja Descontado por Año', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Año', fontsize=10, fontweight='bold')
    ax1.set_ylabel('Flujo Descontado (Miles USD)', fontsize=10, fontweight='bold')
    ax1.grid(True, axis='y', linestyle=':', alpha=0.5)
    
    # Agregar valores en barras
    for bar, valor in zip(bars, flujos_descontados):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'${valor:.1f}', ha='center', va='bottom' if valor > 0 else 'top', 
                fontsize=8, fontweight='bold')
    
    # Gráfico 2: Flujo acumulado
    ax2.plot(anios, flujos_acumulados, marker='o', linestyle='-', 
             linewidth=2.5, markersize=8, color='#1f77b4', label='VPN Acumulado')
    ax2.axhline(0, color='#d62728', linestyle='--', linewidth=1.5, label='Break-even')
    ax2.fill_between(anios, flujos_acumulados, 0, where=(flujos_acumulados >= 0), 
                     alpha=0.2, color='green')
    ax2.fill_between(anios, flujos_acumulados, 0, where=(flujos_acumulados < 0), 
                     alpha=0.2, color='red')
    
    ax2.set_title(f'VPN Acumulado (Tasa: {tasa_descuento*100:.0f}%) | VPN Total: ${vpn:.2f}K', 
                  fontsize=12, fontweight='bold')
    ax2.set_xlabel('Año', fontsize=10, fontweight='bold')
    ax2.set_ylabel('VPN Acumulado (Miles USD)', fontsize=10, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.legend(loc='upper left')
    
    plt.tight_layout()
    plt.savefig('dcf_analysis.png', dpi=150, bbox_inches='tight')
    print(f"✓ DCF Analysis: VPN = ${vpn:.2f}K | TIR implícita > {tasa_descuento*100:.0f}%")


# =============================================================================
# EJEMPLO 4: Análisis de Sensibilidad Multivariable
# =============================================================================
def sensitivity_analysis():
    precios = np.linspace(50, 150, 50)
    costos_base = [80, 100, 120]
    
    plt.figure(figsize=(11, 6))
    
    for costo in costos_base:
        margen = ((precios - costo) / precios) * 100
        plt.plot(precios, margen, linewidth=2.5, marker='o', markersize=5, 
                label=f'Costo: ${costo}', markevery=5)
    
    plt.axhline(0, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Margen Neutro')
    plt.axhline(20, color='green', linestyle=':', linewidth=1.5, alpha=0.7, label='Objetivo 20%')
    
    plt.title('Análisis de Sensibilidad: Margen vs Precio de Venta', fontsize=13, fontweight='bold')
    plt.xlabel('Precio de Venta ($)', fontsize=11, fontweight='bold')
    plt.ylabel('Margen de Ganancia (%)', fontsize=11, fontweight='bold')
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.legend(loc='lower right', framealpha=0.95)
    plt.tight_layout()
    plt.savefig('sensitivity_analysis.png', dpi=150, bbox_inches='tight')
    print("✓ Sensitivity Analysis: 3 escenarios de costos evaluados")


# =============================================================================
# EJEMPLO 5: Dashboard Ejecutivo (4 métricas clave)
# =============================================================================
def executive_dashboard():
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # Métrica 1: Ingresos mensuales
    ax1 = fig.add_subplot(gs[0, 0])
    meses = np.arange(1, 13)
    ingresos = 100 + 8 * meses + np.random.normal(0, 5, 12)
    ax1.bar(meses, ingresos, color='#2ca02c', alpha=0.7, edgecolor='black', linewidth=0.5)
    ax1.set_title('Ingresos Mensuales (Miles USD)', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Mes', fontsize=9)
    ax1.set_ylabel('Ingresos', fontsize=9)
    ax1.grid(True, axis='y', linestyle=':', alpha=0.5)
    
    # Métrica 2: Composición de costos
    ax2 = fig.add_subplot(gs[0, 1])
    categorias_costo = ['Personal', 'Materiales', 'Operación', 'Marketing', 'Otros']
    valores_costo = [35, 28, 18, 12, 7]
    colors_pie = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    wedges, texts, autotexts = ax2.pie(valores_costo, labels=categorias_costo, autopct='%1.1f%%',
                                        colors=colors_pie, startangle=90, textprops={'fontsize': 9})
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    ax2.set_title('Distribución de Costos', fontsize=11, fontweight='bold')
    
    # Métrica 3: ROI por proyecto
    ax3 = fig.add_subplot(gs[1, 0])
    proyectos = ['Proyecto A', 'Proyecto B', 'Proyecto C', 'Proyecto D']
    roi_valores = [18.5, 24.3, 12.7, 31.2]
    colors_roi = ['#2ca02c' if r > 20 else '#ff7f0e' for r in roi_valores]
    bars = ax3.barh(proyectos, roi_valores, color=colors_roi, alpha=0.7, edgecolor='black', linewidth=0.5)
    ax3.axvline(20, color='red', linestyle='--', linewidth=1.5, label='Objetivo 20%')
    ax3.set_title('ROI por Proyecto (%)', fontsize=11, fontweight='bold')
    ax3.set_xlabel('ROI (%)', fontsize=9)
    ax3.legend(loc='lower right', fontsize=8)
    ax3.grid(True, axis='x', linestyle=':', alpha=0.5)
    
    # Métrica 4: Tendencia trimestral
    ax4 = fig.add_subplot(gs[1, 1])
    trimestres = ['Q1', 'Q2', 'Q3', 'Q4']
    ventas = [280, 320, 350, 410]
    utilidad = [45, 58, 67, 85]
    x_pos = np.arange(len(trimestres))
    width = 0.35
    ax4.bar(x_pos - width/2, ventas, width, label='Ventas', color='#1f77b4', alpha=0.7)
    ax4.bar(x_pos + width/2, utilidad, width, label='Utilidad', color='#2ca02c', alpha=0.7)
    ax4.set_title('Desempeño Trimestral (Miles USD)', fontsize=11, fontweight='bold')
    ax4.set_xlabel('Trimestre', fontsize=9)
    ax4.set_ylabel('Valor (K USD)', fontsize=9)
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(trimestres)
    ax4.legend(loc='upper left', fontsize=8)
    ax4.grid(True, axis='y', linestyle=':', alpha=0.5)
    
    fig.suptitle('Dashboard Ejecutivo - Métricas Clave de Desempeño', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    plt.savefig('executive_dashboard.png', dpi=150, bbox_inches='tight')
    print("✓ Executive Dashboard: 4 métricas clave integradas")


# =============================================================================
# EJECUTAR TODOS LOS EJEMPLOS AVANZADOS
# =============================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("GENERANDO ANÁLISIS AVANZADOS")
    print("="*70 + "\n")
    
    break_even_analysis()
    pareto_chart()
    dcf_analysis()
    sensitivity_analysis()
    executive_dashboard()
    
    print("\n" + "="*70)
    print("✓ TODOS LOS ANÁLISIS AVANZADOS COMPLETADOS")
    print("="*70 + "\n")
    print("Archivos generados:")
    print("  1. break_even_analysis.png - Punto de equilibrio con zonas")
    print("  2. pareto_chart.png - Diagrama de Pareto 80/20")
    print("  3. dcf_analysis.png - Flujo de caja descontado (DCF)")
    print("  4. sensitivity_analysis.png - Análisis de sensibilidad")
    print("  5. executive_dashboard.png - Dashboard ejecutivo integrado")
    print()
