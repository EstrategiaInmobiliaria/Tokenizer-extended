import { useEffect, useRef, useState } from "react";
import { Play, RotateCcw } from "lucide-react";
import { Button } from "~/components/Button";
import {
  RACE_FAMILIES,
  formatMillis,
  formatOps,
  operations,
  type ComplexityId,
} from "~/utils/complexity";
import { cn } from "~/utils/cn";

type RaceResult = {
  id: ComplexityId;
  ms: number | null;
  running: boolean;
  progress: number;
  error?: string;
};

const WORKER_SOURCE = `
self.onmessage = (event) => {
  const { id, kind, n } = event.data;
  const t0 = performance.now();
  let checksum = 0;
  const report = (done, total) => {
    self.postMessage({
      type: "progress",
      id,
      progress: total === 0 ? 1 : done / total,
      elapsed: performance.now() - t0,
    });
  };

  if (kind === "linear") {
    const total = n;
    for (let i = 0; i < n; i++) {
      checksum += i;
      if ((i & 1048575) === 0) report(i, total);
    }
    report(total, total);
  } else if (kind === "quadratic") {
    const total = n * n;
    let done = 0;
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        checksum += (i + j) & 7;
        done++;
      }
      if ((i & 15) === 0) report(done, total);
    }
    report(total, total);
  } else if (kind === "cubic") {
    const total = n * n * n;
    let done = 0;
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        for (let k = 0; k < n; k++) {
          checksum += (i + j + k) & 7;
          done++;
        }
      }
      if ((i & 3) === 0) report(done, total);
    }
    report(total, total);
  } else if (kind === "exponential") {
    const total = 1 << n;
    for (let mask = 0; mask < total; mask++) {
      checksum += mask & 1;
      if ((mask & 262143) === 0) report(mask, total);
    }
    report(total, total);
  }

  self.postMessage({
    type: "done",
    id,
    ms: performance.now() - t0,
    checksum,
  });
};
`;

function emptyResults(): RaceResult[] {
  return RACE_FAMILIES.map((family) => ({
    id: family.id,
    ms: null,
    running: false,
    progress: 0,
  }));
}

type Props = {
  n: number;
};

function raceSize(id: ComplexityId, n: number, sameN: boolean): number {
  if (sameN) {
    return Math.min(22, Math.max(8, n));
  }
  if (id === "linear")
    return Math.min(8_000_000, Math.max(200_000, n * 80_000));
  if (id === "quadratic") return Math.min(4_000, Math.max(80, n * 8));
  if (id === "cubic") return Math.min(400, Math.max(30, n * 2));
  return Math.min(26, Math.max(12, n));
}

export function RealStopwatch({ n }: Props) {
  const [results, setResults] = useState<RaceResult[]>(emptyResults);
  const [busy, setBusy] = useState(false);
  const [liveMs, setLiveMs] = useState(0);
  const [sameN, setSameN] = useState(true);
  const workerRef = useRef<Worker | null>(null);
  const startRef = useRef(0);

  useEffect(() => {
    return () => {
      workerRef.current?.terminate();
    };
  }, []);

  useEffect(() => {
    if (!busy) return;
    const timer = window.setInterval(() => {
      setLiveMs(performance.now() - startRef.current);
    }, 32);
    return () => window.clearInterval(timer);
  }, [busy]);

  const run = async () => {
    workerRef.current?.terminate();
    const blob = new Blob([WORKER_SOURCE], { type: "application/javascript" });
    const worker = new Worker(URL.createObjectURL(blob));
    workerRef.current = worker;
    setBusy(true);
    setResults(emptyResults());
    startRef.current = performance.now();
    setLiveMs(0);

    for (const family of RACE_FAMILIES) {
      const raceN = raceSize(family.id, n, sameN);

      setResults((prev) =>
        prev.map((row) =>
          row.id === family.id ? { ...row, running: true, progress: 0 } : row
        )
      );

      await new Promise<void>((resolve, reject) => {
        const onMessage = (event: MessageEvent) => {
          const data = event.data as {
            type: string;
            id: ComplexityId;
            progress?: number;
            ms?: number;
          };
          if (data.id !== family.id) return;
          if (data.type === "progress") {
            setResults((prev) =>
              prev.map((row) =>
                row.id === family.id
                  ? { ...row, progress: data.progress ?? 0 }
                  : row
              )
            );
          }
          if (data.type === "done") {
            worker.removeEventListener("message", onMessage);
            setResults((prev) =>
              prev.map((row) =>
                row.id === family.id
                  ? {
                      ...row,
                      running: false,
                      progress: 1,
                      ms: data.ms ?? 0,
                    }
                  : row
              )
            );
            resolve();
          }
        };
        worker.addEventListener("error", (err) => reject(err));
        worker.addEventListener("message", onMessage);
        worker.postMessage({ id: family.id, kind: family.id, n: raceN });
      });
    }

    setBusy(false);
  };

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-emerald-700">
            Cronómetro real del navegador
          </p>
          <h2 className="text-2xl font-bold text-slate-900">
            Medimos milisegundos de verdad
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-slate-600">
            Esto no es un dibujo: un worker de JavaScript ejecuta bucles reales
            y usamos{" "}
            <code className="rounded bg-slate-100 px-1">performance.now()</code>
            . En &quot;misma n&quot; los cuatro corren el mismo tamaño: los
            polinomios acaban en un parpadeo y 2ⁿ se nota. En &quot;n
            ajustado&quot; cada uno usa un n distinto para que el cronómetro
            tenga milisegundos que mostrar.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex rounded-lg border border-slate-200 bg-white p-1 text-sm">
            <button
              className={cn(
                "rounded-md px-3 py-1.5",
                sameN && "bg-slate-900 text-white"
              )}
              disabled={busy}
              onClick={() => setSameN(true)}
            >
              Misma n
            </button>
            <button
              className={cn(
                "rounded-md px-3 py-1.5",
                !sameN && "bg-slate-900 text-white"
              )}
              disabled={busy}
              onClick={() => setSameN(false)}
            >
              n ajustado
            </button>
          </div>
          <div className="rounded-xl bg-slate-900 px-4 py-2 font-mono text-2xl tabular-nums text-emerald-300">
            {formatMillis(
              busy ? liveMs : results[results.length - 1]?.ms ?? liveMs
            )}
          </div>
          <Button onClick={() => void run()} disabled={busy}>
            <Play className="mr-2 h-4 w-4" />
            {busy ? "Midiendo…" : "Correr en este ordenador"}
          </Button>
          <Button
            variant="outline"
            disabled={busy}
            onClick={() => {
              setResults(emptyResults());
              setLiveMs(0);
            }}
          >
            <RotateCcw className="mr-2 h-4 w-4" />
            Reset
          </Button>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {RACE_FAMILIES.map((family, index) => {
          const row = results[index];
          const measuredN = raceSize(family.id, n, sameN);
          return (
            <div
              key={family.id}
              className={cn(
                "rounded-xl border p-4",
                row?.running && "poly-pulse"
              )}
              style={{
                borderColor: family.color,
                background: family.colorSoft,
              }}
            >
              <div className="flex items-baseline justify-between">
                <h3 className="font-bold" style={{ color: family.color }}>
                  {family.shortLabel}
                </h3>
                <span className="font-mono text-xl tabular-nums text-slate-900">
                  {row?.running
                    ? "…"
                    : row?.ms == null
                    ? "—"
                    : formatMillis(row.ms)}
                </span>
              </div>
              <p className="text-xs text-slate-600">
                n = {measuredN.toLocaleString("es-ES")} ·{" "}
                {formatOps(operations(family.id, measuredN))} operaciones
              </p>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/80">
                <div
                  className="h-full rounded-full transition-[width] duration-150"
                  style={{
                    width: `${Math.round((row?.progress ?? 0) * 100)}%`,
                    background: family.color,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
