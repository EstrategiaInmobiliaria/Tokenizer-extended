import type { LeadInput, LeadScore, SocialMediaProfile, FinancialSignals, BehaviorSignals } from '~/models/lead-scoring';

interface ScoringWeights {
  financialCapacity: number;
  buyingIntent: number;
  authenticity: number;
  engagement: number;
  socialCredibility: number;
  timelineUrgency: number;
}

const DEFAULT_WEIGHTS: ScoringWeights = {
  financialCapacity: 0.30,
  buyingIntent: 0.25,
  authenticity: 0.20,
  engagement: 0.10,
  socialCredibility: 0.10,
  timelineUrgency: 0.05,
};

export class LeadScorer {
  private weights: ScoringWeights;

  constructor(customWeights?: Partial<ScoringWeights>) {
    this.weights = { ...DEFAULT_WEIGHTS, ...customWeights };
  }

  public scoreLead(lead: LeadInput): LeadScore {
    const scores = {
      financialCapacity: this.scoreFinancialCapacity(lead),
      buyingIntent: this.scoreBuyingIntent(lead),
      authenticity: this.scoreAuthenticity(lead),
      engagement: this.scoreEngagement(lead),
      socialCredibility: this.scoreSocialCredibility(lead),
      timelineUrgency: this.scoreTimelineUrgency(lead),
    };

    const overallScore = this.calculateWeightedScore(scores);
    const category = this.categorizeScore(overallScore);
    const redFlags = this.detectRedFlags(lead, scores);
    const greenFlags = this.detectGreenFlags(lead, scores);
    const recommendations = this.generateRecommendations(lead, scores, category);
    const estimatedROI = this.calculateROI(lead, scores, overallScore);

    return {
      leadId: lead.id || `lead-${Date.now()}`,
      overallScore,
      category,
      scores,
      redFlags,
      greenFlags,
      recommendations,
      estimatedROI,
      timestamp: new Date().toISOString(),
    };
  }

  private scoreFinancialCapacity(lead: LeadInput): number {
    let score = 0;
    const financial = lead.financialSignals;

    if (!financial) return 30;

    if (financial.employmentStatus === 'business_owner') score += 25;
    else if (financial.employmentStatus === 'employed') score += 20;
    else if (financial.employmentStatus === 'self_employed') score += 18;
    else if (financial.employmentStatus === 'retired') score += 15;
    else if (financial.employmentStatus === 'unemployed') score += 5;

    if (financial.companySize === 'enterprise' || financial.companySize === 'large') score += 15;
    else if (financial.companySize === 'medium') score += 12;
    else if (financial.companySize === 'small') score += 8;

    if (financial.estimatedIncome === 'very_high') score += 30;
    else if (financial.estimatedIncome === 'high') score += 20;
    else if (financial.estimatedIncome === 'medium') score += 10;

    if (financial.investmentExperience) score += 15;
    if (financial.propertyOwnership) score += 10;

    if (financial.creditScore === 'excellent') score += 15;
    else if (financial.creditScore === 'good') score += 10;
    else if (financial.creditScore === 'fair') score += 5;
    else if (financial.creditScore === 'poor') score -= 20;

    if (lead.propertyInterest.financingStatus === 'cash_buyer') score += 20;
    else if (lead.propertyInterest.financingStatus === 'pre_approved') score += 15;
    else if (lead.propertyInterest.financingStatus === 'needs_financing') score += 5;

    return Math.min(Math.max(score, 0), 100);
  }

  private scoreBuyingIntent(lead: LeadInput): number {
    let score = 50;

    if (lead.propertyInterest.purpose === 'investment') score += 25;
    else if (lead.propertyInterest.purpose === 'primary_residence') score += 20;
    else if (lead.propertyInterest.purpose === 'vacation_home') score += 15;
    else if (lead.propertyInterest.purpose === 'unsure') score -= 15;

    if (lead.propertyInterest.timeline === 'immediate') score += 25;
    else if (lead.propertyInterest.timeline === '1-3_months') score += 20;
    else if (lead.propertyInterest.timeline === '3-6_months') score += 10;
    else if (lead.propertyInterest.timeline === '6-12_months') score += 5;
    else if (lead.propertyInterest.timeline === 'just_browsing') score -= 30;

    const behavior = lead.behaviorSignals;
    if (behavior) {
      if ((behavior.pageViews ?? 0) > 10) score += 10;
      if ((behavior.documentsDownloaded ?? 0) > 2) score += 10;
      if ((behavior.questionsAsked ?? 0) > 3) score += 15;
      if (behavior.returnVisitor) score += 10;
    }

    return Math.min(Math.max(score, 0), 100);
  }

  private scoreAuthenticity(lead: LeadInput): number {
    let score = 60;
    const redFlagCount = this.detectRedFlags(lead, {} as any).length;
    
    score -= redFlagCount * 15;

    if (!lead.phone || lead.phone.length < 10) score -= 10;
    if (!lead.age || lead.age < 18 || lead.age > 85) score -= 10;
    
    const behavior = lead.behaviorSignals;
    if (behavior) {
      if ((behavior.timeOnSite ?? 0) < 30) score -= 15;
      if (behavior.interactionQuality === 'high') score += 20;
      else if (behavior.interactionQuality === 'low') score -= 20;
      
      if ((behavior.responseTime ?? 0) < 3600) score += 10;
    }

    const hasMultipleSocialProfiles = (lead.socialProfiles?.length ?? 0) >= 2;
    if (hasMultipleSocialProfiles) score += 15;

    if (lead.source === 'referral') score += 15;
    else if (lead.source === 'organic') score += 10;
    else if (lead.source === 'paid_ads') score -= 5;

    return Math.min(Math.max(score, 0), 100);
  }

  private scoreEngagement(lead: LeadInput): number {
    let score = 40;
    const behavior = lead.behaviorSignals;

    if (!behavior) return 40;

    const pageViews = behavior.pageViews ?? 0;
    if (pageViews > 20) score += 30;
    else if (pageViews > 10) score += 20;
    else if (pageViews > 5) score += 10;
    else if (pageViews < 2) score -= 10;

    const timeOnSite = behavior.timeOnSite ?? 0;
    if (timeOnSite > 600) score += 20;
    else if (timeOnSite > 300) score += 15;
    else if (timeOnSite > 120) score += 10;
    else if (timeOnSite < 30) score -= 15;

    const videoWatchTime = behavior.videoWatchTime ?? 0;
    if (videoWatchTime > 300) score += 15;
    else if (videoWatchTime > 120) score += 10;

    if ((behavior.documentsDownloaded ?? 0) > 0) score += 10;
    if ((behavior.questionsAsked ?? 0) > 0) score += 10;
    if (behavior.returnVisitor) score += 15;

    return Math.min(Math.max(score, 0), 100);
  }

  private scoreSocialCredibility(lead: LeadInput): number {
    let score = 40;
    const socials = lead.socialProfiles ?? [];

    if (socials.length === 0) return 30;

    for (const profile of socials) {
      if (profile.verified) score += 15;
      if (profile.businessProfile) score += 10;
      if (profile.professionalContent) score += 10;

      const followers = profile.followers ?? 0;
      if (profile.platform === 'linkedin') {
        if (followers > 1000) score += 15;
        else if (followers > 500) score += 10;
      }

      if (profile.activityLevel === 'high') score += 10;
      else if (profile.activityLevel === 'medium') score += 5;
      else if (profile.activityLevel === 'none') score -= 5;
    }

    const hasLinkedIn = socials.some(p => p.platform === 'linkedin');
    if (hasLinkedIn) score += 15;

    return Math.min(Math.max(score, 0), 100);
  }

  private scoreTimelineUrgency(lead: LeadInput): number {
    const timelineMap: Record<string, number> = {
      'immediate': 100,
      '1-3_months': 80,
      '3-6_months': 60,
      '6-12_months': 40,
      'over_1_year': 20,
      'just_browsing': 10,
    };

    return timelineMap[lead.propertyInterest.timeline] ?? 50;
  }

  private calculateWeightedScore(scores: Record<keyof ScoringWeights, number>): number {
    let weightedSum = 0;
    
    for (const [key, value] of Object.entries(scores)) {
      const weight = this.weights[key as keyof ScoringWeights];
      weightedSum += value * weight;
    }

    return Math.round(weightedSum);
  }

  private categorizeScore(score: number): 'hot' | 'warm' | 'cold' | 'disqualified' {
    if (score >= 75) return 'hot';
    if (score >= 50) return 'warm';
    if (score >= 30) return 'cold';
    return 'disqualified';
  }

  private detectRedFlags(lead: LeadInput, scores: Record<keyof ScoringWeights, number>): Array<{ type: string; severity: 'high' | 'medium' | 'low'; description: string }> {
    const flags: Array<{ type: string; severity: 'high' | 'medium' | 'low'; description: string }> = [];

    if (lead.propertyInterest.timeline === 'just_browsing') {
      flags.push({
        type: 'no_urgency',
        severity: 'high',
        description: 'Lead indica que solo está navegando sin intención de compra',
      });
    }

    if (lead.propertyInterest.purpose === 'unsure') {
      flags.push({
        type: 'unclear_purpose',
        severity: 'medium',
        description: 'Lead no tiene claro el propósito de la compra',
      });
    }

    if (!lead.phone || lead.phone.length < 10) {
      flags.push({
        type: 'incomplete_contact',
        severity: 'medium',
        description: 'Información de contacto incompleta',
      });
    }

    const behavior = lead.behaviorSignals;
    if (behavior && (behavior.timeOnSite ?? 0) < 30) {
      flags.push({
        type: 'low_engagement',
        severity: 'high',
        description: 'Tiempo en el sitio muy bajo (<30 segundos), posible curiosidad',
      });
    }

    if (behavior && (behavior.pageViews ?? 0) < 2) {
      flags.push({
        type: 'minimal_interaction',
        severity: 'medium',
        description: 'Pocas páginas vistas, baja exploración del contenido',
      });
    }

    if (!lead.socialProfiles || lead.socialProfiles.length === 0) {
      flags.push({
        type: 'no_social_presence',
        severity: 'low',
        description: 'Sin perfiles sociales verificables',
      });
    }

    const financial = lead.financialSignals;
    if (financial?.creditScore === 'poor') {
      flags.push({
        type: 'credit_issues',
        severity: 'high',
        description: 'Historial crediticio deficiente',
      });
    }

    if (financial?.employmentStatus === 'unemployed') {
      flags.push({
        type: 'employment_risk',
        severity: 'high',
        description: 'Sin empleo actual',
      });
    }

    if (lead.propertyInterest.financingStatus === 'unsure') {
      flags.push({
        type: 'financing_uncertainty',
        severity: 'medium',
        description: 'Situación financiera poco clara',
      });
    }

    return flags;
  }

  private detectGreenFlags(lead: LeadInput, scores: Record<keyof ScoringWeights, number>): Array<{ type: string; description: string }> {
    const flags: Array<{ type: string; description: string }> = [];

    if (lead.propertyInterest.financingStatus === 'cash_buyer') {
      flags.push({
        type: 'cash_buyer',
        description: 'Comprador en efectivo - alta probabilidad de cierre',
      });
    }

    if (lead.propertyInterest.timeline === 'immediate' || lead.propertyInterest.timeline === '1-3_months') {
      flags.push({
        type: 'urgent_timeline',
        description: 'Timeline urgente de compra',
      });
    }

    const financial = lead.financialSignals;
    if (financial?.investmentExperience) {
      flags.push({
        type: 'experienced_investor',
        description: 'Experiencia previa en inversiones inmobiliarias',
      });
    }

    if (financial?.propertyOwnership) {
      flags.push({
        type: 'property_owner',
        description: 'Ya es propietario de inmuebles',
      });
    }

    const hasVerifiedSocial = lead.socialProfiles?.some(p => p.verified);
    if (hasVerifiedSocial) {
      flags.push({
        type: 'verified_identity',
        description: 'Identidad verificada en redes sociales',
      });
    }

    const hasLinkedIn = lead.socialProfiles?.some(p => p.platform === 'linkedin' && p.professionalContent);
    if (hasLinkedIn) {
      flags.push({
        type: 'professional_profile',
        description: 'Perfil profesional activo en LinkedIn',
      });
    }

    if (lead.source === 'referral') {
      flags.push({
        type: 'referral_source',
        description: 'Lead referido - mayor confianza',
      });
    }

    const behavior = lead.behaviorSignals;
    if (behavior && (behavior.documentsDownloaded ?? 0) > 2) {
      flags.push({
        type: 'high_interest',
        description: 'Ha descargado múltiples documentos',
      });
    }

    if (behavior?.returnVisitor) {
      flags.push({
        type: 'repeat_visitor',
        description: 'Visitante recurrente - interés sostenido',
      });
    }

    return flags;
  }

  private generateRecommendations(lead: LeadInput, scores: Record<keyof ScoringWeights, number>, category: string): string[] {
    const recommendations: string[] = [];

    if (category === 'hot') {
      recommendations.push('🔥 PRIORIDAD ALTA: Contactar inmediatamente por teléfono');
      recommendations.push('Preparar propuesta personalizada de inversión con análisis ROI');
      recommendations.push('Agendar visita presencial lo antes posible');
    } else if (category === 'warm') {
      recommendations.push('Contactar en las próximas 24-48 horas');
      recommendations.push('Enviar catálogo de propiedades que coincidan con su rango de precio');
      recommendations.push('Seguimiento por email con información de financiamiento');
    } else if (category === 'cold') {
      recommendations.push('Agregar a campaña de nurturing por email');
      recommendations.push('Enviar contenido educativo sobre inversión inmobiliaria');
      recommendations.push('Seguimiento mensual suave');
    } else {
      recommendations.push('NO PRIORIZAR: Bajo potencial de conversión');
      recommendations.push('Considerar descalificar si no mejora engagement');
    }

    if (scores.financialCapacity < 40) {
      recommendations.push('⚠️ Verificar capacidad financiera antes de invertir tiempo');
    }

    if (scores.authenticity < 50) {
      recommendations.push('⚠️ Validar identidad y seriedad del prospecto');
    }

    if (scores.buyingIntent < 40) {
      recommendations.push('Educar sobre beneficios de inversión inmobiliaria');
    }

    const financial = lead.financialSignals;
    if (financial?.investmentExperience) {
      recommendations.push('💡 Destacar métricas de ROI y proyecciones financieras');
    }

    if (lead.propertyInterest.financingStatus === 'needs_financing') {
      recommendations.push('Conectar con asesor financiero o banco aliado');
    }

    return recommendations;
  }

  private calculateROI(lead: LeadInput, scores: Record<keyof ScoringWeights, number>, overallScore: number): {
    conversionProbability: number;
    estimatedValue?: number;
    recommendedActions: string[];
  } {
    const conversionProbability = this.estimateConversionProbability(overallScore, scores);
    
    const avgPropertyPrice = (lead.propertyInterest.priceRange.min + lead.propertyInterest.priceRange.max) / 2;
    const commissionRate = 0.03;
    const estimatedValue = avgPropertyPrice * commissionRate * (conversionProbability / 100);

    const recommendedActions: string[] = [];

    if (conversionProbability > 70) {
      recommendedActions.push('Asignar a tu mejor agente de ventas');
      recommendedActions.push('Preparar análisis de inversión personalizado');
      recommendedActions.push('Priorizar seguimiento diario');
    } else if (conversionProbability > 40) {
      recommendedActions.push('Seguimiento regular cada 2-3 días');
      recommendedActions.push('Nutrir con contenido relevante');
      recommendedActions.push('Invitar a webinar o evento');
    } else {
      recommendedActions.push('Automatizar seguimiento');
      recommendedActions.push('Monitorear cambios en comportamiento');
      recommendedActions.push('Considerar descalificar si no hay mejora en 30 días');
    }

    return {
      conversionProbability,
      estimatedValue,
      recommendedActions,
    };
  }

  private estimateConversionProbability(overallScore: number, scores: Record<keyof ScoringWeights, number>): number {
    let probability = overallScore * 0.7;

    if (scores.financialCapacity > 80) probability += 10;
    if (scores.buyingIntent > 80) probability += 10;
    if (scores.authenticity < 40) probability -= 20;

    return Math.min(Math.max(Math.round(probability), 0), 100);
  }
}

export const leadScorer = new LeadScorer();
