# 🎯 Sistema de Calificación de Leads Inmobiliarios con IA

## 📋 Descripción General

Este sistema utiliza **Inteligencia Artificial** para analizar y calificar leads de propiedades inmobiliarias, ayudándote a:

✅ **Filtrar curiosos** - Identifica personas que solo están navegando sin intención real de compra  
✅ **Detectar inversionistas reales** - Analiza comportamiento en redes sociales y señales financieras  
✅ **Priorizar prospectos** - Enfoca tu tiempo en leads con mayor probabilidad de conversión  
✅ **Maximizar ROI** - Estima el valor potencial de cada lead y recomienda acciones específicas  

---

## 🚀 Cómo Usar el Sistema

### 1. Acceder al Dashboard

Navega a la página principal del sistema:
```
http://localhost:3000/lead-scoring
```

### 2. Agregar un Nuevo Lead

Haz clic en el botón **"➕ Nuevo Lead"** y completa el formulario con:

#### 📝 Información Básica
- **Nombre completo** (requerido)
- **Email** (requerido)
- **Teléfono** (opcional pero recomendado)
- **Edad** (opcional)
- **Ubicación** (opcional)
- **Fuente del lead** (orgánico, redes sociales, referido, etc.)

#### 🏠 Interés en Propiedad
- **Rango de precio** (mínimo y máximo)
- **Tipo de propiedad** (departamento, casa, terreno, etc.)
- **Propósito** (inversión, residencia, vacaciones)
- **Timeline** (inmediato, 1-3 meses, 6-12 meses, etc.)
- **Estado de financiamiento** (cash, pre-aprobado, necesita crédito)

### 3. Análisis Automático con IA

El sistema analizará automáticamente:

🔍 **Capacidad Financiera** (30% del score)
- Estado laboral y tamaño de empresa
- Ingresos estimados
- Historial crediticio
- Propiedad de inmuebles
- Experiencia en inversiones

🎯 **Intención de Compra** (25% del score)
- Propósito de la compra
- Timeline de urgencia
- Comportamiento en el sitio
- Documentos descargados
- Preguntas realizadas

✅ **Autenticidad** (20% del score)
- Completitud de información
- Calidad de interacción
- Fuente del lead
- Tiempo en sitio
- Consistencia de datos

📱 **Engagement** (10% del score)
- Páginas vistas
- Tiempo en sitio
- Videos vistos
- Visitas recurrentes
- Documentos descargados

🌐 **Credibilidad Social** (10% del score)
- Perfiles verificados
- Presencia en LinkedIn
- Actividad profesional
- Número de seguidores
- Contenido compartido

⏱️ **Urgencia de Timeline** (5% del score)
- Inmediatez de compra
- Disponibilidad de recursos
- Señales de urgencia

---

## 📊 Interpretación de Resultados

### Categorías de Leads

El sistema clasifica cada lead en una de estas categorías:

#### 🔥 **HOT LEAD** (Score: 75-100)
**Acción requerida:** Contactar INMEDIATAMENTE (en las próximas 2 horas)

Características:
- Alta capacidad financiera verificada
- Intención de compra clara y urgente
- Comportamiento de comprador serio
- Presencia social verificable

**Qué hacer:**
1. ☎️ Llamar por teléfono inmediatamente
2. 📊 Preparar propuesta personalizada con análisis ROI
3. 📅 Agendar visita presencial en las próximas 24-48 horas
4. 💼 Asignar a tu mejor agente de ventas

---

#### ⚡ **LEAD TIBIO** (Score: 50-74)
**Acción requerida:** Contactar en 24-48 horas

Características:
- Capacidad financiera moderada
- Interés presente pero no urgente
- Necesita más información
- Timeline de 1-6 meses

**Qué hacer:**
1. 📧 Enviar email con catálogo personalizado
2. 📱 Seguimiento por WhatsApp
3. 📚 Proporcionar información de financiamiento
4. 🔄 Follow-up cada 3-5 días

---

#### ❄️ **LEAD FRÍO** (Score: 30-49)
**Acción requerida:** Agregar a campaña de nurturing

Características:
- Capacidad financiera incierta
- Timeline largo (6+ meses)
- Bajo engagement
- Necesita educación

**Qué hacer:**
1. 📨 Agregar a secuencia de emails automática
2. 📖 Enviar contenido educativo mensual
3. 🎓 Invitar a webinars o eventos
4. ⏳ Seguimiento cada 2-4 semanas

---

#### 🚫 **DESCALIFICADO** (Score: 0-29)
**Acción requerida:** NO PRIORIZAR

Características:
- Múltiples banderas rojas
- Sin capacidad financiera aparente
- Comportamiento de curiosidad
- Sin intención clara

**Qué hacer:**
1. ⏹️ Pausar seguimiento activo
2. 📋 Revisar en 3-6 meses
3. 🗑️ Considerar eliminar de base de datos activa

---

## 🚩 Banderas Rojas (Red Flags)

El sistema detecta automáticamente estas señales de advertencia:

### 🔴 Alta Severidad
- ⏱️ Tiempo en sitio < 30 segundos (probable curiosidad)
- 💳 Historial crediticio deficiente
- 🚫 Sin empleo actual
- 📧 Email temporal o sospechoso
- ⚠️ Inconsistencias en la información

### 🟠 Media Severidad
- ❓ Propósito de compra poco claro
- 📞 Información de contacto incompleta
- 💰 Situación financiera incierta
- 🔍 Interacción mínima con el contenido

### 🟡 Baja Severidad
- 🌐 Sin perfiles sociales verificables
- 📊 Edad fuera del rango típico
- 🤷 Timeline indefinido

---

## ✅ Banderas Verdes (Green Flags)

Señales positivas que incrementan el score:

### 💚 Muy Positivas
- 💵 **Comprador en efectivo** - Alta probabilidad de cierre rápido
- 🎯 **Timeline urgente** (inmediato o 1-3 meses)
- 🏆 **Inversionista experimentado** - Conoce el proceso
- ✅ **Perfil verificado** - Identidad confirmada

### 💚 Positivas
- 🏢 **Ya es propietario** - Experiencia en bienes raíces
- 💼 **Perfil profesional activo** en LinkedIn
- 🤝 **Lead referido** - Mayor confianza
- 📄 **Descargó múltiples documentos** - Alto interés
- 🔄 **Visitante recurrente** - Interés sostenido

---

## 💡 Sistema de Recomendaciones

Cada lead recibe recomendaciones personalizadas basadas en su perfil:

### Para Leads Hot (🔥)
```
✅ PRIORIDAD ALTA: Contactar inmediatamente
✅ Preparar análisis ROI personalizado
✅ Agendar visita presencial ASAP
✅ Asignar a tu mejor vendedor
```

### Para Inversionistas Experimentados
```
📊 Destacar métricas de ROI
📈 Proyecciones de apreciación a 5 años
💰 Análisis de flujo de caja
🏦 Beneficios fiscales
```

### Para Leads que Necesitan Financiamiento
```
🏦 Conectar con banco aliado
📋 Solicitar pre-calificación
💳 Opciones de crédito disponibles
📊 Calculadora de pagos mensuales
```

---

## 📈 Métricas de ROI

El sistema calcula automáticamente:

### 🎲 Probabilidad de Conversión
Estimación de qué tan probable es que el lead se convierta en cliente

**Cálculo basado en:**
- Score general del lead
- Categoría (Hot/Tibio/Frío)
- Capacidad financiera
- Intención de compra
- Autenticidad verificada

### 💵 Valor Estimado
Comisión potencial si el lead se convierte en venta

**Fórmula:**
```
Valor Estimado = Precio Promedio × 3% × (Probabilidad Conversión / 100)
```

**Ejemplo:**
- Precio promedio: $3,000,000 MXN
- Probabilidad: 75%
- Comisión: 3%
- **Valor Estimado: $67,500 MXN**

### ⏱️ Tiempo Estimado de Cierre
- **Hot Leads:** 1-2 semanas
- **Tibios:** 1-3 meses
- **Fríos:** 3-6 meses
- **Descalificados:** Baja probabilidad

---

## 🎯 Estrategias de Seguimiento

### Para Maximizar Conversiones

#### 1️⃣ **Priorización Inteligente**
Enfoca el 80% de tu tiempo en:
- Hot leads (score > 75)
- Leads tibios con alta capacidad financiera
- Inversionistas experimentados

#### 2️⃣ **Personalización del Mensaje**
- **Inversionistas:** Habla de ROI, apreciación, flujo de caja
- **Residentes:** Habla de calidad de vida, comunidad, amenidades
- **Compradores urgentes:** Habla de disponibilidad y cierre rápido

#### 3️⃣ **Multi-Canal**
- Hot leads → Teléfono + WhatsApp + Email
- Tibios → WhatsApp + Email + SMS
- Fríos → Email automatizado + contenido

#### 4️⃣ **Timing Óptimo**
- **Inmediato:** Hot leads (< 2 horas)
- **24-48h:** Leads tibios
- **Semanal:** Leads fríos

---

## 🔍 Análisis de Redes Sociales

### LinkedIn (Peso: +30 puntos)
**Por qué es importante:**
- Indica seriedad profesional
- Verifica empleo e ingresos
- Muestra red de contactos

**Qué buscar:**
- ✅ Perfil completo y actualizado
- ✅ +500 contactos
- ✅ Publicaciones profesionales
- ✅ Empresa y cargo verificables

### Facebook/Instagram (Peso: +5 puntos)
**Por qué es importante:**
- Valida identidad real
- Muestra estilo de vida
- Indica nivel socioeconómico

**Qué buscar:**
- ✅ Cuenta activa (no abandonada)
- ✅ Fotos personales auténticas
- ✅ Red de amigos real
- ⚠️ ALERTA: Perfiles falsos o recién creados

---

## 🤖 Cómo Funciona la IA

### Algoritmo de Scoring

El sistema utiliza un algoritmo de **scoring ponderado** con múltiples dimensiones:

```typescript
Score Final = 
  (Capacidad Financiera × 0.30) +
  (Intención de Compra × 0.25) +
  (Autenticidad × 0.20) +
  (Engagement × 0.10) +
  (Credibilidad Social × 0.10) +
  (Urgencia Timeline × 0.05)
```

### Análisis de Patrones de Comportamiento

La IA identifica estos patrones automáticamente:

1. **High Intent Researcher** (Confianza: 85%)
   - +15 páginas vistas
   - +10 minutos en sitio
   - Comportamiento de investigación profunda

2. **Serious Buyer** (Confianza: 90%)
   - Descargó 2+ documentos
   - Vio 5+ minutos de video
   - Hizo preguntas específicas

3. **Casual Browser** (Confianza: 75%)
   - < 1 minuto en sitio
   - < 3 páginas vistas
   - Sin interacción

4. **Engaged Prospect** (Confianza: 88%)
   - Visitante recurrente
   - Múltiples preguntas
   - Engagement sostenido

5. **Urgent Buyer** (Confianza: 82%)
   - Respuestas en < 30 minutos
   - Alta frecuencia de contacto
   - Timeline acelerado

### Predicción de Capacidad Financiera

El sistema estima:

- **Ingresos aproximados** basado en empleo, industria y señales sociales
- **Ratio deuda/ingreso** calculado con precio de propiedad e ingresos
- **Score de liquidez** (0-100) basado en financiamiento y activos
- **Capacidad de inversión** (0-100) combinando todos los factores

### Detección de Fraude

Identifica automáticamente:
- 📧 Emails temporales
- 📞 Teléfonos inválidos
- 🚫 Inconsistencias en datos
- ⚠️ Comportamiento sospechoso
- 🔍 Falta de presencia digital

---

## 💻 Uso de API (Para Desarrolladores)

### Endpoints Disponibles

#### 1. Calificar un Lead Individual
```typescript
// Importar tRPC client
import { api } from '~/utils/api';

// Usar en componente React
const scoreLeadMutation = api.leadScoring.scoreLead.useMutation();

const lead = {
  name: "Juan Pérez",
  email: "juan@empresa.com",
  phone: "+52 55 1234 5678",
  age: 35,
  source: "organic",
  propertyInterest: {
    priceRange: { min: 2000000, max: 4000000 },
    propertyType: "apartment",
    purpose: "investment",
    timeline: "1-3_months",
    financingStatus: "pre_approved"
  }
};

const result = await scoreLeadMutation.mutateAsync(lead);
console.log(result.overallScore); // 78
console.log(result.category); // "hot"
```

#### 2. Calificar Múltiples Leads
```typescript
const batchScoreMutation = api.leadScoring.batchScoreLeads.useMutation();

const result = await batchScoreMutation.mutateAsync({
  leads: [lead1, lead2, lead3]
});

console.log(result.summary);
// {
//   totalLeads: 3,
//   hotLeads: 1,
//   warmLeads: 2,
//   avgScore: 65,
//   totalEstimatedValue: 125000
// }
```

#### 3. Analizar Perfil Social
```typescript
const analyzeSocialMutation = api.leadScoring.analyzeSocialProfile.useMutation();

const result = await analyzeSocialMutation.mutateAsync({
  profileUrl: "https://linkedin.com/in/juanperez",
  platform: "linkedin"
});

console.log(result.credibilityScore); // 85
console.log(result.insights.isProfessional); // true
```

#### 4. Predecir Conversión
```typescript
const predictConversionQuery = api.leadScoring.predictConversion.useQuery({
  leadId: "lead-123",
  score: 78,
  category: "hot",
  priceRange: { min: 2000000, max: 4000000 }
});

console.log(predictConversionQuery.data?.conversionProbability); // 75%
console.log(predictConversionQuery.data?.estimatedRevenue); // 67500
```

---

## 📊 Ejemplos de Casos de Uso

### Caso 1: Inversionista Serio (Score: 92 - HOT 🔥)

**Perfil:**
- Edad: 42 años
- Empleo: Dueño de negocio
- Empresa: Grande (500+ empleados)
- LinkedIn: Verificado, 2,000+ contactos
- Propiedades: Ya es propietario
- Experiencia: 3 propiedades de inversión
- Timeline: Inmediato
- Financiamiento: Comprador en efectivo

**Análisis de la IA:**
```
✅ Score General: 92/100
🔥 Categoría: HOT LEAD

Scores Detallados:
- Capacidad Financiera: 95
- Intención de Compra: 90
- Autenticidad: 88
- Engagement: 85
- Credibilidad Social: 92
- Urgencia Timeline: 100

Probabilidad de Conversión: 85%
Valor Estimado: $76,500 MXN

✅ Banderas Verdes:
- Comprador en efectivo
- Inversionista experimentado
- Perfil LinkedIn verificado
- Timeline urgente
- Ya es propietario

Recomendaciones:
1. 🚨 CONTACTAR INMEDIATAMENTE por teléfono
2. 📊 Preparar análisis ROI con proyecciones a 5 años
3. 📅 Agendar visita en próximas 24 horas
4. 💼 Asignar a tu mejor agente
5. 💡 Destacar métricas de apreciación y flujo de caja
```

**Acciones sugeridas:**
1. ☎️ Llamar en las próximas 2 horas
2. 📊 Enviar análisis comparativo de ROI vs otras inversiones
3. 🏢 Mostrar propiedades de alto rendimiento
4. 📈 Presentar proyecciones de apreciación

**Resultado esperado:** 85% probabilidad de cierre en 1-2 semanas

---

### Caso 2: Primer Comprador Motivado (Score: 68 - TIBIO ⚡)

**Perfil:**
- Edad: 28 años
- Empleo: Empleado en empresa mediana
- Ingreso estimado: Medio-Alto
- LinkedIn: Activo, 300 contactos
- Timeline: 1-3 meses
- Financiamiento: Pre-aprobado
- Propósito: Residencia principal

**Análisis de la IA:**
```
✅ Score General: 68/100
⚡ Categoría: LEAD TIBIO

Scores Detallados:
- Capacidad Financiera: 65
- Intención de Compra: 75
- Autenticidad: 70
- Engagement: 68
- Credibilidad Social: 55
- Urgencia Timeline: 80

Probabilidad de Conversión: 60%
Valor Estimado: $36,000 MXN

✅ Banderas Verdes:
- Pre-aprobado para crédito
- Timeline urgente (1-3 meses)
- Perfil profesional activo
- Visitante recurrente

⚠️ Banderas Amarillas:
- Primera compra (sin experiencia)
- Necesita financiamiento
- Capacidad financiera moderada

Recomendaciones:
1. Contactar en próximas 24-48 horas
2. Enviar catálogo personalizado en su rango
3. Explicar proceso de compra paso a paso
4. Conectar con asesor de crédito
5. Follow-up cada 3-5 días
```

**Acciones sugeridas:**
1. 📧 Email con propiedades en su rango ($1.5M - $2.5M)
2. 📱 WhatsApp con calculadora de pagos
3. 📚 Guía "Tu Primera Propiedad: Paso a Paso"
4. 🏦 Introducción con banco aliado

**Resultado esperado:** 60% probabilidad de cierre en 1-3 meses

---

### Caso 3: Curioso sin Intención (Score: 24 - DESCALIFICADO 🚫)

**Perfil:**
- Edad: 19 años
- Email: temporal10@tempmail.com
- Sin teléfono
- Sin perfiles sociales
- Tiempo en sitio: 18 segundos
- Páginas vistas: 1
- Timeline: "Solo estoy viendo"
- Propósito: "No estoy seguro"

**Análisis de la IA:**
```
⚠️ Score General: 24/100
🚫 Categoría: DESCALIFICADO

Scores Detallados:
- Capacidad Financiera: 15
- Intención de Compra: 20
- Autenticidad: 10
- Engagement: 5
- Credibilidad Social: 0
- Urgencia Timeline: 10

Probabilidad de Conversión: 5%
Valor Estimado: $750 MXN

🚩 Banderas Rojas (Alta Severidad):
- Email temporal detectado
- Tiempo en sitio < 30 segundos
- Sin presencia en redes sociales
- Información de contacto incompleta
- Sin intención clara de compra
- Edad fuera del rango típico

Recomendaciones:
1. ⛔ NO PRIORIZAR: Bajo potencial de conversión
2. 🗑️ Considerar descalificar de seguimiento activo
3. ⏸️ No invertir tiempo ni recursos
```

**Acciones sugeridas:**
1. ❌ NO contactar
2. 🗑️ Eliminar de lista activa
3. 📋 Archivo "curiosos" para análisis

**Resultado esperado:** 5% probabilidad, NO vale la pena el seguimiento

---

## 🎓 Mejores Prácticas

### ✅ DO (Hacer)

1. **Actualiza información regularmente**
   - Agrega notas después de cada contacto
   - Actualiza estado de financiamiento
   - Registra cambios en timeline

2. **Usa el sistema diariamente**
   - Revisa dashboard cada mañana
   - Prioriza hot leads primero
   - Actualiza scores después de interacciones

3. **Personaliza tu approach**
   - Lee las recomendaciones de la IA
   - Adapta mensaje según categoría
   - Usa insights de redes sociales

4. **Combina IA con intuición humana**
   - La IA da dirección, tú decides
   - Override manual cuando sea necesario
   - Aprende de conversiones exitosas

### ❌ DON'T (No Hacer)

1. **No ignores banderas rojas**
   - Sistema detecta señales de alerta
   - No persigas leads descalificados
   - Ahorra tiempo para leads calificados

2. **No trates todos los leads igual**
   - Hot leads necesitan atención AHORA
   - Fríos pueden esperar
   - Personaliza según score

3. **No olvides el follow-up**
   - Hot leads: cada 1-2 días
   - Tibios: cada 3-5 días
   - Fríos: cada 2 semanas

4. **No dependas 100% de automatización**
   - Toca humano siempre gana
   - Llamadas > Emails > SMS
   - Construye relación personal

---

## 📞 Soporte y Recursos

### 🆘 ¿Necesitas Ayuda?

- 📧 Email: [tu-email@empresa.com]
- 💬 Chat: [link a soporte]
- 📱 WhatsApp: [número]

### 📚 Recursos Adicionales

- [Video Tutorial: Cómo usar el sistema] (pendiente)
- [Guía de Interpretación de Scores] (este documento)
- [Mejores Prácticas de Seguimiento] (próximamente)
- [API Documentation] (para desarrolladores)

---

## 🔮 Roadmap Futuro

Próximas funcionalidades planeadas:

- [ ] Integración con WhatsApp Business
- [ ] Análisis automático de perfiles sociales vía API
- [ ] Machine Learning para mejorar predicciones
- [ ] Integración con CRM (Salesforce, HubSpot)
- [ ] App móvil para seguimiento
- [ ] Notificaciones push de hot leads
- [ ] Dashboard de métricas de conversión
- [ ] A/B testing de estrategias de seguimiento
- [ ] Análisis de sentiment en interacciones
- [ ] Scoring predictivo mejorado con datos históricos

---

## 📝 Notas Finales

Este sistema es una **herramienta de apoyo a la decisión**, no un reemplazo del juicio humano. 

**Recuerda:**
- La IA proporciona datos y recomendaciones
- Tú tomas las decisiones finales
- Tu experiencia y relación humana son insustituibles
- El sistema mejora con el uso y feedback

**¡Maximiza tu ROI enfocándote en los leads que realmente importan! 🚀**

---

*Última actualización: Septiembre 2026*
*Versión: 1.0.0*
