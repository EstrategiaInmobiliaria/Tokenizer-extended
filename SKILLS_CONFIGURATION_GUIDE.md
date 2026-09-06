# Configuración de Skills - Meta Business Agent

## Guía Completa para RSI Otoño 2026

Esta guía explica cómo configurar **skills (habilidades comportamentales)** para tu Meta Business Agent del curso RSI.

---

## 📋 Índice

1. [¿Qué son las Skills?](#qué-son-las-skills)
2. [Skills vs Knowledge](#skills-vs-knowledge)
3. [Método 1: Configuración desde Meta Business Suite](#método-1-meta-business-suite)
4. [Método 2: Configuración por API con Python](#método-2-configuración-por-api)
5. [Skills Predefinidas para RSI](#skills-predefinidas-para-rsi)
6. [Mejores Prácticas](#mejores-prácticas)
7. [Ejemplos de Uso](#ejemplos-de-uso)
8. [Troubleshooting](#troubleshooting)

---

## ¿Qué son las Skills?

Las **skills (habilidades)** son **instrucciones de comportamiento** que le dicen al agente:
- Cómo responder en situaciones específicas
- Qué tono usar
- Qué pasos seguir
- Cuándo escalar a un humano

**No son conocimiento** (hechos, datos, documentos) - eso va en la sección **Knowledge**.

### Analogía
Piensa en las skills como el **manual de procedimientos** para un empleado nuevo:
- ✅ "Cuando un cliente pregunte por precios, haz X"
- ✅ "Si no sabes la respuesta, di Y"
- ❌ NO son: "El precio del producto A es $100" (eso es Knowledge)

---

## Skills vs Knowledge

| Skills | Knowledge |
|--------|-----------|
| **Comportamiento**: Cómo actuar | **Información**: Qué saber |
| "Saluda al cliente con calidez" | "El curso es Otoño 2026" |
| "Pide matrícula para tareas" | "La economía circular es..." |
| "Escala cuando sea urgente" | "Política de entregas: X días" |
| Máx. 20,000 caracteres | Documentos, PDFs, FAQs |

**Combina ambos** para un agente completo:
- **Skills** → Guían el comportamiento
- **Knowledge** → Proveen los hechos
- **Personality** → Definen el tono general

---

## Método 1: Meta Business Suite

### Configuración Visual (Recomendado para la mayoría)

#### Paso 1: Acceder a Meta Business Suite
1. Ve a [Meta Business Suite](https://business.facebook.com/)
2. Selecciona tu cuenta de negocio
3. En el menú lateral: **All tools** → **Meta Business Agent**
4. Click en la pestaña **Skills** (Habilidades)

#### Paso 2: Crear una Skill
1. Click en **+ Create skill** / **+ Crear habilidad**
2. Completa los campos:

##### **Title (Título)** ⚠️ Restricciones estrictas
- Solo minúsculas, números y guiones (`-`)
- Máximo 64 caracteres
- Ejemplos válidos: `greeting-skill`, `pricing-questions`, `refund-policy`
- ❌ Inválidos: `Greeting Skill`, `greeting_skill`, `Greeting-Skill`

##### **Description (Descripción)**
- Cuándo debe aplicarse esta skill
- Máximo 1,024 caracteres
- Sea específico: "Apply when customer asks about..." es mejor que "General greeting"

##### **Skill (Instrucciones)**
- El contenido principal: pasos, reglas, ejemplos
- Máximo 20,000 caracteres
- Usa numeración, bullets, estructura clara

#### Paso 3: Guardar y Probar
1. Click **Save**
2. Ve a **Test chat** (Chat de prueba)
3. Envía mensajes que deberían activar la skill
4. Click **View sources** para ver qué skill usó el agente
5. Si no funciona: click **Reload** y prueba de nuevo

---

## Método 2: Configuración por API

### Requisitos
- `PHONE_NUMBER_ID` (WhatsApp Business Phone Number ID)
- `WHATSAPP_TOKEN` (Permanent Access Token)
- Python 3.7+ con `requests`

### Instalación
```bash
pip install requests python-dotenv
```

### Uso del Script Incluido

#### 1. Configurar Variables de Entorno
```bash
# En tu archivo .env
PHONE_NUMBER_ID=tu_phone_number_id
WHATSAPP_TOKEN=tu_token_permanente
```

#### 2. Ver Skills Predefinidas
```bash
python skills_manager.py
```

Esto muestra las 10 skills predefinidas para RSI sin subirlas.

#### 3. Subir Skills a Meta
```bash
python skills_manager.py --upload
```

Esto creará todas las skills RSI en tu Meta Business Agent.

#### 4. Listar Skills Existentes
```bash
python skills_manager.py --list
```

### API Manual (con cURL)

#### Crear una Skill
```bash
curl -X POST "https://api.facebook.com/{PHONE_NUMBER_ID}/agent_config/skills" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-API-Version: 2.0.0" \
  -d '{
    "title": "greeting-skill",
    "description": "Apply when customer first messages the agent",
    "skill": "1) Greet warmly\n2) Ask how to help\n3) Keep tone professional"
  }'
```

#### Listar Skills
```bash
curl -X GET "https://api.facebook.com/{PHONE_NUMBER_ID}/agent_config/skills" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "X-API-Version: 2.0.0"
```

#### Obtener una Skill Específica
```bash
curl -X GET "https://api.facebook.com/{PHONE_NUMBER_ID}/agent_config/skills/{SKILL_ID}" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "X-API-Version: 2.0.0"
```

#### Actualizar una Skill
```bash
curl -X PUT "https://api.facebook.com/{PHONE_NUMBER_ID}/agent_config/skills/{SKILL_ID}" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-API-Version: 2.0.0" \
  -d '{
    "title": "greeting-skill",
    "description": "Updated description",
    "skill": "Updated instructions"
  }'
```

#### Eliminar una Skill
```bash
curl -X DELETE "https://api.facebook.com/{PHONE_NUMBER_ID}/agent_config/skills/{SKILL_ID}" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "X-API-Version: 2.0.0"
```

---

## Skills Predefinidas para RSI

El script `skills_manager.py` incluye **10 skills especializadas** para el curso RSI:

### 1. **greeting-skill**
**Cuándo:** Primer mensaje del estudiante  
**Hace:** Saludo cálido + introducción + preguntar cómo ayudar  
**Emoji:** N/A

### 2. **circular-economy-questions**
**Cuándo:** Preguntas sobre economía circular, reciclaje, optimización de recursos  
**Hace:** Explica conceptos clave (max 3 líneas), ejemplos industriales, conecta con RSC  
**Emoji:** ♻️

### 3. **sustainability-questions**
**Cuándo:** Preguntas sobre sostenibilidad, ESG, medio ambiente  
**Hace:** Explica 3 pilares (ambiental, social, económico), menciona SDGs/triple bottom line  
**Emoji:** 🌱

### 4. **csr-rsc-questions**
**Cuándo:** Preguntas sobre RSC/CSR, ética empresarial  
**Hace:** Define RSC, áreas clave, ejemplos de empresas, beneficios económicos  
**Emoji:** 🤝

### 5. **assignment-help**
**Cuándo:** Estudiante menciona "tarea", "entrega", "trabajo"  
**Hace:** Pide nombre + matrícula, guía sin resolver la tarea, ofrece clarificar conceptos  
**Emoji:** 📚

### 6. **course-information**
**Cuándo:** Preguntas sobre syllabus, fechas, calificaciones, profesor  
**Hace:** Provee info conocida, admite cuando no sabe, sugiere revisar syllabus  
**Emoji:** 📅

### 7. **exam-preparation**
**Cuándo:** Preguntas sobre exámenes, quizzes, evaluación  
**Hace:** Sugiere áreas clave, métodos de estudio, pregunta qué temas son difíciles  
**Emoji:** 📝

### 8. **examples-case-studies**
**Cuándo:** Pide ejemplos, casos de estudio, empresas reales  
**Hace:** Provee 2-3 ejemplos concretos (Patagonia, Unilever, etc.), breve explicación  
**Emoji:** 💡

### 9. **unclear-or-offtopic**
**Cuándo:** Mensaje poco claro, fuera de tema, no relacionado al curso  
**Hace:** Pide clarificación, redirige a temas del curso, mantiene tono profesional  
**Emoji:** N/A

### 10. **human-handoff**
**Cuándo:** Estudiante pide hablar con profesor, queja, tema sensible, emergencia  
**Hace:** Reconoce necesidad, provee info de contacto o ofrece escalar, establece expectativas  
**Emoji:** 👨‍🏫

---

## Mejores Prácticas

### ✅ DO (Hacer)

1. **Sé Claro y Directo**
   ```
   ✅ "When customer asks about pricing:
       1) Ask for their location
       2) Provide base price
       3) Mention any current discounts"
   
   ❌ "Try to help with pricing if they ask"
   ```

2. **Usa Estructura Numerada**
   - Facilita que el agente siga pasos en orden
   - Evita ambigüedad

3. **Incluye Ejemplos Cuando Sea Útil**
   ```
   "Examples of urgent cases:
    - Account locked
    - Payment issues
    - Security concerns"
   ```

4. **Combina Skills + Knowledge + Personality**
   - **Personality:** "Tono cálido y profesional"
   - **Skills:** "Cómo saludar y manejar tareas"
   - **Knowledge:** "Fechas del curso, conceptos RSC"

5. **Empieza con Pocas Skills (3-7)**
   - Añade más según conversaciones reales
   - Itera basándote en el Test chat

6. **Usa Test Chat Regularmente**
   - Prueba cada skill después de crearla
   - Revisa "View sources" para ver qué se activó
   - Haz "Reload" si los cambios no aparecen

### ❌ DON'T (No Hacer)

1. **No Crees Skills Conflictivas**
   ```
   ❌ Skill 1: "Always escalate pricing questions"
   ❌ Skill 2: "Never escalate, handle all questions"
   ```

2. **No Uses Títulos Inválidos**
   ```
   ❌ "Greeting Skill" (tiene espacios, mayúsculas)
   ❌ "greeting_skill" (guiones bajos no permitidos)
   ✅ "greeting-skill"
   ```

3. **No Mezcles Comportamiento con Conocimiento**
   ```
   ❌ En Skill: "El precio es $50" → Esto va en Knowledge
   ✅ En Skill: "Cuando pregunten precio, consulta Knowledge base"
   ```

4. **No Hagas Skills Demasiado Largas**
   - Si una skill tiene 50 pasos, divídela en varias
   - Límite: 20,000 caracteres, pero apunta a 500-2000 para claridad

5. **No Olvides Probar**
   - Cada skill nueva = prueba en Test chat
   - Revisa que no interfiera con skills existentes

---

## Ejemplos de Uso

### Ejemplo 1: Estudiante Pregunta por Economía Circular

**Estudiante:** "¿Qué es economía circular?"

**Skill Activada:** `circular-economy-questions`

**Respuesta del Agente:**
> ♻️ La economía circular busca minimizar residuos y maximizar el valor de los recursos mediante sistemas de ciclo cerrado. Se basa en reducir, reusar, reciclar y regenerar. ¿Qué aspecto específico te interesa profundizar?

**Por qué funcionó:**
- La skill detectó "economía circular" en la descripción
- Siguió las instrucciones: explicación concisa (3 líneas), conceptos clave, pregunta de clarificación
- Usó el emoji designado: ♻️

### Ejemplo 2: Estudiante Pide Ayuda con Tarea

**Estudiante:** "Tengo dudas sobre la tarea 2"

**Skill Activada:** `assignment-help`

**Respuesta del Agente:**
> 📚 Para ayudarte mejor con la tarea, necesito tu nombre completo y matrícula. ¿Sobre qué aspecto específico de la tarea 2 tienes dudas?

**Por qué funcionó:**
- Detectó "tarea" → activó `assignment-help`
- Pidió información del estudiante (nombre, matrícula)
- Preguntó por detalles específicos
- No resolvió directamente la tarea

### Ejemplo 3: Mensaje Poco Claro

**Estudiante:** "jajaja que onda"

**Skill Activada:** `unclear-or-offtopic`

**Respuesta del Agente:**
> No estoy seguro de entender tu pregunta. Soy un asistente académico especializado en Responsabilidad Social en la Industria. Puedo ayudarte con economía circular, sostenibilidad o RSC. ¿Tienes alguna consulta sobre el curso?

**Por qué funcionó:**
- El mensaje no coincide con ninguna skill de contenido
- `unclear-or-offtopic` se activa como fallback
- Redirige educadamente al tema del curso

---

## Troubleshooting

### Problema: La skill no se activa

**Soluciones:**
1. **Verifica la descripción** - Debe incluir keywords que los estudiantes realmente usan
2. **Revisa que el título sea válido** - Solo minúsculas, números, guiones
3. **Haz Reload en Test chat** - Los cambios pueden tardar en reflejarse
4. **Revisa "View sources"** - Te dice qué skill se usó (o si ninguna coincidió)

### Problema: Dos skills se activan al mismo tiempo

**Solución:**
- Haz las descripciones más específicas
- Ejemplo:
  ```
  ❌ Skill 1: "Apply when customer asks about products"
  ❌ Skill 2: "Apply when customer asks about pricing"
  (Ambas podrían activarse con "How much is product X?")
  
  ✅ Skill 1: "Apply when customer asks about product features, specifications, or details (NOT pricing)"
  ✅ Skill 2: "Apply ONLY when customer explicitly asks about prices, costs, or 'how much'"
  ```

### Problema: Error al crear skill por API

**Errores comunes:**

1. **"Invalid title"**
   - Verifica que el título solo tenga minúsculas, números, guiones
   - No uses espacios ni guiones bajos

2. **"Description too long"**
   - Máximo 1,024 caracteres
   - Acorta la descripción

3. **"Skill content too long"**
   - Máximo 20,000 caracteres
   - Divide en múltiples skills si es necesario

4. **"Authentication failed"**
   - Verifica que tu `WHATSAPP_TOKEN` sea válido
   - Asegúrate de usar `X-API-Version: 2.0.0` header

### Problema: El agente ignora la skill

**Posibles causas:**
1. **Conflict con Personality** - Si Personality dice "siempre responde brevemente" y Skill dice "da explicaciones largas", habrá conflicto
2. **Knowledge overriding** - Si Knowledge tiene una respuesta muy específica, puede tomar precedencia
3. **Skill demasiado vaga** - Instrucciones ambiguas confunden al agente

**Solución:**
- Haz las skills más específicas y directivas
- Usa "MUST", "ALWAYS", "NEVER" para reglas críticas
- Prueba desactivando otras skills para aislar el problema

---

## Integración con el Bot Existente

### Opción A: Solo Meta Business Agent (Sin Código)
Si usas **Meta Business Agent puro** (sin tu bot Flask):
1. Sube las skills por API o interfaz visual
2. Las skills se aplican automáticamente en las conversaciones de WhatsApp
3. No necesitas modificar `app.py`

### Opción B: Bot Híbrido (Meta Agent + Tu Código Flask)
Si quieres que tu bot Flask de `app.py` coexista:
1. **Configura tu webhook** para que Meta envíe mensajes a tu Flask app
2. **En tu app Flask**, decide cuándo:
   - Responder directamente (con tu `AIAssistant`)
   - O delegar a Meta Business Agent (haciendo un POST al API de Meta)

#### Ejemplo de delegación a Meta Agent:
```python
def delegate_to_meta_agent(message: str, from_number: str):
    """Send message to Meta Business Agent for processing"""
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": from_number,
        "type": "text",
        "text": {"body": message}
    }
    # Meta agent will process according to skills
    # Skills apply on Meta's side, not in your code
```

**Nota:** Las skills de Meta solo funcionan cuando Meta Business Agent procesa el mensaje. Si tu bot Flask responde directamente, las skills no se aplican (usarías tu lógica de `AIAssistant` en su lugar).

---

## Próximos Pasos

1. **Decide tu approach:**
   - 🅰️ **Solo Meta Agent** → Sube skills, conecta WhatsApp directo a Meta
   - 🅱️ **Bot híbrido** → Decide cuándo tu Flask responde vs. cuándo delega a Meta

2. **Sube las skills RSI:**
   ```bash
   python skills_manager.py --upload
   ```

3. **Prueba en Test Chat:**
   - Ve a Meta Business Suite → Meta Business Agent → Test chat
   - Envía mensajes que deberían activar cada skill
   - Revisa "View sources"

4. **Itera:**
   - Ajusta skills según resultados reales
   - Añade más skills si ves patrones de preguntas frecuentes
   - Revisa logs de conversaciones

5. **Combina con Knowledge:**
   - Sube documentos del curso (syllabus, PDFs de material)
   - Las skills guían **cómo** responder, Knowledge provee **qué** responder

---

## Recursos Adicionales

- [Meta Business Agent Documentation](https://developers.facebook.com/docs/whatsapp/business-management-api/agent-config)
- [WhatsApp Business API Reference](https://developers.facebook.com/docs/whatsapp/cloud-api/reference)
- Script incluido: `skills_manager.py`
- Bot incluido: `app.py`
- Tests: `test_bot.py`

---

## Soporte

Para preguntas sobre:
- **Skills de Meta:** [Meta Developer Community](https://developers.facebook.com/community/)
- **Este script:** Revisa los logs de `skills_manager.py` o el código
- **Curso RSI:** Contacta al profesor del curso

---

**Última actualización:** Septiembre 2026  
**Versión:** 1.0.0
