from flask import Flask, request, jsonify
import requests
import os
import logging
from typing import Optional, Dict, Any

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
WABA_ID = os.getenv("WABA_ID", "")
TOKEN = os.getenv("WHATSAPP_TOKEN", "")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "rsi_otono_2026")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

SYSTEM_PROMPT = """
Eres el asistente del profesor de Responsabilidad Social en la Industria - Otoño 2026.
Eres experto en economía circular, sostenibilidad industrial y RSC.
Tono cálido, profesional y directo. Respuestas cortas (máx 3 líneas).
Si preguntan por tareas, pide nombre y matrícula.
"""


class WhatsAppClient:
    def __init__(self, phone_number_id: str, token: str):
        self.phone_number_id = phone_number_id
        self.token = token
        self.base_url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def send_message(self, to: str, message: str) -> Dict[str, Any]:
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
            logger.error(f"Error sending WhatsApp message: {e}")
            return {"success": False, "error": str(e)}

    def mark_as_read(self, message_id: str) -> Dict[str, Any]:
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
            logger.error(f"Error marking message as read: {e}")
            return {"success": False, "error": str(e)}


class AIAssistant:
    def __init__(self, api_key: str, system_prompt: str):
        self.api_key = api_key
        self.system_prompt = system_prompt

    def generate_response(self, user_message: str) -> str:
        if not self.api_key:
            return self._fallback_response(user_message)
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 150,
                    "temperature": 0.7
                },
                timeout=30
            )
            response.raise_for_status()
            
            ai_response = response.json()["choices"][0]["message"]["content"]
            return ai_response.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._fallback_response(user_message)

    def _fallback_response(self, user_message: str) -> str:
        lower_msg = user_message.lower()
        
        if any(word in lower_msg for word in ["tarea", "entrega", "trabajo"]):
            return "📚 Para consultas sobre tareas, por favor proporciona tu nombre completo y matrícula. ¿En qué tarea necesitas ayuda?"
        
        if any(word in lower_msg for word in ["circular", "economía circular"]):
            return "♻️ La economía circular busca minimizar residuos y maximizar el valor de los recursos. ¿Qué aspecto te interesa profundizar?"
        
        if any(word in lower_msg for word in ["sostenibilidad", "sustentable"]):
            return "🌱 La sostenibilidad integra aspectos ambientales, sociales y económicos. ¿Sobre qué tema específico quieres saber?"
        
        if any(word in lower_msg for word in ["rsc", "responsabilidad social"]):
            return "🤝 La RSC implica el compromiso de las empresas con la sociedad y el medio ambiente. ¿Qué aspecto te gustaría explorar?"
        
        return f"¡Hola! Soy el asistente de RSI Otoño 2026. Recibí tu mensaje sobre '{user_message[:50]}...'. ¿En qué puedo ayudarte con economía circular o RSC?"


whatsapp_client = WhatsAppClient(PHONE_NUMBER_ID, TOKEN)
ai_assistant = AIAssistant(OPENAI_API_KEY, SYSTEM_PROMPT)


@app.route("/webhook", methods=["GET"])
def verify():
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
    data = request.json
    
    if not data:
        logger.warning("Received empty webhook data")
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
        
        if "statuses" in value:
            logger.info(f"Received status update: {value['statuses']}")
            return jsonify({"status": "status_update"}), 200
        
        messages = value.get("messages", [])
        if not messages:
            return jsonify({"status": "no_messages"}), 200
        
        msg = messages[0]
        message_id = msg.get("id")
        from_number = msg.get("from")
        message_type = msg.get("type")
        
        if message_type != "text":
            logger.info(f"Received non-text message type: {message_type}")
            whatsapp_client.send_message(
                from_number,
                "Por favor envía mensajes de texto. Otros tipos de mensajes no son soportados actualmente."
            )
            return jsonify({"status": "non_text_message"}), 200
        
        text = msg.get("text", {}).get("body", "")
        
        if not text:
            return jsonify({"status": "empty_text"}), 200
        
        logger.info(f"Processing message from {from_number}: {text}")
        
        whatsapp_client.mark_as_read(message_id)
        
        reply = ai_assistant.generate_response(text)
        
        result = whatsapp_client.send_message(from_number, reply)
        
        if result["success"]:
            logger.info(f"Successfully sent reply to {from_number}")
        else:
            logger.error(f"Failed to send reply: {result.get('error')}")
        
    except KeyError as e:
        logger.error(f"Missing expected key in webhook data: {e}")
        return jsonify({"status": "error", "message": "Invalid data structure"}), 400
    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    
    return jsonify({"status": "success"}), 200


@app.route("/health", methods=["GET"])
def health():
    config_status = {
        "phone_number_id_set": bool(PHONE_NUMBER_ID),
        "waba_id_set": bool(WABA_ID),
        "token_set": bool(TOKEN),
        "verify_token_set": bool(VERIFY_TOKEN),
        "openai_key_set": bool(OPENAI_API_KEY)
    }
    
    all_configured = all([
        PHONE_NUMBER_ID,
        TOKEN,
        VERIFY_TOKEN
    ])
    
    return jsonify({
        "status": "healthy" if all_configured else "missing_config",
        "configuration": config_status
    }), 200


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "RSI WhatsApp Bot - Otoño 2026",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "webhook": "/webhook (GET, POST)",
            "health": "/health (GET)"
        }
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    
    logger.info(f"Starting Flask app on port {port}")
    logger.info(f"Configuration status:")
    logger.info(f"  - Phone Number ID: {'✓' if PHONE_NUMBER_ID else '✗'}")
    logger.info(f"  - WABA ID: {'✓' if WABA_ID else '✗'}")
    logger.info(f"  - WhatsApp Token: {'✓' if TOKEN else '✗'}")
    logger.info(f"  - Verify Token: {'✓' if VERIFY_TOKEN else '✗'}")
    logger.info(f"  - OpenAI API Key: {'✓' if OPENAI_API_KEY else '✗'}")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
