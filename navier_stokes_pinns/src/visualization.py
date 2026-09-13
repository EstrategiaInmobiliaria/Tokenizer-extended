"""
Funciones de visualización para resultados de Navier-Stokes.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from typing import Optional, Tuple
import seaborn as sns

# Configuración de estilo
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.size'] = 10


def plot_velocity_field(
    X: np.ndarray,
    Y: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    title: str = "Campo de Velocidad",
    figsize: Tuple[int, int] = (12, 5),
    cmap: str = "viridis",
    show_streamlines: bool = True,
    show_quiver: bool = False,
    obstacle: Optional[dict] = None
) -> plt.Figure:
    """
    Visualiza campo de velocidad con magnitud, streamlines y quiver.
    
    Args:
        X, Y: Mallas de coordenadas
        u, v: Componentes de velocidad
        title: Título de la figura
        figsize: Tamaño de figura
        cmap: Mapa de colores
        show_streamlines: Mostrar líneas de corriente
        show_quiver: Mostrar flechas de velocidad
        obstacle: Dict con info de obstáculo {'type': 'circle', 'center': (x,y), 'radius': r}
    
    Returns:
        Figura de matplotlib
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Magnitud de velocidad
    vel_mag = np.sqrt(u**2 + v**2)
    
    # Plot 1: Magnitud con streamlines
    im1 = ax1.contourf(X, Y, vel_mag, levels=20, cmap=cmap)
    if show_streamlines:
        ax1.streamplot(X, Y, u, v, color='white', linewidth=0.5, density=1.5, arrowsize=0.8)
    if obstacle:
        add_obstacle_to_plot(ax1, obstacle)
    ax1.set_xlabel('x [m]')
    ax1.set_ylabel('y [m]')
    ax1.set_title('Magnitud de Velocidad |v|')
    ax1.set_aspect('equal')
    plt.colorbar(im1, ax=ax1, label='|v| [m/s]')
    
    # Plot 2: Componentes u y v
    im2 = ax2.contourf(X, Y, u, levels=20, cmap='RdBu_r')
    if show_quiver:
        skip = max(1, len(X) // 20)
        ax2.quiver(X[::skip, ::skip], Y[::skip, ::skip], 
                   u[::skip, ::skip], v[::skip, ::skip],
                   alpha=0.6, scale=20)
    if obstacle:
        add_obstacle_to_plot(ax2, obstacle)
    ax2.set_xlabel('x [m]')
    ax2.set_ylabel('y [m]')
    ax2.set_title('Componente u de Velocidad')
    ax2.set_aspect('equal')
    plt.colorbar(im2, ax=ax2, label='u [m/s]')
    
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    return fig


def plot_vorticity(
    X: np.ndarray,
    Y: np.ndarray,
    vorticity: np.ndarray,
    title: str = "Campo de Vorticidad",
    figsize: Tuple[int, int] = (8, 6),
    cmap: str = "RdBu_r",
    obstacle: Optional[dict] = None
) -> plt.Figure:
    """
    Visualiza campo de vorticidad.
    
    Args:
        X, Y: Mallas de coordenadas
        vorticity: Campo de vorticidad
        title: Título
        figsize: Tamaño de figura
        cmap: Mapa de colores
        obstacle: Información de obstáculo
    
    Returns:
        Figura
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Normalizar vorticidad para mejor visualización
    vmax = np.abs(vorticity).max()
    
    im = ax.contourf(X, Y, vorticity, levels=30, cmap=cmap, vmin=-vmax, vmax=vmax)
    
    if obstacle:
        add_obstacle_to_plot(ax, obstacle)
    
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    
    cbar = plt.colorbar(im, ax=ax, label='ω [1/s]')
    
    plt.tight_layout()
    return fig


def plot_pressure(
    X: np.ndarray,
    Y: np.ndarray,
    p: np.ndarray,
    title: str = "Campo de Presión",
    figsize: Tuple[int, int] = (8, 6),
    cmap: str = "plasma",
    obstacle: Optional[dict] = None
) -> plt.Figure:
    """
    Visualiza campo de presión.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.contourf(X, Y, p, levels=20, cmap=cmap)
    
    if obstacle:
        add_obstacle_to_plot(ax, obstacle)
    
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    
    plt.colorbar(im, ax=ax, label='p [Pa]')
    
    plt.tight_layout()
    return fig


def plot_comparison(
    y: np.ndarray,
    u_pred: np.ndarray,
    u_exact: np.ndarray,
    title: str = "Comparación: PINN vs Analítico",
    figsize: Tuple[int, int] = (10, 5)
) -> plt.Figure:
    """
    Compara solución PINN con solución analítica.
    
    Args:
        y: Coordenadas
        u_pred: Solución predicha
        u_exact: Solución exacta
        title: Título
        figsize: Tamaño
    
    Returns:
        Figura
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Plot 1: Comparación directa
    ax1.plot(u_exact, y, 'b-', linewidth=2, label='Analítico', alpha=0.7)
    ax1.plot(u_pred, y, 'r--', linewidth=2, label='PINN', alpha=0.7)
    ax1.set_xlabel('Velocidad u [m/s]')
    ax1.set_ylabel('Posición y [m]')
    ax1.set_title('Perfil de Velocidad')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Error absoluto
    error = np.abs(u_pred - u_exact)
    ax2.plot(error, y, 'g-', linewidth=2)
    ax2.set_xlabel('Error Absoluto |u_pred - u_exact|')
    ax2.set_ylabel('Posición y [m]')
    ax2.set_title('Error Puntual')
    ax2.grid(True, alpha=0.3)
    
    # Error L2 relativo
    l2_error = np.linalg.norm(u_pred - u_exact) / np.linalg.norm(u_exact) * 100
    ax2.text(0.6, 0.95, f'Error L2: {l2_error:.2f}%',
             transform=ax2.transAxes, fontsize=11,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    return fig


def plot_training_history(
    loss_history: dict,
    figsize: Tuple[int, int] = (10, 5)
) -> plt.Figure:
    """
    Visualiza historia de entrenamiento del PINN.
    
    Args:
        loss_history: Dict con 'total', 'pde', 'bc', etc.
        figsize: Tamaño
    
    Returns:
        Figura
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Plot 1: Loss total
    if 'total' in loss_history:
        iterations = range(len(loss_history['total']))
        ax1.semilogy(iterations, loss_history['total'], 'b-', linewidth=2, label='Total Loss')
        ax1.set_xlabel('Iteración')
        ax1.set_ylabel('Loss (escala log)')
        ax1.set_title('Convergencia del Entrenamiento')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    # Plot 2: Componentes de loss
    ax2_has_data = False
    for key, values in loss_history.items():
        if key != 'total' and len(values) > 0:
            ax2.semilogy(range(len(values)), values, linewidth=2, label=key, alpha=0.7)
            ax2_has_data = True
    
    if ax2_has_data:
        ax2.set_xlabel('Iteración')
        ax2.set_ylabel('Loss (escala log)')
        ax2.set_title('Componentes de Loss')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def add_obstacle_to_plot(ax, obstacle: dict):
    """
    Añade obstáculo al plot.
    
    Args:
        ax: Axes de matplotlib
        obstacle: Dict con info del obstáculo
    """
    if obstacle['type'] == 'circle':
        circle = Circle(obstacle['center'], obstacle['radius'], 
                       color='black', fill=True, alpha=0.5)
        ax.add_patch(circle)
    elif obstacle['type'] == 'rectangle':
        rect = Rectangle(obstacle['lower_left'], obstacle['width'], obstacle['height'],
                        color='black', fill=True, alpha=0.5)
        ax.add_patch(rect)


def save_figure(fig: plt.Figure, filename: str, dpi: int = 300):
    """
    Guarda figura en alta resolución.
    
    Args:
        fig: Figura de matplotlib
        filename: Ruta del archivo
        dpi: Resolución
    """
    fig.savefig(filename, dpi=dpi, bbox_inches='tight', facecolor='white')
    print(f"✓ Figura guardada: {filename}")
