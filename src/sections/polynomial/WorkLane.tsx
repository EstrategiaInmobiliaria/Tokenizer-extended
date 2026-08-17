import { type ReactNode } from "react";
import {
  formatOps,
  operations,
  type ComplexityFamily,
} from "~/utils/complexity";
import { cn } from "~/utils/cn";

type Props = {
  family: ComplexityFamily;
  n: number;
  globalOps: number;
  children?: ReactNode;
};

export function WorkLane({ family, n, globalOps, children }: Props) {
  const total = Math.max(1, operations(family.id, n));
  const done = Math.min(globalOps, total);
  const pct = Math.min(100, (done / total) * 100);
  const finished = globalOps >= total;

  return (
    <article
      className={cn(
        "flex flex-col rounded-2xl border p-4 shadow-sm transition-all",
        finished ? "ring-2 ring-offset-2" : "border-slate-200 bg-white"
      )}
      style={{
        borderColor: family.color,
        background: finished ? family.colorSoft : "#fff",
        boxShadow: finished ? `0 0 0 2px ${family.color}33` : undefined,
      }}
    >
      <div className="mb-2 flex items-baseline justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            {family.polynomial ? "Polinómico" : "No polinómico"}
          </p>
          <h3 className="text-lg font-bold" style={{ color: family.color }}>
            {family.shortLabel} · {family.label}
          </h3>
        </div>
        <p className="text-sm tabular-nums text-slate-600">
          {formatOps(Math.min(done, total))} / {formatOps(total)}
        </p>
      </div>

      <div className="relative mb-3 h-4 overflow-hidden rounded-full bg-slate-100">
        <div
          className="poly-bar-fill h-full rounded-full"
          style={{
            width: `${pct}%`,
            background: family.color,
          }}
        />
        <span
          className="poly-runner absolute top-1/2 h-5 w-5 -translate-y-1/2 rounded-full border-2 border-white shadow"
          style={{
            left: `calc(${pct}% - 10px)`,
            background: family.color,
            opacity: finished ? 0.35 : 1,
          }}
        />
      </div>

      <div className="min-h-[280px]">{children}</div>
      <p className="mt-2 text-xs text-slate-500">{family.whenDoubling}</p>
    </article>
  );
}
