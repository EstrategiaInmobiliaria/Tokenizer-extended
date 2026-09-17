"""
Ejemplos de uso del Sistema de Inteligencia TensorFlow
Ejecutar después de entrenar los modelos y levantar la API
"""

import requests
import json

API_BASE = "http://localhost:3001"


def example_real_estate():
    """Ejemplo 1: Análisis de Oportunidad Inmobiliaria"""
    print("\n" + "=" * 60)
    print("EJEMPLO 1: ANÁLISIS INMOBILIARIO")
    print("=" * 60)
    
    desarrollos = [
        {
            "precio_m2": 45000,
            "ubicacion": "Querétaro",
            "amenidades": 12,
            "velocidad_ventas": 0.85,
            "cap_rate": 7.2
        },
        {
            "precio_m2": 52000,
            "ubicacion": "CDMX",
            "amenidades": 15,
            "velocidad_ventas": 0.72,
            "cap_rate": 6.8
        },
        {
            "precio_m2": 38000,
            "ubicacion": "Monterrey",
            "amenidades": 10,
            "velocidad_ventas": 0.90,
            "cap_rate": 7.5
        }
    ]
    
    print("\n🔍 Analizando 3 desarrollos inmobiliarios...")
    
    resultados = []
    for i, dev in enumerate(desarrollos, 1):
        response = requests.post(f"{API_BASE}/api/predict/real-estate", json=dev)
        resultado = response.json()
        
        print(f"\n📊 Desarrollo {i} - {dev['ubicacion']}")
        print(f"   Precio m2: ${dev['precio_m2']:,}")
        print(f"   ✨ Probabilidad: {resultado['certeza']}")
        print(f"   💰 Precio estimado: ${resultado['precio_estimado']:,.0f}")
        print(f"   📅 Días estimados: {resultado['dias_estimados']}")
        print(f"   🎯 {resultado['recomendacion']}")
        
        resultados.append(resultado)
    
    # Encontrar la mejor oportunidad
    mejor = max(resultados, key=lambda x: x['probabilidad_venta_12m'])
    print(f"\n✅ MEJOR OPORTUNIDAD: {mejor['recomendacion']} con {mejor['certeza']} de probabilidad")


def example_social_media():
    """Ejemplo 2: Optimización de Contenido Social"""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: CALENDARIO SEMANAL DE CONTENIDO")
    print("=" * 60)
    
    temas = [
        "Cap Rate",
        "Estrategia Inmobiliaria",
        "Caso UIA",
        "ExO",
        "Tenis"
    ]
    
    print(f"\n📱 Generando calendario para {len(temas)} temas...")
    
    response = requests.post(
        f"{API_BASE}/api/generate/weekly-content-schedule",
        json={"temas_disponibles": temas}
    )
    
    resultado = response.json()
    schedule = resultado['semana']
    
    print("\n📅 CALENDARIO RECOMENDADO:\n")
    
    for dia in schedule[:3]:  # Mostrar solo 3 días
        print(f"*{dia['dia']}*")
        for post in dia['posts']:
            print(f"  📱 {post['hora']:02d}:00 - {post['tipo']} sobre '{post['tema']}'")
            print(f"     Engagement: {post['engagement_esperado']:.1f}/100")
            print(f"     Viral: {post['prob_viral']*100:.1f}%")
        print()
    
    print(f"\n✅ {resultado['resumen']['total_posts_recomendados']} posts optimizados para la semana")
    print(f"🎯 Mejor día: {resultado['resumen']['mejor_dia']}")


def example_personal_tco():
    """Ejemplo 3: Comparación TCO de Vehículos"""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: COMPARACIÓN TCO GEELY vs RAV4")
    print("=" * 60)
    
    geely = {
        "precio_inicial": 650000,
        "gasolina_mensual": 800,
        "seguro_anual": 12000,
        "mantenimiento_anual": 8000,
        "depreciacion_anual": 65000,
        "km_anuales": 20000,
        "rendimiento_km_l": 25,
        "es_electrico": 1
    }
    
    rav4 = {
        "precio_inicial": 720000,
        "gasolina_mensual": 2500,
        "seguro_anual": 15000,
        "mantenimiento_anual": 12000,
        "depreciacion_anual": 70000,
        "km_anuales": 20000,
        "rendimiento_km_l": 14,
        "es_electrico": 0
    }
    
    print("\n🚗 Comparando costos a 3 años...")
    
    response = requests.post(
        f"{API_BASE}/api/compare/vehicles",
        json={
            "vehicle1": geely,
            "vehicle2": rav4,
            "vehicle1_name": "Geely EX5 EM-i",
            "vehicle2_name": "Toyota RAV4"
        }
    )
    
    resultado = response.json()
    
    print(f"\n💰 GEELY EX5 EM-i:")
    print(f"   TCO 3 años: ${resultado['Geely EX5 EM-i']['tco_total_3_anos']:,.0f}")
    print(f"   Costo mensual: ${resultado['Geely EX5 EM-i']['costo_mensual_promedio']:,.0f}")
    
    print(f"\n💰 TOYOTA RAV4:")
    print(f"   TCO 3 años: ${resultado['Toyota RAV4']['tco_total_3_anos']:,.0f}")
    print(f"   Costo mensual: ${resultado['Toyota RAV4']['costo_mensual_promedio']:,.0f}")
    
    print(f"\n✅ {resultado['recomendacion']}")
    print(f"💵 Ahorro mensual: ${resultado['ahorro_mensual']:,.0f}")


def example_tennis():
    """Ejemplo 4: Optimización de Setup de Tenis"""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: OPTIMIZACIÓN DE TENIS")
    print("=" * 60)
    
    condiciones = {
        "temperatura": 24,
        "rival_nivel": 6,
        "dia_semana": 1,  # Martes
        "horas_descanso": 2
    }
    
    print("\n🎾 Optimizando setup para partido del martes...")
    print(f"   Temperatura: {condiciones['temperatura']}°C")
    print(f"   Nivel rival: {condiciones['rival_nivel']}/10")
    print(f"   Descanso: {condiciones['horas_descanso']} días")
    
    response = requests.post(
        f"{API_BASE}/api/optimize/tennis-setup",
        json=condiciones
    )
    
    resultado = response.json()
    
    print(f"\n✨ CONFIGURACIÓN ÓPTIMA:")
    print(f"   Tensión cordaje: {resultado['tension_kg']} kg")
    print(f"   Pelota: {resultado['pelota']}")
    print(f"   📈 Probabilidad victoria: {resultado['probabilidad_victoria']*100:.1f}%")
    print(f"   🎯 Mejora vs promedio: +{resultado['mejora_vs_promedio']:.1f}%")


def example_whatsapp_integration():
    """Ejemplo 5: Reporte para WhatsApp"""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: REPORTE WHATSAPP")
    print("=" * 60)
    
    print("\n📱 Generando reporte para WhatsApp...")
    
    response = requests.post(
        f"{API_BASE}/api/integrations/whatsapp-report",
        params={"tipo": "inmobiliario"}
    )
    
    resultado = response.json()
    
    print("\n" + resultado['mensaje_whatsapp'])
    print("\n✅ Listo para enviar por WhatsApp (usar n8n workflow)")


def example_powerbi():
    """Ejemplo 6: Datos para Power BI"""
    print("\n" + "=" * 60)
    print("EJEMPLO 6: DATOS PARA POWER BI")
    print("=" * 60)
    
    print("\n📊 Obteniendo datos para dashboard...")
    
    response = requests.get(f"{API_BASE}/api/integrations/powerbi-data")
    datos = response.json()
    
    print("\n📈 MÉTRICAS GENERALES:")
    print(f"\n   Inmobiliario:")
    print(f"   - Desarrollos analizados: {datos['real_estate']['desarrollos_analizados']}")
    print(f"   - Alta prioridad: {datos['real_estate']['oportunidades_alta_prioridad']}")
    print(f"   - Precisión: {datos['real_estate']['tasa_exito_predicciones']*100:.0f}%")
    
    print(f"\n   Redes Sociales:")
    print(f"   - Posts analizados: {datos['social_media']['posts_analizados']}")
    print(f"   - Engagement promedio: {datos['social_media']['engagement_promedio']}")
    print(f"   - Posts virales: {datos['social_media']['posts_virales_predichos']}")
    
    print(f"\n   Personal:")
    print(f"   - Decisiones optimizadas: {datos['personal']['decisiones_optimizadas']}")
    print(f"   - Ahorro total: ${datos['personal']['ahorro_total_estimado']:,}")
    
    print("\n✅ Conecta Power BI a: http://localhost:3001/api/integrations/powerbi-data")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 EJEMPLOS DE USO - SISTEMA TENSORFLOW")
    print("=" * 60)
    print("\n⚠️  Asegúrate de que la API esté corriendo en http://localhost:3001")
    print("    Ejecutar: cd backend/api && python api.py")
    
    input("\nPresiona ENTER para continuar...")
    
    try:
        # Verificar que la API esté activa
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API conectada correctamente\n")
        else:
            print("❌ API no responde correctamente")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ No se puede conectar a la API. Asegúrate de que esté corriendo.")
        exit(1)
    
    # Ejecutar todos los ejemplos
    example_real_estate()
    input("\nPresiona ENTER para continuar al siguiente ejemplo...")
    
    example_social_media()
    input("\nPresiona ENTER para continuar al siguiente ejemplo...")
    
    example_personal_tco()
    input("\nPresiona ENTER para continuar al siguiente ejemplo...")
    
    example_tennis()
    input("\nPresiona ENTER para continuar al siguiente ejemplo...")
    
    example_whatsapp_integration()
    input("\nPresiona ENTER para continuar al siguiente ejemplo...")
    
    example_powerbi()
    
    print("\n" + "=" * 60)
    print("✅ EJEMPLOS COMPLETADOS")
    print("=" * 60)
    print("\n📚 Próximos pasos:")
    print("   1. Configurar workflows de n8n (ver /workflows)")
    print("   2. Conectar Power BI al endpoint de datos")
    print("   3. Configurar plugin de Obsidian")
    print("   4. Entrenar modelos con tus datos reales")
    print("\n🎯 Documentación completa: tensorflow-system/README.md\n")
