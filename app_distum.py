#!/usr/bin/env python3
"""
WhatsApp Bot for DISTUM PALM DIAMANTE
Connected to EasyBroker API for real-time property inventory
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from flask import Flask, request, jsonify
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "distum_palm_2026")
EASYBROKER_API_KEY = os.getenv("EASYBROKER_API_KEY", "")

# Distum Palm Diamante branding
BRAND_NAME = "Distum Palm Diamante"
MAIN_ZONE = "Metepec, Estado de México"
ASESOR_NAME = "Asesor Distum"
ASESOR_PHONE = os.getenv("ASESOR_PHONE", "")


class EasyBrokerClient:
    """Client for EasyBroker API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.easybroker.com/v1"
        self.headers = {
            "X-Authorization": api_key,
            "Content-Type": "application/json"
        }
    
    def get_available_properties(
        self, 
        property_type: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Get available properties from EasyBroker"""
        try:
            params = {
                "limit": limit,
                "search[statuses][]": "published"
            }
            
            if property_type:
                params["search[property_type]"] = property_type
            
            if min_price:
                params["search[min_price]"] = min_price
            
            if max_price:
                params["search[max_price]"] = max_price
            
            response = requests.get(
                f"{self.base_url}/properties",
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {len(data.get('content', []))} properties from EasyBroker")
            return {"success": True, "data": data}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from EasyBroker: {e}")
            return {"success": False, "error": str(e)}
    
    def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Get detailed info for a specific property"""
        try:
            response = requests.get(
                f"{self.base_url}/properties/{property_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return {"success": True, "data": data}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching property {property_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def format_property_message(self, property_data: Dict) -> str:
        """Format property data into WhatsApp message"""
        prop = property_data
        
        title = prop.get("title", "Propiedad disponible")
        price = prop.get("operations", [{}])[0].get("formatted_amount", "Consultar precio")
        bedrooms = prop.get("bedrooms", "N/A")
        bathrooms = prop.get("bathrooms", "N/A")
        size = prop.get("construction_size", "N/A")
        location = prop.get("location", "Metepec")
        public_url = prop.get("public_url", "")
        
        message = f"""🏡 *{title}*

💰 Precio: {price}
🛏 Recámaras: {bedrooms}
🚿 Baños: {bathrooms}
📐 M² construcción: {size}
📍 Ubicación: {location}

Ver más: {public_url}"""
        
        return message


class WhatsAppClient:
    """WhatsApp Business API client"""
    
    def __init__(self, phone_number_id: str, token: str):
        self.phone_number_id = phone_number_id
        self.token = token
        self.base_url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def send_message(self, to: str, message: str) -> Dict[str, Any]:
        """Send text message"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "text": {"body": message}
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message: {e}")
            return {"success": False, "error": str(e)}
    
    def send_image(self, to: str, image_url: str, caption: str = "") -> Dict[str, Any]:
        """Send image with caption"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": {
                "link": image_url,
                "caption": caption
            }
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending image: {e}")
            return {"success": False, "error": str(e)}
    
    def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark message as read"""
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return {"success": True}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error marking as read: {e}")
            return {"success": False, "error": str(e)}


class LeadQualifier:
    """Qualify leads and determine next actions"""
    
    def __init__(self, easybroker_client: EasyBrokerClient, whatsapp_client: WhatsAppClient):
        self.easybroker = easybroker_client
        self.whatsapp = whatsapp_client
        self.lead_data = {}  # In production, use database
    
    def handle_greeting(self, from_number: str, message: str) -> str:
        """Handle initial contact"""
        greeting = f"""¡Hola! Bienvenido a *{BRAND_NAME}* 🏡

Somos especialistas en {MAIN_ZONE}, con inventario exclusivo de casas y departamentos.

Para mostrarte las mejores opciones:

1️⃣ ¿Buscas para vivir o invertir?
2️⃣ ¿Cuál es tu presupuesto aproximado?
   Ej: $2-3M, $3-4M, $4M+

¡Tenemos propiedades increíbles disponibles! 🔥"""
        
        return greeting
    
    def extract_budget(self, message: str) -> Optional[Dict[str, int]]:
        """Extract budget from message"""
        message_lower = message.lower()
        
        # Common patterns
        if "2" in message and "3" in message or "2-3" in message:
            return {"min": 2000000, "max": 3000000}
        elif "3" in message and "4" in message or "3-4" in message:
            return {"min": 3000000, "max": 4000000}
        elif "4" in message and "5" in message or "4-5" in message:
            return {"min": 4000000, "max": 5000000}
        elif "5" in message or "5m" in message_lower:
            return {"min": 5000000, "max": 10000000}
        
        return None
    
    def qualify_and_send_properties(self, from_number: str, message: str) -> str:
        """Qualify lead and send matching properties"""
        budget = self.extract_budget(message)
        
        if not budget:
            return """Para mostrarte las opciones perfectas, ¿cuál es tu presupuesto aproximado?

Por ejemplo:
📊 $2-3 millones
📊 $3-4 millones  
📊 $4-5 millones
📊 Más de $5 millones"""
        
        # Fetch properties from EasyBroker
        result = self.easybroker.get_available_properties(
            min_price=budget["min"],
            max_price=budget["max"],
            limit=3
        )
        
        if not result["success"]:
            return f"""Perfecto, tenemos excelentes opciones en tu rango de ${budget['min']/1000000:.1f}-{budget['max']/1000000:.1f}M 🏡

Te conecto con {ASESOR_NAME} para enviarte fichas técnicas completas y agendar tu visita.

📱 En 2 minutos te escribe para coordinar. ¿Te parece bien?"""
        
        properties = result["data"].get("content", [])
        
        if not properties:
            return f"""Gracias por tu interés. Actualmente estamos actualizando nuestro inventario en ese rango.

Te conecto con {ASESOR_NAME} quien te puede mostrar opciones similares que tenemos.

📱 ¿Te parece bien que te contacte?"""
        
        # Send properties
        response = f"""¡Excelente! Encontré {len(properties)} propiedades en {MAIN_ZONE} dentro de tu presupuesto:\n\n"""
        
        for prop in properties[:3]:
            response += self.easybroker.format_property_message(prop) + "\n\n---\n\n"
        
        response += f"""¿Cuál te interesa más? Te agendo una visita esta semana 📅

O si prefieres, te conecto directo con {ASESOR_NAME} para ver todas las opciones disponibles."""
        
        return response
    
    def detect_hot_signals(self, message: str) -> bool:
        """Detect if lead is hot and needs immediate escalation"""
        hot_keywords = [
            "cuando puedo ver",
            "quiero ver",
            "agendar",
            "visita",
            "disponible",
            "enganche",
            "credito aprobado",
            "pre-aprobado",
            "urgente",
            "necesito",
            "cuanto es lo menos",
            "acepta",
            "ofertar"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in hot_keywords)
    
    def handle_hot_lead(self, from_number: str) -> str:
        """Handle hot lead escalation"""
        return f"""¡Perfecto! 🔥

Te conecto AHORA con {ASESOR_NAME}, nuestro especialista.

Él/ella te va a:
✅ Enviar fichas técnicas completas
✅ Agendar tu visita prioritaria
✅ Conseguir la mejor condición

📱 En menos de 2 minutos te escribe directamente.

¿Confirmado? 👍"""


# Initialize clients
whatsapp_client = WhatsAppClient(PHONE_NUMBER_ID, WHATSAPP_TOKEN)
easybroker_client = EasyBrokerClient(EASYBROKER_API_KEY) if EASYBROKER_API_KEY else None
lead_qualifier = LeadQualifier(easybroker_client, whatsapp_client) if easybroker_client else None


@app.route("/webhook", methods=["GET"])
def verify():
    """Webhook verification"""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return challenge, 200
    
    logger.warning("Webhook verification failed")
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming WhatsApp messages"""
    data = request.json
    
    if not data:
        return "Bad Request", 400
    
    logger.info(f"Webhook received: {data}")
    
    try:
        entry = data.get("entry", [])
        if not entry:
            return jsonify({"status": "no_entry"}), 200
        
        changes = entry[0].get("changes", [])
        if not changes:
            return jsonify({"status": "no_changes"}), 200
        
        value = changes[0].get("value", {})
        
        # Skip status updates
        if "statuses" in value:
            return jsonify({"status": "status_update"}), 200
        
        messages = value.get("messages", [])
        if not messages:
            return jsonify({"status": "no_messages"}), 200
        
        msg = messages[0]
        message_id = msg.get("id")
        from_number = msg.get("from")
        message_type = msg.get("type")
        
        # Only handle text messages
        if message_type != "text":
            whatsapp_client.send_message(
                from_number,
                "Por favor envía mensajes de texto. ¡Gracias! 😊"
            )
            return jsonify({"status": "non_text_message"}), 200
        
        text = msg.get("text", {}).get("body", "")
        
        if not text:
            return jsonify({"status": "empty_text"}), 200
        
        logger.info(f"Processing message from {from_number}: {text}")
        
        # Mark as read
        whatsapp_client.mark_as_read(message_id)
        
        # Determine response based on conversation stage
        text_lower = text.lower()
        
        # Check if hot lead
        if lead_qualifier and lead_qualifier.detect_hot_signals(text):
            response = lead_qualifier.handle_hot_lead(from_number)
        
        # Check if first message (greeting keywords)
        elif any(word in text_lower for word in ["hola", "info", "informacion", "buenos", "buenas", "disponible"]):
            response = lead_qualifier.handle_greeting(from_number, text) if lead_qualifier else handle_fallback_greeting()
        
        # Check if contains budget info
        elif any(char.isdigit() for char in text) or "millon" in text_lower or "millones" in text_lower:
            response = lead_qualifier.qualify_and_send_properties(from_number, text) if lead_qualifier else handle_fallback_budget()
        
        # Default: ask for more info
        else:
            response = """Perfecto, ¿me ayudas con un poco más de info?

1️⃣ ¿Cuál es tu presupuesto aproximado?
2️⃣ ¿Buscas casa o departamento?

Así te muestro las opciones exactas que tenemos 🏡"""
        
        # Send response
        whatsapp_client.send_message(from_number, response)
        logger.info(f"Response sent to {from_number}")
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return jsonify({"status": "error"}), 500
    
    return jsonify({"status": "success"}), 200


def handle_fallback_greeting() -> str:
    """Fallback greeting when EasyBroker not configured"""
    return f"""¡Hola! Bienvenido a *{BRAND_NAME}* 🏡

Somos especialistas en {MAIN_ZONE}.

Para mostrarte nuestras mejores propiedades:
📍 ¿En qué zona buscas?
💰 ¿Cuál es tu presupuesto aproximado?
🏠 ¿Casa o departamento?

¡Tenemos opciones increíbles disponibles!"""


def handle_fallback_budget() -> str:
    """Fallback budget response when EasyBroker not configured"""
    return f"""¡Perfecto! Tenemos excelentes opciones en ese rango 🏡

Te conecto con {ASESOR_NAME} quien te enviará:
✅ Fichas técnicas completas
✅ Fotos y videos
✅ Agenda tu visita

📱 En 2 minutos te escribe. ¿De acuerdo?"""


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    config_status = {
        "phone_number_id_set": bool(PHONE_NUMBER_ID),
        "whatsapp_token_set": bool(WHATSAPP_TOKEN),
        "verify_token_set": bool(VERIFY_TOKEN),
        "easybroker_api_key_set": bool(EASYBROKER_API_KEY),
        "asesor_phone_set": bool(ASESOR_PHONE)
    }
    
    return jsonify({
        "status": "healthy",
        "brand": BRAND_NAME,
        "zone": MAIN_ZONE,
        "configuration": config_status,
        "easybroker_connected": bool(EASYBROKER_API_KEY)
    }), 200


@app.route("/", methods=["GET"])
def home():
    """Home endpoint"""
    return jsonify({
        "service": f"WhatsApp Bot - {BRAND_NAME}",
        "version": "1.0.0",
        "status": "running",
        "zone": MAIN_ZONE,
        "easybroker": "connected" if EASYBROKER_API_KEY else "not_configured"
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    
    logger.info(f"Starting {BRAND_NAME} WhatsApp Bot on port {port}")
    logger.info(f"Zone: {MAIN_ZONE}")
    logger.info(f"EasyBroker: {'✓ Connected' if EASYBROKER_API_KEY else '✗ Not configured'}")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
