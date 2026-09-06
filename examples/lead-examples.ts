import type { LeadInput } from '~/models/lead-scoring';

export const exampleLeads: Record<string, LeadInput> = {
  hotInvestor: {
    name: "Carlos Empresario",
    email: "carlos@empresagrande.com",
    phone: "+52 55 1234 5678",
    age: 42,
    location: "Ciudad de México, CDMX",
    source: "referral",
    
    socialProfiles: [
      {
        platform: "linkedin",
        profileUrl: "https://linkedin.com/in/carlosempresario",
        followers: 2500,
        verified: true,
        businessProfile: true,
        professionalContent: true,
        activityLevel: "high",
      },
      {
        platform: "facebook",
        followers: 1200,
        verified: false,
        activityLevel: "medium",
      }
    ],
    
    financialSignals: {
      employmentStatus: "business_owner",
      industryType: "Technology",
      companySize: "large",
      estimatedIncome: "very_high",
      investmentExperience: true,
      propertyOwnership: true,
      creditScore: "excellent",
    },
    
    behaviorSignals: {
      pageViews: 25,
      timeOnSite: 720,
      documentsDownloaded: 4,
      videoWatchTime: 380,
      questionsAsked: 5,
      responseTime: 1200,
      interactionQuality: "high",
      returnVisitor: true,
      deviceType: "desktop",
    },
    
    propertyInterest: {
      priceRange: {
        min: 3000000,
        max: 5000000,
      },
      propertyType: "apartment",
      purpose: "investment",
      timeline: "immediate",
      financingStatus: "cash_buyer",
    },
    
    notes: "Inversionista experimentado. Ya tiene 3 propiedades en renta. Busca ROI > 8%.",
  },

  warmFirstBuyer: {
    name: "Ana Profesional",
    email: "ana.garcia@empresa.com",
    phone: "+52 55 8765 4321",
    age: 28,
    location: "Monterrey, NL",
    source: "organic",
    
    socialProfiles: [
      {
        platform: "linkedin",
        profileUrl: "https://linkedin.com/in/anagarcia",
        followers: 350,
        verified: false,
        businessProfile: false,
        professionalContent: true,
        activityLevel: "medium",
      }
    ],
    
    financialSignals: {
      employmentStatus: "employed",
      industryType: "Finance",
      companySize: "medium",
      estimatedIncome: "high",
      investmentExperience: false,
      propertyOwnership: false,
      creditScore: "good",
    },
    
    behaviorSignals: {
      pageViews: 12,
      timeOnSite: 480,
      documentsDownloaded: 2,
      videoWatchTime: 180,
      questionsAsked: 3,
      responseTime: 3600,
      interactionQuality: "medium",
      returnVisitor: true,
      deviceType: "mobile",
    },
    
    propertyInterest: {
      priceRange: {
        min: 1500000,
        max: 2500000,
      },
      propertyType: "apartment",
      purpose: "primary_residence",
      timeline: "1-3_months",
      financingStatus: "pre_approved",
    },
    
    notes: "Primera compra. Pre-aprobada por banco. Muy motivada.",
  },

  coldCurious: {
    name: "Pedro Browser",
    email: "pedro123@email.com",
    phone: "+52 55 9999 8888",
    age: 35,
    location: "Guadalajara, JAL",
    source: "paid_ads",
    
    socialProfiles: [
      {
        platform: "facebook",
        followers: 200,
        activityLevel: "low",
      }
    ],
    
    financialSignals: {
      employmentStatus: "employed",
      companySize: "small",
      estimatedIncome: "medium",
      investmentExperience: false,
      propertyOwnership: false,
      creditScore: "fair",
    },
    
    behaviorSignals: {
      pageViews: 4,
      timeOnSite: 120,
      documentsDownloaded: 0,
      videoWatchTime: 0,
      questionsAsked: 0,
      interactionQuality: "low",
      returnVisitor: false,
      deviceType: "mobile",
    },
    
    propertyInterest: {
      priceRange: {
        min: 800000,
        max: 1500000,
      },
      propertyType: "apartment",
      purpose: "unsure",
      timeline: "6-12_months",
      financingStatus: "unsure",
    },
    
    notes: "Llegó de anuncio pagado. Baja interacción.",
  },

  disqualifiedFake: {
    name: "Usuario Temporal",
    email: "temp123@tempmail.com",
    age: 19,
    location: "Desconocido",
    source: "other",
    
    behaviorSignals: {
      pageViews: 1,
      timeOnSite: 18,
      documentsDownloaded: 0,
      videoWatchTime: 0,
      questionsAsked: 0,
      interactionQuality: "low",
      returnVisitor: false,
      deviceType: "mobile",
    },
    
    propertyInterest: {
      priceRange: {
        min: 500000,
        max: 10000000,
      },
      propertyType: "apartment",
      purpose: "unsure",
      timeline: "just_browsing",
      financingStatus: "unsure",
    },
    
    notes: "Email temporal. Sospechoso.",
  },

  retiredInvestor: {
    name: "Roberto Jubilado",
    email: "roberto.inversionista@gmail.com",
    phone: "+52 55 4444 3333",
    age: 68,
    location: "Querétaro, QRO",
    source: "referral",
    
    socialProfiles: [
      {
        platform: "linkedin",
        followers: 800,
        verified: false,
        professionalContent: false,
        activityLevel: "low",
      }
    ],
    
    financialSignals: {
      employmentStatus: "retired",
      estimatedIncome: "high",
      investmentExperience: true,
      propertyOwnership: true,
      creditScore: "excellent",
    },
    
    behaviorSignals: {
      pageViews: 15,
      timeOnSite: 900,
      documentsDownloaded: 3,
      videoWatchTime: 240,
      questionsAsked: 4,
      responseTime: 7200,
      interactionQuality: "high",
      returnVisitor: true,
      deviceType: "desktop",
    },
    
    propertyInterest: {
      priceRange: {
        min: 2000000,
        max: 3500000,
      },
      propertyType: "house",
      purpose: "investment",
      timeline: "3-6_months",
      financingStatus: "cash_buyer",
    },
    
    notes: "Jubilado con experiencia. Busca diversificar patrimonio. No tiene prisa pero es serio.",
  },

  youngProfessional: {
    name: "Laura Startup",
    email: "laura@startup.tech",
    phone: "+52 55 7777 6666",
    age: 26,
    location: "Ciudad de México, CDMX",
    source: "social_media",
    
    socialProfiles: [
      {
        platform: "linkedin",
        followers: 500,
        verified: false,
        businessProfile: false,
        professionalContent: true,
        activityLevel: "high",
      },
      {
        platform: "instagram",
        followers: 3200,
        activityLevel: "high",
      }
    ],
    
    financialSignals: {
      employmentStatus: "self_employed",
      industryType: "Technology",
      companySize: "startup",
      estimatedIncome: "medium",
      investmentExperience: false,
      propertyOwnership: false,
      creditScore: "good",
    },
    
    behaviorSignals: {
      pageViews: 18,
      timeOnSite: 540,
      documentsDownloaded: 2,
      videoWatchTime: 300,
      questionsAsked: 6,
      responseTime: 600,
      interactionQuality: "high",
      returnVisitor: true,
      deviceType: "mobile",
    },
    
    propertyInterest: {
      priceRange: {
        min: 1800000,
        max: 2800000,
      },
      propertyType: "condo",
      purpose: "primary_residence",
      timeline: "1-3_months",
      financingStatus: "needs_financing",
    },
    
    notes: "Trabajadora independiente en tech. Ingreso variable pero constante. Muy interesada.",
  },
};

export const exampleScenarios = {
  massQualification: {
    description: "Calificar múltiples leads de una campaña de marketing",
    leads: [
      exampleLeads.hotInvestor,
      exampleLeads.warmFirstBuyer,
      exampleLeads.coldCurious,
      exampleLeads.youngProfessional,
      exampleLeads.retiredInvestor,
    ],
    expectedResults: {
      hot: 2,
      warm: 2,
      cold: 1,
      totalValue: "> $150,000 MXN en comisiones estimadas",
    }
  },

  urgentLeads: {
    description: "Identificar leads que requieren atención inmediata",
    criteria: {
      timeline: "immediate",
      financingStatus: "cash_buyer",
      minScore: 75,
    },
    expectedLeads: ["hotInvestor"],
  },

  investorProfile: {
    description: "Filtrar solo inversionistas experimentados",
    criteria: {
      investmentExperience: true,
      propertyOwnership: true,
      purpose: "investment",
    },
    expectedLeads: ["hotInvestor", "retiredInvestor"],
  },

  highValueTargets: {
    description: "Leads con potencial de comisión > $50,000 MXN",
    criteria: {
      minPrice: 3000000,
      conversionProbability: "> 60%",
    },
    expectedLeads: ["hotInvestor"],
  },

  nurtureSegment: {
    description: "Leads para campaña de email nurturing (fríos pero válidos)",
    criteria: {
      category: "cold",
      minScore: 30,
      notDisqualified: true,
    },
    expectedLeads: ["coldCurious"],
  },
};

export const usageExamples = `
# 📚 Ejemplos de Uso del Sistema

## Ejemplo 1: Calificar Lead Individual

\`\`\`typescript
import { api } from '~/utils/api';
import { exampleLeads } from './examples/lead-examples';

const scoreLeadMutation = api.leadScoring.scoreLead.useMutation();

// Calificar al inversionista hot
const result = await scoreLeadMutation.mutateAsync(exampleLeads.hotInvestor);

console.log(\`Score: \${result.overallScore}/100\`);
// Output: Score: 92/100

console.log(\`Categoría: \${result.category}\`);
// Output: Categoría: hot

console.log(\`Conversión estimada: \${result.estimatedROI.conversionProbability}%\`);
// Output: Conversión estimada: 85%

console.log(\`Valor estimado: $\${result.estimatedROI.estimatedValue?.toLocaleString('es-MX')}\`);
// Output: Valor estimado: $76,500
\`\`\`

## Ejemplo 2: Calificación Masiva

\`\`\`typescript
const batchScoreMutation = api.leadScoring.batchScoreLeads.useMutation();

const campaignLeads = [
  exampleLeads.hotInvestor,
  exampleLeads.warmFirstBuyer,
  exampleLeads.coldCurious,
  exampleLeads.youngProfessional,
  exampleLeads.retiredInvestor,
];

const result = await batchScoreMutation.mutateAsync({ leads: campaignLeads });

console.log(\`Total de leads: \${result.summary.totalLeads}\`);
console.log(\`Hot leads: \${result.summary.hotLeads}\`);
console.log(\`Leads tibios: \${result.summary.warmLeads}\`);
console.log(\`Score promedio: \${result.summary.avgScore.toFixed(1)}\`);
console.log(\`Valor total estimado: $\${result.summary.totalEstimatedValue?.toLocaleString('es-MX')}\`);

// Output:
// Total de leads: 5
// Hot leads: 2
// Leads tibios: 2
// Score promedio: 68.4
// Valor total estimado: $187,250
\`\`\`

## Ejemplo 3: Filtrar Hot Leads para Acción Inmediata

\`\`\`typescript
const { scores } = await batchScoreMutation.mutateAsync({ leads: allLeads });

const hotLeads = scores.filter(score => score.category === 'hot');

hotLeads.forEach(lead => {
  console.log(\`🔥 HOT LEAD: \${lead.leadId}\`);
  console.log(\`   Score: \${lead.overallScore}\`);
  console.log(\`   Acción: \${lead.recommendations[0]}\`);
  console.log(\`   Valor: $\${lead.estimatedROI.estimatedValue?.toLocaleString('es-MX')}\`);
  console.log('');
});

// Output:
// 🔥 HOT LEAD: lead-1694...
//    Score: 92
//    Acción: 🔥 PRIORIDAD ALTA: Contactar inmediatamente por teléfono
//    Valor: $76,500
\`\`\`

## Ejemplo 4: Análisis de Perfil Social

\`\`\`typescript
const analyzeSocialMutation = api.leadScoring.analyzeSocialProfile.useMutation();

const result = await analyzeSocialMutation.mutateAsync({
  profileUrl: "https://linkedin.com/in/carlosempresario",
  platform: "linkedin"
});

console.log(\`Credibilidad: \${result.credibilityScore}/100\`);
console.log(\`¿Es profesional?: \${result.insights.isProfessional ? 'Sí' : 'No'}\`);
console.log(\`¿Es inversionista?: \${result.insights.isInvestor ? 'Sí' : 'No'}\`);
console.log(\`Nivel de engagement: \${result.insights.engagementLevel}\`);

result.insights.greenFlags.forEach(flag => {
  console.log(\`  ✅ \${flag}\`);
});

result.insights.redFlags.forEach(flag => {
  console.log(\`  🚩 \${flag}\`);
});

// Output:
// Credibilidad: 85/100
// ¿Es profesional?: Sí
// ¿Es inversionista?: No
// Nivel de engagement: medium
//   ✅ Perfil profesional en LinkedIn
\`\`\`

## Ejemplo 5: Predicción de Conversión

\`\`\`typescript
const predictConversionQuery = api.leadScoring.predictConversion.useQuery({
  leadId: "lead-123",
  score: 92,
  category: "hot",
  priceRange: { min: 3000000, max: 5000000 }
});

const prediction = predictConversionQuery.data;

console.log(\`Probabilidad de conversión: \${prediction?.conversionProbability}%\`);
console.log(\`Tiempo estimado: \${prediction?.estimatedTimeToClose}\`);
console.log(\`Revenue estimado: $\${prediction?.estimatedRevenue.toLocaleString('es-MX')}\`);
console.log(\`Confianza: \${prediction?.confidenceLevel}\`);

console.log('\\nFactores clave:');
prediction?.keyFactors.forEach(factor => {
  const emoji = factor.impact === 'positive' ? '✅' : factor.impact === 'negative' ? '❌' : '⚪';
  console.log(\`  \${emoji} \${factor.factor} (peso: \${factor.weight * 100}%)\`);
});

// Output:
// Probabilidad de conversión: 85%
// Tiempo estimado: 1-2 semanas
// Revenue estimado: $102,000
// Confianza: high
//
// Factores clave:
//   ✅ Capacidad financiera (peso: 30%)
//   ✅ Intención de compra (peso: 25%)
//   ✅ Autenticidad del lead (peso: 20%)
\`\`\`

## Ejemplo 6: Obtener Lista Priorizada

\`\`\`typescript
const getPrioritiesQuery = api.leadScoring.getLeadPriorities.useQuery({
  scores: allScores,
  maxLeads: 10
});

const priorities = getPrioritiesQuery.data?.prioritizedLeads;

console.log('📋 LISTA DE PRIORIDADES\\n');
priorities?.forEach((lead, index) => {
  const emoji = lead.category === 'hot' ? '🔥' : lead.category === 'warm' ? '⚡' : '❄️';
  console.log(\`\${index + 1}. \${emoji} Score: \${lead.score} - Prioridad: \${lead.priority}\`);
  console.log(\`   Próxima acción: \${lead.nextAction}\`);
  console.log(\`   Deadline: \${lead.deadline}\`);
  console.log('');
});

// Output:
// 📋 LISTA DE PRIORIDADES
//
// 1. 🔥 Score: 92 - Prioridad: 1
//    Próxima acción: Contactar por teléfono AHORA
//    Deadline: Hoy
//
// 2. 🔥 Score: 88 - Prioridad: 2
//    Próxima acción: Contactar por teléfono AHORA
//    Deadline: Hoy
//
// 3. ⚡ Score: 72 - Prioridad: 100
//    Próxima acción: Enviar propuesta personalizada
//    Deadline: Próximas 48 horas
\`\`\`

## Ejemplo 7: Workflow Completo de Calificación

\`\`\`typescript
async function qualifyAndPrioritizeLeads(rawLeads: LeadInput[]) {
  // 1. Calificar todos los leads
  const { scores, summary } = await batchScoreMutation.mutateAsync({ 
    leads: rawLeads 
  });

  console.log(\`\\n📊 RESUMEN DE CALIFICACIÓN\`);
  console.log(\`Total: \${summary.totalLeads} leads\`);
  console.log(\`🔥 Hot: \${summary.hotLeads}\`);
  console.log(\`⚡ Tibios: \${summary.warmLeads}\`);
  console.log(\`❄️ Fríos: \${summary.coldLeads}\`);
  console.log(\`🚫 Descalificados: \${summary.disqualified}\`);
  console.log(\`💰 Valor total: $\${summary.totalEstimatedValue?.toLocaleString('es-MX')}\`);

  // 2. Obtener lista priorizada
  const { prioritizedLeads } = await getPrioritiesQuery.refetch();

  // 3. Separar por categoría
  const hotLeads = prioritizedLeads.filter(l => l.category === 'hot');
  const warmLeads = prioritizedLeads.filter(l => l.category === 'warm');
  
  // 4. Acciones automáticas
  console.log(\`\\n🚨 ACCIÓN INMEDIATA REQUERIDA:\`);
  hotLeads.forEach(lead => {
    console.log(\`  - Llamar a lead \${lead.leadId} (Score: \${lead.score})\`);
    // Aquí podrías disparar notificaciones, enviar a CRM, etc.
  });

  console.log(\`\\n📅 PROGRAMAR PARA HOY/MAÑANA:\`);
  warmLeads.forEach(lead => {
    console.log(\`  - Email a lead \${lead.leadId} (Score: \${lead.score})\`);
  });

  return {
    hot: hotLeads,
    warm: warmLeads,
    summary
  };
}

// Usar el workflow
const result = await qualifyAndPrioritizeLeads([
  exampleLeads.hotInvestor,
  exampleLeads.warmFirstBuyer,
  exampleLeads.coldCurious,
  exampleLeads.youngProfessional,
  exampleLeads.retiredInvestor,
]);
\`\`\`

## Ejemplo 8: Detección de Fraude

\`\`\`typescript
import { aiPredictor } from '~/utils/ai-predictor';

const fraudCheck = aiPredictor.detectFraudRisk(exampleLeads.disqualifiedFake);

console.log(\`Nivel de riesgo: \${fraudCheck.riskLevel}\`);
console.log(\`Score de riesgo: \${fraudCheck.riskScore}/100\`);

if (fraudCheck.redFlags.length > 0) {
  console.log('\\n🚩 Banderas rojas detectadas:');
  fraudCheck.redFlags.forEach(flag => {
    console.log(\`  - \${flag}\`);
  });
}

// Output:
// Nivel de riesgo: high
// Score de riesgo: 85/100
//
// 🚩 Banderas rojas detectadas:
//   - 🚨 Email temporal detectado
//   - Interacción extremadamente baja
//   - Sin presencia en redes sociales
//   - Sin intención clara de compra
//   - Edad fuera del rango típico de compradores
\`\`\`
`;

export default exampleLeads;
