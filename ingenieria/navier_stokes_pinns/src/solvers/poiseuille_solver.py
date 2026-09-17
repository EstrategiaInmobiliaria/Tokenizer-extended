"""
Solver PINN para flujo de Poiseuille usando DeepXDE.

Caso: Flujo laminar entre placas paralelas con solución analítica conocida.
"""

import deepxde as dde
import numpy as np
from typing import Tuple, Optional


class PoiseuilleFlowPINN:
    """
    Physics-Informed Neural Network para flujo de Poiseuille 2D.
    
    Ecuación diferencial:
        μ * d²u/dy² = dp/dx  (constante)
    
    Condiciones de frontera:
        u(y = -H) = 0  (no-slip pared inferior)
        u(y = +H) = 0  (no-slip pared superior)
    
    Solución analítica:
        u(y) = -1/(2μ) * dp/dx * (H² - y²)
    """
    
    def __init__(
        self,
        H: float = 0.5,
        L: float = 2.0,
        dp_dx: float = -1.0,
        mu: float = 0.01,
        rho: float = 1.0
    ):
        """
        Args:
            H: Medio ancho del canal [m]
            L: Longitud del canal [m]
            dp_dx: Gradiente de presión [Pa/m]
            mu: Viscosidad dinámica [Pa·s]
            rho: Densidad [kg/m³]
        """
        self.H = H
        self.L = L
        self.dp_dx = dp_dx
        self.mu = mu
        self.rho = rho
        self.nu = mu / rho  # Viscosidad cinemática
        
        self.model = None
        self.geom = None
        
    def pde(self, x, u):
        """
        Define la ecuación diferencial parcial.
        
        Para Poiseuille 2D estacionario:
            μ * ∂²u/∂y² = dp/dx
        
        Args:
            x: Coordenadas [x, y]
            u: Velocidad u(x, y)
        
        Returns:
            Residuo de la ecuación
        """
        du_dy = dde.grad.jacobian(u, x, i=0, j=1)  # ∂u/∂y
        du_dyy = dde.grad.hessian(u, x, i=1, j=1)  # ∂²u/∂y²
        
        # Ecuación de Poiseuille
        residual = self.mu * du_dyy - self.dp_dx
        
        return residual
    
    def boundary_condition_bottom(self, x, on_boundary):
        """Condición de frontera: y = -H (pared inferior)"""
        return on_boundary and np.isclose(x[1], -self.H)
    
    def boundary_condition_top(self, x, on_boundary):
        """Condición de frontera: y = +H (pared superior)"""
        return on_boundary and np.isclose(x[1], self.H)
    
    def build_model(
        self,
        num_domain: int = 2000,
        num_boundary: int = 200,
        layer_size: list = [2, 50, 50, 50, 1],
        activation: str = "tanh"
    ):
        """
        Construye el modelo PINN.
        
        Args:
            num_domain: Número de puntos de colocación en el dominio
            num_boundary: Número de puntos en las fronteras
            layer_size: Arquitectura de la red [input, hidden..., output]
            activation: Función de activación
        """
        # Definir geometría del dominio
        self.geom = dde.geometry.Rectangle([0, -self.H], [self.L, self.H])
        
        # Condiciones de frontera (no-slip)
        bc_bottom = dde.icbc.DirichletBC(
            self.geom, lambda x: 0, self.boundary_condition_bottom
        )
        bc_top = dde.icbc.DirichletBC(
            self.geom, lambda x: 0, self.boundary_condition_top
        )
        
        # Definir el problema
        data = dde.data.PDE(
            self.geom,
            self.pde,
            [bc_bottom, bc_top],
            num_domain=num_domain,
            num_boundary=num_boundary,
            num_test=500
        )
        
        # Crear red neuronal
        net = dde.nn.FNN(layer_size, activation, "Glorot uniform")
        
        # Modelo completo
        self.model = dde.Model(data, net)
        
        return self.model
    
    def train(
        self,
        iterations: int = 10000,
        learning_rate: float = 1e-3,
        display_every: int = 1000
    ):
        """
        Entrena el modelo PINN.
        
        Args:
            iterations: Número de iteraciones
            learning_rate: Tasa de aprendizaje
            display_every: Frecuencia de impresión
        """
        # Compilar modelo
        self.model.compile(
            "adam",
            lr=learning_rate,
            metrics=["l2 relative error"]
        )
        
        # Entrenar
        losshistory, train_state = self.model.train(
            iterations=iterations,
            display_every=display_every
        )
        
        # Afinamiento con L-BFGS
        self.model.compile("L-BFGS")
        losshistory, train_state = self.model.train()
        
        return losshistory, train_state
    
    def predict(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        """
        Predice velocidad en puntos dados.
        
        Args:
            X, Y: Mallas de coordenadas
        
        Returns:
            Velocidad u predicha
        """
        points = np.column_stack([X.flatten(), Y.flatten()])
        u_pred = self.model.predict(points)
        return u_pred.reshape(X.shape)
    
    def analytical_solution(self, y: np.ndarray) -> np.ndarray:
        """
        Calcula solución analítica.
        
        Args:
            y: Coordenadas verticales
        
        Returns:
            Velocidad u exacta
        """
        return -self.dp_dx / (2 * self.mu) * (self.H**2 - y**2)
    
    def compute_max_velocity(self) -> float:
        """Calcula velocidad máxima (en el centro del canal)."""
        return -self.dp_dx * self.H**2 / (2 * self.mu)
    
    def compute_reynolds_number(self) -> float:
        """Calcula número de Reynolds basado en velocidad máxima y medio ancho."""
        u_max = self.compute_max_velocity()
        return self.rho * u_max * self.H / self.mu


def run_poiseuille_example():
    """
    Ejecuta ejemplo completo de flujo de Poiseuille.
    """
    print("=" * 60)
    print("FLUJO DE POISEUILLE CON PINN")
    print("=" * 60)
    
    # Crear solver
    solver = PoiseuilleFlowPINN(
        H=0.5,
        L=2.0,
        dp_dx=-1.0,
        mu=0.01,
        rho=1.0
    )
    
    # Info
    print(f"Parámetros:")
    print(f"  Medio ancho del canal: H = {solver.H} m")
    print(f"  Longitud: L = {solver.L} m")
    print(f"  Gradiente de presión: dp/dx = {solver.dp_dx} Pa/m")
    print(f"  Viscosidad dinámica: μ = {solver.mu} Pa·s")
    print(f"  Velocidad máxima (analítica): {solver.compute_max_velocity():.4f} m/s")
    print(f"  Número de Reynolds: Re = {solver.compute_reynolds_number():.2f}")
    print()
    
    # Construir modelo
    print("Construyendo modelo PINN...")
    solver.build_model(
        num_domain=2000,
        num_boundary=200,
        layer_size=[2, 50, 50, 50, 1]
    )
    
    # Entrenar
    print("Entrenando...")
    losshistory, train_state = solver.train(iterations=10000)
    
    # Evaluar
    print("\nEvaluando solución...")
    x = np.linspace(0, solver.L, 100)
    y = np.linspace(-solver.H, solver.H, 100)
    X, Y = np.meshgrid(x, y)
    
    u_pred = solver.predict(X, Y)
    
    # Comparar con analítico en x = L/2
    y_line = np.linspace(-solver.H, solver.H, 100)
    u_analytical = solver.analytical_solution(y_line)
    u_pred_line = solver.predict(
        np.full_like(y_line, solver.L/2),
        y_line
    )
    
    # Error
    l2_error = np.linalg.norm(u_pred_line - u_analytical) / np.linalg.norm(u_analytical)
    print(f"Error L2 relativo: {l2_error*100:.4f}%")
    
    return solver, X, Y, u_pred


if __name__ == "__main__":
    solver, X, Y, u_pred = run_poiseuille_example()
