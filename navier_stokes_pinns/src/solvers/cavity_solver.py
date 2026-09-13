"""
Solver PINN para Lid-Driven Cavity Flow usando DeepXDE.

Caso clásico: cavidad cuadrada con tapa móvil.
"""

import deepxde as dde
import numpy as np
from typing import Tuple


class LidDrivenCavityPINN:
    """
    Physics-Informed Neural Network para Lid-Driven Cavity Flow.
    
    Ecuaciones de Navier-Stokes 2D estacionarias:
        u·∂u/∂x + v·∂u/∂y = -1/ρ·∂p/∂x + ν·(∂²u/∂x² + ∂²u/∂y²)
        u·∂v/∂x + v·∂v/∂y = -1/ρ·∂p/∂y + ν·(∂²v/∂x² + ∂²v/∂y²)
        ∂u/∂x + ∂v/∂y = 0  (incompresibilidad)
    
    Condiciones de frontera:
        Top (y=1): u = U_lid, v = 0
        Otros lados: u = 0, v = 0 (no-slip)
    """
    
    def __init__(
        self,
        L: float = 1.0,
        U_lid: float = 1.0,
        Re: float = 100.0
    ):
        """
        Args:
            L: Lado de la cavidad [m]
            U_lid: Velocidad de la tapa [m/s]
            Re: Número de Reynolds
        """
        self.L = L
        self.U_lid = U_lid
        self.Re = Re
        self.nu = U_lid * L / Re  # Viscosidad cinemática
        
        self.model = None
        self.geom = None
        
    def navier_stokes(self, x, y):
        """
        Sistema de ecuaciones de Navier-Stokes.
        
        Args:
            x: Coordenadas [x, y]
            y: Salidas de la red [u, v, p]
        
        Returns:
            Residuos [continuidad, momento_x, momento_y]
        """
        u = y[:, 0:1]
        v = y[:, 1:2]
        p = y[:, 2:3]
        
        # Derivadas de u
        u_x = dde.grad.jacobian(y, x, i=0, j=0)
        u_y = dde.grad.jacobian(y, x, i=0, j=1)
        u_xx = dde.grad.hessian(y, x, component=0, i=0, j=0)
        u_yy = dde.grad.hessian(y, x, component=0, i=1, j=1)
        
        # Derivadas de v
        v_x = dde.grad.jacobian(y, x, i=1, j=0)
        v_y = dde.grad.jacobian(y, x, i=1, j=1)
        v_xx = dde.grad.hessian(y, x, component=1, i=0, j=0)
        v_yy = dde.grad.hessian(y, x, component=1, i=1, j=1)
        
        # Derivadas de presión
        p_x = dde.grad.jacobian(y, x, i=2, j=0)
        p_y = dde.grad.jacobian(y, x, i=2, j=1)
        
        # Ecuación de continuidad
        continuity = u_x + v_y
        
        # Ecuación de momento en x
        momentum_x = u * u_x + v * u_y + p_x - self.nu * (u_xx + u_yy)
        
        # Ecuación de momento en y
        momentum_y = u * v_x + v * v_y + p_y - self.nu * (v_xx + v_yy)
        
        return [continuity, momentum_x, momentum_y]
    
    def boundary_wall(self, x, on_boundary):
        """Paredes laterales e inferior (u=0, v=0)"""
        return on_boundary and not np.isclose(x[1], self.L)
    
    def boundary_lid(self, x, on_boundary):
        """Tapa superior (u=U_lid, v=0)"""
        return on_boundary and np.isclose(x[1], self.L)
    
    def build_model(
        self,
        num_domain: int = 5000,
        num_boundary: int = 400,
        layer_size: list = [2, 50, 50, 50, 50, 3],
        activation: str = "tanh"
    ):
        """
        Construye el modelo PINN.
        
        Args:
            num_domain: Puntos de colocación en el dominio
            num_boundary: Puntos en fronteras
            layer_size: Arquitectura [input, hidden..., output]
            activation: Función de activación
        """
        # Geometría: cavidad [0, L] x [0, L]
        self.geom = dde.geometry.Rectangle([0, 0], [self.L, self.L])
        
        # Condiciones de frontera
        # Tapa superior: u = U_lid, v = 0
        bc_lid_u = dde.icbc.DirichletBC(
            self.geom, 
            lambda x: self.U_lid, 
            self.boundary_lid,
            component=0
        )
        bc_lid_v = dde.icbc.DirichletBC(
            self.geom,
            lambda x: 0,
            self.boundary_lid,
            component=1
        )
        
        # Paredes: u = 0, v = 0
        bc_wall_u = dde.icbc.DirichletBC(
            self.geom,
            lambda x: 0,
            self.boundary_wall,
            component=0
        )
        bc_wall_v = dde.icbc.DirichletBC(
            self.geom,
            lambda x: 0,
            self.boundary_wall,
            component=1
        )
        
        # Problema PDE
        data = dde.data.PDE(
            self.geom,
            self.navier_stokes,
            [bc_lid_u, bc_lid_v, bc_wall_u, bc_wall_v],
            num_domain=num_domain,
            num_boundary=num_boundary,
            num_test=1000
        )
        
        # Red neuronal con 3 salidas: [u, v, p]
        net = dde.nn.FNN(layer_size, activation, "Glorot normal")
        
        self.model = dde.Model(data, net)
        
        return self.model
    
    def train(
        self,
        iterations: int = 20000,
        learning_rate: float = 1e-3,
        display_every: int = 1000
    ):
        """
        Entrena el modelo.
        
        Args:
            iterations: Número de iteraciones
            learning_rate: Tasa de aprendizaje
            display_every: Frecuencia de impresión
        """
        # Primera fase: Adam
        self.model.compile("adam", lr=learning_rate)
        losshistory, train_state = self.model.train(
            iterations=iterations,
            display_every=display_every
        )
        
        # Segunda fase: L-BFGS (refinamiento)
        self.model.compile("L-BFGS")
        losshistory, train_state = self.model.train()
        
        return losshistory, train_state
    
    def predict(self, X: np.ndarray, Y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predice velocidades y presión.
        
        Args:
            X, Y: Mallas de coordenadas
        
        Returns:
            u, v, p: Componentes de velocidad y presión
        """
        points = np.column_stack([X.flatten(), Y.flatten()])
        output = self.model.predict(points)
        
        u = output[:, 0].reshape(X.shape)
        v = output[:, 1].reshape(X.shape)
        p = output[:, 2].reshape(X.shape)
        
        return u, v, p


def run_cavity_example(Re: float = 100):
    """
    Ejecuta ejemplo de lid-driven cavity.
    
    Args:
        Re: Número de Reynolds
    """
    print("=" * 60)
    print(f"LID-DRIVEN CAVITY FLOW - Re = {Re}")
    print("=" * 60)
    
    solver = LidDrivenCavityPINN(L=1.0, U_lid=1.0, Re=Re)
    
    print(f"Parámetros:")
    print(f"  Lado de la cavidad: L = {solver.L} m")
    print(f"  Velocidad de la tapa: U = {solver.U_lid} m/s")
    print(f"  Número de Reynolds: Re = {solver.Re}")
    print(f"  Viscosidad cinemática: ν = {solver.nu:.6f} m²/s")
    print()
    
    print("Construyendo modelo...")
    solver.build_model(
        num_domain=5000,
        num_boundary=400,
        layer_size=[2, 50, 50, 50, 50, 3]
    )
    
    print("Entrenando (esto puede tomar varios minutos)...")
    losshistory, train_state = solver.train(iterations=20000)
    
    print("\nEvaluando solución...")
    x = np.linspace(0, solver.L, 100)
    y = np.linspace(0, solver.L, 100)
    X, Y = np.meshgrid(x, y)
    
    u, v, p = solver.predict(X, Y)
    
    print("✓ Entrenamiento completado")
    
    return solver, X, Y, u, v, p


if __name__ == "__main__":
    solver, X, Y, u, v, p = run_cavity_example(Re=100)
