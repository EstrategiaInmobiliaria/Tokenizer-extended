"""Núcleo didáctico de la línea de empaque.

Origen de cada número
---------------------
- 4.5 h / 1.5 h: abstract del paper 2024 (SRC-001). Se usan como
  duración de cambio mayor vs. menor en el ejemplo, no como un run de planta.
- Dólares de paro, ROI, 30 días, operadores: SRC-D01 (aula). No citar como paper.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


# --- Setup times from SRC-001 abstract (major vs clustered/minor) ---
MAJOR_SETUP_H = 4.5
MINOR_SETUP_H = 1.5


@dataclass(frozen=True)
class SKU:
    code: str
    api: str
    blister: str
    fmt: str


# Teaching catalog (didactic). Names are arbitrary.
TEACHING_SKUS = {
    "A": SKU("A", api="X", blister="10", fmt="blister"),
    "B": SKU("B", api="X", blister="20", fmt="blister"),
    "C": SKU("C", api="Y", blister="10", fmt="blister"),
    "D": SKU("D", api="Y", blister="20", fmt="blister"),
}


def setup_hours(prev: SKU, curr: SKU) -> float:
    """Mayor si cambia el API; menor si se queda en la misma familia de sustancia."""
    if prev.api != curr.api:
        return MAJOR_SETUP_H
    return MINOR_SETUP_H


def sequence_setup_hours(codes: Sequence[str], catalog=TEACHING_SKUS) -> float:
    skus = [catalog[c] for c in codes]
    return sum(setup_hours(a, b) for a, b in zip(skus, skus[1:]))


def cluster_then_sequence(codes: Sequence[str], catalog=TEACHING_SKUS) -> List[str]:
    """Agrupa por API y concatena. Ilustra la etapa descriptiva del preprint 2026."""
    by_api: dict[str, List[str]] = {}
    for code in codes:
        by_api.setdefault(catalog[code].api, []).append(code)
    ordered: List[str] = []
    for api in sorted(by_api):
        ordered.extend(by_api[api])
    return ordered


# --- Didactic LFI (monetary cost of not acting). Not an academic index. ---
@dataclass(frozen=True)
class LfiAssumptions:
    costo_hora_linea: float = 14_000.0
    minutos_paro: float = 18.0
    paros_por_turno_antes: int = 6
    paros_por_turno_despues: int = 2
    turnos_por_dia: int = 3
    costo_limpieza_sensor: float = 29.0
    cambios_rollo_por_dia: int = 3
    dias_laborables_mes: int = 25


def costo_por_paro(a: LfiAssumptions) -> float:
    return a.costo_hora_linea * (a.minutos_paro / 60.0)


def lfi_daily(a: LfiAssumptions | None = None) -> dict:
    a = a or LfiAssumptions()
    unit = costo_por_paro(a)
    paros_antes = a.paros_por_turno_antes * a.turnos_por_dia
    paros_despues = a.paros_por_turno_despues * a.turnos_por_dia
    evitados = paros_antes - paros_despues
    perdida_antes = paros_antes * unit
    costo_limpieza = a.costo_limpieza_sensor * a.cambios_rollo_por_dia
    perdida_despues = paros_despues * unit + costo_limpieza
    ahorro = perdida_antes - perdida_despues
    roi = ahorro / costo_limpieza if costo_limpieza else float("inf")
    return {
        "costo_por_paro": unit,
        "paros_antes": paros_antes,
        "paros_despues": paros_despues,
        "paros_evitados": evitados,
        "perdida_antes": perdida_antes,
        "perdida_despues": perdida_despues,
        "costo_limpieza": costo_limpieza,
        "ahorro_diario": ahorro,
        "ahorro_mensual": ahorro * a.dias_laborables_mes,
        "perdida_mensual_antes": perdida_antes * a.dias_laborables_mes,
        "roi": roi,
        "nota": (
            "Didáctico. El 'ahorro diario 4×$4,200' de conversaciones previas "
            "cuenta 4 paros evitados al día; con 4 evitados por turno × 3 turnos "
            "son 12 evitados/día. Este lab usa la aritmética consistente (12)."
        ),
    }


def improvement_curve(days: int = 30, start: float = 18.0, end: float = 6.0, tau: float = 10.0):
    """Curva suave didáctica (no es un fit del paper)."""
    import math

    return [end + (start - end) * math.exp(-d / tau) for d in range(1, days + 1)]
