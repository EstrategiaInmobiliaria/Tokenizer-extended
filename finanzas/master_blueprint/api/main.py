"""
FastAPI Main Application - Master Blueprint API
API REST para evaluación de proyectos inmobiliarios y optimización operativa

Esta API expone los módulos de cálculo financiero como servicios web seguros
y escalables para evaluación en tiempo real de proyectos de inversión.

Endpoints Principales:
---------------------
- POST /api/v1/wacc/calculate - Cálculo de WACC
- POST /api/v1/dcf/analyze - Análisis DCF de proyecto inmobiliario
- POST /api/v1/optimize/mix - Optimización de mix de productos
- GET /health - Health check del servicio
- GET /docs - Documentación interactiva (Swagger UI)
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
import uvicorn
from datetime import datetime

# Importar módulos core
import sys
sys.path.append('..')
from core import (
    WACCEngine, MarketParameters, CapitalStructure,
    RealEstateDCF, ProjectAssumptions, RealEstateCashFlows, TerminalValueAssumptions,
    scenario_analysis,
    OperationsOptimizer, Product, ResourceConstraint, DemandConstraint
)


# =============================================================================
# Configuración de la Aplicación
# =============================================================================

app = FastAPI(
    title="Master Blueprint API",
    description="API para evaluación financiera de proyectos inmobiliarios y optimización operativa",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Modelos Pydantic para Request/Response
# =============================================================================

# --- WACC Models ---

class WACCRequest(BaseModel):
    """Request para cálculo de WACC"""
    risk_free_rate: float = Field(..., ge=0, le=1, description="Tasa libre de riesgo (0-1)")
    market_return: float = Field(..., ge=0, le=1, description="Retorno esperado del mercado")
    corporate_tax_rate: float = Field(..., ge=0, le=1, description="Tasa impositiva corporativa")
    equity_value: float = Field(..., gt=0, description="Valor del patrimonio")
    debt_value: float = Field(..., ge=0, description="Valor de la deuda")
    beta: float = Field(..., ge=0, description="Beta del activo")
    debt_rate: float = Field(..., ge=0, le=1, description="Costo de la deuda")
    
    class Config:
        schema_extra = {
            "example": {
                "risk_free_rate": 0.05,
                "market_return": 0.12,
                "corporate_tax_rate": 0.27,
                "equity_value": 800000000,
                "debt_value": 400000000,
                "beta": 1.15,
                "debt_rate": 0.08
            }
        }


class WACCResponse(BaseModel):
    """Response del cálculo de WACC"""
    wacc: float
    wacc_percentage: float
    cost_of_equity: float
    cost_of_debt_after_tax: float
    equity_weight: float
    debt_weight: float
    debt_to_equity_ratio: float
    detailed_breakdown: Dict


# --- DCF Models ---

class DCFRequest(BaseModel):
    """Request para análisis DCF"""
    project_name: str
    initial_investment: float = Field(..., gt=0)
    discount_rate: float = Field(..., ge=0, le=1)
    projection_years: int = Field(5, ge=1, le=20)
    rental_income: List[float]
    sales_revenue: List[float]
    operating_costs: List[float]
    capex: List[float]
    taxes: List[float]
    terminal_value_method: str = Field("perpetuity", regex="^(perpetuity|exit_multiple)$")
    perpetual_growth_rate: float = Field(0.02, ge=0, le=0.1)
    exit_cap_rate: float = Field(0.08, ge=0, le=1)
    include_scenarios: bool = Field(False, description="Incluir análisis de escenarios")
    
    @validator('rental_income', 'sales_revenue', 'operating_costs', 'capex', 'taxes')
    def check_list_length(cls, v, values):
        if 'projection_years' in values and len(v) != values['projection_years']:
            raise ValueError(f"La lista debe tener {values['projection_years']} elementos")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "project_name": "Edificio Las Condes",
                "initial_investment": 1200000000,
                "discount_rate": 0.096,
                "projection_years": 5,
                "rental_income": [150000000, 165000000, 180000000, 195000000, 210000000],
                "sales_revenue": [0, 0, 200000000, 300000000, 400000000],
                "operating_costs": [50000000, 52000000, 54000000, 56000000, 58000000],
                "capex": [20000000, 15000000, 15000000, 10000000, 10000000],
                "taxes": [25000000, 28000000, 35000000, 45000000, 55000000],
                "terminal_value_method": "perpetuity",
                "perpetual_growth_rate": 0.02,
                "include_scenarios": True
            }
        }


class DCFResponse(BaseModel):
    """Response del análisis DCF"""
    project_name: str
    npv: float
    irr: float
    profitability_index: float
    payback_period: float
    accept_project: bool
    decision_rationale: str
    year_by_year: List[Dict]
    scenarios: Optional[Dict] = None


# --- Optimization Models ---

class ProductModel(BaseModel):
    """Modelo de producto para optimización"""
    name: str
    unit_price: float = Field(..., gt=0)
    variable_cost: float = Field(..., ge=0)
    fixed_cost_allocation: float = Field(0, ge=0)


class ConstraintModel(BaseModel):
    """Modelo de restricción de recurso"""
    name: str
    total_available: float = Field(..., gt=0)
    consumption_rates: List[float]


class OptimizationRequest(BaseModel):
    """Request para optimización de mix"""
    products: List[ProductModel]
    resource_constraints: List[ConstraintModel]
    fixed_costs: float = Field(0, ge=0)
    min_demand: Optional[List[float]] = None
    max_demand: Optional[List[float]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "products": [
                    {
                        "name": "Apartamento Tipo A",
                        "unit_price": 4500000,
                        "variable_cost": 2800000,
                        "fixed_cost_allocation": 0
                    },
                    {
                        "name": "Apartamento Tipo B",
                        "unit_price": 6000000,
                        "variable_cost": 3500000,
                        "fixed_cost_allocation": 0
                    }
                ],
                "resource_constraints": [
                    {
                        "name": "Área Total (m²)",
                        "total_available": 15000,
                        "consumption_rates": [45, 65]
                    },
                    {
                        "name": "Presupuesto ($)",
                        "total_available": 300000000,
                        "consumption_rates": [2800000, 3500000]
                    }
                ],
                "fixed_costs": 50000000,
                "min_demand": [20, 15],
                "max_demand": [200, 150]
            }
        }


class OptimizationResponse(BaseModel):
    """Response de optimización"""
    success: bool
    method: str
    optimal_quantities: Optional[List[float]]
    optimal_profit: Optional[float]
    products: List[str]
    detailed_breakdown: Optional[Dict]
    message: Optional[str] = None


# =============================================================================
# Endpoints de la API
# =============================================================================

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "service": "Master Blueprint API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "wacc": "/api/v1/wacc/calculate",
            "dcf": "/api/v1/dcf/analyze",
            "optimization": "/api/v1/optimize/mix"
        }
    }


@app.get("/health")
async def health_check():
    """Health check del servicio"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Master Blueprint API",
        "version": "1.0.0"
    }


@app.post(
    "/api/v1/wacc/calculate",
    response_model=WACCResponse,
    status_code=status.HTTP_200_OK,
    tags=["WACC - Finanzas Corporativas"]
)
async def calculate_wacc(request: WACCRequest):
    """
    Calcula el WACC (Weighted Average Cost of Capital)
    
    El WACC es la tasa de descuento mínima que un proyecto debe generar
    para crear valor para los accionistas.
    
    **Fórmula**: WACC = (E/V) * Re + (D/V) * Rd * (1 - Tc)
    """
    try:
        # Crear objetos del core
        market = MarketParameters(
            risk_free_rate=request.risk_free_rate,
            market_return=request.market_return,
            corporate_tax_rate=request.corporate_tax_rate
        )
        
        capital = CapitalStructure(
            equity_value=request.equity_value,
            debt_value=request.debt_value,
            beta=request.beta,
            debt_rate=request.debt_rate
        )
        
        # Calcular WACC
        engine = WACCEngine(market, capital)
        breakdown = engine.get_detailed_breakdown()
        
        return WACCResponse(
            wacc=breakdown["wacc"],
            wacc_percentage=breakdown["wacc_percentage"],
            cost_of_equity=breakdown["cost_of_equity"],
            cost_of_debt_after_tax=breakdown["cost_of_debt_after_tax"],
            equity_weight=breakdown["equity_weight"],
            debt_weight=breakdown["debt_weight"],
            debt_to_equity_ratio=breakdown["debt_to_equity_ratio"],
            detailed_breakdown=breakdown
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en cálculo de WACC: {str(e)}"
        )


@app.post(
    "/api/v1/dcf/analyze",
    response_model=DCFResponse,
    status_code=status.HTTP_200_OK,
    tags=["DCF - Análisis de Inversión Inmobiliaria"]
)
async def analyze_dcf(request: DCFRequest):
    """
    Análisis de Flujo de Caja Descontado (DCF) para proyectos inmobiliarios
    
    Calcula:
    - VPN (Valor Presente Neto)
    - TIR (Tasa Interna de Retorno)
    - Índice de Rentabilidad
    - Período de Recuperación (Payback)
    - Análisis año por año
    - Opcionalmente: Análisis de escenarios (optimista, base, pesimista)
    """
    try:
        # Crear objetos del core
        assumptions = ProjectAssumptions(
            project_name=request.project_name,
            initial_investment=request.initial_investment,
            discount_rate=request.discount_rate,
            projection_years=request.projection_years
        )
        
        cash_flows = RealEstateCashFlows(
            rental_income=request.rental_income,
            sales_revenue=request.sales_revenue,
            operating_costs=request.operating_costs,
            capex=request.capex,
            taxes=request.taxes
        )
        
        terminal_assumptions = TerminalValueAssumptions(
            method=request.terminal_value_method,
            perpetual_growth_rate=request.perpetual_growth_rate,
            exit_cap_rate=request.exit_cap_rate
        )
        
        # Análisis DCF
        dcf = RealEstateDCF(assumptions, cash_flows, terminal_assumptions)
        analysis = dcf.get_comprehensive_analysis()
        
        # Análisis de escenarios (opcional)
        scenarios_result = None
        if request.include_scenarios:
            scenarios_result = scenario_analysis(dcf)
        
        return DCFResponse(
            project_name=analysis["project_name"],
            npv=analysis["npv"],
            irr=analysis["irr"],
            profitability_index=analysis["profitability_index"],
            payback_period=analysis["payback_period"],
            accept_project=analysis["accept_project"],
            decision_rationale=analysis["decision_rationale"],
            year_by_year=analysis["year_by_year"],
            scenarios=scenarios_result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en análisis DCF: {str(e)}"
        )


@app.post(
    "/api/v1/optimize/mix",
    response_model=OptimizationResponse,
    status_code=status.HTTP_200_OK,
    tags=["Optimización - Mix de Productos"]
)
async def optimize_product_mix(request: OptimizationRequest):
    """
    Optimización del mix de productos/unidades bajo restricciones
    
    Encuentra la combinación óptima de productos que maximiza el beneficio
    sujeto a restricciones de recursos, capacidad y demanda.
    
    **Método**: Programación Lineal (Simplex)
    """
    try:
        # Validar que todas las restricciones tengan el mismo número de tasas
        n_products = len(request.products)
        for constraint in request.resource_constraints:
            if len(constraint.consumption_rates) != n_products:
                raise ValueError(
                    f"Restricción '{constraint.name}' debe tener {n_products} tasas"
                )
        
        # Crear objetos del core
        products = [
            Product(
                name=p.name,
                unit_price=p.unit_price,
                variable_cost=p.variable_cost,
                fixed_cost_allocation=p.fixed_cost_allocation
            )
            for p in request.products
        ]
        
        constraints = [
            ResourceConstraint(
                name=c.name,
                total_available=c.total_available,
                consumption_rates=c.consumption_rates
            )
            for c in request.resource_constraints
        ]
        
        demand = DemandConstraint(
            min_demand=request.min_demand or [],
            max_demand=request.max_demand or []
        )
        
        # Optimizar
        optimizer = OperationsOptimizer(
            products=products,
            resource_constraints=constraints,
            demand_constraints=demand,
            fixed_costs=request.fixed_costs
        )
        
        result = optimizer.optimize_linear_programming()
        
        return OptimizationResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en optimización: {str(e)}"
        )


# =============================================================================
# Ejecución de la Aplicación
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Hot reload en desarrollo
        log_level="info"
    )
