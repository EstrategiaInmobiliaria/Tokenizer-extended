# 📁 WhatsApp Bot RSI - Índice de Archivos

Este documento te ayuda a navegar todos los archivos del proyecto y saber cuál leer según tus necesidades.

---

## 🚀 Empezar Aquí

| Archivo | Para quién | Tiempo | Descripción |
|---------|-----------|--------|-------------|
| **`README_ES.md`** | 👥 Todos | 5 min | Guía de inicio rápido en español |
| **`WHATSAPP_BOT_README.md`** | 👨‍💻 Desarrolladores | 15 min | Documentación técnica completa del bot |

---

## 📚 Documentación por Tema

### 🤖 Bot de WhatsApp

| Archivo | Contenido | Para quién |
|---------|-----------|-----------|
| **`WHATSAPP_BOT_README.md`** | Setup completo, API docs, deployment | Desarrolladores |
| **`ARCHITECTURE.md`** | Diagramas, flujo de datos, componentes | Arquitectos, desarrolladores senior |
| **`app.py`** | Código fuente del Flask bot | Desarrolladores |
| **`test_bot.py`** | Tests automatizados | Desarrolladores, QA |

### 🎯 Meta Business Agent Skills

| Archivo | Contenido | Para quién |
|---------|-----------|-----------|
| **`SKILLS_QUICK_REFERENCE.md`** | Cheat sheet de 1 página | Todos (quick lookup) |
| **`RSI_SKILLS_TEMPLATES.md`** | 10 skills listas para copiar | Usuarios no-técnicos, admins |
| **`SKILLS_CONFIGURATION_GUIDE.md`** | Guía completa de configuración | Desarrolladores, power users |
| **`skills_manager.py`** | Script de gestión de skills | Desarrolladores |

### 🛠️ Configuración

| Archivo | Contenido | Para quién |
|---------|-----------|-----------|
| **`.env.whatsapp`** | Template de variables de entorno | Desarrolladores |
| **`requirements.txt`** | Dependencias Python | Desarrolladores |
| **`Dockerfile`** | Configuración Docker | DevOps |
| **`docker-compose.yml`** | Orquestación Docker | DevOps |

---

## 🎯 Rutas de Lectura por Rol

### 👨‍💻 Desarrollador Backend

**Objetivo:** Implementar y desplegar el bot

**Ruta recomendada (45 min):**
1. `README_ES.md` (5 min) - Overview
2. `WHATSAPP_BOT_README.md` (20 min) - Setup técnico
3. `app.py` (código) (10 min) - Revisar implementación
4. `ARCHITECTURE.md` (10 min) - Entender el sistema

**Después:**
- Configurar `.env`
- Ejecutar `test_bot.py`
- Deploy a staging

### 🎨 Desarrollador Frontend / Integraciones

**Objetivo:** Integrar con el bot o construir UI

**Ruta recomendada (30 min):**
1. `README_ES.md` (5 min)
2. `WHATSAPP_BOT_README.md` → Sección API (10 min)
3. `ARCHITECTURE.md` → Sección "Endpoints" (5 min)
4. `ARCHITECTURE.md` → Sección "Flujo de Datos" (10 min)

**Después:**
- Probar endpoints con cURL
- Integrar con tu sistema

### 📊 Product Owner / Project Manager

**Objetivo:** Entender qué hace el sistema y cómo funciona

**Ruta recomendada (20 min):**
1. `README_ES.md` (5 min) - Overview completo
2. `ARCHITECTURE.md` → "Vista General del Sistema" (5 min)
3. `RSI_SKILLS_TEMPLATES.md` → Ver las 10 skills (5 min)
4. `README_ES.md` → Sección "Casos de Uso" (5 min)

**Después:**
- Definir métricas de éxito
- Planear rollout con estudiantes

### 🎓 Profesor / Administrador del Curso

**Objetivo:** Configurar el bot para el curso RSI

**Ruta recomendada (25 min):**
1. `README_ES.md` (5 min)
2. `RSI_SKILLS_TEMPLATES.md` (10 min) - Ver skills disponibles
3. `SKILLS_CONFIGURATION_GUIDE.md` → Método 1 (Meta Suite) (10 min)

**Después:**
- Ir a Meta Business Suite
- Copiar y pegar skills
- Probar en Test chat

### ⚙️ DevOps / SRE

**Objetivo:** Desplegar y monitorear en producción

**Ruta recomendada (35 min):**
1. `README_ES.md` (5 min)
2. `WHATSAPP_BOT_README.md` → Sección "Deployment" (10 min)
3. `ARCHITECTURE.md` → "Monitoreo y Métricas" (10 min)
4. `Dockerfile` + `docker-compose.yml` (código) (10 min)

**Después:**
- Setup CI/CD pipeline
- Configurar monitoring (Datadog, Prometheus)
- Configurar alerting

### 🆘 Soporte Técnico

**Objetivo:** Resolver issues de usuarios

**Ruta recomendada (15 min):**
1. `README_ES.md` → Sección "Troubleshooting" (5 min)
2. `ARCHITECTURE.md` → Sección "Troubleshooting" (10 min)

**Tener a mano:**
- `SKILLS_QUICK_REFERENCE.md` (common errors)
- `WHATSAPP_BOT_README.md` → "Troubleshooting"

---

## 📖 Documentación por Profundidad

### 🏃 Quick (5-10 min)

**Solo necesito empezar YA:**
1. `README_ES.md` → Sección "Inicio Rápido (5 minutos)"
2. Ejecutar comandos
3. Listo

### 🚶 Medium (20-30 min)

**Quiero entender cómo funciona:**
1. `README_ES.md` (5 min)
2. `WHATSAPP_BOT_README.md` (15 min)
3. `SKILLS_QUICK_REFERENCE.md` (5 min)

### 🧗 Deep (1-2 horas)

**Necesito dominar el sistema completo:**
1. `README_ES.md` (5 min)
2. `WHATSAPP_BOT_README.md` (20 min)
3. `ARCHITECTURE.md` (20 min)
4. `SKILLS_CONFIGURATION_GUIDE.md` (30 min)
5. Código fuente: `app.py`, `skills_manager.py` (30 min)

---

## 🎯 Documentación por Objetivo

### "Quiero correr el bot localmente"
→ `README_ES.md` → Sección "Inicio Rápido"

### "Quiero desplegar a producción"
→ `WHATSAPP_BOT_README.md` → Sección "Deployment"

### "Quiero configurar las skills"
→ `SKILLS_CONFIGURATION_GUIDE.md` → Método 1 o 2

### "Quiero ver qué skills hay disponibles"
→ `RSI_SKILLS_TEMPLATES.md` (todas las skills)
→ `SKILLS_QUICK_REFERENCE.md` (tabla resumen)

### "Quiero entender cómo funciona el sistema"
→ `ARCHITECTURE.md`

### "Tengo un error y no sé qué hacer"
→ `README_ES.md` → "Troubleshooting"
→ `ARCHITECTURE.md` → "Troubleshooting"

### "Quiero saber qué endpoints hay"
→ `WHATSAPP_BOT_README.md` → "API Endpoints"

### "Quiero modificar el código"
→ `app.py` (Flask bot)
→ `skills_manager.py` (Skills manager)
→ `ARCHITECTURE.md` (para entender arquitectura)

### "Quiero añadir nuevas skills"
→ `SKILLS_CONFIGURATION_GUIDE.md`
→ `skills_manager.py` → Editar `RSI_SKILLS`

---

## 📊 Matriz de Documentación

| Necesito... | Archivo | Sección |
|------------|---------|---------|
| **Setup rápido** | `README_ES.md` | "Inicio Rápido (5 minutos)" |
| **Credenciales de Meta** | `WHATSAPP_BOT_README.md` | "Configuration" |
| **Instalar dependencias** | `requirements.txt` + `README_ES.md` | - |
| **Variables de entorno** | `.env.whatsapp` | - |
| **Probar el bot** | `test_bot.py` + `README_ES.md` | "Testing" |
| **Correr en desarrollo** | `README_ES.md` | "Comandos Útiles" |
| **Desplegar a producción** | `WHATSAPP_BOT_README.md` | "Deployment" |
| **Configurar Docker** | `Dockerfile` + `docker-compose.yml` | - |
| **Ver skills disponibles** | `RSI_SKILLS_TEMPLATES.md` | Todas las skills |
| **Configurar skills (visual)** | `SKILLS_CONFIGURATION_GUIDE.md` | "Método 1" |
| **Configurar skills (API)** | `SKILLS_CONFIGURATION_GUIDE.md` | "Método 2" |
| **Upload skills automático** | `skills_manager.py` + `README_ES.md` | "Comandos Útiles" |
| **Entender arquitectura** | `ARCHITECTURE.md` | "Vista General" |
| **Ver flujo de datos** | `ARCHITECTURE.md` | "Flujo de Datos Detallado" |
| **Troubleshooting** | `README_ES.md` + `ARCHITECTURE.md` | "Troubleshooting" |
| **API reference** | `WHATSAPP_BOT_README.md` | "API Endpoints" |
| **Ejemplos de uso** | `README_ES.md` | "Casos de Uso" |
| **Monitoreo** | `ARCHITECTURE.md` | "Monitoreo y Métricas" |
| **Health checks** | `WHATSAPP_BOT_README.md` | "Health Monitoring" |
| **Security** | `WHATSAPP_BOT_README.md` | "Security Considerations" |

---

## 🔍 Búsqueda Rápida de Conceptos

### Bot de Flask
- **Setup:** `WHATSAPP_BOT_README.md`
- **Código:** `app.py`
- **Tests:** `test_bot.py`
- **Arquitectura:** `ARCHITECTURE.md`

### Skills
- **Overview:** `SKILLS_QUICK_REFERENCE.md`
- **Templates:** `RSI_SKILLS_TEMPLATES.md`
- **Guía completa:** `SKILLS_CONFIGURATION_GUIDE.md`
- **Script:** `skills_manager.py`

### Deployment
- **Railway/Render:** `WHATSAPP_BOT_README.md` → "Deployment"
- **Docker:** `Dockerfile` + `docker-compose.yml`

### Configuración
- **Env vars:** `.env.whatsapp`
- **Dependencias:** `requirements.txt`

### API
- **Endpoints:** `WHATSAPP_BOT_README.md` → "API Endpoints"
- **WhatsApp API:** `app.py` → `WhatsAppClient`
- **Skills API:** `skills_manager.py` → `SkillsManager`

### Troubleshooting
- **Quick:** `README_ES.md` → "Troubleshooting"
- **Detallado:** `ARCHITECTURE.md` → "Troubleshooting"

---

## 📏 Tamaño de Archivos (Tiempo de lectura estimado)

| Archivo | Líneas | Tiempo lectura | Nivel |
|---------|--------|----------------|-------|
| `README_ES.md` | ~500 | 5-10 min | Básico |
| `README.md` (original repo) | ~20 | 1 min | - |
| `WHATSAPP_BOT_README.md` | ~400 | 15-20 min | Intermedio |
| `ARCHITECTURE.md` | ~550 | 20-25 min | Avanzado |
| `SKILLS_QUICK_REFERENCE.md` | ~250 | 5 min | Básico |
| `RSI_SKILLS_TEMPLATES.md` | ~300 | 10 min | Básico |
| `SKILLS_CONFIGURATION_GUIDE.md` | ~500 | 30 min | Intermedio |
| `app.py` | ~350 | 15 min | Código |
| `skills_manager.py` | ~450 | 20 min | Código |
| `test_bot.py` | ~200 | 10 min | Código |

**Total documentación:** ~2,500 líneas  
**Total código:** ~1,000 líneas  
**Tiempo lectura completa:** ~2-3 horas

---

## 🎯 Flows Comunes

### Flow 1: "Soy nuevo, ¿por dónde empiezo?"
```
README_ES.md (5 min)
    ↓
¿Eres técnico?
    ├─ Sí → WHATSAPP_BOT_README.md (15 min)
    │         ↓
    │      Setup local + tests
    │
    └─ No → SKILLS_CONFIGURATION_GUIDE.md → Método 1 (10 min)
              ↓
           Meta Business Suite
```

### Flow 2: "Quiero desplegar YA"
```
README_ES.md → "Inicio Rápido" (5 min)
    ↓
pip install + .env config (5 min)
    ↓
python test_bot.py (2 min)
    ↓
Deploy a Railway/Render (10 min)
    ↓
Configurar webhook en Meta (5 min)
    ↓
✅ Listo (27 min total)
```

### Flow 3: "Necesito entender todo el sistema"
```
README_ES.md (5 min)
    ↓
ARCHITECTURE.md (20 min)
    ↓
WHATSAPP_BOT_README.md (15 min)
    ↓
SKILLS_CONFIGURATION_GUIDE.md (30 min)
    ↓
Revisar código: app.py + skills_manager.py (30 min)
    ↓
✅ Dominio completo (100 min total)
```

---

## 🗺️ Mapa Mental del Proyecto

```
WhatsApp Bot RSI
│
├── 📖 Documentación
│   ├── README_ES.md (empezar aquí)
│   ├── WHATSAPP_BOT_README.md (bot docs)
│   ├── ARCHITECTURE.md (arquitectura)
│   │
│   └── Skills Docs
│       ├── SKILLS_QUICK_REFERENCE.md (cheat sheet)
│       ├── RSI_SKILLS_TEMPLATES.md (templates)
│       └── SKILLS_CONFIGURATION_GUIDE.md (guía completa)
│
├── 💻 Código
│   ├── app.py (Flask bot)
│   ├── skills_manager.py (Skills manager)
│   └── test_bot.py (Tests)
│
├── ⚙️ Configuración
│   ├── .env.whatsapp (template)
│   ├── requirements.txt (deps)
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── 📊 Utilities
    └── FILE_INDEX.md (este archivo)
```

---

## 🚀 Quick Links

### Para empezar:
- [README_ES.md](README_ES.md) - Guía de inicio rápido
- [WHATSAPP_BOT_README.md](WHATSAPP_BOT_README.md) - Docs técnicas

### Skills:
- [SKILLS_QUICK_REFERENCE.md](SKILLS_QUICK_REFERENCE.md) - Cheat sheet
- [RSI_SKILLS_TEMPLATES.md](RSI_SKILLS_TEMPLATES.md) - Templates listos

### Avanzado:
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura completa
- [SKILLS_CONFIGURATION_GUIDE.md](SKILLS_CONFIGURATION_GUIDE.md) - Guía detallada

### Código:
- [app.py](app.py) - Flask bot
- [skills_manager.py](skills_manager.py) - Skills manager
- [test_bot.py](test_bot.py) - Tests

---

## 💡 Tips de Navegación

1. **Usa Ctrl+F (Cmd+F en Mac)** para buscar términos específicos en los docs
2. **Empieza siempre por `README_ES.md`** - es el mejor punto de entrada
3. **No necesitas leer todo** - usa este índice para ir directo a lo que necesitas
4. **Los archivos están interconectados** - encontrarás referencias entre ellos
5. **Hay redundancia intencional** - conceptos importantes se explican en múltiples lugares
6. **El código está bien documentado** - lee los comentarios en `app.py` y `skills_manager.py`

---

## 📞 ¿Sigues perdido?

Si después de revisar este índice no sabes por dónde empezar:

1. **Si eres técnico:** Lee `README_ES.md` completo (10 min)
2. **Si no eres técnico:** Lee `README_ES.md` hasta "Casos de Uso" (5 min)
3. **Si tienes prisa:** Ve a `README_ES.md` → "Inicio Rápido (5 minutos)"
4. **Si necesitas ayuda:** Abre un issue en GitHub con tu pregunta específica

---

**Última actualización:** Septiembre 2026  
**Versión:** 1.0.0  
**Mantenido por:** Team RSI Bot
