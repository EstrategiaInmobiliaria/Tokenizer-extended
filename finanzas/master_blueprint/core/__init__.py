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
]
