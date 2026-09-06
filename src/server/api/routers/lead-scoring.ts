import { z } from 'zod';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';
import { LeadInputSchema, LeadScoreSchema } from '~/models/lead-scoring';
import { leadScorer } from '~/utils/lead-scorer';

export const leadScoringRouter = createTRPCRouter({
  scoreLead: publicProcedure
    .input(LeadInputSchema)
    .output(LeadScoreSchema)
    .mutation(({ input }) => {
      return leadScorer.scoreLead(input);
    }),

  batchScoreLeads: publicProcedure
    .input(z.object({
      leads: z.array(LeadInputSchema),
    }))
    .output(z.object({
      scores: z.array(LeadScoreSchema),
      summary: z.object({
        totalLeads: z.number(),
        hotLeads: z.number(),
        warmLeads: z.number(),
        coldLeads: z.number(),
        disqualified: z.number(),
        avgScore: z.number(),
        totalEstimatedValue: z.number().optional(),
      }),
    }))
    .mutation(({ input }) => {
      const scores = input.leads.map(lead => leadScorer.scoreLead(lead));
      
      const summary = {
        totalLeads: scores.length,
        hotLeads: scores.filter(s => s.category === 'hot').length,
        warmLeads: scores.filter(s => s.category === 'warm').length,
        coldLeads: scores.filter(s => s.category === 'cold').length,
        disqualified: scores.filter(s => s.category === 'disqualified').length,
        avgScore: scores.reduce((sum, s) => sum + s.overallScore, 0) / scores.length,
        totalEstimatedValue: scores.reduce((sum, s) => sum + (s.estimatedROI.estimatedValue ?? 0), 0),
      };

      return { scores, summary };
    }),

  analyzeSocialProfile: publicProcedure
    .input(z.object({
      profileUrl: z.string().url(),
      platform: z.enum(['linkedin', 'facebook', 'instagram', 'twitter', 'tiktok']),
    }))
    .output(z.object({
      credibilityScore: z.number().min(0).max(100),
      insights: z.object({
        isProfessional: z.boolean(),
        isInvestor: z.boolean(),
        engagementLevel: z.enum(['high', 'medium', 'low', 'none']),
        redFlags: z.array(z.string()),
        greenFlags: z.array(z.string()),
      }),
      recommendations: z.array(z.string()),
    }))
    .mutation(({ input }) => {
      const insights = {
        isProfessional: input.platform === 'linkedin',
        isInvestor: false,
        engagementLevel: 'medium' as const,
        redFlags: [] as string[],
        greenFlags: [] as string[],
      };

      let credibilityScore = 50;

      if (input.platform === 'linkedin') {
        credibilityScore += 20;
        insights.isProfessional = true;
        insights.greenFlags.push('Perfil profesional en LinkedIn');
      }

      if (input.platform === 'instagram' || input.platform === 'tiktok') {
        insights.redFlags.push('Plataforma orientada a entretenimiento, no profesional');
        credibilityScore -= 10;
      }

      const recommendations: string[] = [];
      
      if (credibilityScore > 70) {
        recommendations.push('Alto nivel de credibilidad social');
        recommendations.push('Continuar con proceso de calificación');
      } else if (credibilityScore > 40) {
        recommendations.push('Nivel moderado de credibilidad');
        recommendations.push('Solicitar información adicional');
      } else {
        recommendations.push('Baja credibilidad social');
        recommendations.push('Verificar identidad antes de continuar');
      }

      return {
        credibilityScore,
        insights,
        recommendations,
      };
    }),

  predictConversion: publicProcedure
    .input(z.object({
      leadId: z.string(),
      score: z.number().min(0).max(100),
      category: z.enum(['hot', 'warm', 'cold', 'disqualified']),
      priceRange: z.object({
        min: z.number(),
        max: z.number(),
      }),
    }))
    .output(z.object({
      conversionProbability: z.number().min(0).max(100),
      estimatedTimeToClose: z.string(),
      estimatedRevenue: z.number(),
      confidenceLevel: z.enum(['high', 'medium', 'low']),
      keyFactors: z.array(z.object({
        factor: z.string(),
        impact: z.enum(['positive', 'negative', 'neutral']),
        weight: z.number(),
      })),
    }))
    .query(({ input }) => {
      let conversionProbability = input.score * 0.7;
      
      if (input.category === 'hot') {
        conversionProbability = Math.min(conversionProbability + 20, 95);
      } else if (input.category === 'disqualified') {
        conversionProbability = Math.max(conversionProbability - 30, 5);
      }

      const avgPrice = (input.priceRange.min + input.priceRange.max) / 2;
      const commissionRate = 0.03;
      const estimatedRevenue = avgPrice * commissionRate * (conversionProbability / 100);

      const estimatedTimeToClose = 
        input.category === 'hot' ? '1-2 semanas' :
        input.category === 'warm' ? '1-3 meses' :
        input.category === 'cold' ? '3-6 meses' :
        'Baja probabilidad';

      const confidenceLevel = 
        input.score > 75 ? 'high' as const :
        input.score > 40 ? 'medium' as const :
        'low' as const;

      const keyFactors = [
        {
          factor: 'Capacidad financiera',
          impact: input.score > 70 ? 'positive' as const : 'negative' as const,
          weight: 0.30,
        },
        {
          factor: 'Intención de compra',
          impact: input.category === 'hot' ? 'positive' as const : 'neutral' as const,
          weight: 0.25,
        },
        {
          factor: 'Autenticidad del lead',
          impact: input.score > 60 ? 'positive' as const : 'negative' as const,
          weight: 0.20,
        },
      ];

      return {
        conversionProbability: Math.round(conversionProbability),
        estimatedTimeToClose,
        estimatedRevenue: Math.round(estimatedRevenue),
        confidenceLevel,
        keyFactors,
      };
    }),

  getLeadPriorities: publicProcedure
    .input(z.object({
      scores: z.array(LeadScoreSchema),
      maxLeads: z.number().optional(),
    }))
    .output(z.object({
      prioritizedLeads: z.array(z.object({
        leadId: z.string(),
        score: z.number(),
        category: z.enum(['hot', 'warm', 'cold', 'disqualified']),
        priority: z.number(),
        nextAction: z.string(),
        deadline: z.string(),
      })),
    }))
    .query(({ input }) => {
      const maxLeads = input.maxLeads ?? 20;
      
      const prioritizedLeads = input.scores
        .filter(s => s.category !== 'disqualified')
        .sort((a, b) => b.overallScore - a.overallScore)
        .slice(0, maxLeads)
        .map((score, index) => {
          let priority = 0;
          let nextAction = '';
          let deadline = '';

          if (score.category === 'hot') {
            priority = 1 + index;
            nextAction = 'Contactar por teléfono AHORA';
            deadline = 'Hoy';
          } else if (score.category === 'warm') {
            priority = 100 + index;
            nextAction = 'Enviar propuesta personalizada';
            deadline = 'Próximas 48 horas';
          } else {
            priority = 500 + index;
            nextAction = 'Agregar a campaña de email';
            deadline = 'Esta semana';
          }

          return {
            leadId: score.leadId,
            score: score.overallScore,
            category: score.category,
            priority,
            nextAction,
            deadline,
          };
        });

      return { prioritizedLeads };
    }),
});
