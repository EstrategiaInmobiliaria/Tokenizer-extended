"""Simulación 2: Secuenciación manual vs optimizada (paper TSP + clustering)."""

import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

productos_manual = ["A", "C", "B", "D", "A", "C", "B", "D"]
setups_manual = [4, 4, 1.5, 4, 4, 4, 1.5, 4]
colores_manual = ["#d62728" if s > 2 else "#ff7f0e" for s in setups_manual]

ax1.bar(range(len(productos_manual)), setups_manual, color=colores_manual)
ax1.set_xticks(range(len(productos_manual)))
ax1.set_xticklabels(productos_manual)
ax1.set_ylabel("Tiempo de setup (h)")
ax1.set_title(f"Secuencia MANUAL — Total: {sum(setups_manual)}h")
ax1.axhline(y=2, color="gray", linestyle="--", alpha=0.5, label="Umbral cambio mayor")
ax1.legend()
ax1.grid(axis="y", alpha=0.3)

productos_opt = ["A", "B", "A", "B", "C", "D", "C", "D"]
setups_opt = [1.5, 1.5, 1.5, 1.5, 4, 1.5, 4, 1.5]
colores_opt = ["#d62728" if s > 2 else "#2ca02c" for s in setups_opt]

ax2.bar(range(len(productos_opt)), setups_opt, color=colores_opt)
ax2.set_xticks(range(len(productos_opt)))
ax2.set_xticklabels(productos_opt)
ax2.set_ylabel("Tiempo de setup (h)")
ax2.set_title(f"Secuencia OPTIMIZADA (TSP+Clustering) — Total: {sum(setups_opt)}h")
ax2.axhline(y=2, color="gray", linestyle="--", alpha=0.5)
ax2.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("secuenciacion_tsp.png", dpi=150)
reduccion = (sum(setups_manual) - sum(setups_opt)) / sum(setups_manual) * 100
print(f"Setup manual: {sum(setups_manual)}h")
print(f"Setup optimizado: {sum(setups_opt)}h")
print(f"Reducción: {sum(setups_manual) - sum(setups_opt)}h ({reduccion:.0f}%)")
