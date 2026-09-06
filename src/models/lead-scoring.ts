import { z } from 'zod';

export const SocialMediaProfileSchema = z.object({
  platform: z.enum(['linkedin', 'facebook', 'instagram', 'twitter', 'tiktok']),
  profileUrl: z.string().url().optional(),
  followers: z.number().optional(),
  engagement: z.number().optional(),
  verified: z.boolean().optional(),
  businessProfile: z.boolean().optional(),
  professionalContent: z.boolean().optional(),
  activityLevel: z.enum(['high', 'medium', 'low', 'none']).optional(),
});

export const FinancialSignalsSchema = z.object({
  employmentStatus: z.enum(['employed', 'self_employed', 'business_owner', 'unemployed', 'retired', 'unknown']).optional(),
  industryType: z.string().optional(),
  companySize: z.enum(['startup', 'small', 'medium', 'large', 'enterprise', 'unknown']).optional(),
  estimatedIncome: z.enum(['low', 'medium', 'high', 'very_high', 'unknown']).optional(),
  investmentExperience: z.boolean().optional(),
  propertyOwnership: z.boolean().optional(),
  creditScore: z.enum(['excellent', 'good', 'fair', 'poor', 'unknown']).optional(),
});

export const BehaviorSignalsSchema = z.object({
  pageViews: z.number().optional(),
  timeOnSite: z.number().optional(),
  documentsDownloaded: z.number().optional(),
  videoWatchTime: z.number().optional(),
  questionsAsked: z.number().optional(),
  responseTime: z.number().optional(),
  interactionQuality: z.enum(['high', 'medium', 'low']).optional(),
  returnVisitor: z.boolean().optional(),
  deviceType: z.enum(['mobile', 'desktop', 'tablet', 'unknown']).optional(),
  timeOfDay: z.string().optional(),
});

export const LeadInputSchema = z.object({
  id: z.string().optional(),
  name: z.string(),
  email: z.string().email(),
  phone: z.string().optional(),
  age: z.number().optional(),
  location: z.string().optional(),
  source: z.enum(['organic', 'paid_ads', 'referral', 'social_media', 'email', 'other']),
  
  socialProfiles: z.array(SocialMediaProfileSchema).optional(),
  financialSignals: FinancialSignalsSchema.optional(),
  behaviorSignals: BehaviorSignalsSchema.optional(),
  
  propertyInterest: z.object({
    priceRange: z.object({
      min: z.number(),
      max: z.number(),
    }),
    propertyType: z.enum(['apartment', 'house', 'condo', 'land', 'commercial']),
    purpose: z.enum(['investment', 'primary_residence', 'vacation_home', 'unsure']),
    timeline: z.enum(['immediate', '1-3_months', '3-6_months', '6-12_months', 'over_1_year', 'just_browsing']),
    financingStatus: z.enum(['cash_buyer', 'pre_approved', 'needs_financing', 'unsure']),
  }),
  
  notes: z.string().optional(),
  timestamp: z.string().datetime().optional(),
});

export const LeadScoreSchema = z.object({
  leadId: z.string(),
  overallScore: z.number().min(0).max(100),
  category: z.enum(['hot', 'warm', 'cold', 'disqualified']),
  
  scores: z.object({
    financialCapacity: z.number().min(0).max(100),
    buyingIntent: z.number().min(0).max(100),
    authenticity: z.number().min(0).max(100),
    engagement: z.number().min(0).max(100),
    socialCredibility: z.number().min(0).max(100),
    timelineUrgency: z.number().min(0).max(100),
  }),
  
  redFlags: z.array(z.object({
    type: z.string(),
    severity: z.enum(['high', 'medium', 'low']),
    description: z.string(),
  })).optional(),
  
  greenFlags: z.array(z.object({
    type: z.string(),
    description: z.string(),
  })).optional(),
  
  recommendations: z.array(z.string()),
  estimatedROI: z.object({
    conversionProbability: z.number().min(0).max(100),
    estimatedValue: z.number().optional(),
    recommendedActions: z.array(z.string()),
  }),
  
  timestamp: z.string().datetime(),
});

export type SocialMediaProfile = z.infer<typeof SocialMediaProfileSchema>;
export type FinancialSignals = z.infer<typeof FinancialSignalsSchema>;
export type BehaviorSignals = z.infer<typeof BehaviorSignalsSchema>;
export type LeadInput = z.infer<typeof LeadInputSchema>;
export type LeadScore = z.infer<typeof LeadScoreSchema>;
