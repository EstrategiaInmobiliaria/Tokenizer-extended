# Guía de Instalación y Configuración

## Instalación Local

### Requisitos Previos

- Python 3.8+
- pip

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO/navier_stokes_pinns
```

### Paso 2: Crear Ambiente Virtual

```bash
# Crear ambiente
python -m venv venv

# Activar (Linux/Mac)
source venv/bin/activate

# Activar (Windows)
venv\Scripts\activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Nota:** DeepXDE requiere un backend de deep learning. Por defecto se instala TensorFlow. Si prefieres PyTorch:

```bash
pip uninstall tensorflow
pip install torch torchvision
```

### Paso 4: Verificar Instalación

```bash
python -c "import deepxde; import tensorflow; print('✓ Todo instalado correctamente')"
```

## Uso Rápido

### Opción 1: Notebooks Interactivos

```bash
jupyter notebook notebooks/
```

Abre cualquiera de los notebooks:
- `01_poiseuille.ipynb` - Flujo de Poiseuille (con solución analítica)
- `02_cavity.ipynb` - Lid-driven cavity

### Opción 2: Scripts Standalone

```bash
cd examples
python run_poiseuille.py
```

## Google Colab

1. Abre cualquier notebook en GitHub
2. Click en el badge "Open in Colab"
3. Ejecuta la primera celda para instalar dependencias
4. ¡Listo! No necesitas instalar nada local

## Estructura de Archivos

```
navier_stokes_pinns/
├── requirements.txt          # Dependencias
├── README.md                 # Documentación principal
├── docs/
│   └── INSTALL.md           # Esta guía
├── notebooks/               # Jupyter notebooks interactivos
│   ├── 01_poiseuille.ipynb
│   └── 02_cavity.ipynb
├── src/                     # Código fuente
│   ├── utils.py            # Utilidades
│   ├── visualization.py    # Funciones de plotting
│   └── solvers/            # Implementaciones de PINNs
│       ├── poiseuille_solver.py
│       └── cavity_solver.py
├── examples/                # Scripts de ejemplo
│   └── run_poiseuille.py
└── visualizations/          # Resultados guardados (generados)
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'deepxde'"

Asegúrate de haber activado el ambiente virtual e instalado las dependencias:

```bash
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
```

### Error: "TensorFlow not found"

DeepXDE requiere TensorFlow o PyTorch. Instala uno:

```bash
pip install tensorflow>=2.13.0
# O
pip install torch>=2.0.0
```

### Warning: "GPU not available"

Es normal. DeepXDE funciona en CPU (más lento pero funcional). Para usar GPU:

- TensorFlow: Instala `tensorflow-gpu`
- PyTorch: Sigue la [guía de instalación oficial](https://pytorch.org/get-started/locally/)

### Error al importar módulos en notebooks

Si ves `ModuleNotFoundError` para módulos locales (`src/`), asegúrate de que el notebook tenga:

```python
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
```

Esto añade el directorio padre al path de Python.

## Configuración de DeepXDE

Por defecto, DeepXDE usa TensorFlow. Para cambiar a PyTorch:

```python
import deepxde as dde
dde.config.set_default_float("float32")
dde.config.set_backend("pytorch")
```

## Recursos Adicionales

- [Documentación de DeepXDE](https://deepxde.readthedocs.io/)
- [Tutorial de PINNs](https://towardsdatascience.com/physics-informed-neural-networks-pinns-an-intuitive-guide-fff138069563)
- [Paper original](https://www.sciencedirect.com/science/article/pii/S0021999118307125)
