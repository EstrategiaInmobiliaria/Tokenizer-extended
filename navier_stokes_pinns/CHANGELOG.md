# Changelog

Historial de cambios del proyecto Navier-Stokes PINNs.

## [1.0.0] - 2026-09-13

### Añadido
- Implementación completa de Flujo de Poiseuille con DeepXDE
- Implementación de Lid-Driven Cavity Flow
- Notebooks interactivos para Jupyter
  - `01_poiseuille.ipynb` - Flujo de Poiseuille con validación analítica
  - `02_cavity.ipynb` - Lid-Driven Cavity Flow
- Scripts standalone de ejemplo
  - `run_poiseuille.py` - Ejecuta y visualiza Poiseuille
- Módulos reutilizables
  - `src/utils.py` - Utilidades matemáticas y físicas
  - `src/visualization.py` - Funciones de plotting avanzadas
  - `src/solvers/` - Implementaciones de PINNs
- Documentación completa
  - `README.md` - Introducción y guía de uso
  - `docs/INSTALL.md` - Guía de instalación
  - `docs/THEORY.md` - Fundamentos matemáticos
  - `docs/COMPARISON.md` - Comparación con CFD tradicional
- Configuración de proyecto
  - `requirements.txt` - Dependencias Python
  - `.gitignore` - Archivos a ignorar
  - `test_setup.py` - Script de verificación de instalación

### Características
- Soporte para TensorFlow y PyTorch como backends
- Visualizaciones de alta calidad con matplotlib y seaborn
- Cálculo automático de métricas de error
- Comparación con soluciones analíticas donde disponibles
- Ejemplos listos para Google Colab
- Documentación extensa con ecuaciones LaTeX

### Validación
- Error L2 < 1% en flujo de Poiseuille
- Reproducción exitosa de patrones de vórtices en cavity flow
- Todos los módulos testeados y funcionales

## Roadmap Futuro

### [1.1.0] - Planeado
- [ ] Flujo alrededor de cilindro (Von Kármán vortex street)
- [ ] Casos transitorios (dependientes del tiempo)
- [ ] Visualizaciones animadas
- [ ] Comparación cuantitativa con datos de Ghia et al.

### [1.2.0] - Planeado
- [ ] Soporte para geometrías 3D
- [ ] Implementación de casos con fuerzas externas
- [ ] Inverse problems (inferir parámetros)
- [ ] Transfer learning entre diferentes Re

### [2.0.0] - Futuro
- [ ] Integración con NVIDIA Modulus
- [ ] Turbulencia con arquitecturas multi-escala
- [ ] Casos multifísicos (térmico + fluidos)
- [ ] Dashboard interactivo con Plotly

## Contribuciones

Las contribuciones son bienvenidas. Ver `README.md` para detalles.

## Licencia

MIT License - Ver `LICENSE` para más información.
