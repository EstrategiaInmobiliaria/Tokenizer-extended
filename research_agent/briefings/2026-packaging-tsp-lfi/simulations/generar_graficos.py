"""Gráficos del lab. Todos los paneles llevan etiqueta DIDÁCTICO salvo el de setup 4.5→1.5."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from packaging_lab import (
    TEACHING_SKUS,
    cluster_then_sequence,
    improvement_curve,
    lfi_daily,
    sequence_setup_hours,
)


def _stamp(ax, text="DIDÁCTICO — no es resultado del paper"):
    ax.text(
        0.99,
        0.02,
        text,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        color="#555555",
    )


def plot_lfi(out: Path) -> None:
    m = lfi_daily()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    turnos = ["Turno 1", "Turno 2", "Turno 3"]
    x = np.arange(len(turnos))
    w = 0.35
    ax1.bar(x - w / 2, [6, 6, 6], w, label="Antes", color="#d62728")
    ax1.bar(x + w / 2, [2, 2, 2], w, label="Después", color="#2ca02c")
    ax1.set_xticks(x, turnos)
    ax1.set_ylabel("Paros no planificados")
    ax1.set_title("Paros por turno (supuestos de aula)")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)
    _stamp(ax1)

    vals = [m["perdida_antes"], m["perdida_despues"]]
    bars = ax2.bar(["Antes", "Después"], vals, color=["#d62728", "#2ca02c"])
    ax2.set_ylabel("Pérdida diaria ($)")
    ax2.set_title(f"Ahorro diario: ${m['ahorro_diario']:,.0f}  |  ROI {m['roi']:.0f}×")
    for bar, val in zip(bars, vals):
        ax2.text(bar.get_x() + bar.get_width() / 2, val, f"${val:,.0f}", ha="center", va="bottom")
    ax2.grid(axis="y", alpha=0.3)
    _stamp(ax2)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_tsp(out: Path) -> None:
    manual = list("ACBDACBD")
    clustered = cluster_then_sequence(manual)
    setups_m = [
        4.5 if TEACHING_SKUS[a].api != TEACHING_SKUS[b].api else 1.5
        for a, b in zip(manual, manual[1:])
    ]
    setups_o = [
        4.5 if TEACHING_SKUS[a].api != TEACHING_SKUS[b].api else 1.5
        for a, b in zip(clustered, clustered[1:])
    ]
    # prepend a dummy first-job setup of 0 for alignment with product labels
    ym = [0] + setups_m
    yo = [0] + setups_o

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7))
    colors_m = ["#d62728" if s > 2 else "#ff7f0e" for s in ym]
    colors_o = ["#d62728" if s > 2 else "#2ca02c" for s in yo]
    ax1.bar(range(len(manual)), ym, color=colors_m)
    ax1.set_xticks(range(len(manual)), manual)
    ax1.set_ylabel("Setup (h)")
    ax1.set_title(
        f"Secuencia MANUAL {''.join(manual)} — total {sequence_setup_hours(manual):.1f} h  "
        f"(ilustrativo; 4.5/1.5 h vienen del abstract SRC-001)"
    )
    ax1.axhline(2, color="gray", ls="--", alpha=0.5)
    ax1.grid(axis="y", alpha=0.3)
    _stamp(ax1, "Setup 4.5/1.5 h: SRC-001 · secuencia: DIDÁCTICO")

    ax2.bar(range(len(clustered)), yo, color=colors_o)
    ax2.set_xticks(range(len(clustered)), clustered)
    ax2.set_ylabel("Setup (h)")
    ax2.set_title(
        f"Secuencia CLUSTER+TSP ilustrativo {''.join(clustered)} — total {sequence_setup_hours(clustered):.1f} h"
    )
    ax2.axhline(2, color="gray", ls="--", alpha=0.5)
    ax2.grid(axis="y", alpha=0.3)
    _stamp(ax2, "Setup 4.5/1.5 h: SRC-001 · secuencia: DIDÁCTICO")
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_loop(out: Path) -> None:
    days = np.arange(1, 31)
    sin_lfi = np.full(30, 18.0)
    con = np.array(improvement_curve(30, 18.0, 6.0, 10.0))
    costo = 4200
    ahorro = np.cumsum((sin_lfi - con) * costo)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.plot(days, sin_lfi, "r--", lw=2, label="Sin priorizar restricciones")
    ax1.plot(days, con, "g-", lw=2, label="Con priorización + secuencia (ilustración)")
    ax1.set_xlabel("Días")
    ax1.set_ylabel("Paros / día")
    ax1.set_title("Evolución ilustrativa de paros")
    ax1.legend()
    ax1.grid(alpha=0.3)
    _stamp(ax1)

    ax2.fill_between(days, ahorro, color="#2ca02c", alpha=0.3)
    ax2.plot(days, ahorro, "g-", lw=2)
    ax2.set_xlabel("Días")
    ax2.set_ylabel("Ahorro acumulado ($)")
    ax2.set_title(f"Ahorro ilustrativo 30 días: ${ahorro[-1]:,.0f}")
    ax2.grid(alpha=0.3)
    _stamp(ax2)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def generate_all(outdir: Path) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    files = [
        outdir / "lfi_comparacion.png",
        outdir / "secuenciacion_tsp.png",
        outdir / "bucle_mejora.png",
    ]
    plot_lfi(files[0])
    plot_tsp(files[1])
    plot_loop(files[2])
    return files


if __name__ == "__main__":
    here = Path(__file__).resolve().parent.parent / "output"
    for p in generate_all(here):
        print(f"wrote {p}")
