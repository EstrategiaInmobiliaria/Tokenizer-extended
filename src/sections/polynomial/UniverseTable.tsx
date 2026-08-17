import { useMemo, useState } from "react";
import {
  FAMILIES,
  POLYNOMIAL_OPS_PER_SEC_CLASSROOM,
  UNIVERSE_N_VALUES,
  formatDuration,
  formatOps,
  operations,
  projectedSeconds,
  type ComplexityId,
} from "~/utils/complexity";
import { cn } from "~/utils/cn";

type Props = {
  opsPerSec: number;
  highlightN: number;
};

const TABLE_IDS: ComplexityId[] = [
  "linear",
  "quadratic",
  "cubic",
  "exponential",
];

export function UniverseTable({ opsPerSec, highlightN }: Props) {
  const [showTheory, setShowTheory] = useState(true);
  const rate = showTheory ? POLYNOMIAL_OPS_PER_SEC_CLASSROOM : opsPerSec;
  const nearest = useMemo(() => {
    return UNIVERSE_N_VALUES.reduce((best, value) =>
      Math.abs(value - highlightN) < Math.abs(best - highlightN) ? value : best
    );
  }, [highlightN]);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-violet-700">
            Si el ordenador hiciera {formatOps(rate)} ops/s
          </p>
          <h2 className="text-2xl font-bold text-slate-900">
            ¿Cuánto tardaría de verdad?
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-slate-600">
            Una máquina de 1 GHz puede hacer, a groso modo, mil millones de
            pasos por segundo. Cambia a &quot;este dispositivo&quot; para usar
            la calibración real del navegador.
          </p>
        </div>
        <div className="flex rounded-lg border border-slate-200 p-1 text-sm">
          <button
            className={cn(
              "rounded-md px-3 py-1.5",
              showTheory && "bg-slate-900 text-white"
            )}
            onClick={() => setShowTheory(true)}
          >
            1×10⁹ ops/s
          </button>
          <button
            className={cn(
              "rounded-md px-3 py-1.5",
              !showTheory && "bg-slate-900 text-white"
            )}
            onClick={() => setShowTheory(false)}
          >
            Este dispositivo
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[640px] border-collapse text-sm">
          <thead>
            <tr className="border-b text-left text-slate-500">
              <th className="py-2 pr-3 font-medium">n</th>
              {TABLE_IDS.map((id) => {
                const family = FAMILIES.find((item) => item.id === id);
                return (
                  <th key={id} className="py-2 pr-3 font-medium">
                    <span style={{ color: family?.color }}>
                      {family?.shortLabel}
                    </span>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {UNIVERSE_N_VALUES.map((n) => (
              <tr
                key={n}
                className={cn(
                  "border-b border-slate-100",
                  n === nearest && "bg-amber-50"
                )}
              >
                <td className="py-2.5 pr-3 font-mono font-semibold">{n}</td>
                {TABLE_IDS.map((id) => {
                  const family = FAMILIES.find((item) => item.id === id);
                  const seconds = projectedSeconds(id, n, rate);
                  const huge = seconds > 3600;
                  return (
                    <td
                      key={id}
                      className={cn(
                        "py-2.5 pr-3 tabular-nums",
                        !family?.polynomial &&
                          huge &&
                          "font-semibold text-red-700"
                      )}
                    >
                      <div>{formatDuration(seconds)}</div>
                      <div className="text-[11px] text-slate-400">
                        {formatOps(operations(id, n))} ops
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-xs text-slate-500">
        Fíjate en n = 60: O(n³) sigue en milisegundos o segundos; O(2ⁿ) ya se
        mide en veces la edad del universo. Eso es exactamente la diferencia
        entre tiempo polinómico y tiempo exponencial.
      </p>
    </section>
  );
}
