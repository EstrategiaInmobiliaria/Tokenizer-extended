# 🎯 læds® - Arquitectura del Sistema de Matching Automatizado

## 📋 Visión del Sistema

**læds®** es un **motor de matching inteligente** que conecta compradores calificados con propiedades/vendedores, automatiza el proceso completo y cobra una reference fee solo al cierre.

### Diferenciación Clave
- ❌ **NO es** otro CRM inmobiliario tradicional
- ✅ **ES** un motor de matching + calificación IA + monetización por referidos
- ✅ **Opera** con pasos simples conectando ecosistemas (WhatsApp + CRM + portales + IA)

---

## 🏗️ Arquitectura en 5 Pasos Simples

```
┌─────────────────────────────────────────────────────────────────┐
│                         læds® FLOW                              │
└─────────────────────────────────────────────────────────────────┘

1️⃣ CAPTURA                    → WhatsApp + Meta Ads + Portales
                               ↓
2️⃣ CALIFICACIÓN IA             → Scoring 0-100 + Banderas
                               ↓
3️⃣ MATCHING INTELIGENTE        → Comprador ↔ Propiedad/Vendedor
                               ↓
4️⃣ COORDINACIÓN                → Fichas + Visitas + Seguimiento
                               ↓
5️⃣ CIERRE + REFERENCE FEE      → Pago + Registro + Post-venta
```

---

## 🔧 Stack Tecnológico Híbrido

### Capa 1: Entrada (Captura)
```
┌─────────────────────────────────────────────────────────────┐
│ CANALES DE ENTRADA                                          │
├─────────────────────────────────────────────────────────────┤
│ • WhatsApp Business API (canal principal)                  │
│ • Meta Business Agent (chatbot IA)                         │
│ • Meta Ads → Lead Forms                                    │
│ • Instagram DM → WhatsApp                                  │
│ • Portales (Inmuebles24, Lamudi) → Webhook                │
│ • Sitio web → Formulario                                   │
└─────────────────────────────────────────────────────────────┘
                         ↓
              Todo converge a WhatsApp
```

**Herramientas:**
- **WhatsApp Business API** (oficial)
- **Meta Business Agent** o **Wazzap/Newton.AI** para IA conversacional
- **Webhooks** para conectar todos los canales

### Capa 2: Calificación (Scoring IA)
```
┌─────────────────────────────────────────────────────────────┐
│ MOTOR DE CALIFICACIÓN IA                                    │
├─────────────────────────────────────────────────────────────┤
│ • Análisis de conversación (intención, urgencia)           │
│ • Scoring multi-dimensional (6 factores)                   │
│ • Detección de banderas rojas/verdes                       │
│ • Estimación de capacidad financiera                       │
│ • Predicción de probabilidad de cierre                     │
└─────────────────────────────────────────────────────────────┘
                         ↓
              Score: 0-100 + Categoría
```

**Herramientas:**
- **Sistema actual de Lead Scoring** (ya implementado)
- **Claude/GPT API** para análisis de conversaciones
- **tRPC API** para procesamiento

### Capa 3: Matching (Cerebro)
```
┌─────────────────────────────────────────────────────────────┐
│ MOTOR DE MATCHING INTELIGENTE                               │
├─────────────────────────────────────────────────────────────┤
│ • Comprador + Requisitos → Vector embedding                │
│ • Propiedades disponibles → Vector embedding               │
│ • Cálculo de compatibilidad (cosine similarity)            │
│ • Ranking de mejores matches                               │
│ • Asignación automática o sugerida                         │
└─────────────────────────────────────────────────────────────┘
                         ↓
              Top 3-5 propiedades compatibles
```

**Herramientas:**
- **Vector DB** (Pinecone o PostgreSQL + pgvector)
- **IA Embeddings** (OpenAI text-embedding-3)
- **Algoritmo de matching** (implementación custom)

### Capa 4: Inventario (Datos)
```
┌─────────────────────────────────────────────────────────────┐
│ FUENTES DE INVENTARIO                                       │
├─────────────────────────────────────────────────────────────┤
│ • EasyBroker (propiedades + Bolsa Inmobiliaria)           │
│ • API de portales (Inmuebles24, Lamudi)                   │
│ • Base de datos propia                                     │
│ • Red de agentes/vendedores                                │
└─────────────────────────────────────────────────────────────┘
```

**Herramientas:**
- **EasyBroker API** (inventario principal)
- **PostgreSQL** (base de datos central)
- **Webhooks** para sincronización

### Capa 5: Coordinación (Automatización)
```
┌─────────────────────────────────────────────────────────────┐
│ ORQUESTACIÓN Y SEGUIMIENTO                                  │
├─────────────────────────────────────────────────────────────┤
│ • Envío automático de fichas por WhatsApp                  │
│ • Agendamiento de visitas                                  │
│ • Seguimiento multi-canal (WhatsApp, email, SMS)          │
│ • Recordatorios automáticos                                │
│ • Actualización de pipeline                                │
└─────────────────────────────────────────────────────────────┘
```

**Herramientas:**
- **Make.com** o **n8n** (orquestación)
- **WhatsApp Business API** (comunicación)
- **Calendly** o similar (agendamiento)

### Capa 6: Monetización (Reference Fee)
```
┌─────────────────────────────────────────────────────────────┐
│ TRACKING Y COBRO DE FEES                                    │
├─────────────────────────────────────────────────────────────┤
│ • Registro de referido (quién trajo el lead)               │
│ • Tracking de asignación (a qué agente/propiedad)          │
│ • Detección de cierre (firma de contrato)                  │
│ • Cálculo automático de fee (% o fijo)                     │
│ • Facturación y cobro                                      │
└─────────────────────────────────────────────────────────────┘
```

**Herramientas:**
- **Pipedrive** o **HubSpot** (pipeline + deals)
- **Stripe** (cobros)
- **Sistema de facturación** (integración)

---

## 📊 Flujo Completo Paso a Paso

### PASO 1: CAPTURA 📱

**Entrada desde WhatsApp:**
```
Cliente → "Hola, busco departamento en Polanco"
              ↓
Meta Business Agent/Chatbot IA
              ↓
Preguntas calificadoras:
- "¿Cuál es tu presupuesto aproximado?"
- "¿Es para vivir o para inversión?"
- "¿En qué timeline buscas comprar?"
- "¿Tienes financiamiento pre-aprobado?"
              ↓
Datos capturados → Sistema læds®
```

**Entrada desde Meta Ads:**
```
Lead Form Facebook/Instagram
              ↓
Webhook → læds®
              ↓
Mensaje automático a WhatsApp:
"Hola [nombre], vi que te interesa [propiedad].
¿Te parece si platicamos por aquí?"
              ↓
Conversación → Calificación
```

### PASO 2: CALIFICACIÓN IA 🤖

**Motor de Scoring (ya implementado):**
```javascript
const lead = {
  name: "María López",
  whatsappConversation: "...",
  budget: { min: 3000000, max: 5000000 },
  timeline: "1-3_months",
  purpose: "investment",
  // ... más datos extraídos de conversación
};

const score = await api.leadScoring.scoreLead.mutate(lead);

// Resultado:
{
  overallScore: 85,
  category: "hot", // 🔥
  scores: {
    financialCapacity: 80,
    buyingIntent: 90,
    authenticity: 85,
    engagement: 88,
    socialCredibility: 70,
    timelineUrgency: 90
  },
  conversionProbability: 78,
  estimatedValue: 67500, // MXN comisión
  recommendations: [
    "Contactar en próximas 2 horas",
    "Mostrar propiedades premium",
    "Preparar análisis ROI"
  ]
}
```

**IA de Conversación:**
```typescript
// Análisis de mensajes con Claude/GPT
const conversationAnalysis = await analyzeWhatsAppConversation({
  messages: conversationHistory,
  extractInfo: [
    'budget_signals',
    'urgency_level',
    'serious_buyer_indicators',
    'red_flags'
  ]
});

// Output:
{
  budgetSignals: {
    mentionedCash: true,
    priceReactionNegative: false,
    confidence: 'high'
  },
  urgencyLevel: 'high',
  seriousBuyerScore: 8.5,
  redFlags: []
}
```

### PASO 3: MATCHING INTELIGENTE 🎯

**Algoritmo de Matching:**
```typescript
// 1. Obtener perfil del comprador
const buyerProfile = {
  id: "buyer-123",
  budget: { min: 3000000, max: 5000000 },
  location: ["Polanco", "Lomas"],
  propertyType: "apartment",
  bedrooms: 2,
  purpose: "investment",
  preferences: [
    "vista panorámica",
    "amenidades",
    "plusvalía",
    "cerca metro"
  ],
  score: 85 // Hot lead
};

// 2. Buscar propiedades compatibles
const matches = await matchingEngine.findMatches({
  buyer: buyerProfile,
  minCompatibility: 70,
  limit: 5
});

// 3. Resultado:
[
  {
    propertyId: "prop-456",
    compatibility: 95,
    reasons: [
      "100% dentro de presupuesto",
      "Zona preferida (Polanco)",
      "Alta plusvalía histórica (8%/año)",
      "Amenidades premium"
    ],
    property: {
      title: "Depto 2 rec Polanco con vista",
      price: 4200000,
      location: "Polanco, CDMX",
      broker: "Juan Pérez",
      commission: 3,
      images: [...],
      roi: {
        rentalYield: 6.5,
        appreciation: 8,
        total: 14.5
      }
    },
    estimatedFee: 3780 // 30% de comisión del broker
  },
  // ... 4 propiedades más
]
```

**Sistema de Embeddings:**
```typescript
// Vectorización para matching semántico
import { OpenAI } from 'openai';

async function createBuyerEmbedding(buyer) {
  const description = `
    Comprador busca ${buyer.propertyType} en ${buyer.location.join(', ')}
    con presupuesto de $${buyer.budget.min}-${buyer.budget.max}.
    Propósito: ${buyer.purpose}.
    Preferencias: ${buyer.preferences.join(', ')}.
    Score de calificación: ${buyer.score}/100.
  `;
  
  const embedding = await openai.embeddings.create({
    model: "text-embedding-3-small",
    input: description
  });
  
  return embedding.data[0].embedding;
}

// Buscar propiedades similares en vector DB
const matches = await vectorDB.query({
  vector: buyerEmbedding,
  topK: 10,
  filter: {
    price: { $gte: buyer.budget.min, $lte: buyer.budget.max },
    status: 'available'
  }
});
```

### PASO 4: COORDINACIÓN 📋

**Envío Automático de Fichas:**
```typescript
// Cuando hay match > 70%
async function sendPropertyToWhatsApp(buyer, matches) {
  for (const match of matches.slice(0, 3)) {
    await whatsappAPI.sendMessage({
      to: buyer.phone,
      type: 'template',
      template: {
        name: 'property_showcase',
        language: { code: 'es_MX' },
        components: [
          {
            type: 'header',
            parameters: [{
              type: 'image',
              image: { link: match.property.images[0] }
            }]
          },
          {
            type: 'body',
            parameters: [
              { type: 'text', text: match.property.title },
              { type: 'text', text: `$${match.property.price.toLocaleString('es-MX')}` },
              { type: 'text', text: match.property.location },
              { type: 'text', text: `${match.compatibility}%` }
            ]
          },
          {
            type: 'button',
            sub_type: 'url',
            index: 0,
            parameters: [{
              type: 'text',
              text: `tour-virtual/${match.propertyId}`
            }]
          }
        ]
      }
    });
    
    // Log de envío
    await trackingDB.insert({
      leadId: buyer.id,
      propertyId: match.propertyId,
      action: 'property_sent',
      channel: 'whatsapp',
      compatibility: match.compatibility,
      timestamp: new Date()
    });
  }
}
```

**Pipeline de Seguimiento:**
```typescript
// Estado del lead en el pipeline
const pipeline = {
  stages: [
    { name: 'Capturado', leads: [] },
    { name: 'Calificado', leads: [] },
    { name: 'Propiedades Enviadas', leads: [] },
    { name: 'Interesado', leads: [] },
    { name: 'Visita Agendada', leads: [] },
    { name: 'Visita Realizada', leads: [] },
    { name: 'Negociación', leads: [] },
    { name: 'Firma de Contrato', leads: [] },
    { name: 'Cerrado', leads: [] }
  ]
};

// Mover lead automáticamente según acciones
async function updatePipelineStage(leadId, action) {
  const actions = {
    'property_sent': 'Propiedades Enviadas',
    'property_clicked': 'Interesado',
    'visit_scheduled': 'Visita Agendada',
    'visit_completed': 'Visita Realizada',
    'offer_made': 'Negociación',
    'contract_signed': 'Firma de Contrato',
    'deal_closed': 'Cerrado'
  };
  
  await pipelineDB.update(leadId, {
    stage: actions[action],
    updatedAt: new Date()
  });
  
  // Disparar automatizaciones según etapa
  await triggerAutomations(leadId, actions[action]);
}
```

**Recordatorios Automáticos:**
```typescript
// Make.com / n8n workflow
const followUpRules = [
  {
    trigger: 'property_sent',
    wait: '24 hours',
    action: 'send_followup',
    message: "Hola {name}, ¿tuviste chance de ver las propiedades que te envié? ¿Alguna te llamó la atención?"
  },
  {
    trigger: 'no_response',
    wait: '48 hours',
    action: 'send_reminder',
    message: "¿Sigues buscando departamento en {location}? Tengo nuevas opciones que podrían interesarte."
  },
  {
    trigger: 'visit_scheduled',
    wait: '1 day before',
    action: 'send_reminder',
    message: "Te recuerdo tu visita mañana a las {time} en {address}. ¿Confirmamos?"
  }
];
```

### PASO 5: CIERRE + REFERENCE FEE 💰

**Tracking de Referidos:**
```typescript
// Registro inicial
const referral = {
  id: "ref-789",
  leadId: "buyer-123",
  propertyId: "prop-456",
  brokerId: "broker-juan",
  referredBy: "laeds",
  referredAt: new Date(),
  status: "active",
  
  // Para cálculo de fee
  propertyPrice: 4200000,
  brokerCommission: 3, // %
  brokerCommissionAmount: 126000, // MXN
  
  // Reference fee de læds®
  feeStructure: {
    type: "percentage", // o "flat"
    percentage: 30, // 30% de la comisión del broker
    flatAmount: null
  },
  
  estimatedFee: 37800, // MXN
  
  // Estados
  visitScheduled: true,
  visitCompleted: true,
  offerMade: true,
  contractSigned: false,
  dealClosed: false,
  feePaid: false
};
```

**Detección Automática de Cierre:**
```typescript
// Webhook desde EasyBroker o actualización manual
async function handleDealClosed(data) {
  const referral = await db.referrals.findOne({
    leadId: data.leadId,
    propertyId: data.propertyId
  });
  
  if (!referral) {
    console.warn('Referral not found - potential leak!');
    return;
  }
  
  // Actualizar estado
  await db.referrals.update(referral.id, {
    status: 'closed',
    contractSigned: true,
    dealClosed: true,
    closedAt: new Date(),
    
    // Datos finales
    finalPrice: data.finalPrice,
    finalCommission: data.finalPrice * (referral.brokerCommission / 100),
    finalFee: data.finalPrice * (referral.brokerCommission / 100) * (referral.feeStructure.percentage / 100)
  });
  
  // Generar factura automática
  await generateInvoice({
    referralId: referral.id,
    amount: referral.finalFee,
    brokerId: referral.brokerId
  });
  
  // Enviar notificación de cobro
  await sendPaymentRequest({
    to: referral.brokerId,
    amount: referral.finalFee,
    concept: `Fee por referido - ${data.propertyAddress}`
  });
}
```

**Dashboard de Fees:**
```typescript
// Métricas de monetización
const feeMetrics = {
  thisMonth: {
    referrals: 15,
    closed: 4,
    conversionRate: 26.7,
    
    totalFeesGenerated: 156000, // MXN
    feesPaid: 98000,
    feesPending: 58000,
    
    avgFeePerDeal: 39000,
    
    topBrokers: [
      { name: "Juan Pérez", deals: 2, fees: 78000 },
      { name: "Ana García", deals: 1, fees: 42000 }
    ]
  },
  
  pipeline: {
    active: 22,
    visitScheduled: 8,
    negotiation: 5,
    estimatedFeesInPipeline: 425000
  }
};
```

---

## 🔌 Integraciones Clave

### 1. WhatsApp Business API

**Setup:**
```typescript
import { Client } from 'whatsapp-web.js';

const whatsapp = new WhatsAppBusinessAPI({
  phoneNumberId: process.env.WHATSAPP_PHONE_ID,
  accessToken: process.env.WHATSAPP_ACCESS_TOKEN,
  webhookVerifyToken: process.env.WEBHOOK_VERIFY_TOKEN
});

// Webhook para mensajes entrantes
app.post('/webhook/whatsapp', async (req, res) => {
  const message = req.body.entry[0].changes[0].value.messages[0];
  
  // Procesar mensaje
  await processIncomingMessage({
    from: message.from,
    text: message.text.body,
    timestamp: message.timestamp
  });
  
  res.sendStatus(200);
});
```

### 2. EasyBroker API

**Obtener Inventario:**
```typescript
// API oficial de EasyBroker
const easybroker = new EasyBrokerAPI({
  apiKey: process.env.EASYBROKER_API_KEY
});

// Obtener propiedades
const properties = await easybroker.properties.list({
  limit: 50,
  search: {
    operation_type: 'sale',
    property_type: 'apartment',
    location: 'Polanco',
    min_price: 3000000,
    max_price: 5000000
  }
});

// Sincronizar a DB local
for (const property of properties) {
  await db.properties.upsert({
    externalId: property.public_id,
    source: 'easybroker',
    title: property.title,
    price: property.operations[0].amount,
    location: property.location.name,
    bedrooms: property.bedrooms,
    bathrooms: property.bathrooms,
    area: property.construction_size,
    description: property.description,
    images: property.property_images.map(img => img.url),
    broker: property.agent.name,
    updatedAt: new Date()
  });
}
```

### 3. Meta Business Agent

**Configuración del Bot:**
```javascript
// En Meta Business Suite
const botConfig = {
  greeting: "¡Hola! Soy el asistente de læds®. Te ayudo a encontrar la propiedad perfecta. ¿Qué estás buscando?",
  
  keywords: {
    'departamento|depa': { action: 'qualify_apartment' },
    'casa': { action: 'qualify_house' },
    'inversion|invertir': { action: 'qualify_investment' },
    'comprar': { action: 'qualify_purchase' }
  },
  
  flows: [
    {
      trigger: 'qualify_apartment',
      questions: [
        "¿En qué zona buscas?",
        "¿Cuántas recámaras necesitas?",
        "¿Cuál es tu presupuesto aproximado?",
        "¿Es para vivir o para inversión?",
        "¿En cuánto tiempo planeas comprar?"
      ]
    }
  ],
  
  escalation: {
    keywords: ['hablar con persona', 'agente humano'],
    action: 'transfer_to_human'
  }
};
```

---

## 📊 Modelos de Reference Fee

### Opción 1: Porcentaje de Comisión del Broker
```
Precio propiedad: $4,000,000 MXN
Comisión broker (3%): $120,000 MXN
læds® fee (30%): $36,000 MXN
Broker recibe: $84,000 MXN
```

**Pros:**
- Incentivo alineado (solo cobras al cierre)
- Escalable con el valor de propiedades
- Justo para todas las partes

**Contras:**
- Dependes del cierre
- Broker puede intentar "saltarse" el sistema

### Opción 2: Fee Fija por Lead Calificado + Success Fee
```
Lead calificado entregado: $500 MXN (pago inmediato)
Si cierra (success fee 20%): $24,000 MXN
Total læds® si cierra: $24,500 MXN
```

**Pros:**
- Ingreso inmediato por leads calificados
- Menor riesgo
- Predecible

**Contras:**
- Puede ser caro para brokers sin cierre
- Necesitas facturar por lead

### Opción 3: Suscripción + Success Fee Reducido
```
Suscripción mensual broker: $2,000 MXN
Leads ilimitados calificados
Success fee: 15% de comisión
```

**Pros:**
- Ingreso recurrente predecible
- Brokers ven valor inmediato
- Menor success fee es atractivo

**Contras:**
- Requiere volumen de leads consistente
- Más complejo de vender

**Recomendación inicial:** Opción 1 (30% de comisión solo al cierre) para validar el modelo sin fricción.

---

## 🎯 Métricas Clave (KPIs)

### Funnel de Conversión
```
1000 leads capturados
  ↓ 60% calificados (score > 50)
600 leads calificados
  ↓ 50% con matches enviados
300 leads con propiedades
  ↓ 30% agenda visita
90 visitas agendadas
  ↓ 70% realiza visita
63 visitas realizadas
  ↓ 40% hace oferta
25 ofertas realizadas
  ↓ 60% cierra
15 cierres
```

**Conversión total:** 1.5% (1000 → 15)  
**Valor promedio deal:** $4M MXN  
**Comisión promedio broker:** $120K MXN (3%)  
**Fee læds® promedio:** $36K MXN (30%)  
**Revenue læds® por mes:** $540K MXN

### Métricas Operacionales
- **Time to first response:** < 5 minutos
- **Time to qualification:** < 24 horas
- **Time to first match:** < 48 horas
- **Time to visit:** < 7 días
- **Time to close:** 30-45 días promedio

### Métricas de Calidad
- **Buyer satisfaction score:** > 4.5/5
- **Broker satisfaction score:** > 4.0/5
- **Match accuracy:** > 70% compatibilidad
- **Conversion rate (calificado → cierre):** > 10%

---

## 🚀 Roadmap de Implementación

### Fase 1: MVP (Semanas 1-4)
- [x] Sistema de scoring de leads (✅ YA IMPLEMENTADO)
- [ ] Integración WhatsApp Business API básica
- [ ] Captura manual de propiedades
- [ ] Matching manual asistido por IA
- [ ] Tracking manual de fees

**Objetivo:** Validar que el modelo funciona con 10 deals

### Fase 2: Automatización (Semanas 5-8)
- [ ] Motor de matching automático
- [ ] Integración EasyBroker API
- [ ] Pipeline automatizado en HubSpot/Pipedrive
- [ ] Envío automático de fichas por WhatsApp
- [ ] Webhooks para eventos clave

**Objetivo:** Escalar a 50 leads/mes con 5 cierres

### Fase 3: Escala (Semanas 9-12)
- [ ] Meta Business Agent completamente configurado
- [ ] Vector DB para matching semántico
- [ ] Orquestación completa en Make/n8n
- [ ] Dashboard de métricas en tiempo real
- [ ] Sistema de facturación automática

**Objetivo:** 200 leads/mes, 20 cierres, $720K MXN revenue

### Fase 4: Optimización (Mes 4+)
- [ ] Machine Learning en scoring
- [ ] Análisis predictivo de cierre
- [ ] A/B testing de mensajes
- [ ] Integración con más portales
- [ ] App móvil para brokers

---

## 💡 Próximos Pasos Inmediatos

1. ✅ **Mantener** el sistema de scoring actual (ya está listo)
2. 🔧 **Implementar** módulo de matching básico
3. 🔌 **Conectar** WhatsApp Business API
4. 📊 **Crear** sistema de tracking de referidos
5. 💰 **Diseñar** flujo de cobro de fees
6. 🤝 **Integrar** con EasyBroker

---

**¿Quieres que implemente alguno de estos módulos específicos ahora?**

Opciones:
1. Motor de matching inteligente (con embeddings)
2. Integración WhatsApp Business API
3. Sistema de tracking de referidos y fees
4. Módulo de integración con EasyBroker
5. Dashboard de métricas de læds®

