import { z } from 'zod';

export const PropertySchema = z.object({
  id: z.string(),
  externalId: z.string().optional(),
  source: z.enum(['easybroker', 'manual', 'portal', 'network']),
  
  basic: z.object({
    title: z.string(),
    description: z.string(),
    propertyType: z.enum(['apartment', 'house', 'condo', 'land', 'commercial', 'other']),
    operationType: z.enum(['sale', 'rent', 'both']),
  }),
  
  location: z.object({
    address: z.string(),
    neighborhood: z.string(),
    city: z.string(),
    state: z.string(),
    zipCode: z.string().optional(),
    coordinates: z.object({
      lat: z.number(),
      lng: z.number(),
    }).optional(),
  }),
  
  specs: z.object({
    bedrooms: z.number(),
    bathrooms: z.number(),
    halfBathrooms: z.number().optional(),
    parkingSpots: z.number().optional(),
    constructionSize: z.number(),
    landSize: z.number().optional(),
    floor: z.number().optional(),
    totalFloors: z.number().optional(),
    yearBuilt: z.number().optional(),
  }),
  
  pricing: z.object({
    price: z.number(),
    currency: z.enum(['MXN', 'USD']).default('MXN'),
    maintenance: z.number().optional(),
    pricePerM2: z.number().optional(),
  }),
  
  features: z.object({
    amenities: z.array(z.string()).optional(),
    nearbyPlaces: z.array(z.string()).optional(),
    view: z.string().optional(),
    orientation: z.string().optional(),
    condition: z.enum(['new', 'excellent', 'good', 'needs_renovation']).optional(),
  }),
  
  media: z.object({
    images: z.array(z.string()),
    videos: z.array(z.string()).optional(),
    virtualTour: z.string().optional(),
    floorPlan: z.string().optional(),
  }),
  
  investment: z.object({
    rentalYield: z.number().optional(),
    appreciationRate: z.number().optional(),
    totalROI: z.number().optional(),
    monthlyRent: z.number().optional(),
  }).optional(),
  
  broker: z.object({
    id: z.string(),
    name: z.string(),
    email: z.string().optional(),
    phone: z.string().optional(),
    commission: z.number(),
    agency: z.string().optional(),
  }),
  
  status: z.enum(['available', 'reserved', 'sold', 'inactive']).default('available'),
  
  metadata: z.object({
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
    publishedAt: z.string().datetime().optional(),
    views: z.number().optional(),
    favorites: z.number().optional(),
  }),
});

export const BuyerPreferencesSchema = z.object({
  leadId: z.string(),
  
  requirements: z.object({
    budget: z.object({
      min: z.number(),
      max: z.number(),
      flexible: z.boolean().optional(),
    }),
    locations: z.array(z.string()),
    propertyTypes: z.array(z.enum(['apartment', 'house', 'condo', 'land', 'commercial'])),
    purpose: z.enum(['investment', 'primary_residence', 'vacation_home', 'rental']),
    timeline: z.enum(['immediate', '1-3_months', '3-6_months', '6-12_months', 'flexible']),
  }),
  
  mustHave: z.object({
    minBedrooms: z.number(),
    minBathrooms: z.number(),
    parking: z.boolean().optional(),
    petFriendly: z.boolean().optional(),
    furnished: z.boolean().optional(),
  }),
  
  preferences: z.object({
    amenities: z.array(z.string()).optional(),
    nearbyPlaces: z.array(z.string()).optional(),
    views: z.array(z.string()).optional(),
    floor: z.object({
      min: z.number().optional(),
      max: z.number().optional(),
    }).optional(),
    maxAge: z.number().optional(),
  }).optional(),
  
  dealBreakers: z.array(z.string()).optional(),
  
  investmentCriteria: z.object({
    minROI: z.number().optional(),
    minRentalYield: z.number().optional(),
    minAppreciation: z.number().optional(),
    investmentHorizon: z.number().optional(),
  }).optional(),
});

export const MatchResultSchema = z.object({
  matchId: z.string(),
  buyerId: z.string(),
  propertyId: z.string(),
  
  compatibility: z.object({
    overall: z.number().min(0).max(100),
    breakdown: z.object({
      location: z.number().min(0).max(100),
      price: z.number().min(0).max(100),
      specs: z.number().min(0).max(100),
      features: z.number().min(0).max(100),
      investment: z.number().min(0).max(100).optional(),
    }),
  }),
  
  matchReasons: z.array(z.object({
    category: z.string(),
    reason: z.string(),
    impact: z.enum(['positive', 'neutral', 'negative']),
    weight: z.number(),
  })),
  
  dealBreakers: z.array(z.string()).optional(),
  
  property: PropertySchema,
  
  estimatedFee: z.object({
    brokerCommission: z.number(),
    laedsCommission: z.number(),
    feePercentage: z.number(),
  }),
  
  recommendedActions: z.array(z.string()),
  
  createdAt: z.string().datetime(),
});

export const ReferralSchema = z.object({
  id: z.string(),
  
  buyer: z.object({
    leadId: z.string(),
    name: z.string(),
    email: z.string(),
    phone: z.string(),
    score: z.number(),
  }),
  
  property: z.object({
    propertyId: z.string(),
    title: z.string(),
    price: z.number(),
    address: z.string(),
  }),
  
  broker: z.object({
    brokerId: z.string(),
    name: z.string(),
    agency: z.string().optional(),
    commission: z.number(),
  }),
  
  referredBy: z.string().default('laeds'),
  
  matching: z.object({
    matchId: z.string(),
    compatibility: z.number(),
    matchedAt: z.string().datetime(),
  }),
  
  timeline: z.object({
    referredAt: z.string().datetime(),
    propertySentAt: z.string().datetime().optional(),
    viewedAt: z.string().datetime().optional(),
    visitScheduledAt: z.string().datetime().optional(),
    visitCompletedAt: z.string().datetime().optional(),
    offerMadeAt: z.string().datetime().optional(),
    contractSignedAt: z.string().datetime().optional(),
    dealClosedAt: z.string().datetime().optional(),
  }),
  
  status: z.enum([
    'referred',
    'property_sent',
    'viewed',
    'visit_scheduled',
    'visit_completed',
    'offer_made',
    'negotiation',
    'contract_signed',
    'closed',
    'lost',
    'expired'
  ]),
  
  financial: z.object({
    propertyPrice: z.number(),
    finalPrice: z.number().optional(),
    brokerCommissionAmount: z.number(),
    
    feeStructure: z.object({
      type: z.enum(['percentage', 'flat', 'hybrid']),
      percentage: z.number().optional(),
      flatAmount: z.number().optional(),
    }),
    
    estimatedFee: z.number(),
    actualFee: z.number().optional(),
    
    feePaid: z.boolean().default(false),
    paidAt: z.string().datetime().optional(),
    invoiceId: z.string().optional(),
  }),
  
  notes: z.array(z.object({
    text: z.string(),
    createdBy: z.string(),
    createdAt: z.string().datetime(),
  })).optional(),
  
  metadata: z.object({
    source: z.string(),
    channel: z.string(),
    campaign: z.string().optional(),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
  }),
});

export type Property = z.infer<typeof PropertySchema>;
export type BuyerPreferences = z.infer<typeof BuyerPreferencesSchema>;
export type MatchResult = z.infer<typeof MatchResultSchema>;
export type Referral = z.infer<typeof ReferralSchema>;
