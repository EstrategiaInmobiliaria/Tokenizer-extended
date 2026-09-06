import type { LeadInput, LeadScore } from '~/models/lead-scoring';

interface BehaviorPattern {
  pattern: string;
  confidence: number;
  indicators: string[];
}

interface FinancialCapacityAnalysis {
  estimatedIncome: number;
  debtToIncomeRatio: number;
  liquidityScore: number;
  investmentCapacity: number;
  confidence: 'high' | 'medium' | 'low';
  reasoning: string[];
}

interface SocialMediaInsights {
  professionalScore: number;
  wealthIndicators: string[];
  businessOwnershipSignals: boolean;
  investorProfile: boolean;
  lifestyleAlignment: 'luxury' | 'premium' | 'standard' | 'budget';
  trustScore: number;
}

export class AIPredictor {
  public analyzeBehaviorPattern(lead: LeadInput): BehaviorPattern[] {
    const patterns: BehaviorPattern[] = [];
    const behavior = lead.behaviorSignals;

    if (!behavior) {
      return [{
        pattern: 'insufficient_data',
        confidence: 0.3,
        indicators: ['Sin datos de comportamiento disponibles'],
      }];
    }

    if ((behavior.pageViews ?? 0) > 15 && (behavior.timeOnSite ?? 0) > 600) {
      patterns.push({
        pattern: 'high_intent_researcher',
        confidence: 0.85,
        indicators: [
          'Múltiples páginas vistas',
          'Alto tiempo de permanencia',
          'Comportamiento de investigación profunda',
        ],
      });
    }

    if ((behavior.documentsDownloaded ?? 0) > 2 && (behavior.videoWatchTime ?? 0) > 300) {
      patterns.push({
        pattern: 'serious_buyer',
        confidence: 0.9,
        indicators: [
          'Descarga de documentos legales/financieros',
          'Visualización completa de videos',
          'Interés en detalles técnicos',
        ],
      });
    }

    if ((behavior.timeOnSite ?? 0) < 60 && (behavior.pageViews ?? 0) < 3) {
      patterns.push({
        pattern: 'casual_browser',
        confidence: 0.75,
        indicators: [
          'Visita breve',
          'Pocas páginas exploradas',
          'Probable curiosidad sin intención',
        ],
      });
    }

    if (behavior.returnVisitor && (behavior.questionsAsked ?? 0) > 2) {
      patterns.push({
        pattern: 'engaged_prospect',
        confidence: 0.88,
        indicators: [
          'Visitante recurrente',
          'Hace preguntas específicas',
          'Muestra engagement sostenido',
        ],
      });
    }

    if ((behavior.responseTime ?? Infinity) < 1800) {
      patterns.push({
        pattern: 'urgent_buyer',
        confidence: 0.82,
        indicators: [
          'Respuestas rápidas',
          'Alta urgencia en comunicación',
          'Timeline acelerado',
        ],
      });
    }

    return patterns.length > 0 ? patterns : [{
      pattern: 'standard_lead',
      confidence: 0.5,
      indicators: ['Comportamiento estándar sin patrones destacables'],
    }];
  }

  public predictFinancialCapacity(lead: LeadInput): FinancialCapacityAnalysis {
    const financial = lead.financialSignals;
    let estimatedIncome = 0;
    let confidence: 'high' | 'medium' | 'low' = 'low';
    const reasoning: string[] = [];

    if (!financial) {
      return {
        estimatedIncome: 0,
        debtToIncomeRatio: 0.5,
        liquidityScore: 30,
        investmentCapacity: 20,
        confidence: 'low',
        reasoning: ['Sin información financiera disponible'],
      };
    }

    if (financial.employmentStatus === 'business_owner') {
      estimatedIncome = 150000;
      reasoning.push('Dueño de negocio - ingresos estimados altos');
      confidence = 'medium';
    } else if (financial.employmentStatus === 'employed') {
      if (financial.companySize === 'enterprise' || financial.companySize === 'large') {
        estimatedIncome = 100000;
        reasoning.push('Empleado en empresa grande - ingresos estables');
      } else {
        estimatedIncome = 60000;
        reasoning.push('Empleado - ingresos moderados');
      }
      confidence = 'medium';
    } else if (financial.employmentStatus === 'self_employed') {
      estimatedIncome = 80000;
      reasoning.push('Trabajador independiente - ingresos variables');
      confidence = 'low';
    } else if (financial.employmentStatus === 'retired') {
      estimatedIncome = 50000;
      reasoning.push('Jubilado - ingresos de pensión');
      confidence = 'medium';
    }

    if (financial.estimatedIncome === 'very_high') {
      estimatedIncome = Math.max(estimatedIncome, 200000);
      reasoning.push('Señales de ingresos muy altos');
      confidence = 'high';
    } else if (financial.estimatedIncome === 'high') {
      estimatedIncome = Math.max(estimatedIncome, 120000);
      reasoning.push('Señales de ingresos altos');
      confidence = 'high';
    }

    if (financial.propertyOwnership) {
      estimatedIncome *= 1.3;
      reasoning.push('Ya es propietario - aumenta estimación de patrimonio');
    }

    if (financial.investmentExperience) {
      reasoning.push('Experiencia en inversiones - conocimiento financiero');
      confidence = confidence === 'low' ? 'medium' : 'high';
    }

    const propertyPrice = (lead.propertyInterest.priceRange.min + lead.propertyInterest.priceRange.max) / 2;
    const debtToIncomeRatio = this.calculateDebtRatio(lead.propertyInterest.financingStatus, propertyPrice, estimatedIncome);
    
    let liquidityScore = 50;
    if (lead.propertyInterest.financingStatus === 'cash_buyer') {
      liquidityScore = 95;
      reasoning.push('Comprador en efectivo - alta liquidez');
    } else if (lead.propertyInterest.financingStatus === 'pre_approved') {
      liquidityScore = 75;
      reasoning.push('Pre-aprobado para crédito - liquidez verificada');
    } else if (lead.propertyInterest.financingStatus === 'needs_financing') {
      liquidityScore = 40;
      reasoning.push('Necesita financiamiento - liquidez limitada');
    }

    if (financial.creditScore === 'excellent') {
      liquidityScore += 10;
      reasoning.push('Excelente historial crediticio');
    } else if (financial.creditScore === 'poor') {
      liquidityScore -= 30;
      reasoning.push('⚠️ Historial crediticio deficiente');
    }

    const investmentCapacity = this.calculateInvestmentCapacity(
      estimatedIncome,
      propertyPrice,
      liquidityScore,
      debtToIncomeRatio
    );

    return {
      estimatedIncome,
      debtToIncomeRatio,
      liquidityScore,
      investmentCapacity,
      confidence,
      reasoning,
    };
  }

  public analyzeSocialMedia(lead: LeadInput): SocialMediaInsights {
    const socials = lead.socialProfiles ?? [];
    let professionalScore = 0;
    const wealthIndicators: string[] = [];
    let businessOwnershipSignals = false;
    let investorProfile = false;
    let trustScore = 50;

    if (socials.length === 0) {
      return {
        professionalScore: 20,
        wealthIndicators: ['Sin presencia en redes sociales'],
        businessOwnershipSignals: false,
        investorProfile: false,
        lifestyleAlignment: 'standard',
        trustScore: 30,
      };
    }

    for (const profile of socials) {
      if (profile.platform === 'linkedin') {
        professionalScore += 30;
        trustScore += 15;
        
        if (profile.professionalContent) {
          professionalScore += 20;
          wealthIndicators.push('Contenido profesional en LinkedIn');
        }
        
        if ((profile.followers ?? 0) > 1000) {
          professionalScore += 15;
          wealthIndicators.push('Amplia red profesional (>1000 contactos)');
        }
        
        if (profile.businessProfile) {
          businessOwnershipSignals = true;
          wealthIndicators.push('Perfil de dueño de negocio');
        }
      }

      if (profile.verified) {
        trustScore += 20;
        wealthIndicators.push('Cuenta verificada');
      }

      if (profile.activityLevel === 'high') {
        trustScore += 10;
        professionalScore += 10;
      }

      if (profile.platform === 'instagram' && (profile.followers ?? 0) > 10000) {
        wealthIndicators.push('Influencer o figura pública');
        professionalScore += 10;
      }
    }

    if (lead.financialSignals?.investmentExperience) {
      investorProfile = true;
      wealthIndicators.push('Experiencia documentada en inversiones');
    }

    const lifestyleAlignment = this.determineLifestyle(
      professionalScore,
      wealthIndicators.length,
      lead.propertyInterest.priceRange
    );

    return {
      professionalScore: Math.min(professionalScore, 100),
      wealthIndicators,
      businessOwnershipSignals,
      investorProfile,
      lifestyleAlignment,
      trustScore: Math.min(trustScore, 100),
    };
  }

  public generateAIRecommendations(
    score: LeadScore,
    behaviorPatterns: BehaviorPattern[],
    financialAnalysis: FinancialCapacityAnalysis,
    socialInsights: SocialMediaInsights
  ): string[] {
    const recommendations: string[] = [];

    const hasSerious = behaviorPatterns.some(p => p.pattern === 'serious_buyer' || p.pattern === 'urgent_buyer');
    if (hasSerious && score.category === 'hot') {
      recommendations.push('🚨 ACCIÓN INMEDIATA: Este es un comprador serio con alta urgencia. Contactar en las próximas 2 horas.');
    }

    if (financialAnalysis.investmentCapacity > 70 && socialInsights.investorProfile) {
      recommendations.push('💼 PERFIL INVERSIONISTA: Preparar análisis ROI detallado con proyecciones a 5 años.');
      recommendations.push('📊 Destacar métricas de apreciación, flujo de caja y beneficios fiscales.');
    }

    if (financialAnalysis.liquidityScore < 40) {
      recommendations.push('💰 FINANCIAMIENTO: Conectar con asesor financiero antes de mostrar propiedades.');
      recommendations.push('📋 Solicitar pre-calificación de crédito como paso siguiente.');
    }

    if (socialInsights.businessOwnershipSignals) {
      recommendations.push('🏢 DUEÑO DE NEGOCIO: Mencionar beneficios fiscales y opciones de propiedad corporativa.');
    }

    const hasCasual = behaviorPatterns.some(p => p.pattern === 'casual_browser');
    if (hasCasual && score.category === 'cold') {
      recommendations.push('⏱️ NO PRIORIZAR: Comportamiento indica curiosidad, no urgencia. Nutrir con contenido educativo.');
    }

    if (socialInsights.trustScore < 40) {
      recommendations.push('⚠️ VALIDACIÓN REQUERIDA: Baja credibilidad social. Solicitar referencias o documentación de identidad.');
    }

    if (financialAnalysis.confidence === 'high' && financialAnalysis.investmentCapacity > 80) {
      recommendations.push('✅ ALTA CONFIANZA: Capacidad financiera verificada. Mostrar propiedades premium sin restricciones.');
    }

    const avgPrice = score.estimatedROI.estimatedValue ?? 0;
    if (avgPrice > 50000) {
      recommendations.push(`💵 ALTO VALOR ESTIMADO: Este lead podría generar $${avgPrice.toLocaleString('es-MX')} en comisiones.`);
    }

    return recommendations;
  }

  private calculateDebtRatio(financingStatus: string, propertyPrice: number, income: number): number {
    if (income === 0) return 0.5;
    
    if (financingStatus === 'cash_buyer') {
      return 0.0;
    }
    
    const monthlyPayment = (propertyPrice * 0.8) / (30 * 12) * 1.06;
    const monthlyIncome = income / 12;
    
    return Math.min(monthlyPayment / monthlyIncome, 1.0);
  }

  private calculateInvestmentCapacity(
    income: number,
    propertyPrice: number,
    liquidityScore: number,
    debtRatio: number
  ): number {
    let capacity = 50;

    const priceToIncomeRatio = propertyPrice / income;
    
    if (priceToIncomeRatio < 3) {
      capacity += 30;
    } else if (priceToIncomeRatio < 5) {
      capacity += 15;
    } else if (priceToIncomeRatio > 10) {
      capacity -= 30;
    }

    capacity += (liquidityScore - 50) * 0.4;

    if (debtRatio < 0.28) {
      capacity += 20;
    } else if (debtRatio > 0.43) {
      capacity -= 30;
    }

    return Math.min(Math.max(Math.round(capacity), 0), 100);
  }

  private determineLifestyle(
    professionalScore: number,
    wealthIndicatorCount: number,
    priceRange: { min: number; max: number }
  ): 'luxury' | 'premium' | 'standard' | 'budget' {
    const avgPrice = (priceRange.min + priceRange.max) / 2;
    
    if (avgPrice > 5000000 && professionalScore > 70 && wealthIndicatorCount > 3) {
      return 'luxury';
    }
    
    if (avgPrice > 3000000 && professionalScore > 50) {
      return 'premium';
    }
    
    if (avgPrice < 1000000 && professionalScore < 30) {
      return 'budget';
    }
    
    return 'standard';
  }

  public detectFraudRisk(lead: LeadInput): {
    riskLevel: 'high' | 'medium' | 'low';
    riskScore: number;
    redFlags: string[];
  } {
    const redFlags: string[] = [];
    let riskScore = 0;

    if (!lead.phone || lead.phone.length < 10) {
      redFlags.push('Teléfono faltante o inválido');
      riskScore += 20;
    }

    if (!lead.socialProfiles || lead.socialProfiles.length === 0) {
      redFlags.push('Sin presencia en redes sociales');
      riskScore += 15;
    }

    const behavior = lead.behaviorSignals;
    if (behavior && (behavior.timeOnSite ?? 0) < 30 && (behavior.pageViews ?? 0) < 2) {
      redFlags.push('Interacción extremadamente baja');
      riskScore += 25;
    }

    if (lead.propertyInterest.timeline === 'just_browsing' && lead.propertyInterest.purpose === 'unsure') {
      redFlags.push('Sin intención clara de compra');
      riskScore += 20;
    }

    const financial = lead.financialSignals;
    if (financial?.employmentStatus === 'unemployed' && lead.propertyInterest.financingStatus === 'cash_buyer') {
      redFlags.push('⚠️ Inconsistencia: sin empleo pero comprador en efectivo');
      riskScore += 30;
    }

    if (!lead.age || lead.age < 21 || lead.age > 80) {
      redFlags.push('Edad fuera del rango típico de compradores');
      riskScore += 10;
    }

    const emailDomain = lead.email.split('@')[1];
    if (emailDomain && ['tempmail.com', 'guerrillamail.com', '10minutemail.com'].includes(emailDomain)) {
      redFlags.push('🚨 Email temporal detectado');
      riskScore += 40;
    }

    const riskLevel = riskScore > 50 ? 'high' : riskScore > 25 ? 'medium' : 'low';

    return {
      riskLevel,
      riskScore: Math.min(riskScore, 100),
      redFlags,
    };
  }
}

export const aiPredictor = new AIPredictor();
