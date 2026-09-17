"""
Solvers package for Navier-Stokes PINNs.
"""

from .poiseuille_solver import PoiseuilleFlowPINN, run_poiseuille_example
from .cavity_solver import LidDrivenCavityPINN, run_cavity_example

__all__ = [
    'PoiseuilleFlowPINN',
    'run_poiseuille_example',
    'LidDrivenCavityPINN',
    'run_cavity_example',
]
