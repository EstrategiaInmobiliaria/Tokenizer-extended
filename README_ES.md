# 🎓 WhatsApp Bot RSI - Guía de Inicio Rápido

## ¿Qué es este proyecto?

Un **bot de WhatsApp completo y listo para producción** para el curso "Responsabilidad Social en la Industria - Otoño 2026". El bot actúa como asistente de enseñanza con experiencia en:

- ♻️ Economía circular
- 🌱 Sostenibilidad industrial  
- 🤝 Responsabilidad Social Corporativa (RSC)

---

## 🚀 Inicio Rápido (5 minutos)

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar credenciales
```bash
cp .env.whatsapp .env
# Editar .env con tus credenciales de Meta
```

### 3. Probar
```bash
python test_bot.py
```

### 4. Ejecutar
```bash
python app.py
```

**¡Listo!** Tu bot está corriendo en `http://localhost:5000`

---

## 📚 Documentación Completa

Este proyecto incluye documentación exhaustiva en varios archivos:

### 🏗️ Para Empezar

| Archivo | Descripción | Tiempo de lectura |
|---------|-------------|-------------------|
| **`README.md`** (este archivo) | Guía de inicio rápido | 5 min |
| **`WHATSAPP_BOT_README.md`** | Documentación completa del bot | 15 min |
| **`ARCHITECTURE.md`** | Arquitectura del sistema | 20 min |

### 🎯 Skills de Meta Business Agent

| Archivo | Descripción | Tiempo de lectura |
|---------|-------------|-------------------|
| **`SKILLS_QUICK_REFERENCE.md`** | Cheat sheet de skills | 5 min |
| **`RSI_SKILLS_TEMPLATES.md`** | 10 skills listas para copiar | 10 min |
| **`SKILLS_CONFIGURATION_GUIDE.md`** | Guía completa de configuración | 30 min |

### 🛠️ Código

| Archivo | Descripción |
|---------|-------------|
| **`app.py`** | Bot Flask principal |
| **`skills_manager.py`** | Gestión de skills via API |
| **`test_bot.py`** | Suite de tests |
| **`.env.whatsapp`** | Template de variables de entorno |
| **`Dockerfile`** | Configuración Docker |
| **`docker-compose.yml`** | Orquestación Docker |

---

## 🎯 Características Principales

### ✅ Bot Flask con IA
- Integración con WhatsApp Business API
- Respuestas inteligentes con OpenAI GPT-4
- Fallback inteligente basado en keywords
- Logging comprehensivo
- Health monitoring

### ✅ Sistema de Skills
- 10 skills predefinidas para RSI
- Gestión programática via API
- Validación de requisitos de Meta
- Upload masivo con un comando

### ✅ Producción Ready
- Docker support
- Gunicorn configurado
- Health checks
- Error handling robusto
- Environment-based configuration

---

## 📖 Flujo de Trabajo Recomendado

### Para Desarrolladores

1. **Lee primero:**
   - `README.md` (este archivo) ← EMPEZAR AQUÍ
   - `WHATSAPP_BOT_README.md` (setup detallado)

2. **Configura el bot:**
   ```bash
   pip install -r requirements.txt
   cp .env.whatsapp .env
   # Edita .env con tus credenciales
   ```

3. **Prueba localmente:**
   ```bash
   python test_bot.py  # Verifica todo esté OK
   python app.py        # Corre el bot
   ```

4. **Opcional - Configura skills:**
   - Lee `SKILLS_QUICK_REFERENCE.md`
   - Ejecuta `python skills_manager.py --upload`

5. **Deploy:**
   - Ver sección "Deployment" en `WHATSAPP_BOT_README.md`

### Para Usuarios No-Técnicos

1. **Opción A: Usar solo Meta Business Agent (sin código)**
   - No necesitas correr el Flask bot
   - Lee `SKILLS_CONFIGURATION_GUIDE.md` → Método 1
   - Configura skills en Meta Business Suite
   - Conecta WhatsApp directo a Meta Agent

2. **Opción B: Pedir ayuda técnica**
   - Envía todo este repositorio a tu equipo técnico
   - Pídeles que lean `WHATSAPP_BOT_README.md`

---

## 🎓 Skills Incluidas

El sistema incluye **10 skills especializadas** para RSI:

| # | Skill | Para qué sirve |
|---|-------|----------------|
| 1 | `greeting-skill` | Saludo inicial cálido |
| 2 | `circular-economy-questions` | Responde sobre economía circular |
| 3 | `sustainability-questions` | Explica sostenibilidad y ESG |
| 4 | `csr-rsc-questions` | Maneja preguntas de RSC |
| 5 | `assignment-help` | Guía en tareas (sin resolverlas) |
| 6 | `course-information` | Info del curso y syllabus |
| 7 | `exam-preparation` | Tips de estudio |
| 8 | `examples-case-studies` | Ejemplos de empresas reales |
| 9 | `unclear-or-offtopic` | Maneja mensajes confusos |
| 10 | `human-handoff` | Escala al profesor |

**Ver detalles:** `RSI_SKILLS_TEMPLATES.md`

---

## 🛠️ Comandos Útiles

### Bot Flask

```bash
# Desarrollo
python app.py

# Producción
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Docker
docker-compose up

# Tests
python test_bot.py

# Health check
curl http://localhost:5000/health
```

### Skills Manager

```bash
# Ver skills predefinidas
python skills_manager.py

# Subir todas las skills RSI a Meta
python skills_manager.py --upload

# Listar skills existentes en Meta
python skills_manager.py --list
```

---

## 🔧 Configuración Requerida

### Credenciales de Meta (Requeridas)

Obtén estas de [Meta Developer Dashboard](https://developers.facebook.com/):

```bash
PHONE_NUMBER_ID=tu_phone_number_id    # WhatsApp → API Setup
WABA_ID=tu_waba_id                    # WhatsApp → Settings
WHATSAPP_TOKEN=tu_token_permanente    # WhatsApp → API Setup
VERIFY_TOKEN=rsi_otono_2026          # Tu elección
```

### OpenAI (Opcional - mejora respuestas)

```bash
OPENAI_API_KEY=tu_openai_api_key     # Para respuestas AI avanzadas
```

**Sin OpenAI:** El bot funciona con respuestas inteligentes basadas en keywords.

---

## 📊 Arquitectura del Sistema

```
Estudiante (WhatsApp)
    ↓
WhatsApp Business API (Meta)
    ↓ [Opcional: Meta Business Agent Skills]
    ↓
Flask Bot (app.py)
    ├── Webhook Handler
    ├── AIAssistant (OpenAI o Fallback)
    └── WhatsAppClient
    ↓
Respuesta enviada al estudiante
```

**Ver diagrama completo:** `ARCHITECTURE.md`

---

## 🎯 Casos de Uso

### Caso 1: Estudiante pregunta sobre economía circular

**Estudiante:** "¿Qué es economía circular?"

**Bot:** "♻️ La economía circular busca minimizar residuos y maximizar el valor de los recursos mediante sistemas de ciclo cerrado. Se basa en reducir, reusar, reciclar y regenerar. ¿Qué aspecto específico te interesa profundizar?"

### Caso 2: Estudiante pide ayuda con tarea

**Estudiante:** "Tengo dudas sobre la tarea 2"

**Bot:** "📚 Para ayudarte mejor con la tarea, necesito tu nombre completo y matrícula. ¿Sobre qué aspecto específico de la tarea 2 tienes dudas?"

*[El bot guía sin resolver la tarea directamente]*

### Caso 3: Mensaje poco claro

**Estudiante:** "asdfgh"

**Bot:** "No estoy seguro de entender tu pregunta. Soy un asistente académico especializado en RSI. Puedo ayudarte con economía circular, sostenibilidad o RSC. ¿Tienes alguna consulta sobre el curso?"

---

## 🚀 Opciones de Deploy

### Opción 1: Railway (Recomendado)
```bash
railway init
railway up
```

### Opción 2: Render
- Conecta tu repo GitHub
- Build: `pip install -r requirements.txt`
- Start: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

### Opción 3: Docker
```bash
docker-compose up -d
```

### Opción 4: Heroku
```bash
heroku create
git push heroku main
```

**Ver guías detalladas:** `WHATSAPP_BOT_README.md` → Sección "Deployment"

---

## 🧪 Testing

### Test Automático
```bash
python test_bot.py
```

Verifica:
- ✅ Imports de paquetes
- ✅ Variables de entorno
- ✅ Inicialización de app
- ✅ Endpoints funcionales
- ✅ Respuestas de AI

### Test Manual (con ngrok)
```bash
# Terminal 1: Start bot
python app.py

# Terminal 2: Expose con ngrok
ngrok http 5000

# Usa la URL de ngrok en Meta webhook config
# Envía mensajes desde WhatsApp
```

---

## ❓ FAQ

### ¿Necesito OpenAI para que funcione?
No. El bot tiene respuestas inteligentes basadas en keywords. OpenAI mejora las respuestas pero no es requerido.

### ¿Necesito configurar las skills?
No es obligatorio. El Flask bot funciona independientemente. Las skills son un **enhancement opcional**.

### ¿Puedo usar solo Meta Business Agent sin el Flask bot?
Sí. Lee `SKILLS_CONFIGURATION_GUIDE.md` → "Configuración B: Meta Agent Only"

### ¿Cuál es la mejor opción?
**Híbrido** (Flask bot + Skills) da el mejor resultado, pero requiere más configuración inicial.

### ¿Cómo obtengo credenciales de Meta?
1. Ve a [developers.facebook.com](https://developers.facebook.com/)
2. Crea una app → Añade producto WhatsApp
3. Sigue el wizard de configuración
4. Copia Phone Number ID, WABA ID, y Token

### ¿Cuánto cuesta?
- **WhatsApp Business API:** Gratis para < 1000 conversaciones/mes
- **OpenAI API:** ~$0.002 por mensaje con GPT-4o-mini
- **Hosting:** Railway/Render tienen free tier

---

## 🆘 Troubleshooting

### Problema: "Error: Missing credentials"
**Solución:** Verifica que `.env` tenga todas las variables requeridas.

### Problema: Webhook no recibe mensajes
**Solución:** 
1. Verifica que uses HTTPS (Meta no acepta HTTP)
2. Confirma webhook URL en Meta Dashboard
3. Verifica que VERIFY_TOKEN coincida

### Problema: Bot no responde
**Solución:**
1. Revisa logs: `python app.py` (modo development)
2. Ejecuta `python test_bot.py`
3. Verifica `/health` endpoint

**Ver más:** `ARCHITECTURE.md` → Sección "Troubleshooting"

---

## 📞 Soporte

- **Documentación técnica:** Lee los archivos `.md` en este repo
- **Meta API:** [developers.facebook.com/docs](https://developers.facebook.com/docs/whatsapp)
- **Issues:** Abre un issue en GitHub
- **Curso RSI:** Contacta al profesor del curso

---

## 🗂️ Estructura del Proyecto

```
.
├── app.py                          # Bot Flask principal ⭐
├── skills_manager.py               # Gestión de skills ⭐
├── test_bot.py                     # Tests
├── requirements.txt                # Dependencias Python
├── .env.whatsapp                   # Template de env vars
├── Dockerfile                      # Configuración Docker
├── docker-compose.yml              # Orquestación Docker
│
├── README.md                       # ← EMPEZAR AQUÍ ⭐
├── WHATSAPP_BOT_README.md         # Docs completas del bot
├── ARCHITECTURE.md                 # Arquitectura del sistema
│
├── SKILLS_QUICK_REFERENCE.md      # Cheat sheet de skills
├── RSI_SKILLS_TEMPLATES.md        # 10 skills listas
└── SKILLS_CONFIGURATION_GUIDE.md  # Guía completa de skills
```

---

## 🎓 Próximos Pasos

### Desarrolladores:
1. ✅ Clonar repo
2. ✅ Instalar deps: `pip install -r requirements.txt`
3. ✅ Configurar `.env`
4. ✅ Probar: `python test_bot.py`
5. ✅ Correr: `python app.py`
6. 🔄 Opcional: Upload skills: `python skills_manager.py --upload`
7. 🚀 Deploy a producción

### Usuarios no-técnicos:
1. ✅ Ir a Meta Business Suite
2. ✅ Configurar Meta Business Agent
3. ✅ Copiar skills de `RSI_SKILLS_TEMPLATES.md`
4. ✅ Probar en Test chat
5. ✅ Conectar WhatsApp
6. 🚀 Lanzar con estudiantes

### Administradores:
1. ✅ Revisar `ARCHITECTURE.md` para entender el sistema
2. ✅ Configurar monitoring (health checks)
3. ✅ Setup alerting
4. ✅ Revisar logs regularmente
5. 🔄 Iterar según feedback de estudiantes

---

## 📈 Mejoras Futuras

- [ ] Base de datos para historial de conversaciones
- [ ] Dashboard de analytics
- [ ] Sistema de gestión de estudiantes
- [ ] Tracking de tareas y deadlines
- [ ] Multi-idioma (Inglés/Español)
- [ ] Rate limiting
- [ ] Webhook signature verification
- [ ] Integración con LMS (Moodle, Canvas)

---

## 📄 Licencia

MIT License - Ver `LICENSE` file

---

## 🙏 Agradecimientos

- Meta WhatsApp Business API
- OpenAI GPT-4
- Flask framework
- Curso RSI - Otoño 2026

---

**Versión:** 1.0.0  
**Última actualización:** Septiembre 2026  
**Curso:** Responsabilidad Social en la Industria - Otoño 2026  
**Mantenido por:** [Tu nombre/equipo]

---

## 📖 Guía de Lectura Recomendada

**Si tienes 5 minutos:** Lee este `README.md`

**Si tienes 15 minutos:** 
1. Este `README.md`
2. `SKILLS_QUICK_REFERENCE.md`

**Si tienes 30 minutos:**
1. Este `README.md`
2. `WHATSAPP_BOT_README.md`
3. `SKILLS_QUICK_REFERENCE.md`

**Si tienes 1 hora (recomendado):**
1. Este `README.md`
2. `WHATSAPP_BOT_README.md`
3. `ARCHITECTURE.md`
4. `SKILLS_CONFIGURATION_GUIDE.md`

**Si eres desarrollador:**
- Lee todo + revisa `app.py` y `skills_manager.py`

**Si eres usuario no-técnico:**
- `README.md` + `SKILLS_CONFIGURATION_GUIDE.md` (Método 1)

---

¡Disfruta tu bot de WhatsApp para RSI! 🎓♻️🌱🤝
