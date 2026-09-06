# WhatsApp Bot - DISTUM PALM DIAMANTE con EasyBroker

## 🚀 Configuración en Vivo - RÁPIDO

### 1. Variables de Entorno (.env)

```bash
# WhatsApp Business API (Meta)
PHONE_NUMBER_ID=tu_phone_number_id_aqui
WHATSAPP_TOKEN=tu_token_permanente_aqui
VERIFY_TOKEN=distum_palm_2026

# EasyBroker API
EASYBROKER_API_KEY=tu_api_key_de_easybroker

# Configuración Distum
ASESOR_NAME="Asesor Distum"
ASESOR_PHONE="+52xxxxxxxxxx"
FLASK_ENV=production
PORT=5000
```

---

## 📋 Checklist de 10 Minutos para Ir en Vivo

### ✅ Paso 1: Obtener Credenciales (5 min)

#### A) Meta WhatsApp Business API
1. Ve a https://developers.facebook.com/
2. Tu App → WhatsApp → API Setup
3. Copia:
   - **Phone Number ID**
   - **Access Token** (permanent)

#### B) EasyBroker API
1. Inicia sesión en https://www.easybroker.com/
2. Ve a Configuración → Integraciones → API
3. Copia tu **API Key**

### ✅ Paso 2: Configurar (2 min)

```bash
# Copia el template
cp .env.whatsapp .env

# Edita con tus credenciales
nano .env
```

Pega tus credenciales:
```
PHONE_NUMBER_ID=123456789012345
WHATSAPP_TOKEN=EAAxxxxxxxxxx
EASYBROKER_API_KEY=l7u502xxxxxxxxx
```

### ✅ Paso 3: Instalar y Probar (2 min)

```bash
# Instala dependencias
pip install -r requirements.txt

# Prueba local
python app_distum.py
```

Deberías ver:
```
Starting Distum Palm Diamante WhatsApp Bot on port 5000
Zone: Metepec, Estado de México
EasyBroker: ✓ Connected
```

### ✅ Paso 4: Ir en Vivo (1 min)

**Opción A: Railway (más fácil)**
```bash
railway login
railway init
railway up
```

**Opción B: Render**
1. Conecta tu repo GitHub
2. Build: `pip install -r requirements.txt`
3. Start: `python app_distum.py`
4. Añade env vars en dashboard

**Opción C: Docker**
```bash
docker-compose up -d
```

### ✅ Paso 5: Configurar Webhook en Meta (1 min)

1. Meta Developer Dashboard → Tu App → WhatsApp → Configuration
2. **Callback URL:** `https://tu-dominio.com/webhook`
3. **Verify Token:** `distum_palm_2026`
4. **Webhook Fields:** Marca `messages`
5. Click **Verify and Save**

---

## 🎯 Cómo Funciona el Bot

### Flujo Automático

```
Cliente: "Hola, info de casas"
    ↓
Bot: "¡Bienvenido a Distum Palm Diamante! 🏡
     ¿Buscas para vivir o invertir?
     ¿Cuál es tu presupuesto? Ej: $2-3M, $3-4M"
    ↓
Cliente: "3 a 4 millones para vivir"
    ↓
Bot: [Consulta EasyBroker API]
     "¡Encontré 3 propiedades en Metepec:
     
     🏡 Casa en Residencial...
     💰 $3,500,000
     🛏 3 recámaras, 2 baños
     📐 180 m²
     Ver más: [link EasyBroker]
     
     ---
     
     [Propiedad 2...]
     [Propiedad 3...]
     
     ¿Cuál te interesa? Te agendo visita 📅"
    ↓
Cliente: "Quiero ver la primera"
    ↓
Bot: [Detecta señal caliente]
     "¡Perfecto! 🔥
     Te conecto AHORA con Asesor Distum.
     En 2 minutos te escribe para agendar.
     ¿Confirmado? 👍"
    ↓
[Notifica a tu asesor humano para que cierre]
```

---

## 🔥 Detección Automática de Leads Calientes

El bot escala INMEDIATAMENTE al asesor cuando detecta:

- ✅ "Quiero ver"
- ✅ "Cuando puedo visitar"
- ✅ "Agendar"
- ✅ "Ya tengo el enganche"
- ✅ "Crédito aprobado"
- ✅ "¿Cuánto es lo menos?"
- ✅ "Urgente"
- ✅ "Necesito"

---

## 📊 Integración con EasyBroker

### Qué Hace el Bot con EasyBroker

1. **Búsqueda Inteligente**
   - Filtra por rango de presupuesto
   - Filtra por tipo de propiedad
   - Solo muestra propiedades publicadas

2. **Formato Automático**
   - Extrae: título, precio, recámaras, baños, m²
   - Genera mensaje bonito para WhatsApp
   - Incluye link directo a ficha en EasyBroker

3. **Actualización en Tiempo Real**
   - Siempre muestra inventario actual
   - No hay info desactualizada
   - Sincronizado con tu CRM

### API de EasyBroker - Endpoints Usados

```python
# Obtener propiedades disponibles
GET https://api.easybroker.com/v1/properties
Params:
- limit=5
- search[statuses][]=published
- search[min_price]=3000000
- search[max_price]=4000000

# Respuesta:
{
  "content": [
    {
      "title": "Casa en Metepec...",
      "operations": [{"formatted_amount": "$3,500,000"}],
      "bedrooms": 3,
      "bathrooms": 2,
      "construction_size": 180,
      "location": "Metepec",
      "public_url": "https://..."
    }
  ]
}
```

---

## 🎨 Personalización para Distum

### Branding Incluido

```python
BRAND_NAME = "Distum Palm Diamante"
MAIN_ZONE = "Metepec, Estado de México"
ASESOR_NAME = "Asesor Distum"
```

### Saludo Personalizado

```
¡Hola! Bienvenido a *Distum Palm Diamante* 🏡

Somos especialistas en Metepec, Estado de México, 
con inventario exclusivo de casas y departamentos.

Para mostrarte las mejores opciones:

1️⃣ ¿Buscas para vivir o invertir?
2️⃣ ¿Cuál es tu presupuesto aproximado?
   Ej: $2-3M, $3-4M, $4M+

¡Tenemos propiedades increíbles disponibles! 🔥
```

---

## 💰 Rangos de Presupuesto Automáticos

El bot detecta:

| Cliente dice | Bot interpreta |
|--------------|----------------|
| "2 a 3" / "2-3M" | $2,000,000 - $3,000,000 |
| "3 a 4" / "3-4M" | $3,000,000 - $4,000,000 |
| "4 a 5" / "4-5M" | $4,000,000 - $5,000,000 |
| "5" / "5M+" | $5,000,000+ |

---

## 📱 Qué Recibe el Cliente

### Ejemplo de Propiedad Formateada

```
🏡 *Casa Residencial en Metepec*

💰 Precio: $3,500,000
🛏 Recámaras: 3
🚿 Baños: 2
📐 M² construcción: 180
📍 Ubicación: Metepec

Ver más: https://easybroker.com/mx/...
```

---

## 🔧 Troubleshooting Rápido

### Problema: "EasyBroker not configured"

**Solución:**
```bash
# Verifica tu API key
curl -H "X-Authorization: TU_API_KEY" \
  https://api.easybroker.com/v1/properties?limit=1

# Debería devolver JSON con propiedades
# Si da error 401: API key incorrecta
# Si da error 404: endpoint incorrecto
```

### Problema: No muestra propiedades

**Diagnóstico:**
```bash
# Chequea health
curl http://localhost:5000/health

# Debe decir "easybroker_connected": true
```

**Soluciones:**
1. Verifica que tengas propiedades publicadas en EasyBroker
2. Ajusta rangos de presupuesto en el código si es necesario
3. Revisa logs: `python app_distum.py` (modo development)

### Problema: Webhook no recibe mensajes

**Checklist:**
- ✅ Bot corriendo (Railway/Render)
- ✅ HTTPS habilitado (Meta requiere SSL)
- ✅ Webhook configurado en Meta con URL correcta
- ✅ VERIFY_TOKEN coincide: `distum_palm_2026`

---

## 🚀 Comandos de Deploy

### Railway
```bash
railway login
railway init
railway up

# Añadir env vars
railway variables set PHONE_NUMBER_ID=xxx
railway variables set WHATSAPP_TOKEN=xxx
railway variables set EASYBROKER_API_KEY=xxx
```

### Render
```bash
# En dashboard de Render:
# 1. New Web Service
# 2. Connect GitHub repo
# 3. Build: pip install -r requirements.txt
# 4. Start: python app_distum.py
# 5. Environment:
#    PHONE_NUMBER_ID=xxx
#    WHATSAPP_TOKEN=xxx
#    EASYBROKER_API_KEY=xxx
```

### Docker
```bash
docker build -t distum-bot .
docker run -p 5000:5000 \
  -e PHONE_NUMBER_ID=xxx \
  -e WHATSAPP_TOKEN=xxx \
  -e EASYBROKER_API_KEY=xxx \
  distum-bot
```

---

## 📊 Métricas a Monitorear

### Dashboard Recomendado

```
Hoy:
- 📨 Mensajes recibidos: XX
- ✅ Leads calificados: XX
- 🔥 Leads calientes escalados: XX
- 🏡 Propiedades enviadas: XX

Semana:
- 📈 Tasa de calificación: XX%
- 🎯 Tasa de escalamiento: XX%
- ⏱ Tiempo promedio de respuesta: XX segundos
```

### Logs Importantes

```bash
# Ver logs en vivo
tail -f logs/distum_bot.log

# Buscar leads calientes
grep "hot lead" logs/distum_bot.log

# Buscar errores de EasyBroker
grep "Error fetching from EasyBroker" logs/distum_bot.log
```

---

## 🎯 Próximos Pasos Después de Ir en Vivo

### Semana 1: Monitoreo
- ✅ Revisa primeras 10-20 conversaciones
- ✅ Ajusta rangos de presupuesto si es necesario
- ✅ Valida que propiedades se muestren correctamente

### Semana 2: Optimización
- ✅ Añade Meta Business Agent Skills (opcional)
- ✅ Configura notificaciones para asesor
- ✅ Integra con CRM (si lo tienes)

### Semana 3: Escala
- ✅ Activa campañas de Meta Ads
- ✅ Comparte número en redes sociales
- ✅ Mide conversión de lead a visita

---

## 📞 Soporte y Ayuda

### Si algo no funciona:

1. **Revisa logs:**
   ```bash
   python app_distum.py  # Modo debug
   ```

2. **Prueba health check:**
   ```bash
   curl http://localhost:5000/health
   ```

3. **Verifica EasyBroker:**
   ```bash
   curl -H "X-Authorization: TU_KEY" \
     https://api.easybroker.com/v1/properties?limit=1
   ```

4. **Prueba WhatsApp:**
   - Envía mensaje a tu número
   - Revisa logs para ver si llega el webhook

---

## ✅ Checklist Final Antes de Lanzar

- [ ] Credenciales de Meta configuradas
- [ ] API Key de EasyBroker configurada
- [ ] Bot corriendo en servidor (Railway/Render)
- [ ] Webhook configurado en Meta
- [ ] Mensaje de prueba enviado y respondido
- [ ] EasyBroker devuelve propiedades correctamente
- [ ] Escalamiento a asesor probado
- [ ] Health check responde OK

---

**¡Listo para ir en VIVO!** 🚀

El bot ya está conectado a EasyBroker y listo para capturar leads de Distum Palm Diamante en Metepec.

**Tiempo estimado de setup:** 10-15 minutos  
**Costo mensual:** $0 (con free tiers de Railway/Render)  
**WhatsApp:** Gratis hasta 1000 conversaciones/mes  
**EasyBroker API:** Incluido en tu plan

---

**Última actualización:** Septiembre 2026  
**Versión:** 1.0.0 - Distum Palm Diamante  
**Zona:** Metepec, Estado de México
