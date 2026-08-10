#!/usr/bin/env python3
"""
Script de verificación del sistema TensorFlow Intelligence
Ejecutar después de la instalación para validar que todo funciona
"""

import sys
import os
from pathlib import Path
import subprocess

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} (se requiere 3.9+)")
        return False

def check_dependencies():
    """Verificar dependencias instaladas"""
    required = [
        'tensorflow',
        'fastapi',
        'uvicorn',
        'pandas',
        'numpy',
        'sklearn'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print_success(f"{package} instalado")
        except ImportError:
            print_error(f"{package} NO instalado")
            missing.append(package)
    
    return len(missing) == 0

def check_models():
    """Verificar que los modelos existan"""
    base_path = Path(__file__).parent
    models_path = base_path / "backend" / "models"
    
    expected_models = [
        "real_estate_opportunity.tflite",
        "social_content_optimizer.tflite",
        "tco_calculator.tflite",
        "tennis_optimizer.tflite"
    ]
    
    all_exist = True
    for model in expected_models:
        model_path = models_path / model
        if model_path.exists():
            size = model_path.stat().st_size / 1024
            print_success(f"{model} ({size:.1f} KB)")
        else:
            print_error(f"{model} NO encontrado")
            all_exist = False
    
    return all_exist

def check_data_structure():
    """Verificar estructura de directorios"""
    base_path = Path(__file__).parent
    required_dirs = [
        "backend/models",
        "backend/data/real_estate",
        "backend/data/social_media",
        "backend/data/personal",
        "backend/api",
        "workflows",
        "examples"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists():
            print_success(f"{dir_path}/")
        else:
            print_error(f"{dir_path}/ NO existe")
            all_exist = False
    
    return all_exist

def check_api_connection():
    """Intentar conectarse a la API si está corriendo"""
    try:
        import requests
        response = requests.get("http://localhost:3001/health", timeout=2)
        if response.status_code == 200:
            print_success("API respondiendo en http://localhost:3001")
            return True
        else:
            print_warning("API no responde correctamente")
            return False
    except:
        print_warning("API no está corriendo (normal si no la has iniciado)")
        return None

def run_quick_test():
    """Ejecutar test rápido de predicción"""
    try:
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        from models.real_estate_opportunity import RealEstateOpportunityDetector
        
        detector = RealEstateOpportunityDetector()
        test_data = {
            'precio_m2': 45000,
            'ubicacion': 'Querétaro',
            'amenidades': 12,
            'velocidad_ventas': 0.85,
            'cap_rate': 7.2
        }
        
        result = detector.predict(test_data)
        
        if result and 'probabilidad_venta_12m' in result:
            print_success(f"Predicción de prueba: {result['certeza']}")
            return True
        else:
            print_error("Predicción falló")
            return False
    except Exception as e:
        print_error(f"Error en test: {str(e)}")
        return False

def main():
    print_header("VERIFICACIÓN DEL SISTEMA TENSORFLOW INTELLIGENCE")
    
    results = {}
    
    # 1. Python
    print_header("1. VERIFICANDO PYTHON")
    results['python'] = check_python_version()
    
    # 2. Dependencias
    print_header("2. VERIFICANDO DEPENDENCIAS")
    results['dependencies'] = check_dependencies()
    
    # 3. Estructura
    print_header("3. VERIFICANDO ESTRUCTURA")
    results['structure'] = check_data_structure()
    
    # 4. Modelos
    print_header("4. VERIFICANDO MODELOS")
    results['models'] = check_models()
    
    # 5. API
    print_header("5. VERIFICANDO API")
    api_status = check_api_connection()
    results['api'] = api_status if api_status is not None else True
    
    # 6. Test rápido
    if results['models']:
        print_header("6. EJECUTANDO TEST DE PREDICCIÓN")
        results['test'] = run_quick_test()
    else:
        print_warning("Saltando test (modelos no disponibles)")
        results['test'] = False
    
    # Resumen
    print_header("RESUMEN")
    
    passed = sum(1 for v in results.values() if v is True)
    total = len(results)
    
    print(f"\nTests pasados: {passed}/{total}")
    
    if passed == total:
        print_success("\n🎉 Sistema completamente funcional")
        print("\n📋 Próximos pasos:")
        print("   1. Iniciar API: ./start_api.sh")
        print("   2. Ejecutar ejemplos: ./run_examples.sh")
        print("   3. Configurar n8n workflows")
        print("   4. Instalar plugin Obsidian")
        return 0
    else:
        print_error("\n⚠️  Algunos componentes faltan o fallan")
        print("\n🔧 Acciones recomendadas:")
        
        if not results['dependencies']:
            print("   - Instalar dependencias: pip install -r backend/requirements.txt")
        if not results['models']:
            print("   - Entrenar modelos: python backend/scripts/train_all_models.py")
        if not results['test']:
            print("   - Verificar logs en backend/logs/")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
