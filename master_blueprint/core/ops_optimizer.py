"""
Operations Optimizer - Optimización de Mix de Productos y Operaciones
Módulo de Optimización Matemática con Restricciones

Este módulo implementa algoritmos de optimización multivariable para determinar
el mix óptimo de productos/unidades que maximiza el beneficio operativo bajo
restricciones de recursos, capacidad y mercado.

Fundamentos Matemáticos:
------------------------
Función Objetivo (maximizar):
f(x, y) = Px * x + Py * y - Cx * x - Cy * y

Donde:
- x, y = Cantidades de productos A y B
- Px, Py = Precios de venta unitarios
- Cx, Cy = Costos variables unitarios

Restricciones:
g1(x, y) = a1*x + b1*y ≤ R1  (Restricción de recurso 1)
g2(x, y) = a2*x + b2*y ≤ R2  (Restricción de recurso 2)
x ≥ 0, y ≥ 0  (No negatividad)

Condiciones de Optimalidad (Método Lagrange):
∇f(x,y) = λ∇g(x,y)

Para restricciones activas en el óptimo:
∂f/∂x = λ(∂g/∂x)
∂f/∂y = λ(∂g/∂y)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
import numpy as np
from scipy.optimize import minimize, linprog, NonlinearConstraint
import matplotlib.pyplot as plt


@dataclass
class Product:
    """Definición de un producto o unidad operativa"""
    name: str
    unit_price: float          # Precio de venta unitario
    variable_cost: float       # Costo variable unitario
    fixed_cost_allocation: float = 0  # Asignación de costos fijos
    
    @property
    def contribution_margin(self) -> float:
        """Margen de contribución unitario"""
        return self.unit_price - self.variable_cost
    
    @property
    def contribution_margin_ratio(self) -> float:
        """Razón de margen de contribución"""
        return self.contribution_margin / self.unit_price if self.unit_price > 0 else 0


@dataclass
class ResourceConstraint:
    """Restricción de recurso disponible"""
    name: str
    total_available: float           # Cantidad total disponible
    consumption_rates: List[float]   # Tasa de consumo por producto [a1, a2, ..., an]
    
    def is_feasible(self, quantities: List[float]) -> bool:
        """Verifica si las cantidades cumplen la restricción"""
        total_consumption = sum(
            rate * qty for rate, qty in zip(self.consumption_rates, quantities)
        )
        return total_consumption <= self.total_available
    
    def slack(self, quantities: List[float]) -> float:
        """Calcula la holgura (slack) de la restricción"""
        total_consumption = sum(
            rate * qty for rate, qty in zip(self.consumption_rates, quantities)
        )
        return self.total_available - total_consumption


@dataclass
class DemandConstraint:
    """Restricciones de demanda máxima/mínima"""
    min_demand: List[float] = field(default_factory=list)  # Demanda mínima por producto
    max_demand: List[float] = field(default_factory=list)  # Demanda máxima por producto


class OperationsOptimizer:
    """Motor de optimización de operaciones multi-producto"""
    
    def __init__(
        self,
        products: List[Product],
        resource_constraints: List[ResourceConstraint],
        demand_constraints: Optional[DemandConstraint] = None,
        fixed_costs: float = 0
    ):
        self.products = products
        self.resource_constraints = resource_constraints
        self.demand_constraints = demand_constraints or DemandConstraint()
        self.fixed_costs = fixed_costs
        self.n_products = len(products)
        
        # Validaciones
        for constraint in resource_constraints:
            if len(constraint.consumption_rates) != self.n_products:
                raise ValueError(
                    f"Constraint '{constraint.name}' debe tener {self.n_products} tasas"
                )
    
    def objective_function(self, quantities: np.ndarray) -> float:
        """
        Función objetivo: Maximizar beneficio total
        
        Beneficio = Σ(margen_contribución_i * cantidad_i) - Costos_fijos
        
        Nota: Para minimización usamos el negativo
        """
        total_contribution = sum(
            product.contribution_margin * qty
            for product, qty in zip(self.products, quantities)
        )
        return -(total_contribution - self.fixed_costs)
    
    def gradient(self, quantities: np.ndarray) -> np.ndarray:
        """
        Gradiente de la función objetivo
        
        ∇f = [∂f/∂x1, ∂f/∂x2, ..., ∂f/∂xn]
        """
        # Para función lineal, el gradiente es constante
        return np.array([-product.contribution_margin for product in self.products])
    
    def optimize_linear_programming(self) -> Dict[str, any]:
        """
        Optimización usando programación lineal (scipy.optimize.linprog)
        
        Método: Simplex o Interior Point
        
        Returns:
            Dict con solución óptima y métricas
        """
        # Coeficientes de la función objetivo (negativo para maximizar)
        c = np.array([-product.contribution_margin for product in self.products])
        
        # Matriz de restricciones de desigualdad (A_ub * x <= b_ub)
        A_ub = []
        b_ub = []
        
        for constraint in self.resource_constraints:
            A_ub.append(constraint.consumption_rates)
            b_ub.append(constraint.total_available)
        
        A_ub = np.array(A_ub) if A_ub else None
        b_ub = np.array(b_ub) if b_ub else None
        
        # Bounds para cada variable (demanda mín/máx)
        bounds = []
        for i in range(self.n_products):
            min_bound = (
                self.demand_constraints.min_demand[i]
                if i < len(self.demand_constraints.min_demand)
                else 0
            )
            max_bound = (
                self.demand_constraints.max_demand[i]
                if i < len(self.demand_constraints.max_demand)
                else None
            )
            bounds.append((min_bound, max_bound))
        
        # Resolver
        result = linprog(
            c=c,
            A_ub=A_ub,
            b_ub=b_ub,
            bounds=bounds,
            method='highs'  # Método moderno de programación lineal
        )
        
        if not result.success:
            return {
                "success": False,
                "message": result.message,
                "optimal_quantities": None,
                "optimal_profit": None
            }
        
        optimal_quantities = result.x
        optimal_profit = -result.fun - self.fixed_costs
        
        return {
            "success": True,
            "method": "Linear Programming (Simplex)",
            "optimal_quantities": optimal_quantities.tolist(),
            "optimal_profit": optimal_profit,
            "products": [p.name for p in self.products],
            "detailed_breakdown": self._get_detailed_breakdown(optimal_quantities),
            "shadow_prices": self._calculate_shadow_prices(optimal_quantities),
            "sensitivity_analysis": self._sensitivity_ranges(optimal_quantities)
        }
    
    def optimize_nonlinear(
        self,
        initial_guess: Optional[List[float]] = None,
        method: str = 'SLSQP'
    ) -> Dict[str, any]:
        """
        Optimización no lineal con restricciones
        
        Útil cuando hay economías/deseconomías de escala
        
        Args:
            initial_guess: Punto inicial de búsqueda
            method: 'SLSQP', 'trust-constr', etc.
        
        Returns:
            Dict con solución óptima
        """
        if initial_guess is None:
            # Punto inicial: mitad de la demanda máxima o 1000 unidades
            initial_guess = [
                self.demand_constraints.max_demand[i] / 2
                if i < len(self.demand_constraints.max_demand)
                else 1000
                for i in range(self.n_products)
            ]
        
        # Restricciones en formato scipy
        constraints = []
        
        # Restricciones de recursos
        for constraint in self.resource_constraints:
            def resource_constraint(x, rates=constraint.consumption_rates, 
                                  available=constraint.total_available):
                return available - sum(rate * qty for rate, qty in zip(rates, x))
            
            constraints.append({
                'type': 'ineq',
                'fun': resource_constraint
            })
        
        # Bounds
        bounds = []
        for i in range(self.n_products):
            min_bound = (
                self.demand_constraints.min_demand[i]
                if i < len(self.demand_constraints.min_demand)
                else 0
            )
            max_bound = (
                self.demand_constraints.max_demand[i]
                if i < len(self.demand_constraints.max_demand)
                else np.inf
            )
            bounds.append((min_bound, max_bound))
        
        # Optimizar
        result = minimize(
            fun=self.objective_function,
            x0=initial_guess,
            method=method,
            bounds=bounds,
            constraints=constraints,
            jac=self.gradient
        )
        
        if not result.success:
            return {
                "success": False,
                "message": result.message,
                "optimal_quantities": None,
                "optimal_profit": None
            }
        
        optimal_quantities = result.x
        optimal_profit = -result.fun
        
        return {
            "success": True,
            "method": f"Nonlinear Optimization ({method})",
            "optimal_quantities": optimal_quantities.tolist(),
            "optimal_profit": optimal_profit,
            "products": [p.name for p in self.products],
            "detailed_breakdown": self._get_detailed_breakdown(optimal_quantities)
        }
    
    def _get_detailed_breakdown(self, quantities: np.ndarray) -> Dict[str, any]:
        """Desglose detallado de la solución"""
        breakdown = []
        
        total_revenue = 0
        total_variable_costs = 0
        total_contribution = 0
        
        for product, qty in zip(self.products, quantities):
            revenue = product.unit_price * qty
            variable_cost = product.variable_cost * qty
            contribution = product.contribution_margin * qty
            
            total_revenue += revenue
            total_variable_costs += variable_cost
            total_contribution += contribution
            
            breakdown.append({
                "product": product.name,
                "quantity": qty,
                "unit_price": product.unit_price,
                "unit_variable_cost": product.variable_cost,
                "unit_contribution_margin": product.contribution_margin,
                "total_revenue": revenue,
                "total_variable_cost": variable_cost,
                "total_contribution": contribution
            })
        
        # Análisis de restricciones
        constraint_analysis = []
        for constraint in self.resource_constraints:
            used = sum(
                rate * qty for rate, qty in zip(constraint.consumption_rates, quantities)
            )
            slack = constraint.total_available - used
            utilization = (used / constraint.total_available * 100) if constraint.total_available > 0 else 0
            
            constraint_analysis.append({
                "constraint": constraint.name,
                "available": constraint.total_available,
                "used": used,
                "slack": slack,
                "utilization_percentage": utilization,
                "is_binding": abs(slack) < 1e-6  # Restricción activa
            })
        
        return {
            "products": breakdown,
            "summary": {
                "total_revenue": total_revenue,
                "total_variable_costs": total_variable_costs,
                "total_contribution_margin": total_contribution,
                "fixed_costs": self.fixed_costs,
                "ebit": total_contribution - self.fixed_costs,
                "contribution_margin_ratio": (
                    total_contribution / total_revenue * 100
                    if total_revenue > 0 else 0
                )
            },
            "constraints": constraint_analysis
        }
    
    def _calculate_shadow_prices(self, quantities: np.ndarray) -> List[Dict[str, float]]:
        """
        Calcula precios sombra (shadow prices) de las restricciones
        
        El precio sombra indica cuánto aumentaría el beneficio si se
        incrementara en una unidad el recurso disponible
        """
        shadow_prices = []
        
        epsilon = 1.0  # Incremento marginal
        base_profit = -self.objective_function(quantities)
        
        for i, constraint in enumerate(self.resource_constraints):
            # Incrementar recurso temporalmente
            original_available = constraint.total_available
            constraint.total_available += epsilon
            
            # Re-optimizar
            temp_result = self.optimize_linear_programming()
            
            if temp_result["success"]:
                new_profit = temp_result["optimal_profit"]
                shadow_price = (new_profit - base_profit) / epsilon
            else:
                shadow_price = 0
            
            # Restaurar
            constraint.total_available = original_available
            
            shadow_prices.append({
                "constraint": constraint.name,
                "shadow_price": shadow_price,
                "interpretation": (
                    f"Beneficio aumentaría en ${shadow_price:.2f} "
                    f"por cada unidad adicional de {constraint.name}"
                )
            })
        
        return shadow_prices
    
    def _sensitivity_ranges(self, quantities: np.ndarray) -> Dict[str, any]:
        """Análisis de sensibilidad de coeficientes"""
        return {
            "note": "Rangos de sensibilidad para coeficientes de función objetivo",
            "products": [
                {
                    "product": p.name,
                    "current_contribution_margin": p.contribution_margin,
                    "quantity_in_solution": qty
                }
                for p, qty in zip(self.products, quantities)
            ]
        }
    
    def plot_2d_optimization(
        self,
        save_path: Optional[str] = None,
        show_plot: bool = False
    ) -> None:
        """
        Visualización 2D del problema de optimización (solo para 2 productos)
        """
        if self.n_products != 2:
            print("⚠️  La visualización 2D solo funciona con 2 productos")
            return
        
        # Obtener solución óptima
        solution = self.optimize_linear_programming()
        if not solution["success"]:
            print("❌ No se pudo encontrar solución óptima")
            return
        
        optimal_x, optimal_y = solution["optimal_quantities"]
        
        # Crear grid
        x_max = self.demand_constraints.max_demand[0] if self.demand_constraints.max_demand else optimal_x * 2
        y_max = self.demand_constraints.max_demand[1] if len(self.demand_constraints.max_demand) > 1 else optimal_y * 2
        
        x = np.linspace(0, x_max * 1.2, 300)
        y = np.linspace(0, y_max * 1.2, 300)
        X, Y = np.meshgrid(x, y)
        
        # Calcular función objetivo en el grid
        Z = np.zeros_like(X)
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                Z[i, j] = -self.objective_function(np.array([X[i, j], Y[i, j]]))
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Contornos de la función objetivo
        contour = ax.contour(X, Y, Z, levels=15, cmap='viridis', alpha=0.6)
        ax.clabel(contour, inline=True, fontsize=8)
        
        # Restricciones
        colors = ['red', 'blue', 'green', 'orange']
        for i, constraint in enumerate(self.resource_constraints):
            a, b = constraint.consumption_rates
            available = constraint.total_available
            
            # Línea de la restricción: a*x + b*y = available
            if b != 0:
                y_constraint = (available - a * x) / b
                ax.plot(x, y_constraint, color=colors[i % len(colors)], 
                       linewidth=2, label=f'{constraint.name}: {a}x + {b}y ≤ {available}')
                ax.fill_between(x, 0, y_constraint, where=(y_constraint >= 0), 
                               alpha=0.1, color=colors[i % len(colors)])
        
        # Punto óptimo
        ax.plot(optimal_x, optimal_y, 'r*', markersize=20, 
               label=f'Óptimo: ({optimal_x:.0f}, {optimal_y:.0f})')
        
        ax.set_xlabel(f'{self.products[0].name} (unidades)', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'{self.products[1].name} (unidades)', fontsize=12, fontweight='bold')
        ax.set_title('Optimización de Mix de Productos\nFunción Objetivo y Restricciones', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, x_max * 1.2)
        ax.set_ylim(0, y_max * 1.2)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ Gráfico guardado: {save_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()


if __name__ == "__main__":
    print("=" * 70)
    print("OPERATIONS OPTIMIZER - Ejemplo de Optimización")
    print("=" * 70)
    
    # Definir productos
    producto_a = Product(
        name="Apartamento Tipo A",
        unit_price=4_500_000,  # $4.5M CLP
        variable_cost=2_800_000  # $2.8M CLP
    )
    
    producto_b = Product(
        name="Apartamento Tipo B",
        unit_price=6_000_000,  # $6M CLP
        variable_cost=3_500_000  # $3.5M CLP
    )
    
    # Restricciones de recursos
    constraint_area = ResourceConstraint(
        name="Área Total Construible (m²)",
        total_available=15_000,
        consumption_rates=[45, 65]  # m² por unidad tipo A y B
    )
    
    constraint_budget = ResourceConstraint(
        name="Presupuesto de Construcción (M$)",
        total_available=300_000_000,
        consumption_rates=[2_800_000, 3_500_000]
    )
    
    # Restricciones de demanda
    demand = DemandConstraint(
        min_demand=[20, 15],
        max_demand=[200, 150]
    )
    
    # Crear optimizador
    optimizer = OperationsOptimizer(
        products=[producto_a, producto_b],
        resource_constraints=[constraint_area, constraint_budget],
        demand_constraints=demand,
        fixed_costs=50_000_000  # $50M costos fijos
    )
    
    # Optimizar
    print("\n🔍 Optimizando mix de productos...")
    solution = optimizer.optimize_linear_programming()
    
    if solution["success"]:
        print(f"\n✅ SOLUCIÓN ÓPTIMA ENCONTRADA")
        print(f"\n📊 Cantidades Óptimas:")
        for product, qty in zip(solution["products"], solution["optimal_quantities"]):
            print(f"   {product}: {qty:.0f} unidades")
        
        print(f"\n💰 Beneficio Óptimo: ${solution['optimal_profit']:,.0f}")
        
        breakdown = solution["detailed_breakdown"]
        print(f"\n📈 Resumen Financiero:")
        print(f"   Ingresos Totales:         ${breakdown['summary']['total_revenue']:,.0f}")
        print(f"   Costos Variables:         ${breakdown['summary']['total_variable_costs']:,.0f}")
        print(f"   Margen de Contribución:   ${breakdown['summary']['total_contribution_margin']:,.0f}")
        print(f"   Costos Fijos:             ${breakdown['summary']['fixed_costs']:,.0f}")
        print(f"   EBIT:                     ${breakdown['summary']['ebit']:,.0f}")
        
        print(f"\n🔧 Análisis de Restricciones:")
        for constraint in breakdown["constraints"]:
            status = "🔴 ACTIVA" if constraint["is_binding"] else "🟢 Holgura"
            print(f"   {constraint['constraint']}: {constraint['utilization_percentage']:.1f}% usado {status}")
        
        # Visualizar
        optimizer.plot_2d_optimization(save_path="optimization_plot.png")
    
    print("\n" + "=" * 70)
