"""Simulación 3: Bucle cerrado LFI + LPS — evolución de 30 días."""

import matplotlib.pyplot as plt
import numpy as np

dias = np.arange(1, 31)
paros_sin_lfi = np.full(30, 18)
paros_con_lfi = 18 - (18 - 2) * (1 - np.exp(-dias / 10))

costo_paro = 4200
costo_sin_lfi = paros_sin_lfi * costo_paro
costo_con_lfi = paros_con_lfi * costo_paro

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.plot(dias, paros_sin_lfi, "r--", label="Sin optimización", linewidth=2)
ax1.plot(dias, paros_con_lfi, "g-", label="Con LFI + LPS", linewidth=2)
ax1.set_xlabel("Días")
ax1.set_ylabel("Paros por día")
ax1.set_title("Evolución de paros: mejora continua")
ax1.legend()
ax1.grid(alpha=0.3)

ahorro_acumulado = np.cumsum(costo_sin_lfi - costo_con_lfi)
ax2.fill_between(dias, 0, ahorro_acumulado, color="#2ca02c", alpha=0.3)
ax2.plot(dias, ahorro_acumulado, "g-", linewidth=2)
ax2.set_xlabel("Días")
ax2.set_ylabel("Ahorro acumulado ($)")
ax2.set_title(f"Ahorro total en 30 días: ${ahorro_acumulado[-1]:,.0f}")
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("bucle_lfi_lps.png", dpi=150)
print(f"Ahorro acumulado en 30 días: ${ahorro_acumulado[-1]:,.0f}")
