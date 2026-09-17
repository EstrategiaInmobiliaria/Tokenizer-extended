"""
Ejemplos de Gráficos para Análisis Financiero e Ingeniería
Colección de plantillas listas para personalizar
"""

import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# EJEMPLO 1: Análisis de Inversión con VPN (Valor Presente Neto)
# =============================================================================
def grafico_vpn():
    tasas_descuento = np.linspace(0.05, 0.25, 50)  # Tasas del 5% al 25%
    vpn = 100 / (1 + tasas_descuento)**5 - 80  # VPN simplificado
    
    plt.figure(figsize=(10, 5))
    plt.plot(tasas_descuento * 100, vpn, linewidth=2.5, color='#2ca02c')
    plt.axhline(0, color='red', linestyle='--', linewidth=1, alpha=0.7)
    plt.fill_between(tasas_descuento * 100, vpn, 0, where=(vpn >= 0), 
                     alpha=0.3, color='green', label='Zona Rentable')
    plt.fill_between(tasas_descuento * 100, vpn, 0, where=(vpn < 0), 
                     alpha=0.3, color='red', label='Zona No Rentable')
    
    plt.title('Sensibilidad del VPN vs Tasa de Descuento', fontsize=13, fontweight='bold')
    plt.xlabel('Tasa de Descuento (%)', fontsize=11, fontweight='bold')
    plt.ylabel('VPN (Millones USD)', fontsize=11, fontweight='bold')
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig('vpn_sensibilidad.png', dpi=150, bbox_inches='tight')
    print("✓ Gráfico VPN generado: vpn_sensibilidad.png")


# =============================================================================
# EJEMPLO 2: Comparación de Alternativas con Barras Agrupadas
# =============================================================================
def grafico_comparacion_proyectos():
    proyectos = ['Proyecto A', 'Proyecto B', 'Proyecto C', 'Proyecto D']
    costo_inicial = [12.5, 18.3, 9.8, 15.2]
    ingreso_anual = [4.2, 6.1, 3.5, 5.8]
    roi = np.array(ingreso_anual) / np.array(costo_inicial) * 100
    
    x = np.arange(len(proyectos))
    width = 0.25
    
    plt.figure(figsize=(11, 6))
    plt.bar(x - width, costo_inicial, width, label='Inversión Inicial (M$)', color='#ff7f0e')
    plt.bar(x, ingreso_anual, width, label='Ingreso Anual (M$)', color='#1f77b4')
    plt.bar(x + width, roi, width, label='ROI (%)', color='#2ca02c')
    
    plt.title('Comparación Financiera de Proyectos', fontsize=13, fontweight='bold')
    plt.xlabel('Proyectos', fontsize=11, fontweight='bold')
    plt.ylabel('Valores', fontsize=11, fontweight='bold')
    plt.xticks(x, proyectos, rotation=15, ha='right')
    plt.legend(loc='upper left', framealpha=0.95)
    plt.grid(True, axis='y', linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig('comparacion_proyectos.png', dpi=150, bbox_inches='tight')
    print("✓ Gráfico de Comparación generado: comparacion_proyectos.png")


# =============================================================================
# EJEMPLO 3: Serie de Tiempo con Tendencia y Bandas de Confianza
# =============================================================================
def grafico_series_tiempo():
    meses = np.arange(1, 25)  # 24 meses
    produccion_base = 100 + 5 * meses + np.random.normal(0, 8, len(meses))
    tendencia = 100 + 5 * meses
    banda_superior = tendencia + 15
    banda_inferior = tendencia - 15
    
    plt.figure(figsize=(12, 6))
    plt.plot(meses, produccion_base, marker='o', linestyle='-', 
             color='#1f77b4', linewidth=2, markersize=5, label='Producción Real')
    plt.plot(meses, tendencia, linestyle='--', color='#d62728', 
             linewidth=2, label='Tendencia Lineal')
    plt.fill_between(meses, banda_inferior, banda_superior, 
                     alpha=0.2, color='gray', label='Banda de Confianza ±15')
    
    plt.title('Producción Mensual con Proyección de Tendencia', fontsize=13, fontweight='bold')
    plt.xlabel('Mes', fontsize=11, fontweight='bold')
    plt.ylabel('Unidades Producidas (miles)', fontsize=11, fontweight='bold')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    plt.savefig('serie_tiempo_produccion.png', dpi=150, bbox_inches='tight')
    print("✓ Gráfico de Serie de Tiempo generado: serie_tiempo_produccion.png")


# =============================================================================
# EJEMPLO 4: Diagrama de Dispersión con Regresión
# =============================================================================
def grafico_dispersion_regresion():
    np.random.seed(42)
    costos_produccion = np.random.uniform(5, 50, 40)
    precios_venta = 1.8 * costos_produccion + np.random.normal(0, 5, 40)
    
    # Regresión lineal simple
    coef = np.polyfit(costos_produccion, precios_venta, 1)
    linea_regresion = np.poly1d(coef)
    x_linea = np.linspace(costos_produccion.min(), costos_produccion.max(), 100)
    
    plt.figure(figsize=(10, 6))
    plt.scatter(costos_produccion, precios_venta, s=80, alpha=0.6, 
                color='#1f77b4', edgecolors='black', linewidth=0.5, label='Observaciones')
    plt.plot(x_linea, linea_regresion(x_linea), color='#d62728', 
             linewidth=2.5, label=f'Regresión: y = {coef[0]:.2f}x + {coef[1]:.2f}')
    
    plt.title('Relación Costo de Producción vs Precio de Venta', fontsize=13, fontweight='bold')
    plt.xlabel('Costo de Producción ($)', fontsize=11, fontweight='bold')
    plt.ylabel('Precio de Venta ($)', fontsize=11, fontweight='bold')
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    plt.savefig('dispersion_regresion.png', dpi=150, bbox_inches='tight')
    print("✓ Gráfico de Dispersión generado: dispersion_regresion.png")


# =============================================================================
# EJEMPLO 5: Gráfico de Área Apilada (Composición de Costos)
# =============================================================================
def grafico_area_apilada():
    anios = np.arange(2020, 2027)
    materiales = np.array([25, 28, 30, 33, 36, 39, 42])
    mano_obra = np.array([35, 37, 40, 43, 45, 48, 51])
    gastos_generales = np.array([15, 16, 17, 18, 19, 20, 21])
    
    plt.figure(figsize=(11, 6))
    plt.fill_between(anios, 0, materiales, alpha=0.7, color='#1f77b4', label='Materiales')
    plt.fill_between(anios, materiales, materiales + mano_obra, 
                     alpha=0.7, color='#ff7f0e', label='Mano de Obra')
    plt.fill_between(anios, materiales + mano_obra, 
                     materiales + mano_obra + gastos_generales, 
                     alpha=0.7, color='#2ca02c', label='Gastos Generales')
    
    plt.title('Composición de Costos Operativos por Año', fontsize=13, fontweight='bold')
    plt.xlabel('Año', fontsize=11, fontweight='bold')
    plt.ylabel('Costos (Millones USD)', fontsize=11, fontweight='bold')
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    plt.savefig('area_apilada_costos.png', dpi=150, bbox_inches='tight')
    print("✓ Gráfico de Área Apilada generado: area_apilada_costos.png")


# =============================================================================
# EJECUTAR TODOS LOS EJEMPLOS
# =============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("GENERANDO GRÁFICOS DE EJEMPLO")
    print("="*60 + "\n")
    
    grafico_vpn()
    grafico_comparacion_proyectos()
    grafico_series_tiempo()
    grafico_dispersion_regresion()
    grafico_area_apilada()
    
    print("\n" + "="*60)
    print("✓ TODOS LOS GRÁFICOS GENERADOS EXITOSAMENTE")
    print("="*60 + "\n")
    print("Archivos creados:")
    print("  1. vpn_sensibilidad.png - Análisis de sensibilidad VPN")
    print("  2. comparacion_proyectos.png - Comparación de alternativas")
    print("  3. serie_tiempo_produccion.png - Tendencias temporales")
    print("  4. dispersion_regresion.png - Análisis de correlación")
    print("  5. area_apilada_costos.png - Composición de costos")
    print()
