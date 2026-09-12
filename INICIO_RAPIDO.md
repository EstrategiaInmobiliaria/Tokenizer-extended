# 🚀 Guía de Instalación y Uso Rápido

## 📦 Instalación en 30 Segundos

### Paso 1: Instalar las librerías
```bash
pip install numpy matplotlib
```

### Paso 2: Verificar instalación
```bash
python3 -c "import numpy as np; import matplotlib.pyplot as plt; print('✓ Entorno configurado correctamente')"
```

---

## ⚡ Ejecutar los Ejemplos

### Opción 1: Gráfico de Prueba Básico
```bash
python3 test_plot.py
```
**Genera:** `grafica_prueba.png`

### Opción 2: 5 Ejemplos Intermedios
```bash
python3 ejemplos_graficos.py
```
**Genera:**
- `vpn_sensibilidad.png`
- `comparacion_proyectos.png`
- `serie_tiempo_produccion.png`
- `dispersion_regresion.png`
- `area_apilada_costos.png`

### Opción 3: 5 Análisis Avanzados
```bash
python3 ejemplos_avanzados.py
```
**Genera:**
- `break_even_analysis.png`
- `pareto_chart.png`
- `dcf_analysis.png`
- `sensitivity_analysis.png`
- `executive_dashboard.png`

---

## 📊 Resumen de Archivos Generados

| Archivo | Descripción | Nivel |
|---------|-------------|-------|
| `grafica_prueba.png` | Flujo de caja con break-even | Básico |
| `vpn_sensibilidad.png` | VPN vs tasa de descuento | Intermedio |
| `comparacion_proyectos.png` | Barras agrupadas | Intermedio |
| `serie_tiempo_produccion.png` | Tendencia temporal | Intermedio |
| `dispersion_regresion.png` | Correlación lineal | Intermedio |
| `area_apilada_costos.png` | Composición de costos | Intermedio |
| `break_even_analysis.png` | Análisis punto equilibrio | Avanzado |
| `pareto_chart.png` | Diagrama de Pareto 80/20 | Avanzado |
| `dcf_analysis.png` | Flujo de caja descontado | Avanzado |
| `sensitivity_analysis.png` | Análisis de sensibilidad | Avanzado |
| `executive_dashboard.png` | Dashboard 4 métricas | Avanzado |

---

## 🎯 Plantilla Personalizable Rápida

Copia este código y modifica los datos según tus necesidades:

```python
import numpy as np
import matplotlib.pyplot as plt

# TUS DATOS AQUÍ
x_datos = np.array([0, 1, 2, 3, 4, 5])
y_datos = np.array([10, 25, 40, 55, 70, 85])

# CREAR GRÁFICO
plt.figure(figsize=(10, 6))
plt.plot(x_datos, y_datos, marker='o', linewidth=2.5, color='#1f77b4')

# PERSONALIZACIÓN
plt.title('Tu Título Aquí', fontsize=13, fontweight='bold')
plt.xlabel('Eje X', fontsize=11, fontweight='bold')
plt.ylabel('Eje Y', fontsize=11, fontweight='bold')
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()

# GUARDAR
plt.savefig('mi_grafico.png', dpi=150, bbox_inches='tight')
print("✓ Gráfico guardado: mi_grafico.png")
```

---

## 🔧 Solución de Problemas

### Error: "pip: command not found"
```bash
# En Ubuntu/Debian
sudo apt-get update && sudo apt-get install python3-pip

# En macOS
brew install python3
```

### Error: "Permission denied"
```bash
pip install --user numpy matplotlib
```

### Error: "RuntimeError: Invalid DISPLAY"
Agrega al inicio de tu script:
```python
import matplotlib
matplotlib.use('Agg')  # Usar backend sin GUI
import matplotlib.pyplot as plt
```

---

## 📖 Documentación Completa

Ver `GRAFICOS_README.md` para:
- Guía detallada de personalización
- Casos de uso específicos
- Ejemplos de código adicionales
- Tips avanzados y mejores prácticas

---

## 🎓 Próximos Pasos

1. ✅ Ejecuta los 3 scripts para ver los ejemplos
2. 📝 Abre y lee los archivos `.py` para entender el código
3. 🔧 Modifica los parámetros (colores, tamaños, títulos)
4. 📊 Reemplaza los datos de prueba con tus datos reales
5. 🚀 Combina técnicas para crear tus propias visualizaciones

---

**¡Todo listo para empezar a graficar! 📈**
