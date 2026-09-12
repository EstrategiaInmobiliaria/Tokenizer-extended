"""
Script de Verificación del Entorno
Ejecuta este script para confirmar que todo está instalado correctamente
"""

import sys

def verificar_entorno():
    print("\n" + "="*60)
    print("VERIFICACIÓN DEL ENTORNO DE GRAFICACIÓN")
    print("="*60 + "\n")
    
    errores = []
    
    # Verificar Python
    print("1. Verificando Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro} detectado")
    else:
        print(f"   ✗ Python {version.major}.{version.minor} (se requiere 3.8+)")
        errores.append("Python version")
    
    # Verificar NumPy
    print("\n2. Verificando NumPy...")
    try:
        import numpy as np
        print(f"   ✓ NumPy {np.__version__} instalado")
        
        # Prueba rápida
        arr = np.array([1, 2, 3, 4, 5])
        resultado = np.mean(arr)
        print(f"   ✓ Cálculo de prueba exitoso: media([1,2,3,4,5]) = {resultado}")
    except ImportError:
        print("   ✗ NumPy no está instalado")
        errores.append("NumPy")
    except Exception as e:
        print(f"   ✗ Error en NumPy: {e}")
        errores.append("NumPy")
    
    # Verificar Matplotlib
    print("\n3. Verificando Matplotlib...")
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        print(f"   ✓ Matplotlib {matplotlib.__version__} instalado")
        
        # Verificar backend
        backend = matplotlib.get_backend()
        print(f"   ✓ Backend activo: {backend}")
        
        # Prueba de gráfico simple
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot([1, 2, 3], [1, 4, 9])
        ax.set_title("Test")
        plt.savefig('test_verificacion.png', dpi=50, bbox_inches='tight')
        plt.close()
        print("   ✓ Generación de gráfico de prueba exitosa: test_verificacion.png")
    except ImportError:
        print("   ✗ Matplotlib no está instalado")
        errores.append("Matplotlib")
    except Exception as e:
        print(f"   ✗ Error en Matplotlib: {e}")
        errores.append("Matplotlib")
    
    # Verificar scripts de ejemplo
    print("\n4. Verificando scripts de ejemplo...")
    import os
    scripts = ['test_plot.py', 'ejemplos_graficos.py', 'ejemplos_avanzados.py']
    for script in scripts:
        if os.path.exists(script):
            print(f"   ✓ {script} disponible")
        else:
            print(f"   ✗ {script} no encontrado")
            errores.append(f"Script {script}")
    
    # Verificar documentación
    print("\n5. Verificando documentación...")
    docs = ['GRAFICOS_README.md', 'INICIO_RAPIDO.md', 'requirements.txt']
    for doc in docs:
        if os.path.exists(doc):
            print(f"   ✓ {doc} disponible")
        else:
            print(f"   ⚠ {doc} no encontrado")
    
    # Resultado final
    print("\n" + "="*60)
    if not errores:
        print("✓ VERIFICACIÓN EXITOSA - ENTORNO LISTO PARA USAR")
        print("="*60)
        print("\nPróximos pasos:")
        print("  1. Ejecuta: python3 test_plot.py")
        print("  2. Ejecuta: python3 ejemplos_graficos.py")
        print("  3. Ejecuta: python3 ejemplos_avanzados.py")
        print("  4. Lee: INICIO_RAPIDO.md")
        return True
    else:
        print("✗ VERIFICACIÓN FALLIDA - PROBLEMAS DETECTADOS")
        print("="*60)
        print(f"\nComponentes con problemas ({len(errores)}):")
        for error in errores:
            print(f"  - {error}")
        print("\nSolución:")
        print("  Ejecuta: pip install --upgrade numpy matplotlib")
        return False

if __name__ == "__main__":
    exito = verificar_entorno()
    sys.exit(0 if exito else 1)
