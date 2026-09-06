import type { Property, BuyerPreferences, MatchResult } from '~/models/matching';

interface MatchingWeights {
  location: number;
  price: number;
  specs: number;
  features: number;
  investment: number;
}

const DEFAULT_WEIGHTS: MatchingWeights = {
  location: 0.30,
  price: 0.25,
  specs: 0.20,
  features: 0.15,
  investment: 0.10,
};

export class MatchingEngine {
  private weights: MatchingWeights;

  constructor(customWeights?: Partial<MatchingWeights>) {
    this.weights = { ...DEFAULT_WEIGHTS, ...customWeights };
  }

  public async findMatches(
    buyer: BuyerPreferences,
    properties: Property[],
    options: {
      minCompatibility?: number;
      limit?: number;
      includeInvestment?: boolean;
    } = {}
  ): Promise<MatchResult[]> {
    const {
      minCompatibility = 50,
      limit = 10,
      includeInvestment = buyer.requirements.purpose === 'investment',
    } = options;

    const matches: MatchResult[] = [];

    for (const property of properties) {
      if (property.status !== 'available') continue;

      const compatibility = this.calculateCompatibility(buyer, property, includeInvestment);

      if (compatibility.overall >= minCompatibility) {
        const matchResult = this.createMatchResult(buyer, property, compatibility);
        matches.push(matchResult);
      }
    }

    matches.sort((a, b) => b.compatibility.overall - a.compatibility.overall);

    return matches.slice(0, limit);
  }

  private calculateCompatibility(
    buyer: BuyerPreferences,
    property: Property,
    includeInvestment: boolean
  ): MatchResult['compatibility'] {
    const scores = {
      location: this.scoreLocation(buyer, property),
      price: this.scorePrice(buyer, property),
      specs: this.scoreSpecs(buyer, property),
      features: this.scoreFeatures(buyer, property),
      investment: includeInvestment ? this.scoreInvestment(buyer, property) : undefined,
    };

    const weights = includeInvestment 
      ? this.weights 
      : this.adjustWeightsWithoutInvestment(this.weights);

    const overall = Math.round(
      scores.location * weights.location +
      scores.price * weights.price +
      scores.specs * weights.specs +
      scores.features * weights.features +
      (scores.investment ?? 0) * weights.investment
    );

    return {
      overall: Math.min(Math.max(overall, 0), 100),
      breakdown: scores,
    };
  }

  private scoreLocation(buyer: BuyerPreferences, property: Property): number {
    let score = 0;

    const buyerLocations = buyer.requirements.locations.map(l => l.toLowerCase());
    const propertyNeighborhood = property.location.neighborhood.toLowerCase();
    const propertyCity = property.location.city.toLowerCase();

    const isExactMatch = buyerLocations.some(loc => 
      propertyNeighborhood.includes(loc) || loc.includes(propertyNeighborhood)
    );

    if (isExactMatch) {
      score = 100;
    } else {
      const isCityMatch = buyerLocations.some(loc => 
        propertyCity.includes(loc) || loc.includes(propertyCity)
      );
      
      if (isCityMatch) {
        score = 60;
      } else {
        score = 20;
      }
    }

    if (buyer.preferences?.nearbyPlaces && property.features.nearbyPlaces) {
      const nearbyMatches = buyer.preferences.nearbyPlaces.filter(place =>
        property.features.nearbyPlaces!.some(prop => 
          prop.toLowerCase().includes(place.toLowerCase())
        )
      );
      
      const bonus = Math.min(nearbyMatches.length * 5, 20);
      score = Math.min(score + bonus, 100);
    }

    return score;
  }

  private scorePrice(buyer: BuyerPreferences, property: Property): number {
    const price = property.pricing.price;
    const { min, max, flexible } = buyer.requirements.budget;

    if (price >= min && price <= max) {
      const midPoint = (min + max) / 2;
      const distanceFromMid = Math.abs(price - midPoint);
      const range = max - min;
      
      const score = 100 - (distanceFromMid / range) * 30;
      return Math.round(Math.max(score, 70));
    }

    if (flexible) {
      const overbudgetPercentage = ((price - max) / max) * 100;
      const underbudgetPercentage = ((min - price) / min) * 100;

      if (overbudgetPercentage > 0 && overbudgetPercentage <= 15) {
        return 60 - Math.round(overbudgetPercentage * 2);
      }
      
      if (underbudgetPercentage > 0 && underbudgetPercentage <= 20) {
        return 50 - Math.round(underbudgetPercentage);
      }
    }

    return 0;
  }

  private scoreSpecs(buyer: BuyerPreferences, property: Property): number {
    let score = 50;

    const bedroomMatch = property.specs.bedrooms >= buyer.mustHave.minBedrooms;
    const bathroomMatch = property.specs.bathrooms >= buyer.mustHave.minBathrooms;

    if (!bedroomMatch || !bathroomMatch) {
      return 0;
    }

    if (property.specs.bedrooms === buyer.mustHave.minBedrooms) {
      score += 25;
    } else if (property.specs.bedrooms === buyer.mustHave.minBedrooms + 1) {
      score += 30;
    } else if (property.specs.bedrooms > buyer.mustHave.minBedrooms + 1) {
      score += 15;
    }

    if (property.specs.bathrooms === buyer.mustHave.minBathrooms) {
      score += 15;
    } else if (property.specs.bathrooms > buyer.mustHave.minBathrooms) {
      score += 20;
    }

    if (buyer.mustHave.parking && (property.specs.parkingSpots ?? 0) > 0) {
      score += 10;
    } else if (buyer.mustHave.parking && (property.specs.parkingSpots ?? 0) === 0) {
      score -= 20;
    }

    if (buyer.preferences?.floor) {
      const { min, max } = buyer.preferences.floor;
      const propFloor = property.specs.floor;
      
      if (propFloor !== undefined) {
        const inRange = (!min || propFloor >= min) && (!max || propFloor <= max);
        score += inRange ? 10 : -10;
      }
    }

    if (buyer.preferences?.maxAge && property.specs.yearBuilt) {
      const age = new Date().getFullYear() - property.specs.yearBuilt;
      if (age <= buyer.preferences.maxAge) {
        score += 10;
      } else {
        score -= 15;
      }
    }

    return Math.min(Math.max(score, 0), 100);
  }

  private scoreFeatures(buyer: BuyerPreferences, property: Property): number {
    let score = 50;

    if (buyer.preferences?.amenities && property.features.amenities) {
      const matchedAmenities = buyer.preferences.amenities.filter(amenity =>
        property.features.amenities!.some(propAmenity =>
          propAmenity.toLowerCase().includes(amenity.toLowerCase())
        )
      );

      const matchPercentage = matchedAmenities.length / buyer.preferences.amenities.length;
      score += Math.round(matchPercentage * 40);
    }

    if (buyer.preferences?.views && property.features.view) {
      const hasPreferredView = buyer.preferences.views.some(view =>
        property.features.view!.toLowerCase().includes(view.toLowerCase())
      );
      
      if (hasPreferredView) {
        score += 15;
      }
    }

    if (property.features.condition === 'new' || property.features.condition === 'excellent') {
      score += 10;
    } else if (property.features.condition === 'needs_renovation') {
      score -= 15;
    }

    if (property.media.virtualTour) {
      score += 5;
    }

    return Math.min(Math.max(score, 0), 100);
  }

  private scoreInvestment(buyer: BuyerPreferences, property: Property): number {
    if (!buyer.investmentCriteria || !property.investment) {
      return 50;
    }

    let score = 50;
    const criteria = buyer.investmentCriteria;
    const investment = property.investment;

    if (criteria.minROI && investment.totalROI !== undefined) {
      if (investment.totalROI >= criteria.minROI) {
        const overperformance = investment.totalROI - criteria.minROI;
        score += Math.min(overperformance * 2, 30);
      } else {
        score -= 30;
      }
    }

    if (criteria.minRentalYield && investment.rentalYield !== undefined) {
      if (investment.rentalYield >= criteria.minRentalYield) {
        score += 15;
      } else {
        score -= 20;
      }
    }

    if (criteria.minAppreciation && investment.appreciationRate !== undefined) {
      if (investment.appreciationRate >= criteria.minAppreciation) {
        score += 15;
      } else {
        score -= 15;
      }
    }

    if (buyer.requirements.purpose === 'investment') {
      if (investment.totalROI && investment.totalROI > 10) {
        score += 10;
      }
    }

    return Math.min(Math.max(score, 0), 100);
  }

  private createMatchResult(
    buyer: BuyerPreferences,
    property: Property,
    compatibility: MatchResult['compatibility']
  ): MatchResult {
    const matchReasons = this.generateMatchReasons(buyer, property, compatibility);
    const dealBreakers = this.checkDealBreakers(buyer, property);
    const estimatedFee = this.calculateEstimatedFee(property);
    const recommendedActions = this.generateRecommendedActions(compatibility, dealBreakers);

    return {
      matchId: `match-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      buyerId: buyer.leadId,
      propertyId: property.id,
      compatibility,
      matchReasons,
      dealBreakers: dealBreakers.length > 0 ? dealBreakers : undefined,
      property,
      estimatedFee,
      recommendedActions,
      createdAt: new Date().toISOString(),
    };
  }

  private generateMatchReasons(
    buyer: BuyerPreferences,
    property: Property,
    compatibility: MatchResult['compatibility']
  ): MatchResult['matchReasons'] {
    const reasons: MatchResult['matchReasons'] = [];

    if (compatibility.breakdown.location >= 90) {
      reasons.push({
        category: 'location',
        reason: `Ubicación exacta en ${property.location.neighborhood}`,
        impact: 'positive',
        weight: this.weights.location,
      });
    }

    if (compatibility.breakdown.price >= 80) {
      const price = property.pricing.price;
      const { min, max } = buyer.requirements.budget;
      const midPoint = (min + max) / 2;
      
      if (price <= midPoint) {
        reasons.push({
          category: 'price',
          reason: `Excelente precio: $${price.toLocaleString('es-MX')} dentro de presupuesto`,
          impact: 'positive',
          weight: this.weights.price,
        });
      }
    }

    if (property.specs.bedrooms > buyer.mustHave.minBedrooms) {
      reasons.push({
        category: 'specs',
        reason: `${property.specs.bedrooms} recámaras (pides mínimo ${buyer.mustHave.minBedrooms})`,
        impact: 'positive',
        weight: this.weights.specs,
      });
    }

    if (property.investment?.totalROI && property.investment.totalROI > 10) {
      reasons.push({
        category: 'investment',
        reason: `ROI excelente: ${property.investment.totalROI}% anual`,
        impact: 'positive',
        weight: this.weights.investment,
      });
    }

    if (property.features.amenities && property.features.amenities.length > 0) {
      reasons.push({
        category: 'features',
        reason: `Amenidades premium: ${property.features.amenities.slice(0, 3).join(', ')}`,
        impact: 'positive',
        weight: this.weights.features,
      });
    }

    return reasons;
  }

  private checkDealBreakers(buyer: BuyerPreferences, property: Property): string[] {
    const dealBreakers: string[] = [];

    if (buyer.dealBreakers) {
      for (const dealBreaker of buyer.dealBreakers) {
        const lowerBreaker = dealBreaker.toLowerCase();
        
        if (property.location.neighborhood.toLowerCase().includes(lowerBreaker)) {
          dealBreakers.push(`Ubicación en zona no deseada: ${property.location.neighborhood}`);
        }
        
        if (property.features.condition === 'needs_renovation' && lowerBreaker.includes('remodelación')) {
          dealBreakers.push('Propiedad requiere remodelación');
        }
      }
    }

    if (buyer.mustHave.parking && (property.specs.parkingSpots ?? 0) === 0) {
      dealBreakers.push('No tiene estacionamiento (requerido)');
    }

    return dealBreakers;
  }

  private calculateEstimatedFee(property: Property): MatchResult['estimatedFee'] {
    const brokerCommission = property.pricing.price * (property.broker.commission / 100);
    const laedsPercentage = 30;
    const laedsCommission = brokerCommission * (laedsPercentage / 100);

    return {
      brokerCommission,
      laedsCommission,
      feePercentage: laedsPercentage,
    };
  }

  private generateRecommendedActions(
    compatibility: MatchResult['compatibility'],
    dealBreakers: string[]
  ): string[] {
    const actions: string[] = [];

    if (dealBreakers.length > 0) {
      actions.push('⚠️ Revisar deal breakers antes de enviar');
      actions.push('💬 Discutir con buyer si es flexible en estos puntos');
      return actions;
    }

    if (compatibility.overall >= 85) {
      actions.push('🔥 Compatibilidad excelente - Enviar INMEDIATAMENTE');
      actions.push('📞 Seguir con llamada telefónica');
      actions.push('📅 Agendar visita lo antes posible');
    } else if (compatibility.overall >= 70) {
      actions.push('✅ Buena compatibilidad - Enviar propiedad');
      actions.push('💬 Seguimiento por WhatsApp en 24h');
      actions.push('📊 Preparar análisis comparativo');
    } else if (compatibility.overall >= 50) {
      actions.push('📧 Compatibilidad moderada - Incluir en batch de opciones');
      actions.push('🔍 Mencionar pros específicos');
      actions.push('❓ Preguntar si hay flexibilidad en requisitos');
    }

    return actions;
  }

  private adjustWeightsWithoutInvestment(weights: MatchingWeights): MatchingWeights {
    const investmentWeight = weights.investment;
    const remaining = 1 - investmentWeight;
    
    const factor = 1 / remaining;
    
    return {
      location: weights.location * factor,
      price: weights.price * factor,
      specs: weights.specs * factor,
      features: weights.features * factor,
      investment: 0,
    };
  }

  public async scorePropertyForBuyer(
    buyer: BuyerPreferences,
    property: Property
  ): Promise<MatchResult> {
    const includeInvestment = buyer.requirements.purpose === 'investment';
    const compatibility = this.calculateCompatibility(buyer, property, includeInvestment);
    return this.createMatchResult(buyer, property, compatibility);
  }

  public async getBestMatches(
    buyers: BuyerPreferences[],
    properties: Property[],
    topN: number = 3
  ): Promise<Map<string, MatchResult[]>> {
    const resultsMap = new Map<string, MatchResult[]>();

    for (const buyer of buyers) {
      const matches = await this.findMatches(buyer, properties, {
        minCompatibility: 60,
        limit: topN,
      });

      resultsMap.set(buyer.leadId, matches);
    }

    return resultsMap;
  }
}

export const matchingEngine = new MatchingEngine();
