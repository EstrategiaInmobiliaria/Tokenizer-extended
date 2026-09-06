#!/usr/bin/env tsx

import { leadScorer } from '../src/utils/lead-scorer';
import { aiPredictor } from '../src/utils/ai-predictor';
import { exampleLeads } from '../examples/lead-examples';

console.log('🎯 DEMO: Sistema de Calificación de Leads Inmobiliarios con IA\n');
console.log('═══════════════════════════════════════════════════════════════\n');

const leads = Object.entries(exampleLeads);

for (const [key, lead] of leads) {
  console.log(`\n${'─'.repeat(60)}`);
  console.log(`\n📋 LEAD: ${lead.name}`);
  console.log(`   Email: ${lead.email}`);
  console.log(`   Fuente: ${lead.source}`);
  console.log(`   Rango: $${lead.propertyInterest.priceRange.min.toLocaleString('es-MX')} - $${lead.propertyInterest.priceRange.max.toLocaleString('es-MX')}`);
  console.log(`   Timeline: ${lead.propertyInterest.timeline}`);
  console.log(`   Financiamiento: ${lead.propertyInterest.financingStatus}`);

  const score = leadScorer.scoreLead(lead);
  
  const categoryEmojis = {
    hot: '🔥',
    warm: '⚡',
    cold: '❄️',
    disqualified: '🚫',
  };

  const categoryLabels = {
    hot: 'HOT LEAD',
    warm: 'LEAD TIBIO',
    cold: 'LEAD FRÍO',
    disqualified: 'DESCALIFICADO',
  };

  console.log(`\n${categoryEmojis[score.category]} RESULTADO: ${categoryLabels[score.category]}`);
  console.log(`   Score General: ${score.overallScore}/100`);
  console.log(`\n   📊 Scores Detallados:`);
  console.log(`      💰 Capacidad Financiera: ${score.scores.financialCapacity}`);
  console.log(`      🎯 Intención de Compra: ${score.scores.buyingIntent}`);
  console.log(`      ✅ Autenticidad: ${score.scores.authenticity}`);
  console.log(`      📱 Engagement: ${score.scores.engagement}`);
  console.log(`      🌐 Credibilidad Social: ${score.scores.socialCredibility}`);
  console.log(`      ⏱️  Urgencia Timeline: ${score.scores.timelineUrgency}`);

  console.log(`\n   🎲 Probabilidad de Conversión: ${score.estimatedROI.conversionProbability}%`);
  if (score.estimatedROI.estimatedValue) {
    console.log(`   💵 Valor Estimado: $${score.estimatedROI.estimatedValue.toLocaleString('es-MX')} MXN`);
  }

  if (score.redFlags && score.redFlags.length > 0) {
    console.log(`\n   🚩 Banderas Rojas:`);
    score.redFlags.forEach(flag => {
      console.log(`      - [${flag.severity.toUpperCase()}] ${flag.description}`);
    });
  }

  if (score.greenFlags && score.greenFlags.length > 0) {
    console.log(`\n   ✅ Banderas Verdes:`);
    score.greenFlags.forEach(flag => {
      console.log(`      - ${flag.description}`);
    });
  }

  console.log(`\n   💡 Recomendaciones:`);
  score.recommendations.slice(0, 3).forEach(rec => {
    console.log(`      - ${rec}`);
  });

  const behaviorPatterns = aiPredictor.analyzeBehaviorPattern(lead);
  if (behaviorPatterns.length > 0 && behaviorPatterns[0]?.pattern !== 'insufficient_data') {
    console.log(`\n   🔍 Patrones de Comportamiento:`);
    behaviorPatterns.slice(0, 2).forEach(pattern => {
      console.log(`      - ${pattern.pattern} (confianza: ${Math.round(pattern.confidence * 100)}%)`);
    });
  }

  const financialAnalysis = aiPredictor.predictFinancialCapacity(lead);
  console.log(`\n   💰 Análisis Financiero:`);
  console.log(`      - Ingresos estimados: $${financialAnalysis.estimatedIncome.toLocaleString('es-MX')} MXN/año`);
  console.log(`      - Score de liquidez: ${financialAnalysis.liquidityScore}/100`);
  console.log(`      - Capacidad de inversión: ${financialAnalysis.investmentCapacity}/100`);
  console.log(`      - Confianza: ${financialAnalysis.confidence}`);

  const socialInsights = aiPredictor.analyzeSocialMedia(lead);
  console.log(`\n   🌐 Análisis Social:`);
  console.log(`      - Score profesional: ${socialInsights.professionalScore}/100`);
  console.log(`      - Score de confianza: ${socialInsights.trustScore}/100`);
  console.log(`      - ¿Dueño de negocio?: ${socialInsights.businessOwnershipSignals ? 'Sí' : 'No'}`);
  console.log(`      - ¿Perfil inversionista?: ${socialInsights.investorProfile ? 'Sí' : 'No'}`);
  console.log(`      - Alineación lifestyle: ${socialInsights.lifestyleAlignment}`);

  const fraudCheck = aiPredictor.detectFraudRisk(lead);
  console.log(`\n   🔒 Detección de Fraude:`);
  console.log(`      - Nivel de riesgo: ${fraudCheck.riskLevel.toUpperCase()}`);
  console.log(`      - Score de riesgo: ${fraudCheck.riskScore}/100`);
  if (fraudCheck.redFlags.length > 0) {
    console.log(`      - Alertas: ${fraudCheck.redFlags.length}`);
  }

  console.log(`\n   🎯 Próximos Pasos:`);
  score.estimatedROI.recommendedActions.slice(0, 2).forEach(action => {
    console.log(`      - ${action}`);
  });
}

console.log(`\n${'─'.repeat(60)}`);
console.log('\n📊 RESUMEN GENERAL\n');

const allScores = leads.map(([_, lead]) => leadScorer.scoreLead(lead));

const summary = {
  total: allScores.length,
  hot: allScores.filter(s => s.category === 'hot').length,
  warm: allScores.filter(s => s.category === 'warm').length,
  cold: allScores.filter(s => s.category === 'cold').length,
  disqualified: allScores.filter(s => s.category === 'disqualified').length,
  avgScore: allScores.reduce((sum, s) => sum + s.overallScore, 0) / allScores.length,
  totalValue: allScores.reduce((sum, s) => sum + (s.estimatedROI.estimatedValue ?? 0), 0),
};

console.log(`Total de leads analizados: ${summary.total}`);
console.log(`\n🔥 Hot Leads: ${summary.hot} (${Math.round(summary.hot / summary.total * 100)}%)`);
console.log(`⚡ Leads Tibios: ${summary.warm} (${Math.round(summary.warm / summary.total * 100)}%)`);
console.log(`❄️ Leads Fríos: ${summary.cold} (${Math.round(summary.cold / summary.total * 100)}%)`);
console.log(`🚫 Descalificados: ${summary.disqualified} (${Math.round(summary.disqualified / summary.total * 100)}%)`);
console.log(`\n📈 Score Promedio: ${summary.avgScore.toFixed(1)}/100`);
console.log(`💰 Valor Total Estimado: $${Math.round(summary.totalValue).toLocaleString('es-MX')} MXN\n`);

console.log('═══════════════════════════════════════════════════════════════');
console.log('\n✅ Demo completado! Revisa los resultados arriba.\n');
console.log('💡 Tip: Los Hot Leads deben contactarse INMEDIATAMENTE');
console.log('💡 Tip: Los Descalificados no valen tu tiempo\n');
console.log('🚀 Para usar en tu aplicación:');
console.log('   1. yarn dev');
console.log('   2. Navega a http://localhost:3000/lead-scoring');
console.log('   3. Agrega tus leads y deja que la IA haga el trabajo!\n');
