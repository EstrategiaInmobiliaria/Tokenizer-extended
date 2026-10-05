"""
Master Blueprint - Core Financial & Optimization Modules
"""

from .wacc_engine import WACCEngine, MarketParameters, CapitalStructure, quick_wacc_calculation
from .real_estate_dcf import (
    RealEstateDCF,
    ProjectAssumptions,
    RealEstateCashFlows,
    TerminalValueAssumptions,
    scenario_analysis
)
from .ops_optimizer import (
    MathematicalOptimizerCore,
    OperationsOptimizer,
    Product,
    ResourceConstraint,
    DemandConstraint
)
from .opportunity_score import (
    FORMULA_VERSION,
    InvestmentThesis,
    Listing,
    OpportunityEngine,
    ScoreAssumptions,
    load_book,
    score_inventory,
)
from .easybroker_adapter import from_easybroker_property

__version__ = "1.0.0"
__author__ = "Master Blueprint Project"

__all__ = [
    # WACC Engine
    "WACCEngine",
    "MarketParameters",
    "CapitalStructure",
    "quick_wacc_calculation",
    
    # Real Estate DCF
    "RealEstateDCF",
    "ProjectAssumptions",
    "RealEstateCashFlows",
    "TerminalValueAssumptions",
    "scenario_analysis",
    
    # Operations Optimizer
    "MathematicalOptimizerCore",  # Nuevo: Solución analítica determinista
    "OperationsOptimizer",
    "Product",
    "ResourceConstraint",
    "DemandConstraint",

    # Læds Opportunity Score
    "FORMULA_VERSION",
    "InvestmentThesis",
    "Listing",
    "OpportunityEngine",
    "ScoreAssumptions",
    "load_book",
    "score_inventory",
    "from_easybroker_property",
]
