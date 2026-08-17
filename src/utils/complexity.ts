export type ComplexityId =
  | "constant"
  | "linear"
  | "quadratic"
  | "cubic"
  | "exponential";

export type ComplexityFamily = {
  id: ComplexityId;
  label: string;
  shortLabel: string;
  formula: string;
  color: string;
  colorSoft: string;
  polynomial: boolean;
  degree: number | null;
  classroom: string;
  metaphor: string;
  whenDoubling: string;
};

export const POLYNOMIAL_OPS_PER_SEC_CLASSROOM = 1_000_000_000;

export const FAMILIES: ComplexityFamily[] = [
  {
    id: "constant",
    label: "Constante",
    shortLabel: "O(1)",
    formula: "1",
    color: "#64748b",
    colorSoft: "#f1f5f9",
    polynomial: true,
    degree: 0,
    classroom:
      "Escribir el título en la pizarra: da igual si hay 5 o 500 alumnos.",
    metaphor: "Un solo paso, siempre.",
    whenDoubling: "El tiempo no cambia.",
  },
  {
    id: "linear",
    label: "Lineal",
    shortLabel: "O(n)",
    formula: "n",
    color: "#16a34a",
    colorSoft: "#dcfce7",
    polynomial: true,
    degree: 1,
    classroom: "Pasar lista: el profesor mira a cada alumno una vez.",
    metaphor: "Recorrer una fila de n cajas.",
    whenDoubling: "Si duplicas n, el tiempo se duplica (×2).",
  },
  {
    id: "quadratic",
    label: "Cuadrático",
    shortLabel: "O(n²)",
    formula: "n²",
    color: "#2563eb",
    colorSoft: "#dbeafe",
    polynomial: true,
    degree: 2,
    classroom: "Cada alumno saluda a todos los demás: n × n miradas.",
    metaphor: "Comparar cada pareja de datos (como en una burbuja).",
    whenDoubling: "Si duplicas n, el tiempo se multiplica por 4.",
  },
  {
    id: "cubic",
    label: "Cúbico",
    shortLabel: "O(n³)",
    formula: "n³",
    color: "#7c3aed",
    colorSoft: "#ede9fe",
    polynomial: true,
    degree: 3,
    classroom: "Probar cada trío de alumnos para un equipo de 3.",
    metaphor: "Tres bucles anidados: i, j y k.",
    whenDoubling: "Si duplicas n, el tiempo se multiplica por 8.",
  },
  {
    id: "exponential",
    label: "Exponencial",
    shortLabel: "O(2ⁿ)",
    formula: "2ⁿ",
    color: "#dc2626",
    colorSoft: "#fee2e2",
    polynomial: false,
    degree: null,
    classroom: "Probar todos los subconjuntos posibles de alumnos.",
    metaphor: "Cada alumno extra duplica el número de casos.",
    whenDoubling:
      "Si n crece en 1, el tiempo se duplica. Si duplicas n, el tiempo se eleva al cuadrado.",
  },
];

export const RACE_FAMILIES = FAMILIES.filter(
  (family) => family.id !== "constant"
);

export function operations(id: ComplexityId, n: number): number {
  const size = Math.max(0, n);
  switch (id) {
    case "constant":
      return 1;
    case "linear":
      return size;
    case "quadratic":
      return size * size;
    case "cubic":
      return size * size * size;
    case "exponential":
      return Math.pow(2, size);
  }
}

export function formatOps(ops: number): string {
  if (!Number.isFinite(ops)) return "∞";
  if (ops < 1000) return Math.round(ops).toLocaleString("es-ES");
  if (ops < 1e6) return `${(ops / 1e3).toFixed(ops < 1e4 ? 1 : 0)} mil`;
  if (ops < 1e9) return `${(ops / 1e6).toFixed(ops < 1e7 ? 1 : 0)} millones`;
  if (ops < 1e12)
    return `${(ops / 1e9).toFixed(ops < 1e10 ? 1 : 0)} mil millones`;
  if (ops < 1e15) return `${(ops / 1e12).toFixed(1)} billones`;
  if (ops < 1e18) return `${(ops / 1e15).toFixed(1)} mil billones`;
  return ops.toExponential(1).replace("e+", "×10^");
}

export function formatDuration(seconds: number): string {
  if (!Number.isFinite(seconds)) return "más que la edad del universo";
  if (seconds <= 0) return "0 s";
  if (seconds < 1e-6) return `${(seconds * 1e9).toFixed(0)} ns`;
  if (seconds < 1e-3) return `${(seconds * 1e6).toFixed(1)} μs`;
  if (seconds < 1) return `${(seconds * 1e3).toFixed(1)} ms`;
  if (seconds < 60) return `${seconds.toFixed(seconds < 10 ? 2 : 1)} s`;
  if (seconds < 3600) return `${(seconds / 60).toFixed(1)} min`;
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)} h`;
  if (seconds < 31557600) return `${(seconds / 86400).toFixed(1)} días`;
  const years = seconds / 31557600;
  if (years < 1000) return `${years.toFixed(years < 10 ? 1 : 0)} años`;
  if (years < 1e6) return `${(years / 1e3).toFixed(1)} mil años`;
  if (years < 1e9) return `${(years / 1e6).toFixed(1)} millones de años`;
  if (years < 13.8e9) return `${(years / 1e9).toFixed(1)} mil millones de años`;
  return `${(years / 13.8e9).toFixed(0)} veces la edad del universo`;
}

export function formatMillis(ms: number): string {
  if (!Number.isFinite(ms)) return "—";
  if (ms < 0.01) return "< 0,01 ms";
  if (ms < 1) return `${ms.toFixed(2)} ms`;
  if (ms < 10) return `${ms.toFixed(2)} ms`;
  if (ms < 1000) return `${ms.toFixed(1)} ms`;
  return formatDuration(ms / 1000);
}

export function projectedSeconds(
  id: ComplexityId,
  n: number,
  opsPerSec: number
): number {
  return operations(id, n) / Math.max(1, opsPerSec);
}

export function decodePair(step: number, n: number): { i: number; j: number } {
  if (n <= 0) return { i: 0, j: 0 };
  const bounded = Math.max(0, step) % Math.max(1, n * n);
  return { i: Math.floor(bounded / n), j: bounded % n };
}

export function decodeTriple(
  step: number,
  n: number
): { i: number; j: number; k: number } {
  if (n <= 0) return { i: 0, j: 0, k: 0 };
  const bounded = Math.max(0, step) % Math.max(1, n * n * n);
  const i = Math.floor(bounded / (n * n));
  const rem = bounded % (n * n);
  return { i, j: Math.floor(rem / n), k: rem % n };
}

export function subsetBits(mask: number, n: number): number[] {
  const bits: number[] = [];
  for (let i = 0; i < n; i++) {
    if (mask & (1 << i)) bits.push(i);
  }
  return bits;
}

export const UNIVERSE_N_VALUES = [10, 20, 30, 40, 50, 60] as const;
