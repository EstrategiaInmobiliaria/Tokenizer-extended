import { operations, type ComplexityId } from "~/utils/complexity";

type Props = {
  n: number;
  globalOps: number;
  id: ComplexityId;
  color: string;
};

const MAX_CELLS = 144;

export function OperationGrid({ n, globalOps, id, color }: Props) {
  const total = Math.max(1, operations(id, n));
  const visual = Math.min(MAX_CELLS, total);
  const filled = Math.min(
    visual,
    Math.floor((Math.min(globalOps, total) / total) * visual)
  );
  const cols = Math.ceil(Math.sqrt(visual));

  return (
    <div className="flex h-full flex-col justify-center">
      <div
        className="mx-auto grid w-full max-w-[240px] gap-[3px]"
        style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
      >
        {Array.from({ length: visual }, (_, i) => (
          <div
            key={i}
            className="aspect-square rounded-[3px] transition-colors duration-75"
            style={{
              background: i < filled ? color : "#e2e8f0",
              transform: i === filled - 1 ? "scale(1.15)" : "scale(1)",
            }}
          />
        ))}
      </div>
      {total > MAX_CELLS && (
        <p className="mt-2 text-center text-[11px] text-slate-500">
          Miniatura: {visual} celdas de {total.toLocaleString("es-ES")}{" "}
          operaciones
        </p>
      )}
    </div>
  );
}
