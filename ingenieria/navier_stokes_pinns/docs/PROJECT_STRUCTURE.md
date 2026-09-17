# Estructura del Proyecto

```
navier_stokes_pinns/
│
├── README.md                    # Documentación principal y guía de inicio
├── LICENSE                      # Licencia MIT
├── CHANGELOG.md                 # Historial de cambios
├── requirements.txt             # Dependencias Python
├── .gitignore                   # Archivos a ignorar en git
├── test_setup.py               # Script de verificación de instalación
│
├── docs/                        # Documentación detallada
│   ├── INSTALL.md              # Guía de instalación paso a paso
│   ├── THEORY.md               # Fundamentos matemáticos de N-S y PINNs
│   └── COMPARISON.md           # Comparación PINN vs CFD tradicional
│
├── notebooks/                   # Jupyter notebooks interactivos
│   ├── 00_intro.ipynb          # Introducción rápida al proyecto
│   ├── 01_poiseuille.ipynb     # Flujo de Poiseuille (con solución analítica)
│   └── 02_cavity.ipynb         # Lid-Driven Cavity Flow
│
├── src/                         # Código fuente reutilizable
│   ├── __init__.py
│   ├── utils.py                # Utilidades matemáticas y físicas
│   ├── visualization.py        # Funciones de plotting avanzadas
│   └── solvers/                # Implementaciones de PINNs
│       ├── __init__.py
│       ├── poiseuille_solver.py   # Solver para flujo de Poiseuille
│       └── cavity_solver.py       # Solver para lid-driven cavity
│
├── examples/                    # Scripts standalone de ejemplo
│   ├── __init__.py
│   └── run_poiseuille.py       # Ejecuta y visualiza Poiseuille
│
└── visualizations/              # Directorio para resultados (generado)
    └── (imágenes y animaciones generadas automáticamente)
```

## Descripción de Archivos Clave

### Notebooks (notebooks/)

**00_intro.ipynb**
- Introducción al proyecto y conceptos
- Verificación de instalación
- Links a otros notebooks

**01_poiseuille.ipynb**
- Implementación completa de flujo de Poiseuille
- Comparación con solución analítica
- Visualizaciones de campo de velocidad
- Error < 1% típicamente

**02_cavity.ipynb**
- Lid-driven cavity flow (Re=100)
- Visualización de vórtices
- Campos de velocidad, presión y vorticidad
- Comparación con benchmarks de Ghia et al.

### Código Fuente (src/)

**utils.py**
- `create_domain_2d()`: Crea mallas para evaluación
- `compute_vorticity()`: Calcula vorticidad
- `compute_reynolds_number()`: Calcula Re
- `poiseuille_analytical()`: Solución analítica
- `PhysicsConstants`: Propiedades de fluidos

**visualization.py**
- `plot_velocity_field()`: Visualiza campos con streamlines
- `plot_vorticity()`: Mapa de vorticidad
- `plot_pressure()`: Campo de presión
- `plot_comparison()`: Compara PINN vs analítico
- `plot_training_history()`: Convergencia del loss

**solvers/poiseuille_solver.py**
- `PoiseuilleFlowPINN`: Clase solver completa
- Métodos: `build_model()`, `train()`, `predict()`
- Incluye solución analítica para validación

**solvers/cavity_solver.py**
- `LidDrivenCavityPINN`: Solver para cavity flow
- Implementa sistema completo de Navier-Stokes 2D
- 3 outputs: [u, v, p]

### Documentación (docs/)

**INSTALL.md**
- Requisitos previos
- Instalación local paso a paso
- Uso en Google Colab
- Troubleshooting común

**THEORY.md**
- Derivación de Navier-Stokes
- Teoría de PINNs
- Diferenciación automática
- Función de pérdida explicada
- Referencias al Problema del Milenio

**COMPARISON.md**
- Tabla comparativa PINN vs CFD
- Casos de uso recomendados
- Benchmarks de performance
- Estrategias híbridas

### Ejemplos (examples/)

**run_poiseuille.py**
- Script standalone ejecutable
- No requiere Jupyter
- Genera y guarda visualizaciones
- Perfecto para testing rápido

## Flujo de Trabajo Típico

### Para Aprendizaje:

1. Ejecuta `python test_setup.py` (verificación)
2. Abre `notebooks/00_intro.ipynb`
3. Sigue a `01_poiseuille.ipynb`
4. Experimenta con parámetros
5. Avanza a `02_cavity.ipynb`

### Para Desarrollo:

1. Importa módulos de `src/`
2. Usa clases base: `PoiseuilleFlowPINN`, etc.
3. Extiende para nuevos casos
4. Guarda visualizaciones en `visualizations/`

### Para Investigación:

1. Estudia `docs/THEORY.md`
2. Modifica solvers en `src/solvers/`
3. Crea nuevo notebook en `notebooks/`
4. Compara resultados con literatura

## Extensibilidad

### Añadir Nuevo Caso de Flujo:

1. Crea `src/solvers/nuevo_caso_solver.py`
2. Hereda estructura de clases existentes
3. Define PDE específica
4. Crea `notebooks/0X_nuevo_caso.ipynb`
5. Documenta en README

### Añadir Nueva Visualización:

1. Añade función a `src/visualization.py`
2. Sigue convención de nombres `plot_*`
3. Usa seaborn/matplotlib
4. Añade docstring con ejemplo

### Añadir Documentación:

1. Nuevos docs en `docs/`
2. Usa markdown + LaTeX
3. Link desde README principal

## Dependencias

Ver `requirements.txt` para lista completa.

**Core:**
- deepxde >= 1.10.0
- tensorflow >= 2.13.0 o pytorch >= 2.0.0
- numpy >= 1.24.0

**Visualización:**
- matplotlib >= 3.7.0
- seaborn >= 0.12.0

**Notebooks:**
- jupyter >= 1.0.0

## Testing

```bash
# Verificar instalación
python test_setup.py

# Ejecutar ejemplo rápido
cd examples
python run_poiseuille.py

# Lanzar notebooks
jupyter notebook notebooks/
```

## Contribuciones

Para contribuir:
1. Fork el repositorio
2. Crea branch: `git checkout -b feature/nueva-caracteristica`
3. Commit: `git commit -m 'Añade nueva característica'`
4. Push: `git push origin feature/nueva-caracteristica`
5. Abre Pull Request

## Soporte

- Issues: Abre un issue en GitHub
- Preguntas: Discusiones en el repo
- Email: (añadir si aplica)

## Licencia

MIT - Ver `LICENSE` para detalles completos.
