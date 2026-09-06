#!/usr/bin/env python3
"""
Meta Business Agent Skills Manager - INMOBILIARIA
Manage skills for real estate lead capture and qualification
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """Represents a Meta Business Agent skill"""
    title: str
    description: str
    skill: str
    skill_id: Optional[str] = None

    def validate(self):
        """Validate skill parameters according to Meta's limits"""
        if len(self.title) > 64:
            raise ValueError(f"Title too long: {len(self.title)} chars (max 64)")
        
        if not self.title.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Title must contain only lowercase letters, numbers, and hyphens")
        
        if self.title != self.title.lower():
            raise ValueError("Title must be lowercase")
        
        if len(self.description) > 1024:
            raise ValueError(f"Description too long: {len(self.description)} chars (max 1024)")
        
        if len(self.skill) > 20000:
            raise ValueError(f"Skill content too long: {len(self.skill)} chars (max 20000)")

    def to_api_dict(self) -> Dict[str, str]:
        """Convert to API request format"""
        return {
            "title": self.title,
            "description": self.description,
            "skill": self.skill
        }


class SkillsManager:
    """Manages Meta Business Agent skills via API"""
    
    def __init__(self, phone_number_id: str, access_token: str):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = f"https://api.facebook.com/{phone_number_id}/agent_config/skills"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-API-Version": "2.0.0"
        }

    def create_skill(self, skill: Skill) -> Dict[str, Any]:
        """Create a new skill"""
        skill.validate()
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=skill.to_api_dict(),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"✓ Created skill '{skill.title}': {result.get('id')}")
            return {"success": True, "data": result}
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error creating skill '{skill.title}': {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            return {"success": False, "error": str(e)}

    def list_skills(self) -> Dict[str, Any]:
        """List all skills"""
        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            skills = result.get('data', [])
            logger.info(f"✓ Retrieved {len(skills)} skills")
            return {"success": True, "data": skills}
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error listing skills: {e}")
            return {"success": False, "error": str(e)}

    def bulk_create_skills(self, skills: List[Skill]) -> Dict[str, Any]:
        """Create multiple skills"""
        results = {"created": [], "failed": []}
        
        for skill in skills:
            result = self.create_skill(skill)
            if result["success"]:
                results["created"].append(skill.title)
            else:
                results["failed"].append({"skill": skill.title, "error": result.get("error")})
        
        return results


# Predefined skills for INMOBILIARIA (Real Estate Lead Capture & Qualification)
INMOBILIARIA_SKILLS = [
    Skill(
        title="greeting-inmobiliaria",
        description="Apply when customer first messages about properties, real estate, or housing",
        skill="""Cuando el cliente escribe por primera vez:
1. Saluda: "¡Hola! Soy tu asesor inmobiliario digital de [Tu Marca]. 🏡"
2. Pregunta clave para calificar: "¿Buscas para vivir, invertir o rentar?"
3. Pide zona: "¿En qué zona te interesa? Ej: Metepec, Lerma, CDMX"
4. Tono: Cercano, profesional, sin sonar a robot. Max 3 líneas.

Ejemplo:
"¡Hola! Soy tu asesor inmobiliario digital de Estrategia Inmobiliaria. 🏡 ¿Buscas para vivir, invertir o rentar? ¿En qué zona te interesa?"

Mantén el tono conversacional y amigable. NO uses lenguaje muy formal o corporativo."""
    ),
    
    Skill(
        title="calificacion-lead",
        description="Use to qualify lead before sending inventory. Collect: budget, property type, timeline, payment method",
        skill="""Para calificar, SIEMPRE obtén en orden:

1. Presupuesto aproximado: "¿Cuál es tu presupuesto estimado?"
   - Si dice "no sé", sugiere rangos: "$2-3M, $3-5M, $5M+"
   
2. Tipo de propiedad: casa, depto, terreno, local comercial
   - Pregunta: "¿Qué tipo de propiedad buscas? Casa, departamento, terreno..."

3. Timeline: "¿Para cuándo la necesitas? ¿Urgente, 3 meses, 6 meses?"
   - Esto indica qué tan caliente está el lead

4. Forma de pago: contado, crédito INFONAVIT, FOVISSSTE, bancario, recursos propios
   - Pregunta: "¿Cómo planeas adquirirla? ¿Crédito o recursos propios?"

REGLA CRÍTICA:
NO mandes propiedades hasta tener al menos:
- Presupuesto (o rango)
- Zona de interés
- Tipo de propiedad

Una vez tengas esta info, di:
"Perfecto, con esta información puedo mostrarte las mejores opciones que tenemos en [zona]. Dame un momento..."

Guarda internamente toda esta información como lead calificado para el asesor."""
    ),
    
    Skill(
        title="estrategia-marketing-propiedad",
        description="When owner wants to sell their property or asks how you market properties",
        skill="""Cuando un propietario pregunta cómo vendes su propiedad:

1. Explica tu método en 3 pasos:
   a) Marketing Digital en Meta + WhatsApp: "Alcance de 50,000 personas en tu zona en 7 días"
   b) Sesión profesional de fotos/video + tour virtual: "Presentamos tu propiedad como se merece"
   c) Filtro de compradores calificados: "Solo contactan personas con presupuesto real, no curiosos"

2. Pregunta clave:
   "¿Qué propiedad quieres vender y en qué zona está?"

3. Ofrece valor inmediato:
   "¿Agendamos una valoración gratuita esta semana? Te doy el precio real de mercado en 48 horas."

4. Si pregunta por comisión, di:
   "Nuestra comisión es competitiva y la hablamos en la valoración. Lo importante es que vendas al mejor precio y rápido."

Tono: Profesional pero accesible. Transmite confianza y experiencia.
NO des porcentajes de comisión por WhatsApp.
NO prometas precios sin ver la propiedad."""
    ),
    
    Skill(
        title="agendar-cita-visita",
        description="Use when lead is qualified and wants to see a property. Schedule appointment with human agent",
        skill="""Cuando el lead quiere visitar una propiedad:

1. Confirma disponibilidad:
   "Perfecto, tengo disponibilidad esta semana:"
   - Martes y Jueves: 11am o 4pm
   - Sábados: 10am, 12pm, o 3pm
   "¿Cuál te viene mejor?"

2. Pide datos para confirmar:
   - Nombre completo
   - Confirma número de WhatsApp
   - Pregunta: "¿Vendrás solo/a o con alguien más?"

3. Confirma la cita:
   "Listo, te agendo [día] a las [hora]. Te enviaré:"
   - Ubicación exacta 1 hora antes
   - Ficha técnica de la propiedad
   - Recordatorio el día anterior
   "¿Te parece bien?"

4. Recordatorio importante:
   "Si por algún motivo no puedes, avísame con tiempo para reagendar. ¿De acuerdo?"

DESPUÉS DE AGENDAR:
Marca internamente como HOT LEAD y notifica al asesor inmediatamente.

Si el lead no puede en esos horarios, pregunta:
"¿Qué día y hora te viene mejor? Veo si puedo coordinar una cita especial."""
    ),
    
    Skill(
        title="human-handoff-asesor",
        description="When to escalate to human closer. Critical buying signals or qualified hot leads",
        skill="""Escala INMEDIATAMENTE a asesor humano cuando detectes:

🔥 SEÑALES DE COMPRA CALIENTE:
1. "¿Cuánto es lo menos?" / "¿Acepta ofertas?"
2. "Ya tengo el enganche" / "Ya tengo pre-aprobado el crédito"
3. "Quiero ver varias propiedades este fin de semana"
4. "Necesito mudarme urgente" / "Se vence mi contrato"
5. "¿Puedo apartar?" / "¿Cómo funciona el proceso de compra?"

🎯 LEAD CALIFICADO + URGENTE:
- Lead con presupuesto definido
- Crédito aprobado o efectivo disponible
- Timeline: urgente o menos de 1 mes
- Ya vio propiedades en otras agencias

MENSAJE DE ESCALAMIENTO:
"¡Excelente! Te conecto ahora con [Nombre Asesor], nuestro especialista senior. Él/ella te va a:"
- Enviar fichas completas
- Conseguir la mejor condición
- Agendar visitas prioritarias
"En 2 minutos te escribe. ¿Te parece bien?"

⚠️ IMPORTANTE:
NO escales si solo están "preguntando" sin presupuesto o zona definida.
Califica primero, escala después.

DESPUÉS DE ESCALAR:
Notifica al asesor con todos los datos del lead:
- Presupuesto
- Zona
- Tipo de propiedad
- Timeline
- Forma de pago
- Señales de urgencia"""
    ),
    
    Skill(
        title="objeciones-precio",
        description="Handle price objections and negotiation attempts professionally",
        skill="""Cuando el lead objete el precio:

OBJECIÓN: "Está muy caro" / "Vi más barato en..."
RESPUESTA:
"Entiendo tu punto. El precio considera:"
- Ubicación privilegiada [menciona beneficios de la zona]
- Estado de la propiedad
- Amenidades / servicios
"¿Qué presupuesto tienes en mente? Puedo mostrarte opciones que se ajusten."

OBJECIÓN: "¿Cuál es el precio más bajo que aceptan?"
RESPUESTA:
"El propietario está abierto a escuchar ofertas serias. Si te interesa, podemos agendar una visita y después presentar una oferta formal. ¿Te parece?"

OBJECIÓN: "Necesito descuento"
RESPUESTA:
"Los precios son competitivos para la zona. Sin embargo, en la visita podemos revisar el estado real de la propiedad y ver si hay margen de negociación. ¿Agendamos?"

OBJECIÓN: "Déjame pensarlo" / "Voy a consultarlo"
RESPUESTA:
"Por supuesto, es una decisión importante. Para ayudarte a decidir, ¿qué información adicional necesitas? También te puedo mostrar opciones similares para que compares."

🎯 TÉCNICA PRO:
Si el lead está comparando precios:
"Te entiendo. Por eso te recomiendo que visites 2-3 opciones para que compares en vivo. Así tomas la mejor decisión. ¿Agendamos para que veas personalmente?"

NO:
- No rebajes precios sin autorización
- No hables mal de otras propiedades
- No presiones agresivamente

SÍ:
- Enfoca en valor, no solo precio
- Ofrece alternativas en su rango
- Invita a comparar en persona"""
    ),
    
    Skill(
        title="seguimiento-lead-frio",
        description="Re-engage cold leads who haven't responded or showed initial interest but went silent",
        skill="""Para reactivar leads que se enfriaron:

ESCENARIO 1: Lead no respondió después de calificación inicial
MENSAJE (después de 24-48 hrs):
"Hola [Nombre], veo que te interesaba [zona/tipo]. Justo nos llegaron 2 propiedades nuevas en [zona] dentro de tu presupuesto. ¿Te las muestro?"

ESCENARIO 2: Lead preguntó pero no avanzó
MENSAJE (después de 3-5 días):
"Hola [Nombre], ¿seguís buscando en [zona]? Te tengo una oportunidad que acaba de salir. ¿Te interesa verla antes que se publique?"

ESCENARIO 3: Lead dijo "lo voy a pensar"
MENSAJE (después de 1 semana):
"Hola [Nombre], espero estés bien. ¿Ya tuviste oportunidad de pensarlo? Si necesitas más info o ver otras opciones, aquí estoy. 😊"

ESCENARIO 4: Lead vio propiedad pero no decidió
MENSAJE (después de 2-3 días):
"Hola [Nombre], gracias por visitar [propiedad]. ¿Qué te pareció? ¿Tienes alguna duda que pueda aclarar?"

🎯 REGLAS DE SEGUIMIENTO:
- Máximo 3 intentos de reactivación
- Espaciar mensajes: 48hrs → 5 días → 2 semanas
- Siempre ofrecer VALOR nuevo (nueva propiedad, info del mercado)
- Tono amigable, nunca desesperado

SI DESPUÉS DE 3 INTENTOS NO RESPONDE:
Marca como "Lead frío - recontactar en 3 meses"

FRASES QUE FUNCIONAN:
- "Justo pensé en ti cuando vi esta propiedad..."
- "No quiero que pierdas esta oportunidad..."
- "¿Sigue en pie tu búsqueda de...?"
- "Te tengo una actualización importante sobre..."

NO:
- "¿Por qué no me contestas?"
- "¿Sigues interesado/a?"
- Spam con muchas propiedades no solicitadas"""
    )
]


def main():
    """Main function - demonstrates usage"""
    print("=" * 70)
    print("Meta Business Agent Skills Manager - INMOBILIARIA")
    print("Captura y Calificación de Leads")
    print("=" * 70)
    
    phone_number_id = os.getenv("PHONE_NUMBER_ID", "")
    access_token = os.getenv("WHATSAPP_TOKEN", "")
    
    if not phone_number_id or not access_token:
        print("\n⚠️  Missing credentials!")
        print("Please set environment variables:")
        print("  - PHONE_NUMBER_ID")
        print("  - WHATSAPP_TOKEN")
        print("\nOr use the interactive mode to view predefined skills.")
        print("\n" + "=" * 70)
        
        print(f"\n🏡 Predefined INMOBILIARIA Skills ({len(INMOBILIARIA_SKILLS)} skills):\n")
        for i, skill in enumerate(INMOBILIARIA_SKILLS, 1):
            print(f"{i}. {skill.title}")
            print(f"   Description: {skill.description}")
            print(f"   Skill length: {len(skill.skill)} characters")
            print()
        
        print("📋 ORDEN RECOMENDADO DE ACTIVACIÓN:")
        print("1. greeting-inmobiliaria (primero - saludo inicial)")
        print("2. calificacion-lead (segundo - filtrar leads)")
        print("3. agendar-cita-visita (tercero - cerrar visitas)")
        print("4. human-handoff-asesor (cuarto - escalar compradores calientes)")
        print("5. objeciones-precio (quinto - manejar objeciones)")
        print("6. estrategia-marketing-propiedad (opcional - captar vendedores)")
        print("7. seguimiento-lead-frio (opcional - reactivar leads)")
        print()
        print("💡 CON LAS PRIMERAS 3 YA ESTÁS CAPTANDO Y FILTRANDO LEADS")
        print()
        print("To upload these skills to Meta Business Agent:")
        print("1. Set environment variables (PHONE_NUMBER_ID, WHATSAPP_TOKEN)")
        print("2. Run: python skills_manager_inmobiliaria.py --upload")
        print("3. Or use the Meta Business Suite interface")
        return
    
    manager = SkillsManager(phone_number_id, access_token)
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--upload":
        print("\n📤 Uploading INMOBILIARIA skills to Meta Business Agent...\n")
        results = manager.bulk_create_skills(INMOBILIARIA_SKILLS)
        
        print(f"\n✓ Successfully created: {len(results['created'])} skills")
        for title in results['created']:
            print(f"  - {title}")
        
        if results['failed']:
            print(f"\n✗ Failed to create: {len(results['failed'])} skills")
            for failure in results['failed']:
                print(f"  - {failure['skill']}: {failure['error']}")
        
    elif len(sys.argv) > 1 and sys.argv[1] == "--list":
        print("\n📋 Listing existing skills...\n")
        result = manager.list_skills()
        if result['success']:
            skills = result['data']
            print(f"Found {len(skills)} skills:\n")
            for skill in skills:
                print(f"ID: {skill.get('id')}")
                print(f"Title: {skill.get('title')}")
                print(f"Description: {skill.get('description')}")
                print("-" * 70)
        else:
            print(f"Error: {result['error']}")
    
    else:
        print("\nUsage:")
        print("  python skills_manager_inmobiliaria.py --upload   # Upload skills")
        print("  python skills_manager_inmobiliaria.py --list     # List existing skills")
        print("\nPredefined INMOBILIARIA Skills:")
        for skill in INMOBILIARIA_SKILLS:
            print(f"  - {skill.title}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    main()
