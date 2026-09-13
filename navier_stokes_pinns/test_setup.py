#!/usr/bin/env python3
"""
Test rápido: Verifica que las dependencias están instaladas correctamente.

Uso:
    python test_setup.py
"""

import sys

def test_imports():
    """Prueba que todos los módulos se pueden importar."""
    
    print("="*60)
    print("VERIFICACIÓN DE DEPENDENCIAS")
    print("="*60 + "\n")
    
    errors = []
    
    # Test 1: Numpy
    try:
        import numpy as np
        print("✓ numpy", np.__version__)
    except ImportError as e:
        errors.append(("numpy", str(e)))
        print("✗ numpy - ERROR")
    
    # Test 2: Matplotlib
    try:
        import matplotlib
        print("✓ matplotlib", matplotlib.__version__)
    except ImportError as e:
        errors.append(("matplotlib", str(e)))
        print("✗ matplotlib - ERROR")
    
    # Test 3: DeepXDE
    try:
        import deepxde as dde
        print("✓ deepxde", dde.__version__)
    except ImportError as e:
        errors.append(("deepxde", str(e)))
        print("✗ deepxde - ERROR")
    
    # Test 4: Backend (TensorFlow o PyTorch)
    backend_found = False
    try:
        import tensorflow as tf
        print("✓ tensorflow", tf.__version__)
        backend_found = True
    except ImportError:
        print("✗ tensorflow - no instalado")
    
    try:
        import torch
        print("✓ pytorch", torch.__version__)
        backend_found = True
    except ImportError:
        print("✗ pytorch - no instalado")
    
    if not backend_found:
        errors.append(("backend", "Necesitas TensorFlow o PyTorch"))
        print("\n⚠️  ADVERTENCIA: Necesitas al menos TensorFlow o PyTorch")
    
    # Test 5: Seaborn
    try:
        import seaborn as sns
        print("✓ seaborn", sns.__version__)
    except ImportError as e:
        errors.append(("seaborn", str(e)))
        print("✗ seaborn - ERROR")
    
    # Test 6: Scipy
    try:
        import scipy
        print("✓ scipy", scipy.__version__)
    except ImportError as e:
        errors.append(("scipy", str(e)))
        print("✗ scipy - ERROR")
    
    print()
    
    # Resumen
    if errors:
        print("="*60)
        print(f"❌ FALLÓ - {len(errors)} error(es) encontrado(s)")
        print("="*60 + "\n")
        
        print("Para instalar dependencias faltantes:")
        print("\n    pip install -r requirements.txt\n")
        
        for package, error in errors:
            print(f"  • {package}: {error}")
        
        return False
    else:
        print("="*60)
        print("✅ ÉXITO - Todas las dependencias están instaladas")
        print("="*60)
        return True


def test_local_modules():
    """Prueba que los módulos locales se pueden importar."""
    
    print("\n" + "="*60)
    print("VERIFICACIÓN DE MÓDULOS LOCALES")
    print("="*60 + "\n")
    
    try:
        from src import utils, visualization
        from src.solvers import poiseuille_solver, cavity_solver
        print("✓ Todos los módulos locales se importaron correctamente")
        return True
    except ImportError as e:
        print(f"✗ Error importando módulos locales: {e}")
        print("\nAsegúrate de ejecutar desde el directorio raíz del proyecto:")
        print("    cd navier_stokes_pinns")
        print("    python test_setup.py")
        return False


def main():
    """Ejecuta todas las pruebas."""
    
    success = True
    
    # Test dependencias
    if not test_imports():
        success = False
    
    # Test módulos locales
    if not test_local_modules():
        success = False
    
    # Resultado final
    print("\n" + "="*60)
    if success:
        print("🎉 TODO LISTO - Puedes empezar a usar los notebooks")
        print("="*60)
        print("\nPróximos pasos:")
        print("  1. jupyter notebook notebooks/")
        print("  2. Abre 01_poiseuille.ipynb")
        print("  3. ¡Ejecuta las celdas!")
    else:
        print("⚠️  CONFIGURACIÓN INCOMPLETA")
        print("="*60)
        print("\nSigue las instrucciones arriba para corregir los errores.")
        sys.exit(1)


if __name__ == "__main__":
    main()
