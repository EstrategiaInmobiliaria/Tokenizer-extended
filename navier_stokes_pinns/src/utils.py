"""
Utilidades comunes para solvers de Navier-Stokes con PINNs.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional, Callable


def create_domain_2d(
    x_range: Tuple[float, float],
    y_range: Tuple[float, float],
    nx: int = 100,
    ny: int = 100
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Crea una malla 2D para evaluación.
    
    Args:
        x_range: (x_min, x_max)
        y_range: (y_min, y_max)
        nx: Número de puntos en x
        ny: Número de puntos en y
    
    Returns:
        X, Y: Mallas de coordenadas
    """
    x = np.linspace(x_range[0], x_range[1], nx)
    y = np.linspace(y_range[0], y_range[1], ny)
    X, Y = np.meshgrid(x, y)
    return X, Y


def compute_vorticity(u: np.ndarray, v: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """
    Calcula vorticidad: ω = ∂v/∂x - ∂u/∂y
    
    Args:
        u: Componente x de velocidad
        v: Componente y de velocidad
        dx: Espaciado en x
        dy: Espaciado en y
    
    Returns:
        Vorticidad
    """
    dvdx = np.gradient(v, dx, axis=1)
    dudy = np.gradient(u, dy, axis=0)
    return dvdx - dudy


def compute_streamfunction(u: np.ndarray, v: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """
    Calcula función de corriente mediante integración.
    
    Args:
        u: Componente x de velocidad
        v: Componente y de velocidad
        dx: Espaciado en x
        dy: Espaciado en y
    
    Returns:
        Función de corriente ψ
    """
    psi = np.zeros_like(u)
    # Integrar v en x para obtener psi
    for i in range(1, u.shape[1]):
        psi[:, i] = psi[:, i-1] + v[:, i] * dx
    return psi


def compute_velocity_magnitude(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Calcula magnitud de velocidad."""
    return np.sqrt(u**2 + v**2)


def compute_reynolds_number(
    velocity: float,
    length: float,
    kinematic_viscosity: float
) -> float:
    """
    Calcula número de Reynolds: Re = UL/ν
    
    Args:
        velocity: Velocidad característica [m/s]
        length: Longitud característica [m]
        kinematic_viscosity: Viscosidad cinemática [m²/s]
    
    Returns:
        Número de Reynolds (adimensional)
    """
    return velocity * length / kinematic_viscosity


def l2_relative_error(pred: np.ndarray, exact: np.ndarray) -> float:
    """
    Calcula error relativo L2.
    
    Args:
        pred: Valores predichos
        exact: Valores exactos
    
    Returns:
        Error relativo L2
    """
    return np.linalg.norm(pred - exact) / np.linalg.norm(exact)


def poiseuille_analytical(
    y: np.ndarray,
    dp_dx: float,
    mu: float,
    H: float
) -> np.ndarray:
    """
    Solución analítica para flujo de Poiseuille.
    
    Perfil parabólico: u(y) = -1/(2μ) * dp/dx * (H² - y²)
    
    Args:
        y: Coordenadas verticales
        dp_dx: Gradiente de presión (negativo para flujo positivo)
        mu: Viscosidad dinámica
        H: Medio ancho del canal
    
    Returns:
        Velocidad u(y)
    """
    return -dp_dx / (2 * mu) * (H**2 - y**2)


class PhysicsConstants:
    """Constantes físicas comunes."""
    
    # Propiedades del agua a 20°C
    WATER_DENSITY = 998.0  # kg/m³
    WATER_DYNAMIC_VISCOSITY = 1.002e-3  # Pa·s
    WATER_KINEMATIC_VISCOSITY = 1.004e-6  # m²/s
    
    # Propiedades del aire a 20°C
    AIR_DENSITY = 1.204  # kg/m³
    AIR_DYNAMIC_VISCOSITY = 1.825e-5  # Pa·s
    AIR_KINEMATIC_VISCOSITY = 1.516e-5  # m²/s


def format_scientific(value: float, precision: int = 2) -> str:
    """Formatea números en notación científica limpia."""
    return f"{value:.{precision}e}"


def print_simulation_info(
    Re: float,
    domain: Tuple[float, float, float, float],
    viscosity: float,
    velocity: float
):
    """
    Imprime información de la simulación.
    
    Args:
        Re: Número de Reynolds
        domain: (x_min, x_max, y_min, y_max)
        viscosity: Viscosidad cinemática
        velocity: Velocidad característica
    """
    print("=" * 60)
    print("PARÁMETROS DE SIMULACIÓN")
    print("=" * 60)
    print(f"Número de Reynolds: Re = {Re:.2f}")
    print(f"Dominio: x ∈ [{domain[0]}, {domain[1]}], y ∈ [{domain[2]}, {domain[3]}]")
    print(f"Viscosidad cinemática: ν = {format_scientific(viscosity)} m²/s")
    print(f"Velocidad característica: U = {velocity:.4f} m/s")
    print("=" * 60)
