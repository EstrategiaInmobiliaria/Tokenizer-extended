# 🚀 Guía de Inicio Rápido

## En 60 segundos

### Opción 1: Google Colab (MÁS FÁCIL)

1. Abre este link: [01_poiseuille.ipynb en GitHub](notebooks/01_poiseuille.ipynb)
2. Click en el badge "Open in Colab"
3. Ejecuta la primera celda (instala dependencias)
4. Ejecuta el resto de celdas
5. ¡Ya tienes tu primer PINN resolviendo Navier-Stokes!

⏱️ Tiempo total: 5 minutos

### Opción 2: Local (requiere Python)

```bash
# 1. Clonar/descargar el proyecto
cd ingenieria/navier_stokes_pinns

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar que todo funciona
python test_setup.py

# 4. Lanzar notebooks
jupyter notebook notebooks/
```

⏱️ Tiempo total: 10 minutos

### Opción 3: Script directo (sin Jupyter)

```bash
cd ingenieria/navier_stokes_pinns/examples
python run_poiseuille.py
```

⏱️ Tiempo total: 3 minutos (después de instalar deps)

## ¿Qué vas a ver?

### Notebook 01: Flujo de Poiseuille

**Qué es:** Flujo laminar entre dos placas paralelas (piensa en aceite entre dos cristales).

**Lo interesante:**
- Tiene solución analítica conocida (ecuación exacta)
- Puedes verificar que el PINN funciona comparando con la fórmula
- Error típico: menos de 1%

**Gráficas que genera:**
- Perfil de velocidad (parábola perfecta)
- Comparación PINN vs analítico
- Campo de velocidad completo
- Convergencia del entrenamiento

**Tiempo de ejecución:** 3-5 minutos

### Notebook 02: Lid-Driven Cavity

**Qué es:** Caja cuadrada llena de fluido. La tapa superior se mueve, arrastrando el fluido y creando vórtices.

**Lo interesante:**
- NO tiene solución analítica
- Es un benchmark clásico de CFD (todos los papers lo usan)
- Genera patrones de remolinos muy visuales

**Gráficas que genera:**
- Campo de velocidad con streamlines (líneas de flujo)
- Vorticidad (rotación del fluido)
- Presión
- Perfiles de velocidad en líneas centrales

**Tiempo de ejecución:** 10-15 minutos

## 🎯 Flujo de Trabajo Recomendado

### Para Principiantes:

```
Día 1: Notebook 00 (intro) + Notebook 01 (Poiseuille)
        ↓
        Lee README.md
        ↓
Día 2: Notebook 02 (Cavity)
        ↓
        Lee docs/THEORY.md (matemáticas)
        ↓
Día 3: Experimenta cambiando parámetros
        - Re = 100, 400, 1000
        - Viscosidad, velocidad
        - Arquitectura de la red
```

### Para Avanzados:

```
1. Lee docs/THEORY.md (fundamentos)
2. Ejecuta Notebook 01 y 02
3. Lee código en src/solvers/
4. Implementa tu propio caso:
   - Copia poiseuille_solver.py
   - Modifica la PDE
   - Define nuevas condiciones de frontera
   - Crea nuevo notebook
```

## 🐛 Troubleshooting Común

### Error: "ModuleNotFoundError: No module named 'deepxde'"

**Solución:**
```bash
pip install deepxde tensorflow
```

### Error: "TensorFlow not found"

**Solución (elige uno):**
```bash
# Opción A: TensorFlow
pip install tensorflow>=2.13.0

# Opción B: PyTorch
pip install torch>=2.0.0
```

### Error: "ModuleNotFoundError" en notebooks para src/

**Solución:** Ejecuta esta celda al inicio:
```python
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
```

### Warning: "GPU not available"

**Es normal.** PINNs funcionan en CPU (más lento pero ok).

Para GPU:
- **Google Colab:** Cambia a GPU en Runtime > Change runtime type
- **Local:** Instala `tensorflow-gpu` o PyTorch con CUDA

### El entrenamiento es muy lento

**Soluciones:**
1. Reduce `num_domain` (menos puntos de colocación)
2. Reduce `iterations` (menos epochs)
3. Usa GPU (Colab o local)

Ejemplo:
```python
# Antes (lento)
solver.build_model(num_domain=5000)
solver.train(iterations=20000)

# Después (rápido)
solver.build_model(num_domain=2000)
solver.train(iterations=10000)
```

## 📚 ¿Qué archivo leer primero?

Si eres...

### 🎓 Estudiante aprendiendo CFD:
1. `README.md` - Introducción general
2. `notebooks/00_intro.ipynb` - Conceptos
3. `notebooks/01_poiseuille.ipynb` - Primer caso
4. `docs/THEORY.md` - Matemáticas profundas

### 💻 Programador queriendo código:
1. `notebooks/01_poiseuille.ipynb` - Ver código en acción
2. `src/solvers/poiseuille_solver.py` - Implementación
3. `src/utils.py` - Funciones auxiliares
4. `examples/run_poiseuille.py` - Script standalone

### 🔬 Investigador/Académico:
1. `docs/THEORY.md` - Fundamentos matemáticos
2. `docs/COMPARISON.md` - PINN vs CFD
3. `notebooks/02_cavity.ipynb` - Caso sin analítico
4. Papers citados en `LICENSE`

### 🏢 Manager/Decision maker:
1. `EXECUTIVE_SUMMARY.md` - Resumen ejecutivo
2. `docs/COMPARISON.md` - Comparación con CFD
3. `README.md` - Casos de uso

## 🎨 Personalización Rápida

### Cambiar parámetros del flujo:

```python
# En notebook 01 (Poiseuille)
H = 0.5          # Medio ancho del canal
dp_dx = -2.0     # Gradiente de presión (prueba -0.5, -1.0, -2.0)
mu = 0.01        # Viscosidad (prueba 0.005, 0.01, 0.02)

# Resultado: velocidades más altas/bajas
```

### Cambiar arquitectura de la red:

```python
# Antes (default)
layer_size = [2, 50, 50, 50, 1]

# Más capas (más lento, más preciso)
layer_size = [2, 100, 100, 100, 100, 1]

# Menos capas (más rápido, menos preciso)
layer_size = [2, 30, 30, 1]
```

### Cambiar número de Reynolds:

```python
# En notebook 02 (Cavity)
Re = 100   # Laminar suave
Re = 400   # Vórtices secundarios
Re = 1000  # Transición a turbulencia
```

## 🎯 Proyectos Sugeridos

### Nivel Principiante:
1. Ejecuta Poiseuille con 3 valores de Re diferentes
2. Compara los perfiles de velocidad
3. Calcula error L2 para cada caso

### Nivel Intermedio:
1. Modifica cavity para Re=400
2. Identifica vórtices secundarios
3. Compara con datos de Ghia et al. (búscalos en Google Scholar)

### Nivel Avanzado:
1. Implementa flujo alrededor de cilindro
2. Captura Von Kármán vortex street
3. Crea animación del flujo transitorio

## 💡 Tips Pro

### Acelerar entrenamiento:
```python
# Usa learning rate adaptativo
model.compile("adam", lr=1e-3, decay=("step", 5000, 0.9))
```

### Mejorar precisión:
```python
# Más puntos en fronteras
data = dde.data.PDE(
    geom, pde, bcs,
    num_domain=2000,
    num_boundary=500,  # Era 200
    num_test=1000
)
```

### Guardar modelo entrenado:
```python
# Después de entrenar
model.save("poiseuille_model")

# Cargar después
model.restore("poiseuille_model-10000.ckpt")
```

## 🆘 Ayuda

### Si tienes problemas:
1. Revisa esta guía
2. Lee `docs/INSTALL.md` (troubleshooting detallado)
3. Ejecuta `python test_setup.py`
4. Busca error en issues de GitHub
5. Abre nuevo issue con:
   - Código que ejecutaste
   - Error completo
   - Versiones de Python, DeepXDE, TensorFlow

### Si quieres contribuir:
1. Fork el repo
2. Crea branch: `git checkout -b feature/mi-caso`
3. Commit: `git commit -m 'Añade caso X'`
4. Push: `git push origin feature/mi-caso`
5. Abre Pull Request

## 📊 Benchmarks de Performance

### Hardware de referencia:

**Google Colab (CPU):**
- Poiseuille: 3-5 min
- Cavity: 10-15 min

**Google Colab (GPU - T4):**
- Poiseuille: 1-2 min
- Cavity: 5-8 min

**Laptop (i7, 16GB RAM):**
- Poiseuille: 4-6 min
- Cavity: 12-20 min

## 🎓 Próximos Pasos

Una vez domines los 2 notebooks:

1. **Lee papers originales:**
   - Raissi et al. (2019) - PINNs
   - Lu et al. (2021) - DeepXDE

2. **Explora DeepXDE docs:**
   - https://deepxde.readthedocs.io/

3. **Implementa casos avanzados:**
   - Flujo transitorio (dependiente del tiempo)
   - Geometrías complejas
   - Inverse problems

4. **Compara con OpenFOAM:**
   - Instala OpenFOAM
   - Corre mismo caso
   - Compara resultados y tiempos

---

**¿Listo?**

```bash
cd ingenieria/navier_stokes_pinns
jupyter notebook notebooks/00_intro.ipynb
```

¡A resolver Navier-Stokes! 🚀
