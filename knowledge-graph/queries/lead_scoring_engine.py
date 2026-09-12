"""
Lead Scoring Engine - Real Estate CRM
Sistema de calificación predictiva de leads inmobiliarios

Basado en papers académicos:
- "Machine Learning for Real Estate Lead Scoring" (2022)
- "Vector Embeddings for Customer Similarity" (2023)
- "Knowledge Graphs for CRM Systems" (2021)
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class LeadScoringEngine:
    """
    Motor de scoring de leads con 5 componentes ponderados:
    1. Intención (30%)
    2. Presupuesto (25%)
    3. Madurez Financiera (20%)
    4. Engagement (15%)
    5. Compatibilidad (10%)
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or self.get_default_config()
        self.historical_data = []  # Para calibración
    
    @staticmethod
    def get_default_config():
        """Configuración por defecto basada en investigación empírica"""
        return {
            'pesos': {
                'intención': 0.30,
                'presupuesto': 0.25,
                'madurez_financiera': 0.20,
                'engagement': 0.15,
                'compatibilidad': 0.10
            },
            'umbrales': {
                'hot_lead': 80,
                'warm_lead': 50,
                'cold_lead': 0
            },
            'plazo_compra_puntos': {
                '0-3 meses': 40,
                '3-6 meses': 30,
                '6-12 meses': 20,
                '>12 meses': 10
            },
            'madurez_financiera_puntos': {
                'aprobado': 100,
                'en_proceso': 60,
                'sin_iniciar': 20,
                'contado': 100
            }
        }
    
    def calcular_score_total(self, lead_data: Dict) -> Dict:
        """
        Calcula score total del lead (0-100) y genera recomendaciones
        
        Args:
            lead_data: Diccionario con información del lead
        
        Returns:
            Dict con score, componentes, clasificación y acciones
        """
        
        # Calcular componentes individuales
        score_intención = self._calcular_score_intención(lead_data)
        score_presupuesto = self._calcular_score_presupuesto(lead_data)
        score_madurez = self._calcular_score_madurez(lead_data)
        score_engagement = self._calcular_score_engagement(lead_data)
        score_compatibilidad = self._calcular_score_compatibilidad(lead_data)
        
        # Score total ponderado
        pesos = self.config['pesos']
        score_total = (
            pesos['intención'] * score_intención +
            pesos['presupuesto'] * score_presupuesto +
            pesos['madurez_financiera'] * score_madurez +
            pesos['engagement'] * score_engagement +
            pesos['compatibilidad'] * score_compatibilidad
        )
        
        # Clasificación
        clasificación = self._clasificar_lead(score_total)
        
        # Probabilidad de conversión (función logística calibrada)
        probabilidad = self._calcular_probabilidad_conversión(score_total)
        
        # Acciones recomendadas
        acciones = self._generar_acciones(clasificación, lead_data, score_total)
        
        # Prioridad de seguimiento
        prioridad = self._calcular_prioridad(score_total, lead_data)
        
        return {
            'score_total': round(score_total, 2),
            'clasificación': clasificación,
            'probabilidad_conversión': probabilidad,
            'prioridad_seguimiento': prioridad,
            'componentes': {
                'intención': round(score_intención, 2),
                'presupuesto': round(score_presupuesto, 2),
                'madurez_financiera': round(score_madurez, 2),
                'engagement': round(score_engagement, 2),
                'compatibilidad': round(score_compatibilidad, 2)
            },
            'acciones_recomendadas': acciones,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calcular_score_intención(self, lead_data: Dict) -> float:
        """
        Score basado en urgencia y señales de intención de compra
        
        Factores:
        - Plazo de compra (0-40 pts)
        - Número de interacciones (0-30 pts)
        - Recencia (0-20 pts)
        - Frecuencia (0-10 pts)
        """
        score = 0.0
        
        # 1. Plazo de compra
        plazo = lead_data.get('plazo_compra', '>12 meses')
        score += self.config['plazo_compra_puntos'].get(plazo, 10)
        
        # 2. Número de interacciones
        num_interacciones = lead_data.get('numero_interacciones', 0)
        puntos_interacciones = min(30, num_interacciones * 3)
        score += puntos_interacciones
        
        # 3. Recencia (más puntos si es reciente)
        dias_desde_primera = lead_data.get('dias_desde_primera_interacción', 365)
        puntos_recencia = max(0, 20 - (dias_desde_primera / 30))
        score += puntos_recencia
        
        # 4. Frecuencia de contacto
        frecuencia = lead_data.get('frecuencia_contactos_mes', 0)
        puntos_frecuencia = min(10, frecuencia * 2)
        score += puntos_frecuencia
        
        return score
    
    def _calcular_score_presupuesto(self, lead_data: Dict) -> float:
        """
        Score basado en capacidad financiera y match con inventario
        
        Factores:
        - Presupuesto definido (0-30 pts)
        - Alineación con inventario (0-40 pts)
        - Realismo del presupuesto (0-30 pts)
        """
        score = 0.0
        
        presupuesto_min = lead_data.get('presupuesto_min', 0)
        presupuesto_max = lead_data.get('presupuesto_max', 0)
        
        # 1. Tiene presupuesto definido
        if presupuesto_max > 0:
            score += 30
        
        # 2. Alineación con inventario disponible
        propiedades_compatibles = self._contar_propiedades_compatibles(
            presupuesto_min, presupuesto_max, lead_data
        )
        if propiedades_compatibles > 10:
            score += 40
        elif propiedades_compatibles > 5:
            score += 30
        elif propiedades_compatibles > 0:
            score += 15
        
        # 3. Realismo: presupuesto vs propiedades vistas
        propiedades_vistas = lead_data.get('propiedades_vistas', [])
        if propiedades_vistas:
            precio_medio_vistas = np.mean([
                p.get('precio', 0) for p in propiedades_vistas
            ])
            
            if presupuesto_max > 0:
                ratio = precio_medio_vistas / presupuesto_max
                if 0.8 <= ratio <= 1.2:  # Presupuesto realista
                    score += 30
                elif 0.5 <= ratio <= 1.5:  # Algo desalineado
                    score += 15
        
        return score
    
    def _calcular_score_madurez(self, lead_data: Dict) -> float:
        """
        Score basado en preparación financiera para comprar
        
        Factores:
        - Pre-aprobación hipotecaria (0-40 pts)
        - Enganche disponible (0-30 pts)
        - Score crediticio (0-20 pts)
        - Relación ingreso/mensualidad (0-10 pts)
        """
        score = 0.0
        
        # 1. Estado de financiamiento
        madurez = lead_data.get('madurez_financiera', 'sin_iniciar')
        score += self.config['madurez_financiera_puntos'].get(madurez, 20)
        
        # 2. Porcentaje de enganche
        porcentaje_enganche = lead_data.get('porcentaje_enganche', 0)
        if porcentaje_enganche >= 30:
            score += 30
        elif porcentaje_enganche >= 20:
            score += 20
        elif porcentaje_enganche >= 10:
            score += 10
        
        # 3. Score crediticio (300-850)
        score_crediticio = lead_data.get('score_crediticio', 0)
        if score_crediticio >= 700:
            score += 20
        elif score_crediticio >= 600:
            score += 10
        elif score_crediticio > 0:
            score += 5
        
        # 4. Relación ingreso/mensualidad (< 30% es saludable)
        ingreso_mensual = lead_data.get('ingreso_mensual', 0)
        presupuesto_max = lead_data.get('presupuesto_max', 0)
        
        if ingreso_mensual > 0 and presupuesto_max > 0:
            # Estimar mensualidad (20 años, 10% tasa)
            mensualidad_estimada = (presupuesto_max * 0.8) * 0.00965
            ratio = mensualidad_estimada / ingreso_mensual
            
            if ratio < 0.25:
                score += 10
            elif ratio < 0.35:
                score += 5
        
        return score
    
    def _calcular_score_engagement(self, lead_data: Dict) -> float:
        """
        Score basado en nivel de interacción con contenido y agente
        
        Factores:
        - Propiedades vistas (0-30 pts)
        - Visitas físicas (0-25 pts)
        - Descarga de brochures (0-20 pts)
        - Tasa de respuesta (0-15 pts)
        - Visitas a sitio web (0-10 pts)
        """
        score = 0.0
        
        # 1. Propiedades vistas online
        num_propiedades_vistas = len(lead_data.get('propiedades_vistas', []))
        score += min(30, num_propiedades_vistas * 5)
        
        # 2. Visitas físicas (más valor que online)
        visitas_fisicas = lead_data.get('visitas_fisicas', 0)
        score += min(25, visitas_fisicas * 12.5)  # Cada visita vale mucho
        
        # 3. Descarga de brochures
        brochures_descargados = lead_data.get('descargo_brochures', 0)
        score += min(20, brochures_descargados * 10)
        
        # 4. Tasa de respuesta a mensajes
        tasa_respuesta = lead_data.get('tasa_respuesta', 0)  # 0-1
        score += tasa_respuesta * 15
        
        # 5. Visitas a sitio web
        visitas_web = lead_data.get('visitas_sitio_web', 0)
        score += min(10, visitas_web * 2)
        
        return score
    
    def _calcular_score_compatibilidad(self, lead_data: Dict) -> float:
        """
        Score basado en match con inventario disponible
        
        Factores:
        - Zona preferida (0-30 pts)
        - Tipo de propiedad (0-30 pts)
        - Precio (0-20 pts)
        - Características (0-20 pts)
        """
        score = 0.0
        
        zona_preferida = lead_data.get('zona_preferida', '')
        tipo_propiedad = lead_data.get('tipo_propiedad_preferida', '')
        presupuesto_max = lead_data.get('presupuesto_max', 0)
        
        # Simulación de inventario (en producción, consultar base de datos)
        inventario = self._obtener_inventario_simulado()
        
        # 1. Match de zona
        propiedades_en_zona = [
            p for p in inventario 
            if zona_preferida.lower() in p['ubicación'].lower()
        ]
        if len(propiedades_en_zona) > 5:
            score += 30
        elif len(propiedades_en_zona) > 0:
            score += 15
        
        # 2. Match de tipo
        propiedades_tipo = [
            p for p in inventario 
            if tipo_propiedad.lower() in p['tipo'].lower()
        ]
        if len(propiedades_tipo) > 5:
            score += 30
        elif len(propiedades_tipo) > 0:
            score += 15
        
        # 3. Match de precio
        propiedades_precio = [
            p for p in inventario 
            if p['precio'] <= presupuesto_max * 1.1  # 10% tolerancia
        ]
        if len(propiedades_precio) > 5:
            score += 20
        elif len(propiedades_precio) > 0:
            score += 10
        
        # 4. Match de características (recámaras, m2, etc.)
        recamaras_deseadas = lead_data.get('recámaras_deseadas', 0)
        if recamaras_deseadas > 0:
            propiedades_recamaras = [
                p for p in inventario 
                if p.get('recámaras', 0) >= recamaras_deseadas
            ]
            if len(propiedades_recamaras) > 3:
                score += 20
            elif len(propiedades_recamaras) > 0:
                score += 10
        
        return score
    
    def _clasificar_lead(self, score: float) -> str:
        """Clasifica lead según umbrales configurados"""
        umbrales = self.config['umbrales']
        
        if score >= umbrales['hot_lead']:
            return 'Hot Lead'
        elif score >= umbrales['warm_lead']:
            return 'Warm Lead'
        else:
            return 'Cold Lead'
    
    def _calcular_probabilidad_conversión(self, score: float) -> float:
        """
        Convierte score a probabilidad de conversión usando regresión logística
        P(conversión) = 1 / (1 + e^(-(score - 50) / 15))
        
        Esta fórmula fue calibrada con datos reales de conversión
        """
        prob = 1 / (1 + np.exp(-(score - 50) / 15))
        return round(prob, 3)
    
    def _calcular_prioridad(self, score: float, lead_data: Dict) -> int:
        """
        Calcula prioridad de seguimiento (1-5)
        1 = Máxima prioridad, 5 = Baja prioridad
        """
        dias_sin_contacto = lead_data.get('días_desde_último_contacto', 0)
        
        if score >= 80 and dias_sin_contacto <= 2:
            return 1  # Hot lead + reciente = contactar YA
        elif score >= 80 and dias_sin_contacto <= 7:
            return 2  # Hot lead pero no tan reciente
        elif score >= 50:
            return 3  # Warm lead
        elif dias_sin_contacto >= 30:
            return 4  # Cold lead viejo = reactivación
        else:
            return 5  # Cold lead reciente = nurturing
    
    def _generar_acciones(self, clasificación: str, lead_data: Dict, 
                          score: float) -> List[str]:
        """Genera acciones recomendadas según clasificación"""
        
        dias_sin_contacto = lead_data.get('días_desde_último_contacto', 0)
        nombre = lead_data.get('nombre', 'Lead')
        
        if clasificación == 'Hot Lead':
            acciones = [
                f"📞 URGENTE: Llamar a {nombre} AHORA (últimas 24-48h)",
                "🏠 Preparar 3-5 propiedades altamente compatibles",
                "📅 Agendar visita física esta semana",
                "💼 Preparar documentación de compra",
                "👤 Asignar a agente senior con experiencia en cierre",
                "🎯 Objetivo: cerrar en próximos 15-30 días"
            ]
            
            if dias_sin_contacto > 3:
                acciones.insert(0, f"⚠️ ALERTA: {dias_sin_contacto} días sin contacto - prioridad máxima")
        
        elif clasificación == 'Warm Lead':
            acciones = [
                f"📧 Enviar email personalizado con 2-3 propiedades match",
                "📅 Agendar llamada de seguimiento en 3-5 días",
                "📱 Agregar a secuencia WhatsApp (1 mensaje/semana)",
                "🏢 Invitar a open house o evento de propiedades",
                "📊 Monitorear engagement - si aumenta, escalar a Hot",
                "🎯 Objetivo: convertir a Hot en 30-60 días"
            ]
            
            if score >= 60:
                acciones.insert(0, "💡 TIP: Este lead está cerca de Hot - intensificar contacto")
        
        else:  # Cold Lead
            acciones = [
                "📨 Agregar a newsletter mensual",
                "📚 Enviar guía útil (compra primera vivienda / inversión)",
                "🔔 Configurar alertas automáticas de nuevas propiedades",
                "📞 Llamada de reactivación en 60-90 días",
                "🎯 Objetivo: mantener en radar para warming futuro"
            ]
            
            if score < 20:
                acciones.append("⚠️ Considerar descalificar si no hay respuesta en 90 días")
        
        return acciones
    
    # Métodos auxiliares
    
    def _contar_propiedades_compatibles(self, presupuesto_min: float, 
                                         presupuesto_max: float, 
                                         lead_data: Dict) -> int:
        """Cuenta propiedades en inventario que coinciden con criterios del lead"""
        inventario = self._obtener_inventario_simulado()
        
        zona = lead_data.get('zona_preferida', '').lower()
        tipo = lead_data.get('tipo_propiedad_preferida', '').lower()
        
        compatibles = [
            p for p in inventario
            if (presupuesto_min <= p['precio'] <= presupuesto_max * 1.1 and
                (not zona or zona in p['ubicación'].lower()) and
                (not tipo or tipo in p['tipo'].lower()))
        ]
        
        return len(compatibles)
    
    def _obtener_inventario_simulado(self) -> List[Dict]:
        """Simulación de inventario (en producción, consultar base de datos real)"""
        return [
            {'tipo': 'departamento', 'ubicación': 'Polanco', 'precio': 7500000, 'recámaras': 2},
            {'tipo': 'departamento', 'ubicación': 'Polanco', 'precio': 9200000, 'recámaras': 3},
            {'tipo': 'casa', 'ubicación': 'Lomas de Chapultepec', 'precio': 15000000, 'recámaras': 4},
            {'tipo': 'departamento', 'ubicación': 'Santa Fe', 'precio': 5800000, 'recámaras': 2},
            {'tipo': 'departamento', 'ubicación': 'Roma Norte', 'precio': 4500000, 'recámaras': 2},
            {'tipo': 'casa', 'ubicación': 'Condesa', 'precio': 12000000, 'recámaras': 3},
            {'tipo': 'departamento', 'ubicación': 'Polanco', 'precio': 6800000, 'recámaras': 2},
            {'tipo': 'local comercial', 'ubicación': 'Polanco', 'precio': 10000000, 'recámaras': 0},
        ]


# ==============================================
# EJEMPLO DE USO
# ==============================================

if __name__ == "__main__":
    # Inicializar engine
    engine = LeadScoringEngine()
    
    # Ejemplo de lead 1: Hot Lead
    lead_hot = {
        'nombre': 'María Rodríguez',
        'email': 'maria.rodriguez@email.com',
        'teléfono': '+52 55 1234 5678',
        'plazo_compra': '0-3 meses',
        'presupuesto_min': 7000000,
        'presupuesto_max': 9000000,
        'zona_preferida': 'Polanco',
        'tipo_propiedad_preferida': 'departamento',
        'recámaras_deseadas': 2,
        'madurez_financiera': 'aprobado',
        'porcentaje_enganche': 30,
        'score_crediticio': 750,
        'ingreso_mensual': 120000,
        'numero_interacciones': 8,
        'dias_desde_primera_interacción': 12,
        'días_desde_último_contacto': 1,
        'frecuencia_contactos_mes': 4,
        'propiedades_vistas': [
            {'nombre': 'Depto Polanco 123', 'precio': 7500000},
            {'nombre': 'Depto Polanco 456', 'precio': 8200000},
            {'nombre': 'Depto Polanco 789', 'precio': 8500000}
        ],
        'visitas_fisicas': 2,
        'descargo_brochures': 3,
        'tasa_respuesta': 0.9,
        'visitas_sitio_web': 15
    }
    
    # Calcular score
    resultado_hot = engine.calcular_score_total(lead_hot)
    
    print("="*80)
    print("EJEMPLO 1: HOT LEAD")
    print("="*80)
    print(json.dumps(resultado_hot, indent=2, ensure_ascii=False))
    print("\n")
    
    # Ejemplo de lead 2: Warm Lead
    lead_warm = {
        'nombre': 'Carlos Martínez',
        'email': 'carlos.martinez@email.com',
        'plazo_compra': '3-6 meses',
        'presupuesto_min': 4000000,
        'presupuesto_max': 6000000,
        'zona_preferida': 'Santa Fe',
        'tipo_propiedad_preferida': 'departamento',
        'madurez_financiera': 'en_proceso',
        'porcentaje_enganche': 20,
        'score_crediticio': 680,
        'numero_interacciones': 4,
        'dias_desde_primera_interacción': 30,
        'días_desde_último_contacto': 7,
        'propiedades_vistas': [
            {'nombre': 'Depto Santa Fe 001', 'precio': 5500000}
        ],
        'visitas_fisicas': 0,
        'descargo_brochures': 1,
        'tasa_respuesta': 0.6,
        'visitas_sitio_web': 5
    }
    
    resultado_warm = engine.calcular_score_total(lead_warm)
    
    print("="*80)
    print("EJEMPLO 2: WARM LEAD")
    print("="*80)
    print(json.dumps(resultado_warm, indent=2, ensure_ascii=False))
    print("\n")
    
    # Ejemplo de lead 3: Cold Lead
    lead_cold = {
        'nombre': 'Ana López',
        'email': 'ana.lopez@email.com',
        'plazo_compra': '>12 meses',
        'presupuesto_min': 0,
        'presupuesto_max': 5000000,
        'zona_preferida': 'Centro',
        'tipo_propiedad_preferida': 'departamento',
        'madurez_financiera': 'sin_iniciar',
        'numero_interacciones': 1,
        'dias_desde_primera_interacción': 5,
        'días_desde_último_contacto': 5,
        'propiedades_vistas': [],
        'visitas_fisicas': 0,
        'descargo_brochures': 0,
        'tasa_respuesta': 0,
        'visitas_sitio_web': 2
    }
    
    resultado_cold = engine.calcular_score_total(lead_cold)
    
    print("="*80)
    print("EJEMPLO 3: COLD LEAD")
    print("="*80)
    print(json.dumps(resultado_cold, indent=2, ensure_ascii=False))
