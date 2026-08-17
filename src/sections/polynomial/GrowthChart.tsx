import { useMemo, useState } from "react";
import {
  FAMILIES,
  formatOps,
  operations,
  type ComplexityId,
} from "~/utils/complexity";
import { cn } from "~/utils/cn";

type Props = {
  n: number;
  nMax: number;
  visible: ComplexityId[];
  logScale: boolean;
};

const W = 720;
const H = 380;
const PAD = { l: 64, r: 24, t: 24, b: 48 };

function niceLogTicks(maxOps: number): number[] {
  const maxExp = Math.max(1, Math.ceil(Math.log10(Math.max(10, maxOps))));
  return Array.from({ length: maxExp + 1 }, (_, i) => Math.pow(10, i));
}

export function GrowthChart({ n, nMax, visible, logScale }: Props) {
  const [hoverN, setHoverN] = useState<number | null>(null);
  const families = FAMILIES.filter((family) => visible.includes(family.id));
  const markerN = hoverN ?? n;

  const series = useMemo(() => {
    const maxOps = Math.max(
      1,
      ...families.map((family) => operations(family.id, nMax))
    );
    const innerW = W - PAD.l - PAD.r;
    const innerH = H - PAD.t - PAD.b;
    const yOf = (ops: number) => {
      if (logScale) {
        const maxLog = Math.log10(maxOps + 1);
        return PAD.t + innerH - (Math.log10(ops + 1) / maxLog) * innerH;
      }
      return PAD.t + innerH - (ops / maxOps) * innerH;
    };
    const xOf = (value: number) => PAD.l + (value / nMax) * innerW;

    return {
      maxOps,
      xOf,
      yOf,
      paths: families.map((family) => {
        const pts: string[] = [];
        for (let i = 0; i <= nMax; i++) {
          pts.push(`${xOf(i)},${yOf(operations(family.id, i))}`);
        }
        return { family, d: pts.join(" ") };
      }),
    };
  }, [families, logScale, nMax]);

  const yTicks = logScale
    ? niceLogTicks(series.maxOps)
    : [0, 0.25, 0.5, 0.75, 1].map((p) => p * series.maxOps);

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="h-auto w-full"
        onMouseLeave={() => setHoverN(null)}
        onMouseMove={(event) => {
          const rect = event.currentTarget.getBoundingClientRect();
          const x = event.clientX - rect.left;
          const innerW = rect.width * ((W - PAD.l - PAD.r) / W);
          const left = rect.width * (PAD.l / W);
          const ratio = Math.min(1, Math.max(0, (x - left) / innerW));
          setHoverN(Math.round(ratio * nMax));
        }}
      >
        <rect x="0" y="0" width={W} height={H} fill="#fff" rx="16" />

        {yTicks.map((tick) => (
          <g key={tick}>
            <line
              x1={PAD.l}
              x2={W - PAD.r}
              y1={series.yOf(tick)}
              y2={series.yOf(tick)}
              stroke="#e2e8f0"
              strokeDasharray="4 6"
            />
            <text
              x={PAD.l - 10}
              y={series.yOf(tick) + 4}
              textAnchor="end"
              fontSize="11"
              fill="#64748b"
            >
              {formatOps(tick)}
            </text>
          </g>
        ))}

        {Array.from({ length: nMax + 1 }, (_, i) => i)
          .filter((i) => i % Math.ceil(nMax / 8) === 0 || i === nMax)
          .map((tick) => (
            <text
              key={tick}
              x={series.xOf(tick)}
              y={H - 18}
              textAnchor="middle"
              fontSize="11"
              fill="#64748b"
            >
              {tick}
            </text>
          ))}

        <text
          x={W / 2}
          y={H - 4}
          textAnchor="middle"
          fontSize="12"
          fill="#334155"
        >
          tamaño de la entrada n
        </text>
        <text
          x="16"
          y="190"
          fontSize="12"
          fill="#334155"
          transform="rotate(-90 16 190)"
        >
          operaciones
        </text>

        {series.paths.map(({ family, d }) => (
          <polyline
            key={family.id}
            points={d}
            fill="none"
            stroke={family.color}
            strokeWidth={family.polynomial ? 3.5 : 4}
            strokeLinejoin="round"
            strokeLinecap="round"
            className={cn(!family.polynomial && "poly-dash-move")}
          />
        ))}

        <line
          x1={series.xOf(markerN)}
          x2={series.xOf(markerN)}
          y1={PAD.t}
          y2={H - PAD.b}
          stroke="#0f172a"
          strokeDasharray="5 5"
          strokeWidth="1.5"
        />

        {families.map((family) => {
          const ops = operations(family.id, markerN);
          return (
            <g key={`dot-${family.id}`}>
              <circle
                cx={series.xOf(markerN)}
                cy={series.yOf(ops)}
                r="6"
                fill={family.color}
                className="poly-pulse"
              />
            </g>
          );
        })}
      </svg>

      <div className="mt-3 flex flex-wrap items-center gap-3 text-sm">
        {families.map((family) => (
          <div key={family.id} className="flex items-center gap-2">
            <span
              className="h-3 w-3 rounded-full"
              style={{ background: family.color }}
            />
            <span className="font-medium text-slate-800">
              {family.shortLabel}
            </span>
            <span className="tabular-nums text-slate-500">
              {formatOps(operations(family.id, markerN))} ops
            </span>
          </div>
        ))}
        <span className="ml-auto tabular-nums text-slate-500">
          n = {markerN}
        </span>
      </div>
    </div>
  );
}
