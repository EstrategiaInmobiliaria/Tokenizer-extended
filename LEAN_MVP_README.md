# 📊 Lean Manufacturing Analyzer - MVP en Streamlit

**Prototipo mínimo para análisis de procesos Lean sin tocar código pesado**

---

## 🎯 ¿Qué es este MVP?

Es una aplicación web interactiva en Python puro que te permite:

1. **Editar procesos** en una tabla como Excel (directo en el navegador)
2. **Analizar automáticamente** métricas Lean (Lead Time, Eficiencia, MUDA)
3. **Visualizar cuellos de botella** con grafos NetworkX
4. **Recibir recomendaciones** basadas en reglas lógicas simples (no IA)

---

## 🔑 Conceptos Clave (para NO confundir)

### Lead Time
- **Qué es**: Tiempo real que tarda algo de inicio a fin en tu proceso
- **Ejemplo**: orden de cliente → materia prima → producción → entrega = 12 días
- **Categoría**: Métrica operativa de negocio
- **Dónde se usa**: En planta, con gerentes de operaciones

### Tiempo Polinómico / Complejidad Computacional
- **Qué es**: Concepto de ciencias de la computación
- **Ejemplo**: Algoritmo que tarda O(n²) o O(n³) pasos con n datos
- **Categoría**: Escala matemática de algoritmos
- **Dónde se usa**: Al evaluar si un algoritmo funcionará con 1M de registros

### 🚨 Diferencia Crítica

| Lead Time | Complejidad Computacional |
|-----------|---------------------------|
| Días, horas, minutos | Escala matemática (O(n), O(n²), O(2ⁿ)) |
| Lo sufres en planta | Te dice si tu código va a colapsar |
| Métrica operativa | Propiedad del algoritmo |

### Punto de Unión

Si tu MVP de análisis Lean tiene que procesar **100k pasos de producción**:
- Mejor que el algoritmo sea **O(n)** u **O(n log n)** → Este MVP ✅
- Si es **O(n³)** → Se congela ❌
- Si es **O(2ⁿ)** → Inviable para n>30 ❌

---

## 🚀 Opción 1: Ejecutar Localmente

### Requisitos Previos
```bash
# Python 3.8 o superior
python3 --version
```

### Instalación

```bash
# 1. Instalar dependencias
pip install streamlit pandas numpy networkx matplotlib

# 2. Verificar instalación
python3 -c "import streamlit; print('Streamlit versión:', streamlit.__version__)"

# 3. Ejecutar la app
streamlit run lean_streamlit_mvp.py
```

### Resultado

```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.10:8501
```

Abre `http://localhost:8501` en tu navegador.

---

## 🌐 Opción 2: Ejecutar en Google Colab (SIN instalar nada)

### Tiempo total: 2 minutos desde cero

#### Paso 1: Abrir Google Colab
1. Ve a https://colab.research.google.com/
2. Clic en **"Nuevo Notebook"**

#### Paso 2: Copiar el código
1. Abre el archivo `lean_colab_notebook.py`
2. Copia **TODO** el contenido
3. Pégalo en una celda de Colab

#### Paso 3: Ejecutar
1. Presiona **Shift + Enter** (o clic en el botón ▶️)
2. Espera ~30 segundos mientras instala dependencias
3. Verás un mensaje como:

```
═══════════════════════════════════════════════════════════════
✅ TÚNEL CREADO EXITOSAMENTE
═══════════════════════════════════════════════════════════════

🚀 ABRE ESTA URL EN TU NAVEGADOR:

   https://1a2b-34-56-78-90.ngrok.io

═══════════════════════════════════════════════════════════════
```

4. **Copia el link** (algo como `https://xxxx.ngrok.io`)
5. **Pégalo en tu navegador**
6. ¡Ya tienes la app funcionando! 🎉

#### ⚠️ Importante
- **NO cierres el notebook de Colab** mientras uses la app
- Si lo cierras, el link dejará de funcionar
- El link es público pero temporal (válido mientras la celda esté ejecutándose)

---

## 📖 Cómo Usar la App

### 1. Editor de Procesos (Sección 1️⃣)

La app viene con un proceso de ejemplo. Puedes:

- **Editar** cualquier celda directamente (como Excel)
- **Agregar filas** con el botón "+" al final de la tabla
- **Eliminar filas** seleccionando y presionando Delete
- **Cambiar tipos** usando el dropdown en la columna "Tipo"

**Columnas:**
- **Paso**: Nombre del paso del proceso
- **Tipo**: Operación | Inspección | Transporte | Demora | Almacenamiento
- **Tiempo (min)**: Duración en minutos
- **Recurso**: Operador, máquina, etc.

### 2. Análisis Automático (Sección 2️⃣)

1. Después de editar, haz clic en **"🚀 Analizar Proceso"**
2. La app calculará instantáneamente:

   - **Lead Time Total**: Suma de todos los pasos
   - **Tiempo de Valor Agregado**: Solo pasos tipo "Operación"
   - **Tiempo de Desperdicio (MUDA)**: Todo lo demás
   - **Eficiencia**: % de tiempo que agrega valor

3. Verás 4 visualizaciones:

   - **Dashboard de métricas** (4 gráficos)
   - **Cuellos de botella** (alertas automáticas)
   - **Mapa de flujo** (grafo NetworkX)
   - **Recomendaciones** (basadas en reglas if-then)

### 3. Configuración de Umbrales (Sidebar ⚙️)

Ajusta los límites para detectar cuellos de botella:

- **Demora**: Si un paso de tipo "Demora" supera X minutos, se marca como cuello de botella
- **Transporte**: Idem para "Transporte"
- **Inspección**: Idem para "Inspección"
- **Almacenamiento**: Idem para "Almacenamiento"

Valores por defecto (puedes cambiarlos):
- Demora: 10 min
- Transporte: 3 min
- Inspección: 5 min
- Almacenamiento: 60 min

---

## 🧠 Lógica del Motor de Análisis

### Complejidad Computacional

```python
# Cálculo de métricas: O(n)
for step in steps:  # Recorre 1 vez
    lead_time += step.duration
    if step.is_value_added:
        value_added_time += step.duration

# Detección de cuellos de botella: O(n)
for step in steps:  # Recorre 1 vez
    if step.duration > THRESHOLD[step.type]:
        bottlenecks.append(step)

# Grafo NetworkX: O(n²) en layout, pero para <1000 nodos es instantáneo
```

**Conclusión**: Este MVP escala bien hasta **100k registros** en análisis lineal.
Solo el layout del grafo se vuelve lento con >1000 nodos (pero eso es visual, no afecta métricas).

### Reglas de Recomendaciones

```python
# Regla 1: Eficiencia
if eficiencia < 40%:
    → "CRÍTICO: Revisar pasos no-operativos"
elif eficiencia < 60%:
    → "MEJORABLE: Priorizar demoras"

# Regla 2: Por tipo de desperdicio
if Demoras > 10 min:
    → "Paralelizar tareas, eliminar esperas, flujo continuo"

if Transporte > 5 min:
    → "Acercar estaciones, rediseñar layout, células de manufactura"

if Inspección > 8 min:
    → "Poka-Yoke, inspección en línea, control estadístico"

if Almacenamiento > 60 min:
    → "Sistema Pull (Kanban), reducir lotes, JIT"

# Regla 3: Lead Time absoluto
if lead_time > 8 horas:
    → "Considerar VSM (Value Stream Mapping) completo"
```

**Nota**: Estas son reglas lógicas simples, **NO IA**. Son condicionales if-then basadas en prácticas Lean estándar.

---

## 🎨 Ejemplo de Uso Real

### Caso: Línea de Ensamblaje Automotriz

**Proceso Actual** (11 pasos):

| Paso | Tipo | Tiempo (min) | Recurso |
|------|------|--------------|---------|
| Recepción MP | Operación | 5 | Operador 1 |
| Transporte a Almacén | Transporte | 3 | Montacargas |
| **Espera en Almacén** | **Demora** | **15** | Almacén |
| Transporte a Producción | Transporte | 4 | Montacargas |
| Setup Máquina | Operación | 10 | Operador 2 |
| Corte | Operación | 20 | CNC |
| Inspección Visual | Inspección | 8 | Inspector |
| Ensamblaje | Operación | 30 | Operador 3 |
| Transporte a Calidad | Transporte | 2 | Montacargas |
| Control de Calidad | Inspección | 12 | Inspector |
| Empaque | Operación | 8 | Operador 4 |

**Resultados del Análisis:**

```
Lead Time Total: 117 minutos (1.95 horas)
Tiempo de Valor Agregado: 73 minutos (62.4%)
Tiempo de Desperdicio: 44 minutos (37.6%)

Cuellos de Botella Detectados:
- Espera en Almacén (Demora): 15 min > 10 min límite

Recomendaciones:
1. DEMORAS: 15 min detectados
   → Paralelizar tareas, eliminar esperas, flujo continuo

2. INSPECCIÓN: 20 min detectados
   → Poka-Yoke, inspección en línea, control estadístico

3. TRANSPORTE: 9 min detectados
   → Acercar estaciones, rediseñar layout, células de manufactura
```

**Acciones Tomadas:**
- Eliminar almacenamiento intermedio → Sistema Pull
- Mover inspección a línea → Ahorro de 8 min
- Acercar estaciones → Ahorro de 5 min

**Resultado Final:**
- Lead Time: 117 min → **104 min** (-11%)
- Eficiencia: 62% → **70%**

---

## 📦 Estructura de Archivos

```
workspace/
├── lean_streamlit_mvp.py         # App principal de Streamlit
├── lean_colab_notebook.py        # Versión para Google Colab con pyngrok
├── LEAN_MVP_README.md            # Esta documentación
└── requirements_lean.txt         # Dependencias (ver abajo)
```

---

## 📋 Requisitos Técnicos

### Python Packages

```txt
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.20.0
networkx>=2.8.0
matplotlib>=3.3.0
pyngrok>=5.0.0  # Solo para versión Colab
```

**Instalar todos:**
```bash
pip install -r requirements_lean.txt
```

### Versiones Probadas

- Python: 3.8, 3.9, 3.10, 3.11
- Streamlit: 1.28+
- OS: Linux, macOS, Windows
- Google Colab: Funciona nativamente (no requiere instalación local)

---

## 🐛 Troubleshooting

### Error: "command not found: streamlit"

**Solución:**
```bash
# Verificar que streamlit esté instalado
pip list | grep streamlit

# Si no está, instalar
pip install streamlit

# Verificar PATH (macOS/Linux)
which streamlit
```

### Error: "Address already in use (port 8501)"

**Solución:**
```bash
# Opción 1: Cambiar puerto
streamlit run lean_streamlit_mvp.py --server.port 8502

# Opción 2: Matar proceso en puerto 8501 (Linux/Mac)
lsof -ti:8501 | xargs kill -9
```

### Error en Colab: "ngrok tunnel not found"

**Solución:**
```python
# En la celda de Colab, agregar antes del ngrok.connect():
from pyngrok import ngrok
ngrok.kill()  # Matar túneles previos
public_url = ngrok.connect(addr="8501", proto="http")
```

### Grafo no se renderiza

**Causa**: NetworkX + Matplotlib a veces tienen conflictos en Jupyter/Colab

**Solución:**
```python
# Agregar al inicio del código:
import matplotlib
matplotlib.use('Agg')
```

---

## 🔬 Siguientes Pasos (Extensiones Posibles)

### Para MVP v2:

1. **Exportar reportes** (PDF, Excel)
2. **Comparar escenarios** (antes/después)
3. **Base de datos** (guardar procesos históricos)
4. **API REST** (integrar con sistemas MES/ERP)
5. **Autenticación** (login para múltiples usuarios)

### Para Producción:

1. **Optimización de grafos** para >10k nodos (usar Plotly/Cytoscape.js)
2. **Paralelización** con Dask para análisis de múltiples plantas
3. **Machine Learning** para predecir Lead Time futuro
4. **Integración IoT** para captura automática de tiempos
5. **Dashboard ejecutivo** con agregación por línea/planta

---

## 📚 Referencias

### Lean Manufacturing
- [Toyota Production System (TPS)](https://global.toyota/en/company/vision-and-philosophy/production-system/)
- [Lean Enterprise Institute](https://www.lean.org/)
- Libro: *Lean Thinking* - Womack & Jones

### Complejidad Computacional
- [Introduction to Algorithms (CLRS)](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Big-O Notation Cheat Sheet](https://www.bigocheatsheet.com/)

### Streamlit
- [Documentación Oficial](https://docs.streamlit.io/)
- [Gallery de Apps](https://streamlit.io/gallery)

### NetworkX
- [Documentación NetworkX](https://networkx.org/documentation/stable/)
- [Algorithms Complexity](https://networkx.org/documentation/stable/reference/algorithms/index.html)

---

## 🤝 Contribuciones

Este es un MVP educativo. Mejoras sugeridas:

1. **Fork** el repositorio
2. **Crea una rama**: `git checkout -b feature/mi-mejora`
3. **Commit**: `git commit -m 'Agrego feature X'`
4. **Push**: `git push origin feature/mi-mejora`
5. **Pull Request**

---

## 📄 Licencia

MIT License - Ver archivo `LICENSE`

---

## 👤 Autor

Creado como parte del proyecto Master Blueprint - Optimización Financiera y Operativa

---

## 🙏 Agradecimientos

- **Streamlit** por hacer Python web development accesible
- **NetworkX** por algoritmos de grafos optimizados
- **Comunidad Lean** por las mejores prácticas documentadas

---

**¿Preguntas?** Abre un issue en el repositorio.

**¿Sugerencias?** Pull requests bienvenidos.

🚀 **Happy Lean Analyzing!**
