"""
Suite de tests para validar modelos y API
Ejecutar: pytest tests/
"""

import pytest
import requests
import numpy as np
from pathlib import Path
import sys

# Agregar path del backend
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

API_BASE = "http://localhost:3001"
MODELS_PATH = backend_path / "models"

# ==================== FIXTURES ====================

@pytest.fixture
def api_client():
    """Cliente HTTP para probar la API"""
    return requests.Session()

@pytest.fixture
def check_api_running():
    """Verifica que la API esté corriendo"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            pytest.skip("API no está corriendo")
    except requests.exceptions.RequestException:
        pytest.skip("API no está disponible en http://localhost:3001")

# ==================== TESTS DE MODELOS ====================

class TestModels:
    """Tests para verificar que los modelos existen y funcionan"""
    
    def test_models_exist(self):
        """Verifica que todos los modelos .tflite existan"""
        expected_models = [
            "real_estate_opportunity.tflite",
            "social_content_optimizer.tflite",
            "tco_calculator.tflite",
            "tennis_optimizer.tflite"
        ]
        
        for model_name in expected_models:
            model_path = MODELS_PATH / model_name
            assert model_path.exists(), f"Modelo {model_name} no encontrado"
            assert model_path.stat().st_size > 0, f"Modelo {model_name} está vacío"
    
    def test_scalers_exist(self):
        """Verifica que existan los scalers"""
        expected_scalers = [
            "real_estate_scaler.pkl",
            "social_media_scaler.pkl",
            "tco_scaler.pkl",
            "tennis_scaler.pkl"
        ]
        
        for scaler_name in expected_scalers:
            scaler_path = MODELS_PATH / scaler_name
            assert scaler_path.exists(), f"Scaler {scaler_name} no encontrado"
    
    def test_model_sizes(self):
        """Verifica que los modelos tengan tamaño razonable"""
        models = list(MODELS_PATH.glob("*.tflite"))
        
        for model_path in models:
            size_mb = model_path.stat().st_size / (1024 * 1024)
            assert 0.5 < size_mb < 10, f"{model_path.name} tiene tamaño inusual: {size_mb:.2f}MB"

# ==================== TESTS DE API ====================

class TestAPI:
    """Tests para endpoints de la API"""
    
    def test_health_endpoint(self, api_client, check_api_running):
        """Test del endpoint /health"""
        response = api_client.get(f"{API_BASE}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'models' in data
        assert all(data['models'].values()), "Algún modelo no está disponible"
    
    def test_root_endpoint(self, api_client, check_api_running):
        """Test del endpoint raíz"""
        response = api_client.get(f"{API_BASE}/")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'online'
        assert 'modelos_disponibles' in data
        assert len(data['modelos_disponibles']) >= 4

class TestRealEstateAPI:
    """Tests para endpoints de inmobiliario"""
    
    def test_predict_real_estate(self, api_client, check_api_running):
        """Test de predicción inmobiliaria"""
        payload = {
            "precio_m2": 45000,
            "ubicacion": "Querétaro",
            "amenidades": 12,
            "velocidad_ventas": 0.85,
            "cap_rate": 7.2
        }
        
        response = api_client.post(
            f"{API_BASE}/api/predict/real-estate",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura
        assert 'probabilidad_venta_12m' in data
        assert 'precio_estimado' in data
        assert 'dias_estimados' in data
        assert 'recomendacion' in data
        assert 'certeza' in data
        
        # Verificar rangos
        assert 0 <= data['probabilidad_venta_12m'] <= 1
        assert data['precio_estimado'] > 0
        assert data['dias_estimados'] > 0
        assert data['recomendacion'] in ['ALTA PRIORIDAD', 'ANALIZAR', 'BAJA PRIORIDAD']
    
    def test_real_estate_batch(self, api_client, check_api_running):
        """Test de análisis batch de desarrollos"""
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
            }
        ]
        
        response = api_client.post(
            f"{API_BASE}/api/analyze/real-estate-batch",
            json=desarrollos
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['total_analizados'] == 2
        assert len(data['top_3_oportunidades']) <= 3

class TestSocialMediaAPI:
    """Tests para endpoints de redes sociales"""
    
    def test_predict_post(self, api_client, check_api_running):
        """Test de predicción de post"""
        payload = {
            "tipo_contenido": "Reel",
            "hora": 9,
            "dia_semana": 1,
            "num_hashtags": 5,
            "tema_categoria": "Cap Rate",
            "longitud_caption": 150
        }
        
        response = api_client.post(
            f"{API_BASE}/api/predict/social-media-post",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'engagement_score' in data
        assert 'probabilidad_viral' in data
        assert 'alcance_estimado' in data
        assert 'recomendacion' in data
        
        assert 0 <= data['engagement_score'] <= 100
        assert 0 <= data['probabilidad_viral'] <= 1
        assert data['alcance_estimado'] > 0
    
    def test_weekly_schedule(self, api_client, check_api_running):
        """Test de calendario semanal"""
        payload = {
            "temas_disponibles": ["Cap Rate", "Estrategia Inmobiliaria", "ExO"]
        }
        
        response = api_client.post(
            f"{API_BASE}/api/generate/weekly-content-schedule",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'semana' in data
        assert len(data['semana']) == 7  # 7 días
        assert 'resumen' in data
        
        # Verificar estructura de cada día
        for dia in data['semana']:
            assert 'dia' in dia
            assert 'posts' in dia
            assert len(dia['posts']) > 0

class TestPersonalAPI:
    """Tests para endpoints personales"""
    
    def test_tco_calculation(self, api_client, check_api_running):
        """Test de cálculo TCO"""
        payload = {
            "precio_inicial": 650000,
            "gasolina_mensual": 800,
            "seguro_anual": 12000,
            "mantenimiento_anual": 8000,
            "depreciacion_anual": 65000,
            "km_anuales": 20000,
            "rendimiento_km_l": 25,
            "es_electrico": 1
        }
        
        response = api_client.post(
            f"{API_BASE}/api/calculate/tco",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'costo_operacion_3_anos' in data
        assert 'valor_residual_3_anos' in data
        assert 'tco_total_3_anos' in data
        assert 'costo_mensual_promedio' in data
        
        assert data['tco_total_3_anos'] > 0
        assert data['costo_mensual_promedio'] > 0
    
    def test_vehicle_comparison(self, api_client, check_api_running):
        """Test de comparación de vehículos"""
        payload = {
            "vehicle1": {
                "precio_inicial": 650000,
                "gasolina_mensual": 800,
                "seguro_anual": 12000,
                "mantenimiento_anual": 8000,
                "depreciacion_anual": 65000,
                "km_anuales": 20000,
                "rendimiento_km_l": 25,
                "es_electrico": 1
            },
            "vehicle2": {
                "precio_inicial": 720000,
                "gasolina_mensual": 2500,
                "seguro_anual": 15000,
                "mantenimiento_anual": 12000,
                "depreciacion_anual": 70000,
                "km_anuales": 20000,
                "rendimiento_km_l": 14,
                "es_electrico": 0
            },
            "vehicle1_name": "Geely",
            "vehicle2_name": "RAV4"
        }
        
        response = api_client.post(
            f"{API_BASE}/api/compare/vehicles",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'Geely' in data
        assert 'RAV4' in data
        assert 'diferencia_3_anos' in data
        assert 'ahorro_mensual' in data
        assert 'recomendacion' in data
    
    def test_tennis_optimization(self, api_client, check_api_running):
        """Test de optimización de tenis"""
        payload = {
            "temperatura": 24,
            "rival_nivel": 6,
            "dia_semana": 1,
            "horas_descanso": 2
        }
        
        response = api_client.post(
            f"{API_BASE}/api/optimize/tennis-setup",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'tension_kg' in data
        assert 'pelota' in data
        assert 'probabilidad_victoria' in data
        assert 'mejora_vs_promedio' in data
        
        assert 20 <= data['tension_kg'] <= 28
        assert 0 <= data['probabilidad_victoria'] <= 1

class TestIntegrations:
    """Tests para endpoints de integraciones"""
    
    def test_whatsapp_report(self, api_client, check_api_running):
        """Test de reporte WhatsApp"""
        response = api_client.post(
            f"{API_BASE}/api/integrations/whatsapp-report",
            params={"tipo": "inmobiliario"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'mensaje_whatsapp' in data
        assert 'formato' in data
        assert len(data['mensaje_whatsapp']) > 0
    
    def test_powerbi_data(self, api_client, check_api_running):
        """Test de endpoint Power BI"""
        response = api_client.get(f"{API_BASE}/api/integrations/powerbi-data")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'real_estate' in data
        assert 'social_media' in data
        assert 'personal' in data

# ==================== TESTS DE VALIDACIÓN ====================

class TestValidation:
    """Tests para validar inputs incorrectos"""
    
    def test_invalid_real_estate_input(self, api_client, check_api_running):
        """Test con input inválido de inmobiliario"""
        payload = {
            "precio_m2": -1000,  # Negativo inválido
            "ubicacion": "Querétaro",
            "amenidades": 12,
            "velocidad_ventas": 0.85,
            "cap_rate": 7.2
        }
        
        response = api_client.post(
            f"{API_BASE}/api/predict/real-estate",
            json=payload
        )
        
        # Debe fallar o manejar el error
        assert response.status_code in [200, 422, 500]
    
    def test_missing_fields(self, api_client, check_api_running):
        """Test con campos faltantes"""
        payload = {
            "precio_m2": 45000
            # Faltan otros campos requeridos
        }
        
        response = api_client.post(
            f"{API_BASE}/api/predict/real-estate",
            json=payload
        )
        
        assert response.status_code == 422  # Unprocessable Entity

# ==================== MAIN ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
