"""Simulación 1: Comparación de paros y pérdida económica (marco LFI)."""

import matplotlib.pyplot as plt
import numpy as np

turnos = ["Turno 1", "Turno 2", "Turno 3"]
paros_antes = [6, 6, 6]
paros_despues = [2, 2, 2]
costo_paro = 4200
costo_limpieza = 29
cambios_bobinado = 3

perdida_antes = sum(paros_antes) * costo_paro
perdida_despues = sum(paros_despues) * costo_paro + (costo_limpieza * cambios_bobinado)
ahorro = perdida_antes - perdida_despues

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

x = np.arange(len(turnos))
width = 0.35
ax1.bar(x - width / 2, paros_antes, width, label="Antes", color="#d62728")
ax1.bar(x + width / 2, paros_despues, width, label="Después", color="#2ca02c")
ax1.set_ylabel("Número de paros")
ax1.set_title("Paros por turno: Antes vs Después")
ax1.set_xticks(x)
ax1.set_xticklabels(turnos)
ax1.legend()
ax1.grid(axis="y", alpha=0.3)

categorias = ["Antes", "Después"]
valores = [perdida_antes, perdida_despues]
colores = ["#d62728", "#2ca02c"]
bars = ax2.bar(categorias, valores, color=colores)
ax2.set_ylabel("Pérdida diaria ($)")
ax2.set_title(f"Ahorro diario: ${ahorro:,.0f}")
for bar, val in zip(bars, valores):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 500,
        f"${val:,.0f}",
        ha="center",
        fontweight="bold",
    )
ax2.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("lfi_comparacion.png", dpi=150)
print(f"Pérdida antes: ${perdida_antes:,.0f}/día")
print(f"Pérdida después: ${perdida_despues:,.0f}/día")
print(f"Ahorro diario: ${ahorro:,.0f} (ROI: {ahorro / (costo_limpieza * cambios_bobinado):.0f}x)")
