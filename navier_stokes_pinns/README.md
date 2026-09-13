# Navier-Stokes con Physics-Informed Neural Networks (PINNs)

Implementación educativa de solvers de Navier-Stokes usando Deep Learning y restricciones físicas.

## 📐 Ecuaciones de Navier-Stokes

Las ecuaciones que gobiernan el flujo de fluidos incompresibles:

**Conservación de momento:**
$$
\rho\left(\frac{\partial \mathbf{v}}{\partial t} + \mathbf{v}\cdot\nabla\mathbf{v}\right) = -\nabla p + \mu\nabla^2\mathbf{v} + \mathbf{f}
$$

**Conservación de masa (incompresibilidad):**
$$
\nabla \cdot \mathbf{v} = 0
$$

## 🎯 Casos Implementados

### 1. Flujo de Poiseuille (Canal 2D)
- Flujo laminar entre placas paralelas
- **Solución analítica conocida** para validación
- Ideal para verificar que el PINN funciona

### 2. Lid-Driven Cavity Flow
- Benchmark clásico de CFD
- Cavidad cuadrada con tapa móvil
- Genera vórtices característicos

### 3. Flujo alrededor de Cilindro
- Von Kármán Vortex Street
- Flujo no estacionario
- Visualización de desprendimiento de vórtices

## 🚀 Inicio Rápido

### Instalación Local

```bash
# Crear ambiente virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Lanzar Jupyter
jupyter notebook notebooks/
```

### Google Colab

1. Abre cualquier notebook en `notebooks/`
2. Click en "Open in Colab" (badge al inicio)
3. Ejecuta la primera celda para instalar dependencias
4. ¡Listo!

## 📁 Estructura del Proyecto

```
navier_stokes_pinns/
├── notebooks/              # Jupyter notebooks interactivos
│   ├── 01_poiseuille.ipynb       # Flujo de Poiseuille
│   ├── 02_cavity.ipynb            # Lid-driven cavity
│   └── 03_cylinder.ipynb          # Flujo alrededor de cilindro
├── src/                    # Código fuente reutilizable
│   ├── solvers/           # Implementaciones de PINNs
│   ├── utils.py           # Utilidades comunes
│   └── visualization.py   # Funciones de graficación
├── visualizations/        # Imágenes y animaciones generadas
└── docs/                  # Documentación adicional
```

## 🧠 ¿Qué es un PINN?

Un **Physics-Informed Neural Network** es una red neuronal que:

1. **Aprende de datos** (como cualquier NN)
2. **Respeta leyes físicas** (Navier-Stokes en este caso)

La función de pérdida incluye:
```python
loss = loss_data + λ_pde * loss_pde + λ_bc * loss_boundary
```

Donde:
- `loss_data`: Error en mediciones (si existen)
- `loss_pde`: Violación de la ecuación diferencial
- `loss_bc`: Violación de condiciones de frontera

## 📊 Comparación: PINN vs CFD Tradicional

| Aspecto | PINN (DeepXDE) | CFD (OpenFOAM/Fluent) |
|---------|----------------|------------------------|
| **Mallado** | No requiere | Crítico (puede tomar días) |
| **Tiempo setup** | Minutos | Horas a días |
| **Acoplamiento con datos** | Natural | Complejo |
| **Precisión** | Media-Alta | Alta |
| **Casos validados** | Investigación | Industria certificada |
| **Hardware** | GPU (Google Colab gratis) | CPU clusters caros |

## 🎓 Para Aprender Más

- [Paper original de PINNs](https://www.sciencedirect.com/science/article/pii/S0021999118307125) (Raissi et al., 2019)
- [Documentación DeepXDE](https://deepxde.readthedocs.io/)
- [Navier-Stokes Millennium Problem](https://www.claymath.org/millennium-problems/navier-stokes-equation)

## 🏆 Desafío del Milenio

Las ecuaciones de Navier-Stokes son uno de los 7 Problemas del Milenio del Clay Mathematics Institute.

**Premio:** $1,000,000 USD

**Pregunta:** ¿Existen soluciones suaves y globalmente definidas para las ecuaciones 3D de Navier-Stokes?

Nadie lo ha resuelto en 200 años. Estos PINNs **NO resuelven el problema**, solo aproximan soluciones numéricas.

## 📝 Licencia

MIT - Úsalo como quieras, aprende, modifica, vende.

## 🤝 Contribuciones

PRs bienvenidos. Ideal para:
- Nuevos casos de prueba
- Mejores visualizaciones
- Optimizaciones de hiperparámetros
- Documentación

---

**Nota:** Este proyecto es educativo. Para aplicaciones industriales críticas, usa solvers validados como ANSYS Fluent o OpenFOAM.
