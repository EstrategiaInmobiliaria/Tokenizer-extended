"""
Script para entrenar todos los modelos del sistema
Ejecutar este script para entrenar los 7 modelos con datos de ejemplo
"""

import sys
from pathlib import Path

# Agregar path del backend
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from models.real_estate_opportunity import RealEstateOpportunityDetector, generate_sample_data as gen_re_data
from models.social_media_optimizer import SocialMediaContentOptimizer, generate_sample_data as gen_sm_data
from models.personal_decision_models import (
    TCOCalculator, TennisOptimizer,
    generate_tco_sample_data, generate_tennis_sample_data
)

def main():
    print("=" * 60)
    print("🚀 ENTRENAMIENTO COMPLETO DEL SISTEMA TENSORFLOW")
    print("=" * 60)
    
    # Crear directorios
    data_path = backend_path / "data"
    models_path = backend_path / "models"
    
    for subdir in ['real_estate', 'social_media', 'personal']:
        (data_path / subdir).mkdir(parents=True, exist_ok=True)
    
    models_path.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("1️⃣  MÓDULO INMOBILIARIO")
    print("=" * 60)
    
    # Real Estate Opportunity Detector
    re_data_path = data_path / "real_estate" / "training_data.csv"
    if not re_data_path.exists():
        print("\n📝 Generando datos de ejemplo para inmobiliario...")
        gen_re_data(re_data_path)
    
    print("\n🏗️  Entrenando Detector de Oportunidades Inmobiliarias...")
    re_detector = RealEstateOpportunityDetector()
    re_detector.train(re_data_path, epochs=150)
    
    # Test
    print("\n🧪 Probando predicción...")
    test_re = {
        'precio_m2': 45000,
        'ubicacion': 'Querétaro',
        'amenidades': 12,
        'velocidad_ventas': 0.85,
        'cap_rate': 7.2
    }
    resultado = re_detector.predict(test_re)
    print(f"   ✅ Probabilidad: {resultado['certeza']}")
    print(f"   ✅ Precio estimado: ${resultado['precio_estimado']:,.0f}")
    
    print("\n" + "=" * 60)
    print("2️⃣  MÓDULO REDES SOCIALES")
    print("=" * 60)
    
    # Social Media Optimizer
    sm_data_path = data_path / "social_media" / "instagram_posts.csv"
    if not sm_data_path.exists():
        print("\n📝 Generando datos de ejemplo para Instagram...")
        gen_sm_data(sm_data_path)
    
    print("\n📱 Entrenando Optimizador de Contenido Social...")
    sm_optimizer = SocialMediaContentOptimizer()
    sm_optimizer.train(sm_data_path, epochs=100)
    
    # Test
    print("\n🧪 Generando calendario semanal...")
    temas = ['Cap Rate', 'Estrategia Inmobiliaria', 'Caso UIA']
    schedule = sm_optimizer.predict_week_schedule(temas)
    print(f"   ✅ Calendario generado para {len(schedule)} días")
    print(f"   ✅ Mejor día: {schedule[0]['dia']} - {schedule[0]['posts'][0]['tipo']}")
    
    print("\n" + "=" * 60)
    print("3️⃣  MÓDULO PERSONAL")
    print("=" * 60)
    
    # TCO Calculator
    tco_data_path = data_path / "personal" / "auto_costs.csv"
    if not tco_data_path.exists():
        print("\n📝 Generando datos de ejemplo TCO...")
        generate_tco_sample_data(tco_data_path)
    
    print("\n🚗 Entrenando Calculadora TCO...")
    tco_calc = TCOCalculator()
    tco_calc.train(tco_data_path, epochs=100)
    
    # Test TCO
    print("\n🧪 Probando comparación Geely vs RAV4...")
    geely = {
        'precio_inicial': 650000, 'gasolina_mensual': 800,
        'seguro_anual': 12000, 'mantenimiento_anual': 8000,
        'depreciacion_anual': 65000, 'km_anuales': 20000,
        'rendimiento_km_l': 25, 'es_electrico': 1
    }
    rav4 = {
        'precio_inicial': 720000, 'gasolina_mensual': 2500,
        'seguro_anual': 15000, 'mantenimiento_anual': 12000,
        'depreciacion_anual': 70000, 'km_anuales': 20000,
        'rendimiento_km_l': 14, 'es_electrico': 0
    }
    comp = tco_calc.compare_vehicles(geely, rav4, 'Geely', 'RAV4')
    print(f"   ✅ {comp['recomendacion']}")
    
    # Tennis Optimizer
    tennis_data_path = data_path / "personal" / "tennis_matches.csv"
    if not tennis_data_path.exists():
        print("\n📝 Generando datos de ejemplo Tennis...")
        generate_tennis_sample_data(tennis_data_path)
    
    print("\n🎾 Entrenando Optimizador de Tenis...")
    tennis_opt = TennisOptimizer()
    tennis_opt.train(tennis_data_path, epochs=80)
    
    # Test Tennis
    print("\n🧪 Probando optimización de tenis...")
    condiciones = {
        'temperatura': 24, 'rival_nivel': 6,
        'dia_semana': 1, 'horas_descanso': 2
    }
    setup = tennis_opt.optimize_setup(condiciones)
    print(f"   ✅ Mejor tensión: {setup['tension_kg']} kg")
    print(f"   ✅ Prob. victoria: {setup['probabilidad_victoria']*100:.1f}%")
    
    print("\n" + "=" * 60)
    print("✅ ENTRENAMIENTO COMPLETO FINALIZADO")
    print("=" * 60)
    print("\n📊 Modelos generados:")
    print("   1. real_estate_opportunity.tflite")
    print("   2. social_content_optimizer.tflite")
    print("   3. tco_calculator.tflite")
    print("   4. tennis_optimizer.tflite")
    print("\n🚀 Sistema listo para producción")
    print("   Ejecuta: cd ../api && npm start")
    

if __name__ == "__main__":
    main()
