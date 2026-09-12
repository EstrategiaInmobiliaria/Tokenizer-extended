"""
Operations Optimizer - Optimización de Mix de Productos y Operaciones
Módulo de Optimización Matemática con Restricciones

Este módulo implementa dos enfoques complementarios:
1. Solución analítica determinista para el modelo cuadrático cerrado
2. Optimización numérica con restricciones para casos generales

═══════════════════════════════════════════════════════════════════════════
MODELO MATEMÁTICO CERRADO (Capítulo 3 de Tesis)
═══════════════════════════════════════════════════════════════════════════

Función Objetivo Cuadrática con Rendimientos Marginales Decrecientes:
    f(x, y) = 152x + 80y - 2x² - y² - xy

Interpretación de Coeficientes:
- 152x, 80y: Margen de contribución bruto
- -2x², -y²: Rendimientos marginales decrecientes (saturación)
- -xy: Efecto de canibalización entre tipos

Condiciones de Primer Orden (∇f = 0):
    ∂f/∂x = 152 - 4x - y = 0  →  4x + y = 152
    ∂f/∂y = 80 - 2y - x = 0   →  x + 2y = 80

Sistema Lineal: Ax = b
    [4  1] [x]   [152]
    [1  2] [y] = [80]

Solución Analítica:
    x* = 32 unidades comerciales
    y* = 24 unidades residenciales
    f(x*, y*) = 3,392 (beneficio máximo)

Matriz Hessiana (Condiciones de Segundo Orden):
    H = [-4  -1]
        [-1  -2]
    
    det(H) = 7 > 0, H₁ = -4 < 0  →  H es negativa definida
    ∴ (32, 24) es un MÁXIMO GLOBAL ESTRICTO

Eigenvalores de H: λ₁ ≈ -5.236, λ₂ ≈ -0.764 (ambos negativos)

═══════════════════════════════════════════════════════════════════════════
MODELO GENERAL CON RESTRICCIONES
═══════════════════════════════════════════════════════════════════════════

Función Objetivo (forma general):
    f(x, y) = Px·x + Py·y - Cx·x - Cy·y

Restricciones:
    g₁(x, y) = a₁x + b₁y ≤ R₁  (Recurso 1)
    g₂(x, y) = a₂x + b₂y ≤ R₂  (Recurso 2)
    x ≥ 0, y ≥ 0  (No negatividad)

Condiciones KKT:
    ∇f(x*) + Σ λᵢ∇gᵢ(x*) = 0     (Estacionariedad)
    gᵢ(x*) ≤ 0, ∀i               (Factibilidad primal)
    λᵢ ≥ 0, ∀i                   (Factibilidad dual)
    λᵢ·gᵢ(x*) = 0, ∀i            (Holgura complementaria)

Interpretación de λᵢ (Precio Sombra):
    λᵢ = ∂f*/∂bᵢ = Incremento en f* por relajar restricción i en 1 unidad
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
import numpy as np
from scipy.optimize import minimize, linprog, NonlinearConstraint
import matplotlib.pyplot as plt


# ═══════════════════════════════════════════════════════════════════════════
# CLASE 1: SOLUCIÓN ANALÍTICA DETERMINISTA (Modelo Matemático Cerrado)
# ═══════════════════════════════════════════════════════════════════════════

class MathematicalOptimizerCore:
    """
    Implementación determinista del problema de optimización cuadrático cerrado.
    
    Función objetivo:
        f(x, y) = 152x + 80y - 2x² - y² - xy
    
    Solución analítica mediante resolución del sistema lineal derivado de ∇f = 0:
        Sistema: Ax = b
        Donde: A = [[4, 1], [1, 2]], b = [152, 80]
        Solución: (x*, y*) = (32, 24)
    
    Este enfoque garantiza:
    - Solución exacta (no iterativa)
    - Tiempo constante O(1) para problema 2x2
    - Reproducibilidad perfecta
    - Validez matemática verificable
    """
    
    def __init__(self):
        # Matriz del sistema Ax = b derivada del gradiente ∇f = 0
        self.A = np.array([
            [4.0, 1.0],   # Coeficientes de ∂f/∂x = 152 - 4x - y = 0
            [1.0, 2.0]    # Coeficientes de ∂f/∂y = 80 - 2y - x = 0
        ], dtype=np.float64)
        
        self.b = np.array([152.0, 80.0], dtype=np.float64)
        
        # Matriz Hessiana (constante para función cuadrática)
        self.H = np.array([
            [-4.0, -1.0],
            [-1.0, -2.0]
        ], dtype=np.float64)
        
        # Coeficientes de la función objetivo f(x, y) = c₁x + c₂y + c₃x² + c₄y² + c₅xy
        self.coef = {
            'linear_x': 152.0,
            'linear_y': 80.0,
            'quadratic_x': -2.0,
            'quadratic_y': -1.0,
            'interaction': -1.0
        }
    
    def solve_analytical(self) -> Tuple[float, float]:
        """
        Resuelve el sistema lineal Ax = b para obtener el punto crítico.
        
        Método: Eliminación Gaussiana (np.linalg.solve)
        Complejidad: O(n³) → O(1) para n=2
        
        Returns:
            (x*, y*): Punto crítico (candidato a óptimo)
        """
        try:
            solution = np.linalg.solve(self.A, self.b)
            return float(solution[0]), float(solution[1])
        except np.linalg.LinAlgError as e:
            raise ValueError(f"Sistema singular o mal condicionado: {e}")
    
    def objective_function(self, x: float, y: float) -> float:
        """
        Evalúa la función objetivo en (x, y).
        
        f(x, y) = 152x + 80y - 2x² - y² - xy
        
        Args:
            x: Cantidad de unidades comerciales
            y: Cantidad de unidades residenciales
        
        Returns:
            Valor de la función objetivo (beneficio operativo)
        """
        c = self.coef
        return (c['linear_x'] * x + 
                c['linear_y'] * y + 
                c['quadratic_x'] * x**2 + 
                c['quadratic_y'] * y**2 + 
                c['interaction'] * x * y)
    
    def gradient(self, x: float, y: float) -> np.ndarray:
        """
        Calcula el gradiente ∇f en (x, y).
        
        ∇f = [∂f/∂x, ∂f/∂y]
        
        ∂f/∂x = 152 - 4x - y
        ∂f/∂y = 80 - 2y - x
        
        Args:
            x, y: Punto de evaluación
        
        Returns:
            Vector gradiente [grad_x, grad_y]
        """
        grad_x = self.coef['linear_x'] + 2 * self.coef['quadratic_x'] * x + self.coef['interaction'] * y
        grad_y = self.coef['linear_y'] + 2 * self.coef['quadratic_y'] * y + self.coef['interaction'] * x
        return np.array([grad_x, grad_y])
    
    def check_optimality(self) -> Dict[str, any]:
        """
        Verifica condiciones de optimalidad de segundo orden mediante análisis de Hessiana.
        
        Criterio de Sylvester para Máximo:
        - H₁ = H[0,0] < 0
        - det(H) > 0
        
        Returns:
            Dict con análisis completo de la matriz Hessiana
        """
        # Menores principales
        H1 = self.H[0, 0]  # Primer menor principal
        det_H = np.linalg.det(self.H)  # Determinante
        
        # Eigenvalores (verificación alternativa de definitud)
        eigenvalues = np.linalg.eigvals(self.H)
        
        # Clasificación según criterio de Sylvester
        is_negative_definite = (H1 < 0) and (det_H > 0)
        
        # Verificación adicional: todos los eigenvalores negativos
        all_eigenvalues_negative = np.all(eigenvalues < 0)
        
        return {
            "first_principal_minor_H1": float(H1),
            "determinant": float(det_H),
            "eigenvalues": eigenvalues.tolist(),
            "is_negative_definite": bool(is_negative_definite),
            "all_eigenvalues_negative": bool(all_eigenvalues_negative),
            "classification": "MÁXIMO GLOBAL" if is_negative_definite else "NO ES MÁXIMO",
            "curvature": {
                "along_x": float(self.H[0, 0]),  # Curvatura en dirección x
                "along_y": float(self.H[1, 1]),  # Curvatura en dirección y
                "interaction": float(self.H[0, 1])  # Curvatura mixta
            }
        }
    
    def get_complete_solution(self) -> Dict[str, any]:
        """
        Retorna solución completa con verificación de optimalidad.
        
        Este método encapsula todo el análisis matemático:
        1. Resolución del sistema (punto crítico)
        2. Evaluación de la función objetivo
        3. Verificación del gradiente (debe ser ~0)
        4. Análisis de la Hessiana (condiciones de segundo orden)
        5. Interpretación en lenguaje natural
        
        Returns:
            Dict con solución completa y análisis
        """
        # Paso 1: Resolver sistema lineal ∇f = 0
        x_opt, y_opt = self.solve_analytical()
        
        # Paso 2: Evaluar función objetivo en el punto crítico
        f_opt = self.objective_function(x_opt, y_opt)
        
        # Paso 3: Verificar que el gradiente es nulo (condición necesaria)
        grad_at_opt = self.gradient(x_opt, y_opt)
        grad_norm = np.linalg.norm(grad_at_opt)
        
        # Paso 4: Análisis de Hessiana (condición suficiente)
        optimality = self.check_optimality()
        
        # Paso 5: Construcción del resultado
        return {
            "status": "success",
            "method": "Analytical (Direct Linear System Solution)",
            "optimal_solution": {
                "x_commercial_units": round(x_opt, 4),
                "y_residential_units": round(y_opt, 4),
                "total_units": round(x_opt + y_opt, 4)
            },
            "optimal_objective_value": round(f_opt, 4),
            "first_order_conditions": {
                "gradient_at_optimum": {
                    "partial_x": round(grad_at_opt[0], 8),
                    "partial_y": round(grad_at_opt[1], 8),
                    "norm": round(grad_norm, 8)
                },
                "satisfies_FOC": grad_norm < 1e-6,
                "interpretation": "∇f = 0 verificado" if grad_norm < 1e-6 else "⚠️ Gradiente no nulo"
            },
            "second_order_conditions": optimality,
            "mathematical_guarantee": (
                "Máximo global estricto garantizado por Hessiana negativa definida"
                if optimality["is_negative_definite"]
                else "El punto crítico no es un máximo"
            ),
            "interpretation": self._generate_interpretation(x_opt, y_opt, f_opt, optimality)
        }
    
    def _generate_interpretation(self, x: float, y: float, f_val: float, opt_analysis: Dict) -> str:
        """
        Genera interpretación en lenguaje natural del resultado.
        
        Args:
            x, y: Coordenadas del óptimo
            f_val: Valor de la función objetivo
            opt_analysis: Análisis de optimalidad
        
        Returns:
            String con interpretación para stakeholders no técnicos
        """
        if opt_analysis["is_negative_definite"]:
            return (
                f"✅ SOLUCIÓN ÓPTIMA VERIFICADA MATEMÁTICAMENTE:\n"
                f"   • Mix óptimo: {x:.0f} unidades comerciales + {y:.0f} unidades residenciales\n"
                f"   • Beneficio operativo máximo: ${f_val:,.2f}\n"
                f"   • Garantía: La matriz Hessiana negativa definida (det H = {opt_analysis['determinant']:.2f}) "
                f"asegura que este es un máximo global estricto.\n"
                f"   • Interpretación: Cualquier desviación del mix ({x:.0f}, {y:.0f}) reduce el beneficio."
            )
        else:
            return (
                f"⚠️ ADVERTENCIA: El punto crítico ({x:.0f}, {y:.0f}) NO es un máximo.\n"
                f"   • Revisar la formulación del problema o las restricciones."
            )


# ═══════════════════════════════════════════════════════════════════════════
# CLASE 2: DEFINICIONES DE DATOS (para modelo general con restricciones)
# ═══════════════════════════════════════════════════════════════════════════


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
    print("=" * 80)
    print("OPERATIONS OPTIMIZER - Dos Enfoques de Solución")
    print("=" * 80)
    
    # =========================================================================
    # ENFOQUE 1: SOLUCIÓN ANALÍTICA DETERMINISTA (Modelo Matemático Cerrado)
    # =========================================================================
    print("\n" + "─" * 80)
    print("ENFOQUE 1: SOLUCIÓN ANALÍTICA DETERMINISTA")
    print("Modelo: f(x, y) = 152x + 80y - 2x² - y² - xy")
    print("─" * 80)
    
    math_optimizer = MathematicalOptimizerCore()
    solution_analytical = math_optimizer.get_complete_solution()
    
    print(f"\n📊 SOLUCIÓN ÓPTIMA:")
    opt_sol = solution_analytical['optimal_solution']
    print(f"   x* (Comerciales):  {opt_sol['x_commercial_units']} unidades")
    print(f"   y* (Residenciales): {opt_sol['y_residential_units']} unidades")
    print(f"   Total:             {opt_sol['total_units']} unidades")
    print(f"   Beneficio Máximo:  ${solution_analytical['optimal_objective_value']:,.2f}")
    
    print(f"\n∇f VERIFICACIÓN (Condiciones de Primer Orden):")
    foc = solution_analytical['first_order_conditions']
    print(f"   ∂f/∂x = {foc['gradient_at_optimum']['partial_x']}")
    print(f"   ∂f/∂y = {foc['gradient_at_optimum']['partial_y']}")
    print(f"   ||∇f|| = {foc['gradient_at_optimum']['norm']}")
    print(f"   ✓ {foc['interpretation']}")
    
    print(f"\n🔍 ANÁLISIS DE SEGUNDO ORDEN (Matriz Hessiana):")
    hess = solution_analytical['second_order_conditions']
    print(f"   Matriz H = [[-4, -1], [-1, -2]]")
    print(f"   H₁ (Primer menor):  {hess['first_principal_minor_H1']}")
    print(f"   det(H):             {hess['determinant']}")
    print(f"   Eigenvalores:       {[f'{ev:.4f}' for ev in hess['eigenvalues']]}")
    print(f"   Negativa Definida:  {hess['is_negative_definite']}")
    print(f"   → {hess['classification']}")
    
    print(f"\n💡 INTERPRETACIÓN:")
    for line in solution_analytical['interpretation'].split('\n'):
        print(f"   {line}")
    
    print(f"\n🎓 GARANTÍA MATEMÁTICA:")
    print(f"   {solution_analytical['mathematical_guarantee']}")
    
    # =========================================================================
    # ENFOQUE 2: OPTIMIZACIÓN CON RESTRICCIONES (Caso General)
    # =========================================================================
    print("\n" + "─" * 80)
    print("ENFOQUE 2: OPTIMIZACIÓN CON RESTRICCIONES (Programación Lineal)")
    print("Caso: Mix con restricciones de área y presupuesto")
    print("─" * 80)
    
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
            status = "🔴 ACTIVA (Limitante)" if constraint["is_binding"] else "🟢 Con holgura"
            print(f"   {constraint['constraint']}:")
            print(f"      Utilización: {constraint['utilization_percentage']:.1f}% - {status}")
            if constraint["is_binding"]:
                print(f"      → Esta restricción limita la solución (precio sombra > 0)")
        
        # Visualizar (solo para 2 productos)
        print(f"\n📊 Generando visualización...")
        optimizer.plot_2d_optimization(save_path="/workspace/master_blueprint/optimization_2d.png")
    
    print("\n" + "=" * 80)
    print("Nota: El Enfoque 1 (analítico) es exacto y eficiente para el modelo cerrado.")
    print("      El Enfoque 2 (numérico) es flexible y maneja restricciones complejas.")
    print("=" * 80)
