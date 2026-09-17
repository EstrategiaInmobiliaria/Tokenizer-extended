#!/usr/bin/env python3
"""
Script de ejemplo: Ejecuta flujo de Poiseuille y genera visualizaciones.

Uso:
    python examples/run_poiseuille.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from src.solvers.poiseuille_solver import PoiseuilleFlowPINN
from src.utils import l2_relative_error, print_simulation_info
from src.visualization import plot_comparison, save_figure


def main():
    """Ejecuta ejemplo de Poiseuille con visualizaciones."""
    
    print("\n" + "="*70)
    print(" FLUJO DE POISEUILLE - PHYSICS-INFORMED NEURAL NETWORK")
    print("="*70 + "\n")
    
    # Parámetros
    H = 0.5          # Medio ancho del canal [m]
    L = 2.0          # Longitud [m]
    dp_dx = -1.0     # Gradiente de presión [Pa/m]
    mu = 0.01        # Viscosidad dinámica [Pa·s]
    rho = 1.0        # Densidad [kg/m³]
    
    # Crear solver
    print("📐 Configurando problema...")
    solver = PoiseuilleFlowPINN(H=H, L=L, dp_dx=dp_dx, mu=mu, rho=rho)
    
    # Info
    u_max = solver.compute_max_velocity()
    Re = solver.compute_reynolds_number()
    
    print_simulation_info(
        Re=Re,
        domain=(0, L, -H, H),
        viscosity=solver.nu,
        velocity=u_max
    )
    
    # Construir modelo
    print("\n🏗️  Construyendo red neuronal...")
    solver.build_model(
        num_domain=2000,
        num_boundary=200,
        layer_size=[2, 50, 50, 50, 1]
    )
    print("   Arquitectura: [2 → 50 → 50 → 50 → 1]")
    print("   Activación: tanh")
    print("   Puntos de colocación: 2000 (dominio) + 200 (frontera)")
    
    # Entrenar
    print("\n🎯 Entrenando PINN...")
    print("   Fase 1: Adam (10,000 iteraciones)")
    print("   Fase 2: L-BFGS (hasta convergencia)")
    print("\n   Esto puede tomar 2-3 minutos...\n")
    
    losshistory, train_state = solver.train(iterations=10000, display_every=2000)
    
    # Evaluar
    print("\n📊 Evaluando solución...")
    
    # Malla completa
    x = np.linspace(0, L, 100)
    y = np.linspace(-H, H, 100)
    X, Y = np.meshgrid(x, y)
    
    u_pred_field = solver.predict(X, Y)
    
    # Línea central para comparación
    y_line = np.linspace(-H, H, 100)
    x_line = np.full_like(y_line, L/2)
    
    u_pred = solver.predict(
        x_line.reshape(-1, 1),
        y_line.reshape(-1, 1)
    ).flatten()
    
    u_exact = solver.analytical_solution(y_line)
    
    # Error
    error = l2_relative_error(u_pred, u_exact)
    
    print(f"\n✅ RESULTADOS:")
    print(f"   Error L2 relativo: {error*100:.4f}%")
    print(f"   Error máximo: {np.abs(u_pred - u_exact).max():.6f} m/s")
    print(f"   Velocidad máxima predicha: {u_pred.max():.4f} m/s")
    print(f"   Velocidad máxima exacta: {u_exact.max():.4f} m/s")
    
    # Visualizaciones
    print("\n📈 Generando visualizaciones...")
    
    # 1. Comparación con analítico
    fig_comparison = plot_comparison(
        y_line, u_pred, u_exact,
        title="Flujo de Poiseuille: PINN vs Analítico"
    )
    
    # 2. Campo de velocidad
    fig_field, ax = plt.subplots(figsize=(12, 5))
    contour = ax.contourf(X, Y, u_pred_field, levels=30, cmap='viridis')
    ax.contour(X, Y, u_pred_field, levels=10, colors='white', linewidths=0.5, alpha=0.4)
    plt.colorbar(contour, ax=ax, label='Velocidad u [m/s]')
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_title('Campo de Velocidad - Flujo de Poiseuille', fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    
    # Guardar
    os.makedirs('../visualizations', exist_ok=True)
    save_figure(fig_comparison, '../visualizations/poiseuille_comparison.png')
    save_figure(fig_field, '../visualizations/poiseuille_field.png')
    
    plt.show()
    
    print("\n" + "="*70)
    print("✓ COMPLETADO - Visualizaciones guardadas en visualizations/")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
