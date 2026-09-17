"""
WACC Engine - Weighted Average Cost of Capital Calculator
Módulo de Finanzas Corporativas

Este módulo implementa el cálculo del WACC (Weighted Average Cost of Capital)
como pilar fundamental para la evaluación de proyectos de inversión.

Fórmulas Teóricas:
------------------
WACC = (E/V) * Re + (D/V) * Rd * (1 - Tc)

Donde:
- E = Valor de mercado del patrimonio (Equity)
- D = Valor de mercado de la deuda (Debt)
- V = E + D (Valor total de la empresa)
- Re = Costo del patrimonio (calculado con CAPM)
- Rd = Costo de la deuda
- Tc = Tasa impositiva corporativa

CAPM (Capital Asset Pricing Model):
Re = Rf + β * (Rm - Rf)

Donde:
- Rf = Tasa libre de riesgo
- β = Beta del activo (riesgo sistemático)
- Rm = Retorno esperado del mercado
"""

from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np


@dataclass
class MarketParameters:
    """Parámetros macroeconómicos del mercado"""
    risk_free_rate: float  # Tasa libre de riesgo (Rf)
    market_return: float   # Retorno esperado del mercado (Rm)
    corporate_tax_rate: float  # Tasa impositiva corporativa (Tc)
    
    def __post_init__(self):
        """Validación de parámetros"""
        if not 0 <= self.risk_free_rate <= 1:
            raise ValueError("La tasa libre de riesgo debe estar entre 0 y 1")
        if not 0 <= self.market_return <= 1:
            raise ValueError("El retorno del mercado debe estar entre 0 y 1")
        if not 0 <= self.corporate_tax_rate <= 1:
            raise ValueError("La tasa impositiva debe estar entre 0 y 1")


@dataclass
class CapitalStructure:
    """Estructura de capital de la empresa"""
    equity_value: float    # Valor del patrimonio (E)
    debt_value: float      # Valor de la deuda (D)
    beta: float            # Beta del activo (riesgo sistemático)
    debt_rate: float       # Costo de la deuda (Rd)
    
    @property
    def total_value(self) -> float:
        """Valor total de la empresa (V = E + D)"""
        return self.equity_value + self.debt_value
    
    @property
    def equity_weight(self) -> float:
        """Proporción del patrimonio (E/V)"""
        return self.equity_value / self.total_value if self.total_value > 0 else 0
    
    @property
    def debt_weight(self) -> float:
        """Proporción de la deuda (D/V)"""
        return self.debt_value / self.total_value if self.total_value > 0 else 0
    
    @property
    def debt_to_equity_ratio(self) -> float:
        """Razón deuda/patrimonio (D/E)"""
        return self.debt_value / self.equity_value if self.equity_value > 0 else 0
    
    def __post_init__(self):
        """Validación de estructura de capital"""
        if self.equity_value < 0 or self.debt_value < 0:
            raise ValueError("Los valores de capital deben ser positivos")
        if self.debt_rate < 0:
            raise ValueError("El costo de la deuda debe ser positivo")


class WACCEngine:
    """Motor de cálculo del WACC y métricas relacionadas"""
    
    def __init__(self, market_params: MarketParameters, capital_structure: CapitalStructure):
        self.market = market_params
        self.capital = capital_structure
    
    def calculate_cost_of_equity(self) -> float:
        """
        Calcula el costo del patrimonio usando CAPM
        
        Re = Rf + β * (Rm - Rf)
        
        Returns:
            float: Costo del patrimonio (Re)
        """
        market_risk_premium = self.market.market_return - self.market.risk_free_rate
        return self.market.risk_free_rate + (self.capital.beta * market_risk_premium)
    
    def calculate_after_tax_cost_of_debt(self) -> float:
        """
        Calcula el costo de la deuda después de impuestos
        
        Rd_after_tax = Rd * (1 - Tc)
        
        Returns:
            float: Costo de la deuda después de impuestos
        """
        return self.capital.debt_rate * (1 - self.market.corporate_tax_rate)
    
    def calculate_wacc(self) -> float:
        """
        Calcula el WACC (Weighted Average Cost of Capital)
        
        WACC = (E/V) * Re + (D/V) * Rd * (1 - Tc)
        
        Returns:
            float: WACC como tasa decimal
        """
        cost_of_equity = self.calculate_cost_of_equity()
        after_tax_debt_cost = self.calculate_after_tax_cost_of_debt()
        
        wacc = (
            self.capital.equity_weight * cost_of_equity +
            self.capital.debt_weight * after_tax_debt_cost
        )
        
        return wacc
    
    def get_detailed_breakdown(self) -> Dict[str, float]:
        """
        Retorna un desglose detallado de todos los componentes del WACC
        
        Returns:
            Dict con todas las métricas calculadas
        """
        cost_of_equity = self.calculate_cost_of_equity()
        after_tax_debt_cost = self.calculate_after_tax_cost_of_debt()
        wacc = self.calculate_wacc()
        
        return {
            # Parámetros de entrada
            "risk_free_rate": self.market.risk_free_rate,
            "market_return": self.market.market_return,
            "market_risk_premium": self.market.market_return - self.market.risk_free_rate,
            "corporate_tax_rate": self.market.corporate_tax_rate,
            
            # Estructura de capital
            "equity_value": self.capital.equity_value,
            "debt_value": self.capital.debt_value,
            "total_value": self.capital.total_value,
            "equity_weight": self.capital.equity_weight,
            "debt_weight": self.capital.debt_weight,
            "debt_to_equity_ratio": self.capital.debt_to_equity_ratio,
            
            # Costos de capital
            "beta": self.capital.beta,
            "cost_of_equity": cost_of_equity,
            "cost_of_debt_before_tax": self.capital.debt_rate,
            "cost_of_debt_after_tax": after_tax_debt_cost,
            "tax_shield_on_debt": self.capital.debt_rate * self.market.corporate_tax_rate,
            
            # Resultado final
            "wacc": wacc,
            "wacc_percentage": wacc * 100
        }
    
    def sensitivity_analysis(
        self, 
        beta_range: Optional[tuple] = None,
        leverage_range: Optional[tuple] = None,
        steps: int = 20
    ) -> Dict[str, np.ndarray]:
        """
        Análisis de sensibilidad del WACC respecto a Beta y Apalancamiento
        
        Args:
            beta_range: Rango de betas a evaluar (min, max)
            leverage_range: Rango de D/E a evaluar (min, max)
            steps: Número de puntos a calcular
        
        Returns:
            Dict con arrays de betas, leverages y matriz de WACCs
        """
        if beta_range is None:
            beta_range = (max(0.5, self.capital.beta - 0.5), self.capital.beta + 0.5)
        
        if leverage_range is None:
            current_leverage = self.capital.debt_to_equity_ratio
            leverage_range = (max(0, current_leverage - 1), current_leverage + 1)
        
        betas = np.linspace(beta_range[0], beta_range[1], steps)
        leverages = np.linspace(leverage_range[0], leverage_range[1], steps)
        
        wacc_matrix = np.zeros((steps, steps))
        
        for i, beta in enumerate(betas):
            for j, leverage in enumerate(leverages):
                # Recalcular estructura de capital con nuevo leverage
                total_value = self.capital.total_value
                debt_value = (leverage / (1 + leverage)) * total_value
                equity_value = total_value - debt_value
                
                # Crear estructura temporal
                temp_capital = CapitalStructure(
                    equity_value=equity_value,
                    debt_value=debt_value,
                    beta=beta,
                    debt_rate=self.capital.debt_rate
                )
                
                # Calcular WACC temporal
                temp_engine = WACCEngine(self.market, temp_capital)
                wacc_matrix[i, j] = temp_engine.calculate_wacc()
        
        return {
            "betas": betas,
            "leverages": leverages,
            "wacc_matrix": wacc_matrix
        }


# Funciones auxiliares para casos de uso rápidos

def quick_wacc_calculation(
    risk_free_rate: float = 0.05,
    market_return: float = 0.12,
    corporate_tax_rate: float = 0.30,
    equity_value: float = 1000000,
    debt_value: float = 500000,
    beta: float = 1.2,
    debt_rate: float = 0.08
) -> Dict[str, float]:
    """
    Función de conveniencia para cálculo rápido de WACC
    
    Ejemplo:
        >>> result = quick_wacc_calculation(
        ...     equity_value=1_000_000,
        ...     debt_value=500_000,
        ...     beta=1.2
        ... )
        >>> print(f"WACC: {result['wacc_percentage']:.2f}%")
    """
    market = MarketParameters(risk_free_rate, market_return, corporate_tax_rate)
    capital = CapitalStructure(equity_value, debt_value, beta, debt_rate)
    engine = WACCEngine(market, capital)
    
    return engine.get_detailed_breakdown()


if __name__ == "__main__":
    # Ejemplo de uso
    print("=" * 70)
    print("WACC ENGINE - Ejemplo de Cálculo")
    print("=" * 70)
    
    # Parámetros de mercado (Chile/Latinoamérica)
    market = MarketParameters(
        risk_free_rate=0.05,      # 5% (bonos del tesoro)
        market_return=0.12,        # 12% (retorno esperado S&P/IPSA)
        corporate_tax_rate=0.27    # 27% (tasa corporativa Chile)
    )
    
    # Estructura de capital de un proyecto inmobiliario
    capital = CapitalStructure(
        equity_value=800_000_000,   # $800M CLP en patrimonio
        debt_value=400_000_000,     # $400M CLP en deuda
        beta=1.15,                  # Beta sector inmobiliario
        debt_rate=0.08             # 8% costo de deuda bancaria
    )
    
    # Calcular WACC
    engine = WACCEngine(market, capital)
    breakdown = engine.get_detailed_breakdown()
    
    print(f"\n📊 ESTRUCTURA DE CAPITAL:")
    print(f"   Patrimonio (E): ${breakdown['equity_value']:,.0f}")
    print(f"   Deuda (D):      ${breakdown['debt_value']:,.0f}")
    print(f"   Valor Total:    ${breakdown['total_value']:,.0f}")
    print(f"   D/E Ratio:      {breakdown['debt_to_equity_ratio']:.2f}")
    
    print(f"\n💰 COSTOS DE CAPITAL:")
    print(f"   Costo Patrimonio (Re):     {breakdown['cost_of_equity']*100:.2f}%")
    print(f"   Costo Deuda antes imptos:  {breakdown['cost_of_debt_before_tax']*100:.2f}%")
    print(f"   Costo Deuda después imp:   {breakdown['cost_of_debt_after_tax']*100:.2f}%")
    print(f"   Escudo Fiscal:             {breakdown['tax_shield_on_debt']*100:.2f}%")
    
    print(f"\n🎯 RESULTADO FINAL:")
    print(f"   WACC = {breakdown['wacc_percentage']:.2f}%")
    print(f"\n   → Esta es la tasa de descuento mínima que el proyecto")
    print(f"     debe generar para crear valor para los accionistas.")
    print("\n" + "=" * 70)
