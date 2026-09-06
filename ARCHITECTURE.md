# Sistema Completo del Bot de WhatsApp RSI - Arquitectura

## Vista General del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESTUDIANTE                                    │
│                   (WhatsApp User)                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Mensaje
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              WhatsApp Business API (Meta)                        │
│              - Recibe mensajes                                   │
│              - Aplica Meta Business Agent Skills (opcional)      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ POST /webhook
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FLASK BOT (app.py)                            │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Webhook Handler                                        │    │
│  │  - Valida mensaje                                       │    │
│  │  - Extrae texto y sender                                │    │
│  │  - Marca como leído                                     │    │
│  └────────────────┬───────────────────────────────────────┘    │
│                   │                                              │
│                   ▼                                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  AIAssistant                                            │    │
│  │  ┌──────────────────────────┐                          │    │
│  │  │ ¿OpenAI API disponible?  │                          │    │
│  │  └──────────┬───────────────┘                          │    │
│  │             │                                            │    │
│  │      ┌──────┴──────┐                                    │    │
│  │      │             │                                     │    │
│  │      ▼ Sí          ▼ No                                 │    │
│  │  ┌─────────┐  ┌──────────────┐                        │    │
│  │  │OpenAI   │  │  Fallback    │                        │    │
│  │  │GPT-4    │  │  Respuestas  │                        │    │
│  │  │Response │  │  (Keywords)   │                        │    │
│  │  └────┬────┘  └──────┬───────┘                        │    │
│  │       │              │                                  │    │
│  │       └──────┬───────┘                                  │    │
│  │              ▼                                           │    │
│  │       Respuesta generada                                │    │
│  └────────────────┬───────────────────────────────────────┘    │
│                   │                                              │
│                   ▼                                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  WhatsAppClient                                         │    │
│  │  - Envía respuesta al estudiante                        │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────────────────────────────────────────┘
```

---

## Componentes del Sistema

### 1. Estudiante (WhatsApp User)
- Envía mensajes vía WhatsApp
- Recibe respuestas del bot
- Puede preguntar sobre economía circular, sostenibilidad, RSC, tareas, etc.

### 2. WhatsApp Business API (Meta)
**Responsabilidades:**
- Recibir mensajes de estudiantes
- Reenviar a tu webhook (Flask bot)
- Opcionalmente aplicar Meta Business Agent Skills
- Enviar respuestas de vuelta al estudiante

**Configuración necesaria:**
- Phone Number ID
- WABA ID (WhatsApp Business Account ID)
- Access Token (permanente)
- Webhook URL configurado

### 3. Flask Bot (`app.py`)

#### 3.1 Webhook Handler
```python
@app.route("/webhook", methods=["POST"])
def webhook():
    # Recibe data de WhatsApp
    # Extrae mensaje y remitente
    # Marca mensaje como leído
    # Pasa a AIAssistant
```

**Entradas:**
- JSON con estructura de mensaje de WhatsApp
- Campos: `from`, `text.body`, `id`, `type`

**Salidas:**
- Status 200 OK
- Respuesta enviada al estudiante

#### 3.2 AIAssistant
```python
class AIAssistant:
    def generate_response(user_message):
        if OPENAI_API_KEY:
            return openai_response()
        else:
            return fallback_response()
```

**Modo A: OpenAI (si API key está configurado)**
- Envía mensaje a GPT-4 con SYSTEM_PROMPT
- SYSTEM_PROMPT incluye contexto de RSI
- Respuesta inteligente y contextual

**Modo B: Fallback (sin API key)**
- Analiza keywords: "tarea", "circular", "sostenibilidad", "RSC"
- Devuelve respuestas predefinidas según keywords
- Funcional pero menos flexible

#### 3.3 WhatsAppClient
```python
class WhatsAppClient:
    def send_message(to, message):
        # POST a Meta Graph API
        # Envía texto al estudiante
```

### 4. Meta Business Agent Skills (Opcional)

**¿Qué son?**
Instrucciones de comportamiento que Meta aplica ANTES de enviar el mensaje a tu webhook.

**¿Cuándo usar?**
- Quieres comportamiento consistente sin depender de tu código
- Necesitas manejar casos edge (mensajes poco claros, off-topic)
- Deseas separar "qué responder" (bot) de "cómo comportarse" (skills)

**10 Skills RSI:**
1. `greeting-skill` → Primer contacto
2. `circular-economy-questions` → Economía circular
3. `sustainability-questions` → Sostenibilidad
4. `csr-rsc-questions` → RSC
5. `assignment-help` → Ayuda con tareas
6. `course-information` → Info del curso
7. `exam-preparation` → Preparación de exámenes
8. `examples-case-studies` → Ejemplos de empresas
9. `unclear-or-offtopic` → Mensajes poco claros
10. `human-handoff` → Escalamiento al profesor

---

## Flujo de Datos Detallado

### Escenario 1: Pregunta sobre Economía Circular

```
1. Estudiante: "¿Qué es economía circular?"
   ↓
2. WhatsApp Business API recibe mensaje
   ↓
3. [OPCIONAL] Meta Business Agent:
   - Skill "circular-economy-questions" se activa
   - Prepara contexto adicional
   ↓
4. POST /webhook a Flask bot
   Body: {
     "entry": [{
       "changes": [{
         "value": {
           "messages": [{
             "from": "1234567890",
             "text": {"body": "¿Qué es economía circular?"}
           }]
         }
       }]
     }]
   }
   ↓
5. Flask webhook handler:
   - Extrae: from="1234567890", text="¿Qué es economía circular?"
   - Mark as read
   ↓
6. AIAssistant.generate_response("¿Qué es economía circular?")
   ↓
7. [OPCIÓN A] OpenAI:
   - POST a OpenAI API
   - System prompt: "Eres asistente RSI..."
   - User message: "¿Qué es economía circular?"
   - Response: "♻️ La economía circular busca..."
   ↓
   [OPCIÓN B] Fallback:
   - Detecta keyword "circular"
   - Response: "♻️ La economía circular busca..."
   ↓
8. WhatsAppClient.send_message("1234567890", "♻️ La economía circular busca...")
   ↓
9. POST a Meta Graph API:
   URL: https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages
   Body: {
     "messaging_product": "whatsapp",
     "to": "1234567890",
     "text": {"body": "♻️ La economía circular busca..."}
   }
   ↓
10. Meta envía mensaje a estudiante
    ↓
11. Estudiante recibe respuesta en WhatsApp ✓
```

### Escenario 2: Ayuda con Tarea

```
1. Estudiante: "Tengo dudas sobre la tarea 2"
   ↓
2-4. [Igual que escenario 1]
   ↓
5. Flask detecta keyword "tarea"
   ↓
6. AIAssistant (fallback o OpenAI):
   - Skill "assignment-help" guía comportamiento
   - Response: "📚 Para ayudarte, necesito tu nombre y matrícula..."
   ↓
7. Estudiante: "Soy Juan Pérez, matrícula 12345"
   ↓
8. Bot: "¿Qué aspecto de la tarea 2 no entiendes?"
   ↓
9. Conversación continúa... (guía sin resolver directamente)
```

### Escenario 3: Mensaje Poco Claro

```
1. Estudiante: "asdfghjkl"
   ↓
2-4. [Igual que escenario 1]
   ↓
5. No hay keywords reconocibles
   ↓
6. AIAssistant (fallback):
   - Skill "unclear-or-offtopic" se aplica
   - Response: "No estoy seguro de entender. Puedo ayudarte con..."
   ↓
7. Redirige a temas del curso
```

---

## Opciones de Configuración

### Configuración A: Solo Flask Bot (Sin Skills)

```
WhatsApp ──► Webhook ──► Flask Bot ──► WhatsApp
                          (AIAssistant)
```

**Pros:**
- ✅ Más simple
- ✅ Full control del código
- ✅ No depende de Meta Agent

**Contras:**
- ❌ Más código para casos edge
- ❌ Mantenimiento manual

**Cuándo usar:**
- Proyecto pequeño
- Necesitas control total
- No quieres configurar Meta Agent

### Configuración B: Meta Agent con Skills (Sin Flask)

```
WhatsApp ──► Meta Business Agent ──► WhatsApp
             (Skills aplican aquí)
```

**Pros:**
- ✅ Menos código
- ✅ UI visual en Meta Suite
- ✅ Comportamiento consistente

**Contras:**
- ❌ Menos flexibilidad
- ❌ Depende de Meta

**Cuándo usar:**
- No quieres código custom
- Prefieres UI visual
- Confías en Meta Agent

### Configuración C: Híbrido (Recomendado) ⭐

```
WhatsApp ──► Meta Agent ──► Flask Bot ──► WhatsApp
             (Skills)        (AIAssistant)
```

**Pros:**
- ✅ Skills manejan estructura/comportamiento
- ✅ Flask bot maneja contenido/IA
- ✅ Best of both worlds

**Contras:**
- ❌ Más complejo de configurar
- ❌ Dos sistemas que mantener

**Cuándo usar:**
- Proyecto grande
- Necesitas sofisticación
- Quieres lo mejor de ambos

---

## Herramientas de Gestión Incluidas

### 1. `app.py` - Flask Bot Principal
```bash
# Desarrollo
python app.py

# Producción
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 2. `skills_manager.py` - Gestión de Skills
```bash
# Ver skills predefinidas
python skills_manager.py

# Subir todas las skills RSI
python skills_manager.py --upload

# Listar skills existentes
python skills_manager.py --list
```

### 3. `test_bot.py` - Tests
```bash
# Ejecutar todos los tests
python test_bot.py

# Verifica:
# - Imports
# - Env vars
# - App initialization
# - Endpoints
# - AI responses
```

### 4. Health Check
```bash
# Verificar estado del bot
curl http://localhost:5000/health

# Response:
# {
#   "status": "healthy",
#   "configuration": {
#     "phone_number_id_set": true,
#     "waba_id_set": true,
#     "token_set": true,
#     "verify_token_set": true,
#     "openai_key_set": false
#   }
# }
```

---

## Variables de Entorno

### Requeridas (Bot funciona sin ellas, pero con funcionalidad limitada)

```bash
PHONE_NUMBER_ID=tu_phone_number_id    # Meta Dashboard → WhatsApp → API Setup
WABA_ID=tu_waba_id                    # Meta Dashboard → WhatsApp → Settings
WHATSAPP_TOKEN=tu_token_permanente    # Meta Dashboard → WhatsApp → API Setup
VERIFY_TOKEN=rsi_otono_2026          # Tu elección (coincide con webhook config)
```

### Opcionales

```bash
OPENAI_API_KEY=tu_openai_key         # Para respuestas AI avanzadas
FLASK_ENV=development                 # development | production
PORT=5000                             # Puerto del servidor
```

---

## Endpoints del Flask Bot

| Endpoint | Método | Propósito |
|----------|--------|-----------|
| `/` | GET | Info del servicio |
| `/health` | GET | Health check |
| `/webhook` | GET | Verificación de webhook (Meta) |
| `/webhook` | POST | Recibir mensajes de WhatsApp |

---

## Seguridad y Mejores Prácticas

### ✅ Implementado

1. **Environment variables** para credenciales
2. **Health monitoring** endpoint
3. **Error handling** comprehensivo
4. **Logging** estructurado
5. **Message validation** (tipo, estructura)
6. **Timeouts** en API calls (10s WhatsApp, 30s OpenAI)

### 🔜 Recomendaciones Futuras

1. **Webhook signature verification** (Meta firma requests)
2. **Rate limiting** (prevenir abuse)
3. **Database** para historial de conversaciones
4. **Token rotation** automática
5. **Monitoring/alerting** (Datadog, Sentry)
6. **Message queue** (Celery, RabbitMQ) para alto volumen

---

## Troubleshooting

### Problema: Webhook no recibe mensajes

**Diagnóstico:**
```bash
# 1. Verifica que el bot esté corriendo
curl http://localhost:5000/health

# 2. Verifica webhook en Meta
# Meta Dashboard → WhatsApp → Configuration → Webhook
# URL debe ser: https://tu-dominio.com/webhook
# Verify Token: rsi_otono_2026

# 3. Verifica logs del bot
tail -f /var/log/whatsapp-bot.log  # o donde estén tus logs
```

**Soluciones:**
- Asegúrate de usar HTTPS (Meta no acepta HTTP)
- Verifica que el puerto esté abierto en firewall
- Confirma que VERIFY_TOKEN coincida

### Problema: Bot responde con error

**Diagnóstico:**
```bash
# 1. Revisa logs
python app.py  # modo development para ver logs

# 2. Verifica env vars
python test_bot.py

# 3. Revisa health
curl http://localhost:5000/health
```

**Soluciones:**
- Verifica WHATSAPP_TOKEN no haya expirado
- Confirma PHONE_NUMBER_ID sea correcto
- Revisa que OpenAI tenga créditos (si usas IA)

### Problema: Skills no se activan

**Diagnóstico:**
```bash
# 1. Lista skills existentes
python skills_manager.py --list

# 2. Verifica en Meta Business Suite
# Meta Business Suite → Meta Business Agent → Skills → Test chat
# Envía mensaje → Click "View sources" → ve qué skill se activó
```

**Soluciones:**
- Verifica título sea lowercase con guiones (no espacios ni underscores)
- Haz "Reload" en Test chat
- Ajusta description para incluir keywords que estudiantes realmente usan

---

## Monitoreo y Métricas

### Logs a Monitorear

```python
# Logs importantes:
INFO - "Processing message from {number}: {text}"
INFO - "Successfully sent reply to {number}"
ERROR - "Error sending WhatsApp message: {error}"
ERROR - "Error generating AI response: {error}"
WARNING - "Received non-text message type: {type}"
```

### Métricas Útiles

- **Mensajes recibidos/enviados por hora**
- **Tiempo de respuesta promedio**
- **Tasa de error de API calls**
- **Skills más activadas** (si usas Meta Agent)
- **Keywords más frecuentes** (para mejorar fallbacks)

### Health Check Monitoring

```bash
# Ping cada 30s
*/30 * * * * curl -f http://localhost:5000/health || alert

# Uptime monitoring (UptimeRobot, Pingdom, etc.)
```

---

## Próximos Pasos

### Fase 1: Setup Básico ✅
- [x] Flask bot funcionando
- [x] Webhook configurado
- [x] Respuestas básicas

### Fase 2: Skills (Actual)
- [x] Skills manager script
- [x] 10 skills RSI predefinidas
- [x] Documentación completa
- [ ] Subir skills a Meta Agent
- [ ] Probar en Test chat

### Fase 3: Producción
- [ ] Deploy a cloud (Railway/Render)
- [ ] Configurar HTTPS
- [ ] Monitoring/alerting
- [ ] Conectar con estudiantes reales

### Fase 4: Mejoras Futuras
- [ ] Database para historial
- [ ] Dashboard de analytics
- [ ] Multi-idioma (EN/ES)
- [ ] Rate limiting
- [ ] Webhook signature verification

---

**Última actualización:** Septiembre 2026  
**Versión del sistema:** 1.0.0  
**Curso:** Responsabilidad Social en la Industria - Otoño 2026
