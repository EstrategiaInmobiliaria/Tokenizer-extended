"""
Real Estate DCF Engine - Discounted Cash Flow for Real Estate Projects
Módulo de Inversión Inmobiliaria

Este módulo implementa el análisis de flujo de caja descontado (DCF) específico
para proyectos de inversión inmobiliaria, incluyendo:
- Proyección de flujos de caja a múltiples períodos
- Cálculo de Valor Presente Neto (VPN/NPV)
- Tasa Interna de Retorno (TIR/IRR)
- Valor Residual (Terminal Value)
- Análisis de escenarios (optimista, base, pesimista)

Fórmulas Teóricas:
------------------
VPN = Σ(CFt / (1 + r)^t) - Inversión Inicial + VR / (1 + r)^n

Donde:
- CFt = Flujo de caja en el período t
- r = Tasa de descuento (WACC)
- t = Período de tiempo
- VR = Valor Residual (Terminal Value)
- n = Número total de períodos

TIR es la tasa r donde VPN = 0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import numpy as np
from scipy.optimize import newton


class ScenarioType(Enum):
    """Tipos de escenarios de análisis"""
    OPTIMISTIC = "optimista"
    BASE = "base"
    PESSIMISTIC = "pesimista"


@dataclass
class ProjectAssumptions:
    """Supuestos macroeconómicos y del proyecto"""
    project_name: str
    initial_investment: float  # Inversión inicial (período 0)
    discount_rate: float       # Tasa de descuento (WACC)
    projection_years: int = 5  # Horizonte de evaluación
    inflation_rate: float = 0.03  # Tasa de inflación anual
    
    def __post_init__(self):
        if self.initial_investment <= 0:
            raise ValueError("La inversión inicial debe ser positiva")
        if not 0 <= self.discount_rate <= 1:
            raise ValueError("La tasa de descuento debe estar entre 0 y 1")
        if self.projection_years <= 0:
            raise ValueError("Los años de proyección deben ser positivos")


@dataclass
class RealEstateCashFlows:
    """Estructura de flujos de caja inmobiliarios"""
    rental_income: List[float] = field(default_factory=list)  # Ingresos por arriendo
    sales_revenue: List[float] = field(default_factory=list)  # Ingresos por venta
    operating_costs: List[float] = field(default_factory=list)  # Costos operativos
    capex: List[float] = field(default_factory=list)  # Inversiones en capital
    taxes: List[float] = field(default_factory=list)  # Impuestos
    
    def get_net_cash_flow(self, period: int) -> float:
        """Calcula el flujo de caja neto para un período específico"""
        income = (
            self.rental_income[period] if period < len(self.rental_income) else 0
        ) + (
            self.sales_revenue[period] if period < len(self.sales_revenue) else 0
        )
        
        expenses = (
            (self.operating_costs[period] if period < len(self.operating_costs) else 0) +
            (self.capex[period] if period < len(self.capex) else 0) +
            (self.taxes[period] if period < len(self.taxes) else 0)
        )
        
        return income - expenses
    
    def get_all_net_cash_flows(self) -> List[float]:
        """Retorna todos los flujos de caja netos"""
        max_periods = max(
            len(self.rental_income),
            len(self.sales_revenue),
            len(self.operating_costs),
            len(self.capex),
            len(self.taxes)
        )
        return [self.get_net_cash_flow(i) for i in range(max_periods)]


@dataclass
class TerminalValueAssumptions:
    """Supuestos para el cálculo del valor residual"""
    method: str = "perpetuity"  # "perpetuity" o "exit_multiple"
    perpetual_growth_rate: float = 0.02  # Para método perpetuidad
    exit_cap_rate: float = 0.08  # Para método exit multiple
    last_year_noi: Optional[float] = None  # NOI del último año
    
    def calculate_terminal_value(self, last_cf: float, discount_rate: float) -> float:
        """
        Calcula el valor residual según el método seleccionado
        
        Método Perpetuidad: VR = CF * (1 + g) / (r - g)
        Método Exit Multiple: VR = NOI / Cap Rate
        """
        if self.method == "perpetuity":
            if discount_rate <= self.perpetual_growth_rate:
                raise ValueError("La tasa de descuento debe ser mayor que g")
            return last_cf * (1 + self.perpetual_growth_rate) / (
                discount_rate - self.perpetual_growth_rate
            )
        elif self.method == "exit_multiple":
            noi = self.last_year_noi if self.last_year_noi is not None else last_cf
            return noi / self.exit_cap_rate
        else:
            raise ValueError(f"Método no reconocido: {self.method}")


class RealEstateDCF:
    """Motor de análisis DCF para proyectos inmobiliarios"""
    
    def __init__(
        self,
        assumptions: ProjectAssumptions,
        cash_flows: RealEstateCashFlows,
        terminal_value_assumptions: Optional[TerminalValueAssumptions] = None
    ):
        self.assumptions = assumptions
        self.cash_flows = cash_flows
        self.terminal_value_assumptions = terminal_value_assumptions or TerminalValueAssumptions()
        
        # Validar que los flujos coincidan con los años de proyección
        net_flows = self.cash_flows.get_all_net_cash_flows()
        if len(net_flows) != assumptions.projection_years:
            print(f"⚠️  Advertencia: Se esperaban {assumptions.projection_years} flujos, "
                  f"se encontraron {len(net_flows)}")
    
    def calculate_npv(self, include_terminal_value: bool = True) -> float:
        """
        Calcula el Valor Presente Neto (VPN)
        
        VPN = -I0 + Σ(CFt / (1 + r)^t) + VR / (1 + r)^n
        
        Args:
            include_terminal_value: Si se incluye el valor residual
        
        Returns:
            float: VPN del proyecto
        """
        net_flows = self.cash_flows.get_all_net_cash_flows()
        discount_rate = self.assumptions.discount_rate
        
        # Calcular VP de los flujos operativos
        pv_operating_flows = sum(
            cf / (1 + discount_rate) ** (t + 1)
            for t, cf in enumerate(net_flows)
        )
        
        # Calcular VP del valor residual
        pv_terminal_value = 0
        if include_terminal_value and net_flows:
            terminal_value = self.terminal_value_assumptions.calculate_terminal_value(
                net_flows[-1], discount_rate
            )
            pv_terminal_value = terminal_value / (
                (1 + discount_rate) ** len(net_flows)
            )
        
        # NPV = -Inversión Inicial + VP Flujos + VP Valor Residual
        npv = -self.assumptions.initial_investment + pv_operating_flows + pv_terminal_value
        
        return npv
    
    def calculate_irr(self) -> float:
        """
        Calcula la Tasa Interna de Retorno (TIR)
        
        TIR es la tasa donde VPN = 0
        
        Returns:
            float: TIR como tasa decimal
        """
        net_flows = self.cash_flows.get_all_net_cash_flows()
        
        # Preparar flujos: [-I0, CF1, CF2, ..., CFn + VR]
        terminal_value = self.terminal_value_assumptions.calculate_terminal_value(
            net_flows[-1] if net_flows else 0,
            self.assumptions.discount_rate
        )
        
        all_flows = [-self.assumptions.initial_investment] + net_flows[:-1] + [
            net_flows[-1] + terminal_value
        ]
        
        # Usar NumPy para calcular IRR
        try:
            irr = np.irr(all_flows)
            return irr if not np.isnan(irr) else 0
        except:
            # Método alternativo usando scipy
            def npv_function(rate):
                return sum(cf / (1 + rate) ** t for t, cf in enumerate(all_flows))
            
            try:
                irr = newton(npv_function, self.assumptions.discount_rate)
                return irr
            except:
                return 0
    
    def calculate_profitability_index(self) -> float:
        """
        Calcula el Índice de Rentabilidad (IR)
        
        IR = VP(Flujos) / Inversión Inicial
        
        Returns:
            float: Índice de rentabilidad
        """
        npv = self.calculate_npv()
        return (npv + self.assumptions.initial_investment) / self.assumptions.initial_investment
    
    def calculate_payback_period(self) -> float:
        """
        Calcula el Período de Recuperación de la Inversión
        
        Returns:
            float: Años hasta recuperar la inversión
        """
        net_flows = self.cash_flows.get_all_net_cash_flows()
        cumulative = -self.assumptions.initial_investment
        
        for t, cf in enumerate(net_flows):
            cumulative += cf
            if cumulative >= 0:
                # Interpolación para obtener el período exacto
                previous_cumulative = cumulative - cf
                fraction = abs(previous_cumulative) / cf if cf != 0 else 0
                return t + fraction
        
        return float('inf')  # No se recupera en el período proyectado
    
    def get_year_by_year_analysis(self) -> List[Dict[str, float]]:
        """
        Retorna análisis año por año con métricas clave
        
        Returns:
            List de dictionaries con métricas por año
        """
        net_flows = self.cash_flows.get_all_net_cash_flows()
        discount_rate = self.assumptions.discount_rate
        
        analysis = []
        cumulative_pv = -self.assumptions.initial_investment
        cumulative_nominal = -self.assumptions.initial_investment
        
        for t, cf in enumerate(net_flows):
            year = t + 1
            discount_factor = 1 / (1 + discount_rate) ** year
            pv_cash_flow = cf * discount_factor
            cumulative_pv += pv_cash_flow
            cumulative_nominal += cf
            
            analysis.append({
                "year": year,
                "cash_flow": cf,
                "discount_factor": discount_factor,
                "pv_cash_flow": pv_cash_flow,
                "cumulative_pv": cumulative_pv,
                "cumulative_nominal": cumulative_nominal
            })
        
        # Agregar valor residual en el último año
        if net_flows:
            terminal_value = self.terminal_value_assumptions.calculate_terminal_value(
                net_flows[-1], discount_rate
            )
            pv_terminal = terminal_value / ((1 + discount_rate) ** len(net_flows))
            
            analysis.append({
                "year": "Terminal Value",
                "cash_flow": terminal_value,
                "discount_factor": 1 / ((1 + discount_rate) ** len(net_flows)),
                "pv_cash_flow": pv_terminal,
                "cumulative_pv": cumulative_pv + pv_terminal,
                "cumulative_nominal": cumulative_nominal + terminal_value
            })
        
        return analysis
    
    def get_comprehensive_analysis(self) -> Dict[str, any]:
        """
        Retorna análisis completo del proyecto
        
        Returns:
            Dict con todas las métricas calculadas
        """
        npv = self.calculate_npv()
        irr = self.calculate_irr()
        pi = self.calculate_profitability_index()
        payback = self.calculate_payback_period()
        net_flows = self.cash_flows.get_all_net_cash_flows()
        
        return {
            "project_name": self.assumptions.project_name,
            "initial_investment": self.assumptions.initial_investment,
            "discount_rate": self.assumptions.discount_rate,
            "projection_years": self.assumptions.projection_years,
            
            # Métricas principales
            "npv": npv,
            "irr": irr,
            "profitability_index": pi,
            "payback_period": payback,
            
            # Análisis de flujos
            "total_nominal_cash_flows": sum(net_flows),
            "average_annual_cash_flow": np.mean(net_flows) if net_flows else 0,
            
            # Decisión de inversión
            "accept_project": npv > 0 and irr > self.assumptions.discount_rate,
            "decision_rationale": self._get_decision_rationale(npv, irr),
            
            # Desglose anual
            "year_by_year": self.get_year_by_year_analysis()
        }
    
    def _get_decision_rationale(self, npv: float, irr: float) -> str:
        """Genera la justificación de la decisión de inversión"""
        if npv > 0 and irr > self.assumptions.discount_rate:
            return (f"✅ PROYECTO VIABLE: VPN positivo (${npv:,.0f}) y "
                   f"TIR ({irr*100:.2f}%) > WACC ({self.assumptions.discount_rate*100:.2f}%)")
        elif npv < 0:
            return f"❌ RECHAZAR: VPN negativo (${npv:,.0f}), destruye valor"
        else:
            return (f"⚠️  REVISAR: TIR ({irr*100:.2f}%) < WACC "
                   f"({self.assumptions.discount_rate*100:.2f}%), riesgo elevado")


def scenario_analysis(
    base_dcf: RealEstateDCF,
    optimistic_adjustment: float = 1.20,
    pessimistic_adjustment: float = 0.80
) -> Dict[str, Dict]:
    """
    Realiza análisis de escenarios (optimista, base, pesimista)
    
    Args:
        base_dcf: Análisis DCF base
        optimistic_adjustment: Factor multiplicador para escenario optimista
        pessimistic_adjustment: Factor multiplicador para escenario pesimista
    
    Returns:
        Dict con resultados de los tres escenarios
    """
    base_analysis = base_dcf.get_comprehensive_analysis()
    
    # Escenario optimista
    optimistic_flows = RealEstateCashFlows(
        rental_income=[r * optimistic_adjustment for r in base_dcf.cash_flows.rental_income],
        sales_revenue=[s * optimistic_adjustment for s in base_dcf.cash_flows.sales_revenue],
        operating_costs=base_dcf.cash_flows.operating_costs,
        capex=base_dcf.cash_flows.capex,
        taxes=[t * optimistic_adjustment for t in base_dcf.cash_flows.taxes]
    )
    optimistic_dcf = RealEstateDCF(
        base_dcf.assumptions, optimistic_flows, base_dcf.terminal_value_assumptions
    )
    
    # Escenario pesimista
    pessimistic_flows = RealEstateCashFlows(
        rental_income=[r * pessimistic_adjustment for r in base_dcf.cash_flows.rental_income],
        sales_revenue=[s * pessimistic_adjustment for s in base_dcf.cash_flows.sales_revenue],
        operating_costs=[c * 1.1 for c in base_dcf.cash_flows.operating_costs],  # Costos 10% mayores
        capex=base_dcf.cash_flows.capex,
        taxes=[t * pessimistic_adjustment for t in base_dcf.cash_flows.taxes]
    )
    pessimistic_dcf = RealEstateDCF(
        base_dcf.assumptions, pessimistic_flows, base_dcf.terminal_value_assumptions
    )
    
    return {
        "optimistic": optimistic_dcf.get_comprehensive_analysis(),
        "base": base_analysis,
        "pessimistic": pessimistic_dcf.get_comprehensive_analysis()
    }


if __name__ == "__main__":
    print("=" * 70)
    print("REAL ESTATE DCF - Ejemplo de Análisis")
    print("=" * 70)
    
    # Supuestos del proyecto
    assumptions = ProjectAssumptions(
        project_name="Edificio Residencial Las Condes",
        initial_investment=1_200_000_000,  # $1,200M CLP
        discount_rate=0.096,  # WACC 9.6%
        projection_years=5
    )
    
    # Flujos de caja proyectados (en CLP)
    cash_flows = RealEstateCashFlows(
        rental_income=[150_000_000, 165_000_000, 180_000_000, 195_000_000, 210_000_000],
        sales_revenue=[0, 0, 200_000_000, 300_000_000, 400_000_000],
        operating_costs=[50_000_000, 52_000_000, 54_000_000, 56_000_000, 58_000_000],
        capex=[20_000_000, 15_000_000, 15_000_000, 10_000_000, 10_000_000],
        taxes=[25_000_000, 28_000_000, 35_000_000, 45_000_000, 55_000_000]
    )
    
    # Valor residual
    terminal_assumptions = TerminalValueAssumptions(
        method="perpetuity",
        perpetual_growth_rate=0.02
    )
    
    # Análisis DCF
    dcf = RealEstateDCF(assumptions, cash_flows, terminal_assumptions)
    analysis = dcf.get_comprehensive_analysis()
    
    print(f"\n🏢 PROYECTO: {analysis['project_name']}")
    print(f"   Inversión Inicial: ${analysis['initial_investment']:,.0f}")
    print(f"   WACC (Descuento):  {analysis['discount_rate']*100:.2f}%")
    
    print(f"\n📊 RESULTADOS PRINCIPALES:")
    print(f"   VPN:  ${analysis['npv']:,.0f}")
    print(f"   TIR:  {analysis['irr']*100:.2f}%")
    print(f"   IR:   {analysis['profitability_index']:.2f}")
    print(f"   Payback: {analysis['payback_period']:.1f} años")
    
    print(f"\n🎯 DECISIÓN:")
    print(f"   {analysis['decision_rationale']}")
    
    print("\n" + "=" * 70)
