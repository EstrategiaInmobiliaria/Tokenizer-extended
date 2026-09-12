import numpy as np
import matplotlib.pyplot as plt

# 1. Generar datos de prueba con NumPy
# Creamos un rango de valores en el tiempo (ej. años 0 a 5)
anios = np.arange(0, 6)
# Simulamos un flujo de caja acumulado con crecimiento exponencial/financiero
flujo_acumulado = -12.5 + 3.85 * anios + 0.2 * (anios ** 1.5)

# 2. Configurar la figura y el diseño del gráfico en Matplotlib
plt.figure(figsize=(9, 5))

# Trazar la línea principal con marcadores y estilo profesional
plt.plot(anios, flujo_acumulado, marker='o', linestyle='-', color='#1f77b4', linewidth=2.5, markersize=8, label='Flujo Acumulado Proyectado')

# Añadir línea de referencia en y = 0 (Punto de Equilibrio / Break-even)
plt.axhline(0, color='#d62728', linestyle='--', linewidth=1.2, label='Punto de Equilibrio (Break-even)')

# 3. Personalización de ejes, etiquetas y estilo
plt.title('Gráfica de Prueba: Comportamiento Financiero Acumulado', fontsize=12, fontweight='bold', pad=15)
plt.xlabel('Horizonte de Tiempo (Años)', fontsize=10, fontweight='bold')
plt.ylabel('Millones USD ($)', fontsize=10, fontweight='bold')

# Cuadrícula y leyenda
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(loc='upper left', frameon=True)

# Ajustar diseño y guardar el gráfico
plt.tight_layout()
plt.savefig('grafica_prueba.png', dpi=150, bbox_inches='tight')
print("✓ Gráfica generada exitosamente: grafica_prueba.png")
print(f"✓ Datos procesados: {len(anios)} años de proyección")
print(f"✓ Flujo inicial: ${flujo_acumulado[0]:.2f}M USD")
print(f"✓ Flujo final: ${flujo_acumulado[-1]:.2f}M USD")
