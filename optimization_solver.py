"""
Optimization Solver for Commercial-Residential Mix Problem

This module solves a constrained optimization problem to find the optimal mix
of commercial (x) and residential (y) products/services that maximizes operating benefit.

Objective Function: max 152x + 80y - 2x² - y² - xy
Subject to constraints defined by the linear system Ax = b
"""

import numpy as np
from typing import Dict, Tuple, Optional


class OperationsOptimizer:
    """
    Solver for the optimal commercial-residential mix problem.
    
    The problem maximizes: f(x,y) = 152x + 80y - 2x² - y² - xy
    Subject to: Ax = b (linear constraints from gradient = 0)
                x ≥ 0, y ≥ 0 (non-negativity constraints)
    
    Attributes:
        A: Coefficient matrix for linear constraints (gradient system)
        b: Right-hand side vector for linear constraints
    """
    
    def __init__(self):
        """
        Initialize the solver with the standard gradient system.
        
        The gradient of f(x,y) = 152x + 80y - 2x² - y² - xy is:
        ∇f = [152 - 4x - y, 80 - 2y - x]
        
        Setting ∇f = 0 gives the linear system:
        4x + y = 152
        x + 2y = 80
        """
        # Coeficientes del sistema lineal para el gradiente igualado a cero
        self.A = np.array([[4.0, 1.0], [1.0, 2.0]])
        self.b = np.array([152.0, 80.0])
    
    def _objective_function(self, x: float, y: float) -> float:
        """Calculate the objective function value."""
        return 152*x + 80*y - 2*x**2 - y**2 - x*y
    
    def _gradient(self, x: float, y: float) -> np.ndarray:
        """
        Calculate the gradient of the objective function.
        
        ∇f(x,y) = [∂f/∂x, ∂f/∂y] = [152 - 4x - y, 80 - 2y - x]
        """
        return np.array([152 - 4*x - y, 80 - 2*y - x])
    
    def _hessian(self) -> np.ndarray:
        """
        Calculate the Hessian matrix of the objective function.
        
        H = [∂²f/∂x²    ∂²f/∂x∂y]   [-4  -1]
            [∂²f/∂y∂x   ∂²f/∂y²] = [-1  -2]
        """
        return np.array([[-4, -1], [-1, -2]])
    
    def _is_maximum(self, x: float, y: float, gradient_tolerance: float = 1e-6) -> Tuple[bool, str]:
        """
        Verify if the critical point is a maximum using second-order conditions.
        
        Args:
            x: x-coordinate of the critical point
            y: y-coordinate of the critical point
            gradient_tolerance: Tolerance for gradient norm to be considered zero
            
        Returns:
            Tuple of (is_maximum, reason)
        """
        grad = self._gradient(x, y)
        grad_norm = np.linalg.norm(grad)
        
        # Check if it's a critical point (gradient ≈ 0)
        if grad_norm > gradient_tolerance:
            return False, f"Not a critical point (gradient norm = {grad_norm:.6f})"
        
        # Check second-order conditions using the Hessian
        H = self._hessian()
        
        # For a maximum, the Hessian must be negative definite
        # This requires: H11 < 0 and det(H) > 0
        det_H = np.linalg.det(H)
        H11 = H[0, 0]
        
        if H11 < 0 and det_H > 0:
            return True, "Hessian is negative definite (local maximum)"
        elif H11 > 0 and det_H > 0:
            return False, "Hessian is positive definite (local minimum)"
        elif det_H < 0:
            return False, "Hessian has mixed signs (saddle point)"
        else:
            return False, "Inconclusive second-order test"
    
    def solve_optimal_mix(self, gradient_tolerance: float = 1e-6) -> dict:
        """
        Resuelve el sistema, valida el dominio no negativo y calcula la norma del gradiente.
        
        Mejoras sobre la versión original:
        - Valida que la matriz no sea singular
        - Verifica matemáticamente si es un máximo usando el Hessiano
        - Proporciona información detallada sobre la verificación
        
        Args:
            gradient_tolerance: Tolerancia para considerar el gradiente como cero
            
        Returns:
            Dictionary containing:
                - status: "success", "infeasible", or "error"
                - optimal_mix: Dictionary with x_commercial and y_residential (if successful)
                - max_operating_benefit: Maximum profit value (if successful)
                - gradient_norm: Norm of gradient at solution (if successful)
                - is_global_maximum: Whether the solution is verified as a maximum (if successful)
                - verification_details: Explanation of the verification result (if successful)
                - msg: Error or status message (if not successful)
        """
        try:
            # Check if matrix is singular (prevents crashes)
            det_A = np.linalg.det(self.A)
            if abs(det_A) < 1e-10:
                return {
                    "status": "error",
                    "msg": f"Matrix A is singular or nearly singular (det = {det_A:.2e})"
                }
            
            # Solve the linear system
            optimal_vars = np.linalg.solve(self.A, self.b)
            x, y = optimal_vars
            
            # Check non-negativity constraints (dominio operativo)
            if x < 0 or y < 0:
                return {
                    "status": "infeasible",
                    "msg": "Solución fuera de dominio operativo"
                }
            
            # Calculate gradient and profit
            grad = np.array([152 - 4 * x - y, 80 - 2 * y - x])
            max_profit = 152 * x + 80 * y - 2 * x**2 - y**2 - x * y
            
            # Verify if it's actually a maximum using second-order conditions
            is_maximum, verification_msg = self._is_maximum(x, y, gradient_tolerance)
            
            return {
                "status": "success",
                "optimal_mix": {
                    "x_commercial": round(float(x), 2),
                    "y_residential": round(float(y), 2)
                },
                "max_operating_benefit": round(float(max_profit), 2),
                "gradient_norm": float(np.linalg.norm(grad)),
                "is_global_maximum": is_maximum,
                "verification_details": verification_msg
            }
            
        except Exception as e:
            return {"status": "error", "msg": str(e)}


def example_usage():
    """Example usage of the OperationsOptimizer."""
    # The optimizer solves the system where the gradient equals zero:
    # ∇f = 0 => [152 - 4x - y = 0]  =>  [4  1][x]   [152]
    #           [80 - 2y - x = 0]       [1  2][y] = [80]
    
    optimizer = OperationsOptimizer()
    result = optimizer.solve_optimal_mix()
    
    print("Optimization Result:")
    print("=" * 50)
    for key, value in result.items():
        print(f"{key}: {value}")
    
    return result


if __name__ == "__main__":
    print(example_usage())
