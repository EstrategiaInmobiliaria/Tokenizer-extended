# 📊 Entorno de Análisis y Graficación Profesional

Plantillas listas para generar gráficos de calidad publicación para análisis financiero, ingeniería económica y ciencia de datos usando **NumPy** y **Matplotlib**.

---

## 🚀 Instalación Rápida

### Requisitos previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Comando de instalación
```bash
pip install numpy matplotlib
```

### Verificar instalación
```bash
python3 -c "import numpy as np; import matplotlib.pyplot as plt; print('✓ Entorno listo')"
```

---

## 📁 Archivos Incluidos

| Archivo | Descripción |
|---------|-------------|
| `test_plot.py` | Script de prueba básico (plantilla inicial) |
| `ejemplos_graficos.py` | 5 ejemplos profesionales listos para ejecutar |
| `GRAFICOS_README.md` | Este archivo (guía completa) |

---

## 🎯 Ejecución Rápida

### 1. Gráfico de Prueba Básico
```bash
python3 test_plot.py
```
**Salida:** `grafica_prueba.png` - Flujo de caja acumulado con punto de equilibrio

### 2. Colección de Ejemplos Profesionales
```bash
python3 ejemplos_graficos.py
```
**Genera 5 gráficos:**
- `vpn_sensibilidad.png` - Análisis VPN vs tasa de descuento
- `comparacion_proyectos.png` - Barras agrupadas para comparación
- `serie_tiempo_produccion.png` - Tendencia temporal con bandas
- `dispersion_regresion.png` - Correlación con línea de regresión
- `area_apilada_costos.png` - Composición de costos por categoría

---

## 📖 Guía de Personalización

### Componentes Clave de NumPy

```python
import numpy as np

# Generar secuencias numéricas
anios = np.arange(0, 10)              # [0, 1, 2, ..., 9]
valores = np.linspace(0, 100, 50)     # 50 valores entre 0 y 100
aleatorios = np.random.normal(0, 5, 100)  # 100 valores con distribución normal

# Operaciones vectorizadas (sin bucles)
flujo = -1000 + 250 * anios + 10 * (anios ** 2)
vpn = flujo / (1.1 ** anios)
```

### Componentes Clave de Matplotlib

#### 1. Configuración de la Figura
```python
import matplotlib.pyplot as plt

plt.figure(figsize=(ancho, alto))     # Tamaño en pulgadas
plt.figure(figsize=(10, 6))           # Ejemplo típico
```

#### 2. Tipos de Gráficos

**Líneas (Tendencias, Series de Tiempo)**
```python
plt.plot(x, y, marker='o', linestyle='-', linewidth=2.5, 
         color='#1f77b4', markersize=8, label='Etiqueta')
```

**Barras (Comparaciones, Categorías)**
```python
plt.bar(categorias, valores, width=0.5, color='#2ca02c', label='Etiqueta')
```

**Dispersión (Correlaciones, Regresiones)**
```python
plt.scatter(x, y, s=80, alpha=0.6, color='#ff7f0e', edgecolors='black')
```

**Área (Composición, Acumulación)**
```python
plt.fill_between(x, y1, y2, alpha=0.5, color='blue')
```

#### 3. Personalización Visual

```python
# Título y etiquetas
plt.title('Título Principal', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Eje X', fontsize=11, fontweight='bold')
plt.ylabel('Eje Y', fontsize=11, fontweight='bold')

# Líneas de referencia
plt.axhline(0, color='red', linestyle='--', linewidth=1.2)  # Horizontal
plt.axvline(5, color='green', linestyle=':', linewidth=1)   # Vertical

# Cuadrícula y leyenda
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(loc='upper left', frameon=True, framealpha=0.95)

# Ajuste automático de márgenes
plt.tight_layout()

# Guardar con alta calidad
plt.savefig('output.png', dpi=150, bbox_inches='tight')
```

#### 4. Colores Profesionales
```python
# Paleta por defecto de Matplotlib (recomendados)
colores = {
    'azul': '#1f77b4',
    'naranja': '#ff7f0e',
    'verde': '#2ca02c',
    'rojo': '#d62728',
    'morado': '#9467bd',
    'cafe': '#8c564b',
    'rosa': '#e377c2',
    'gris': '#7f7f7f'
}
```

---

## 🔧 Ejemplos de Casos de Uso

### Caso 1: Análisis de Break-even
```python
import numpy as np
import matplotlib.pyplot as plt

unidades = np.arange(0, 1001, 50)
costos_fijos = 50000
costo_variable_unitario = 25
precio_venta = 75

costo_total = costos_fijos + costo_variable_unitario * unidades
ingreso_total = precio_venta * unidades

plt.figure(figsize=(10, 6))
plt.plot(unidades, costo_total, label='Costo Total', linewidth=2.5)
plt.plot(unidades, ingreso_total, label='Ingreso Total', linewidth=2.5)
plt.axhline(costos_fijos, linestyle='--', alpha=0.5, label='Costos Fijos')

# Punto de equilibrio
break_even = costos_fijos / (precio_venta - costo_variable_unitario)
plt.axvline(break_even, color='red', linestyle=':', linewidth=2, 
            label=f'Break-even: {break_even:.0f} unidades')

plt.title('Análisis de Punto de Equilibrio', fontsize=13, fontweight='bold')
plt.xlabel('Unidades Producidas', fontsize=11, fontweight='bold')
plt.ylabel('$ (USD)', fontsize=11, fontweight='bold')
plt.legend(loc='upper left')
plt.grid(True, linestyle=':', alpha=0.5)
plt.tight_layout()
plt.savefig('break_even.png', dpi=150)
```

### Caso 2: Diagrama de Pareto (80/20)
```python
import numpy as np
import matplotlib.pyplot as plt

# Datos de ejemplo: causas de defectos
categorias = ['Causa A', 'Causa B', 'Causa C', 'Causa D', 'Causa E']
frecuencias = np.array([145, 89, 67, 23, 12])

# Ordenar de mayor a menor
indices = np.argsort(frecuencias)[::-1]
categorias_ord = [categorias[i] for i in indices]
frecuencias_ord = frecuencias[indices]

# Calcular porcentaje acumulado
porcentaje_acum = np.cumsum(frecuencias_ord) / np.sum(frecuencias_ord) * 100

fig, ax1 = plt.subplots(figsize=(10, 6))

# Barras de frecuencia
ax1.bar(categorias_ord, frecuencias_ord, color='#1f77b4', alpha=0.7)
ax1.set_xlabel('Categorías', fontsize=11, fontweight='bold')
ax1.set_ylabel('Frecuencia', fontsize=11, fontweight='bold', color='#1f77b4')
ax1.tick_params(axis='y', labelcolor='#1f77b4')

# Línea de porcentaje acumulado
ax2 = ax1.twinx()
ax2.plot(categorias_ord, porcentaje_acum, color='#d62728', marker='o', 
         linewidth=2.5, markersize=8)
ax2.set_ylabel('% Acumulado', fontsize=11, fontweight='bold', color='#d62728')
ax2.tick_params(axis='y', labelcolor='#d62728')
ax2.axhline(80, color='green', linestyle='--', alpha=0.7, label='80% (Pareto)')

plt.title('Diagrama de Pareto - Análisis de Causas', fontsize=13, fontweight='bold')
ax1.grid(True, axis='y', linestyle=':', alpha=0.5)
plt.tight_layout()
plt.savefig('pareto.png', dpi=150)
```

---

## 💡 Tips Avanzados

### 1. Subplots (Múltiples gráficos en una figura)
```python
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

axes[0, 0].plot(x1, y1)
axes[0, 0].set_title('Gráfico 1')

axes[0, 1].bar(categorias, valores)
axes[0, 1].set_title('Gráfico 2')

plt.tight_layout()
plt.savefig('dashboard.png', dpi=150)
```

### 2. Anotaciones y Flechas
```python
plt.annotate('Punto Importante', 
             xy=(x_punto, y_punto),          # Coordenadas del punto
             xytext=(x_texto, y_texto),      # Coordenadas del texto
             arrowprops=dict(facecolor='red', shrink=0.05),
             fontsize=10, fontweight='bold')
```

### 3. Estilo Predefinido
```python
# Aplicar un estilo completo
plt.style.use('seaborn-v0_8-darkgrid')  # Otros: 'ggplot', 'bmh', 'fivethirtyeight'
```

### 4. Exportar en Múltiples Formatos
```python
plt.savefig('grafico.png', dpi=300)      # Alta resolución
plt.savefig('grafico.pdf')               # Vectorial (escalable)
plt.savefig('grafico.svg')               # Web/presentaciones
```

---

## 📚 Recursos Adicionales

### Documentación Oficial
- **NumPy:** https://numpy.org/doc/stable/
- **Matplotlib:** https://matplotlib.org/stable/contents.html

### Galería de Ejemplos
- **Matplotlib Gallery:** https://matplotlib.org/stable/gallery/index.html

### Cheat Sheets
- **NumPy Cheat Sheet:** https://numpy.org/doc/stable/user/absolute_beginners.html
- **Matplotlib Cheat Sheet:** https://matplotlib.org/cheatsheets/

---

## 🎓 Próximos Pasos Sugeridos

1. **Ejecuta los ejemplos incluidos** para familiarizarte con la sintaxis
2. **Modifica los parámetros** (colores, tamaños, etiquetas) para ver el efecto
3. **Reemplaza los datos de prueba** con tus propios datos reales
4. **Combina técnicas** de diferentes ejemplos para crear visualizaciones personalizadas
5. **Explora la galería oficial** de Matplotlib para inspiración adicional

---

## ⚙️ Solución de Problemas Comunes

### Error: "ModuleNotFoundError: No module named 'numpy'"
```bash
pip install --upgrade numpy matplotlib
```

### Error: "RuntimeError: Invalid DISPLAY variable"
```python
# Agregar al inicio del script (para entornos sin GUI)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
```

### Gráficos no se guardan correctamente
```python
# Siempre usa plt.savefig() ANTES de plt.show()
plt.savefig('grafico.png', dpi=150, bbox_inches='tight')
plt.show()  # Este debe ir después
```

---

## 📬 Contribuciones y Mejoras

Este entorno es una base sólida y profesional. Para personalizaciones específicas de tu industria o tipo de análisis, adapta las plantillas según tus necesidades.

**¡Feliz graficación! 📊📈📉**
