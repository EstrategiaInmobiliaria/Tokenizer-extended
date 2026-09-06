import type { Referral, MatchResult } from '~/models/matching';
import type { LeadScore } from '~/models/lead-scoring';

interface ReferralMetrics {
  totalReferrals: number;
  activeReferrals: number;
  closedDeals: number;
  conversionRate: number;
  
  fees: {
    estimated: number;
    actual: number;
    pending: number;
    paid: number;
  };
  
  averages: {
    timeToClose: number;
    feePerDeal: number;
    dealSize: number;
  };
  
  pipeline: {
    referred: number;
    propertySent: number;
    visitScheduled: number;
    visitCompleted: number;
    negotiation: number;
    closed: number;
  };
}

interface FeeConfiguration {
  defaultType: 'percentage' | 'flat' | 'hybrid';
  defaultPercentage: number;
  defaultFlatAmount: number;
  
  tiersByBroker?: Map<string, {
    type: 'percentage' | 'flat' | 'hybrid';
    percentage?: number;
    flatAmount?: number;
  }>;
}

export class ReferralTracker {
  private feeConfig: FeeConfiguration;

  constructor(feeConfig?: Partial<FeeConfiguration>) {
    this.feeConfig = {
      defaultType: 'percentage',
      defaultPercentage: 30,
      defaultFlatAmount: 10000,
      ...feeConfig,
    };
  }

  public createReferral(params: {
    buyer: {
      leadId: string;
      name: string;
      email: string;
      phone: string;
      score: number;
    };
    match: MatchResult;
    source: string;
    channel: string;
    campaign?: string;
  }): Referral {
    const { buyer, match, source, channel, campaign } = params;
    const now = new Date().toISOString();

    const brokerConfig = this.feeConfig.tiersByBroker?.get(match.property.broker.id);
    const feeStructure = brokerConfig || {
      type: this.feeConfig.defaultType,
      percentage: this.feeConfig.defaultPercentage,
      flatAmount: this.feeConfig.defaultFlatAmount,
    };

    const brokerCommissionAmount = 
      match.property.pricing.price * (match.property.broker.commission / 100);

    let estimatedFee: number;
    if (feeStructure.type === 'percentage') {
      estimatedFee = brokerCommissionAmount * ((feeStructure.percentage ?? 30) / 100);
    } else if (feeStructure.type === 'flat') {
      estimatedFee = feeStructure.flatAmount ?? 10000;
    } else {
      const percentageFee = brokerCommissionAmount * ((feeStructure.percentage ?? 20) / 100);
      const flatFee = feeStructure.flatAmount ?? 5000;
      estimatedFee = percentageFee + flatFee;
    }

    return {
      id: `ref-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      
      buyer: {
        leadId: buyer.leadId,
        name: buyer.name,
        email: buyer.email,
        phone: buyer.phone,
        score: buyer.score,
      },
      
      property: {
        propertyId: match.property.id,
        title: match.property.basic.title,
        price: match.property.pricing.price,
        address: match.property.location.address,
      },
      
      broker: {
        brokerId: match.property.broker.id,
        name: match.property.broker.name,
        agency: match.property.broker.agency,
        commission: match.property.broker.commission,
      },
      
      referredBy: 'laeds',
      
      matching: {
        matchId: match.matchId,
        compatibility: match.compatibility.overall,
        matchedAt: now,
      },
      
      timeline: {
        referredAt: now,
        propertySentAt: undefined,
        viewedAt: undefined,
        visitScheduledAt: undefined,
        visitCompletedAt: undefined,
        offerMadeAt: undefined,
        contractSignedAt: undefined,
        dealClosedAt: undefined,
      },
      
      status: 'referred',
      
      financial: {
        propertyPrice: match.property.pricing.price,
        finalPrice: undefined,
        brokerCommissionAmount,
        
        feeStructure: {
          type: feeStructure.type,
          percentage: feeStructure.percentage,
          flatAmount: feeStructure.flatAmount,
        },
        
        estimatedFee,
        actualFee: undefined,
        
        feePaid: false,
        paidAt: undefined,
        invoiceId: undefined,
      },
      
      notes: [],
      
      metadata: {
        source,
        channel,
        campaign,
        createdAt: now,
        updatedAt: now,
      },
    };
  }

  public updateReferralStatus(
    referral: Referral,
    newStatus: Referral['status'],
    additionalData?: {
      finalPrice?: number;
      note?: string;
    }
  ): Referral {
    const now = new Date().toISOString();
    
    const updated: Referral = {
      ...referral,
      status: newStatus,
      metadata: {
        ...referral.metadata,
        updatedAt: now,
      },
    };

    switch (newStatus) {
      case 'property_sent':
        updated.timeline.propertySentAt = now;
        break;
      case 'viewed':
        updated.timeline.viewedAt = now;
        break;
      case 'visit_scheduled':
        updated.timeline.visitScheduledAt = now;
        break;
      case 'visit_completed':
        updated.timeline.visitCompletedAt = now;
        break;
      case 'offer_made':
        updated.timeline.offerMadeAt = now;
        break;
      case 'negotiation':
        break;
      case 'contract_signed':
        updated.timeline.contractSignedAt = now;
        break;
      case 'closed':
        updated.timeline.dealClosedAt = now;
        
        if (additionalData?.finalPrice) {
          updated.financial.finalPrice = additionalData.finalPrice;
          updated.financial.actualFee = this.calculateActualFee(
            updated,
            additionalData.finalPrice
          );
        }
        break;
    }

    if (additionalData?.note) {
      updated.notes = [
        ...(updated.notes ?? []),
        {
          text: additionalData.note,
          createdBy: 'system',
          createdAt: now,
        },
      ];
    }

    return updated;
  }

  private calculateActualFee(referral: Referral, finalPrice: number): number {
    const brokerCommission = finalPrice * (referral.broker.commission / 100);
    
    const { type, percentage, flatAmount } = referral.financial.feeStructure;

    if (type === 'percentage') {
      return brokerCommission * ((percentage ?? 30) / 100);
    } else if (type === 'flat') {
      return flatAmount ?? 10000;
    } else {
      const percentageFee = brokerCommission * ((percentage ?? 20) / 100);
      const flat = flatAmount ?? 5000;
      return percentageFee + flat;
    }
  }

  public markFeePaid(
    referral: Referral,
    invoiceId: string
  ): Referral {
    return {
      ...referral,
      financial: {
        ...referral.financial,
        feePaid: true,
        paidAt: new Date().toISOString(),
        invoiceId,
      },
    };
  }

  public calculateMetrics(referrals: Referral[]): ReferralMetrics {
    const activeReferrals = referrals.filter(r => 
      !['closed', 'lost', 'expired'].includes(r.status)
    );

    const closedDeals = referrals.filter(r => r.status === 'closed');

    const conversionRate = referrals.length > 0
      ? (closedDeals.length / referrals.length) * 100
      : 0;

    const estimatedFees = referrals.reduce((sum, r) => 
      sum + r.financial.estimatedFee, 0
    );

    const actualFees = closedDeals.reduce((sum, r) => 
      sum + (r.financial.actualFee ?? 0), 0
    );

    const paidFees = referrals
      .filter(r => r.financial.feePaid)
      .reduce((sum, r) => sum + (r.financial.actualFee ?? r.financial.estimatedFee), 0);

    const pendingFees = actualFees - paidFees;

    const avgTimeToClose = closedDeals.length > 0
      ? this.calculateAverageTimeToClose(closedDeals)
      : 0;

    const avgFeePerDeal = closedDeals.length > 0
      ? actualFees / closedDeals.length
      : 0;

    const avgDealSize = closedDeals.length > 0
      ? closedDeals.reduce((sum, r) => sum + (r.financial.finalPrice ?? r.property.price), 0) / closedDeals.length
      : 0;

    const pipeline = {
      referred: referrals.filter(r => r.status === 'referred').length,
      propertySent: referrals.filter(r => r.status === 'property_sent').length,
      visitScheduled: referrals.filter(r => r.status === 'visit_scheduled').length,
      visitCompleted: referrals.filter(r => r.status === 'visit_completed').length,
      negotiation: referrals.filter(r => ['offer_made', 'negotiation'].includes(r.status)).length,
      closed: closedDeals.length,
    };

    return {
      totalReferrals: referrals.length,
      activeReferrals: activeReferrals.length,
      closedDeals: closedDeals.length,
      conversionRate: Math.round(conversionRate * 10) / 10,
      
      fees: {
        estimated: Math.round(estimatedFees),
        actual: Math.round(actualFees),
        pending: Math.round(pendingFees),
        paid: Math.round(paidFees),
      },
      
      averages: {
        timeToClose: Math.round(avgTimeToClose),
        feePerDeal: Math.round(avgFeePerDeal),
        dealSize: Math.round(avgDealSize),
      },
      
      pipeline,
    };
  }

  private calculateAverageTimeToClose(closedDeals: Referral[]): number {
    const times = closedDeals
      .filter(r => r.timeline.dealClosedAt && r.timeline.referredAt)
      .map(r => {
        const start = new Date(r.timeline.referredAt).getTime();
        const end = new Date(r.timeline.dealClosedAt!).getTime();
        return (end - start) / (1000 * 60 * 60 * 24);
      });

    return times.length > 0
      ? times.reduce((sum, t) => sum + t, 0) / times.length
      : 0;
  }

  public getTopPerformingBrokers(
    referrals: Referral[],
    limit: number = 10
  ): Array<{
    brokerId: string;
    brokerName: string;
    totalReferrals: number;
    closedDeals: number;
    conversionRate: number;
    totalFeesGenerated: number;
    avgDealSize: number;
  }> {
    const brokerMap = new Map<string, {
      brokerId: string;
      brokerName: string;
      referrals: Referral[];
    }>();

    for (const referral of referrals) {
      if (!brokerMap.has(referral.broker.brokerId)) {
        brokerMap.set(referral.broker.brokerId, {
          brokerId: referral.broker.brokerId,
          brokerName: referral.broker.name,
          referrals: [],
        });
      }
      brokerMap.get(referral.broker.brokerId)!.referrals.push(referral);
    }

    const brokerStats = Array.from(brokerMap.values()).map(broker => {
      const closedDeals = broker.referrals.filter(r => r.status === 'closed');
      const conversionRate = broker.referrals.length > 0
        ? (closedDeals.length / broker.referrals.length) * 100
        : 0;

      const totalFeesGenerated = closedDeals.reduce((sum, r) =>
        sum + (r.financial.actualFee ?? r.financial.estimatedFee), 0
      );

      const avgDealSize = closedDeals.length > 0
        ? closedDeals.reduce((sum, r) => sum + (r.financial.finalPrice ?? r.property.price), 0) / closedDeals.length
        : 0;

      return {
        brokerId: broker.brokerId,
        brokerName: broker.brokerName,
        totalReferrals: broker.referrals.length,
        closedDeals: closedDeals.length,
        conversionRate: Math.round(conversionRate * 10) / 10,
        totalFeesGenerated: Math.round(totalFeesGenerated),
        avgDealSize: Math.round(avgDealSize),
      };
    });

    return brokerStats
      .sort((a, b) => b.totalFeesGenerated - a.totalFeesGenerated)
      .slice(0, limit);
  }

  public detectLeakedReferrals(
    referrals: Referral[],
    thresholdDays: number = 60
  ): Referral[] {
    const now = new Date().getTime();
    const threshold = thresholdDays * 24 * 60 * 60 * 1000;

    return referrals.filter(referral => {
      if (referral.status === 'closed' || referral.status === 'lost') {
        return false;
      }

      const lastActivity = this.getLastActivityDate(referral);
      const timeSinceActivity = now - lastActivity.getTime();

      return timeSinceActivity > threshold;
    });
  }

  private getLastActivityDate(referral: Referral): Date {
    const dates = [
      referral.timeline.viewedAt,
      referral.timeline.visitScheduledAt,
      referral.timeline.visitCompletedAt,
      referral.timeline.offerMadeAt,
    ].filter(Boolean);

    if (dates.length === 0) {
      return new Date(referral.timeline.referredAt);
    }

    const latestDate = dates.reduce((latest, current) =>
      new Date(current!) > new Date(latest!) ? current : latest
    );

    return new Date(latestDate!);
  }

  public generateInvoiceData(referral: Referral): {
    invoiceNumber: string;
    date: string;
    dueDate: string;
    
    billTo: {
      name: string;
      company: string;
      email: string;
    };
    
    items: Array<{
      description: string;
      amount: number;
    }>;
    
    subtotal: number;
    tax: number;
    total: number;
    
    notes: string;
  } {
    if (referral.status !== 'closed') {
      throw new Error('Cannot generate invoice for referral that is not closed');
    }

    const invoiceNumber = `LAEDS-${new Date().getFullYear()}-${referral.id.slice(-8).toUpperCase()}`;
    const date = new Date().toISOString();
    const dueDate = new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString();

    const amount = referral.financial.actualFee ?? referral.financial.estimatedFee;
    const tax = amount * 0.16;
    const total = amount + tax;

    return {
      invoiceNumber,
      date,
      dueDate,
      
      billTo: {
        name: referral.broker.name,
        company: referral.broker.agency ?? 'N/A',
        email: 'broker@example.com',
      },
      
      items: [
        {
          description: `Reference Fee - ${referral.property.title} (${referral.property.address})`,
          amount,
        },
      ],
      
      subtotal: amount,
      tax,
      total,
      
      notes: `Pago por referencia exitosa. Buyer: ${referral.buyer.name}. Propiedad: ${referral.property.title}. Compatibility score: ${referral.matching.compatibility}%`,
    };
  }
}

export const referralTracker = new ReferralTracker();
