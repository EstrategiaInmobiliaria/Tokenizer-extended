import { useMemo } from "react";
import {
  FAMILIES,
  decodePair,
  decodeTriple,
  operations,
  subsetBits,
  type ComplexityId,
} from "~/utils/complexity";

type Props = {
  n: number;
  globalOps: number;
  activeId: ComplexityId;
};

const CX = 160;
const CY = 150;
const R = 108;

function studentPos(index: number, n: number) {
  const angle = (index / Math.max(n, 1)) * Math.PI * 2 - Math.PI / 2;
  return {
    x: CX + Math.cos(angle) * R,
    y: CY + Math.sin(angle) * R,
  };
}

export function ClassroomScene({ n, globalOps, activeId }: Props) {
  const family = FAMILIES.find((item) => item.id === activeId) ?? FAMILIES[1]!;
  const total = Math.max(1, operations(activeId, n));
  const step = Math.min(
    Math.floor(globalOps),
    total - (activeId === "constant" ? 0 : 1)
  );
  const done = globalOps >= total;

  const highlighted = useMemo(() => {
    if (activeId === "constant") return [] as number[];
    if (activeId === "linear") return [Math.min(n - 1, Math.max(0, step))];
    if (activeId === "quadratic") {
      const pair = decodePair(step, n);
      return [pair.i, pair.j];
    }
    if (activeId === "cubic") {
      const triple = decodeTriple(step, n);
      return [triple.i, triple.j, triple.k];
    }
    return subsetBits(Math.max(0, step), n);
  }, [activeId, n, step]);

  const pair = activeId === "quadratic" ? decodePair(step, n) : null;
  const visitedLinear =
    activeId === "linear" ? Math.min(n, Math.floor(globalOps)) : 0;

  return (
    <div className="flex h-full flex-col">
      <svg viewBox="0 0 320 300" className="h-[260px] w-full">
        <defs>
          <radialGradient id={`glow-${activeId}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={family.color} stopOpacity="0.18" />
            <stop offset="100%" stopColor={family.color} stopOpacity="0" />
          </radialGradient>
        </defs>
        <circle cx={CX} cy={CY} r={R + 28} fill={`url(#glow-${activeId})`} />
        <circle
          cx={CX}
          cy={CY}
          r={R}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth="2"
          strokeDasharray="6 8"
        />

        {pair && n > 0 && (
          <line
            x1={studentPos(pair.i, n).x}
            y1={studentPos(pair.i, n).y}
            x2={studentPos(pair.j, n).x}
            y2={studentPos(pair.j, n).y}
            stroke={family.color}
            strokeWidth="3"
            strokeLinecap="round"
            className="poly-line-draw"
          />
        )}

        {activeId === "exponential" &&
          highlighted.map((index) => {
            const pos = studentPos(index, n);
            return (
              <line
                key={`spoke-${index}`}
                x1={CX}
                y1={CY}
                x2={pos.x}
                y2={pos.y}
                stroke={family.color}
                strokeWidth="2"
                strokeOpacity="0.45"
              />
            );
          })}

        {Array.from({ length: n }, (_, index) => {
          const pos = studentPos(index, n);
          const isOn = highlighted.includes(index);
          const alreadyVisited = activeId === "linear" && index < visitedLinear;
          return (
            <g key={index} className={isOn ? "poly-bob" : undefined}>
              <circle
                cx={pos.x}
                cy={pos.y}
                r={isOn ? 18 : 15}
                fill={isOn || alreadyVisited ? family.color : "#fff"}
                stroke={family.color}
                strokeWidth="3"
                style={{
                  transition: "r 120ms ease, fill 120ms ease",
                  filter: isOn
                    ? `drop-shadow(0 0 8px ${family.color})`
                    : undefined,
                }}
              />
              <text
                x={pos.x}
                y={pos.y + 5}
                textAnchor="middle"
                fontSize="12"
                fontWeight="700"
                fill={isOn || alreadyVisited ? "#fff" : "#334155"}
              >
                {index + 1}
              </text>
            </g>
          );
        })}

        <g className={done ? "poly-pulse" : undefined}>
          <circle cx={CX} cy={CY} r="28" fill="#0f172a" />
          <text
            x={CX}
            y={CY - 2}
            textAnchor="middle"
            fill="#fff"
            fontSize="11"
            fontWeight="700"
          >
            {family.shortLabel}
          </text>
          <text
            x={CX}
            y={CY + 12}
            textAnchor="middle"
            fill="#cbd5e1"
            fontSize="9"
          >
            {done ? "listo" : "en curso"}
          </text>
        </g>
      </svg>
      <p className="px-1 text-center text-sm leading-snug text-slate-600">
        {family.classroom}
      </p>
    </div>
  );
}
