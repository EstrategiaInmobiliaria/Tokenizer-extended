import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { BookOpen, Clock, Pause, Play, RotateCcw } from "lucide-react";
import { Button } from "~/components/Button";
import { ClassroomScene } from "~/sections/polynomial/ClassroomScene";
import { GrowthChart } from "~/sections/polynomial/GrowthChart";
import { OperationGrid } from "~/sections/polynomial/OperationGrid";
import { RealStopwatch } from "~/sections/polynomial/RealStopwatch";
import { UniverseTable } from "~/sections/polynomial/UniverseTable";
import { WorkLane } from "~/sections/polynomial/WorkLane";
import {
  FAMILIES,
  RACE_FAMILIES,
  formatDuration,
  formatOps,
  operations,
  type ComplexityId,
} from "~/utils/complexity";
import { cn } from "~/utils/cn";

const N_MIN = 4;
const N_MAX = 24;
const CHART_MAX = 40;

function calibrateOpsPerSec(budgetMs = 180): number {
  const t0 = performance.now();
  let ops = 0;
  let checksum = 0;
  while (performance.now() - t0 < budgetMs) {
    for (let i = 0; i < 50_000; i++) checksum += i & 1;
    ops += 50_000;
  }
  const elapsed = Math.max(1, performance.now() - t0);
  return (ops / elapsed) * 1000 + checksum * 0;
}

export function PolynomialLesson() {
  const [n, setN] = useState(8);
  const [playing, setPlaying] = useState(false);
  const [globalOps, setGlobalOps] = useState(0);
  const [speed, setSpeed] = useState(1);
  const [logScale, setLogScale] = useState(true);
  const [chartN, setChartN] = useState(8);
  const [chartPlaying, setChartPlaying] = useState(false);
  const [opsPerSec, setOpsPerSec] = useState(0);
  const [visible, setVisible] = useState<ComplexityId[]>([
    "linear",
    "quadratic",
    "cubic",
    "exponential",
  ]);

  const classroomN = Math.min(10, n);
  const maxOps = useMemo(
    () => Math.max(...RACE_FAMILIES.map((family) => operations(family.id, n))),
    [n]
  );

  const lastRef = useRef<number | null>(null);

  useEffect(() => {
    setOpsPerSec(calibrateOpsPerSec());
  }, []);

  useEffect(() => {
    setGlobalOps(0);
    setPlaying(false);
  }, [n]);

  useEffect(() => {
    if (!playing) {
      lastRef.current = null;
      return;
    }
    let raf = 0;
    const tick = (now: number) => {
      const last = lastRef.current ?? now;
      const dt = (now - last) / 1000;
      lastRef.current = now;
      setGlobalOps((prev) => {
        const rate = Math.max(20, maxOps / 7) * speed;
        const next = prev + dt * rate;
        if (next >= maxOps) {
          setPlaying(false);
          return maxOps;
        }
        return next;
      });
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [playing, maxOps, speed]);

  useEffect(() => {
    if (!chartPlaying) return;
    let raf = 0;
    let last: number | null = null;
    const tick = (now: number) => {
      const prev = last ?? now;
      last = now;
      setChartN((value) => {
        const next = value + ((now - prev) / 1000) * 6 * speed;
        if (next >= CHART_MAX) {
          setChartPlaying(false);
          return CHART_MAX;
        }
        return next;
      });
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [chartPlaying, speed]);

  const toggleFamily = (id: ComplexityId) => {
    setVisible((prev) => {
      if (prev.includes(id)) {
        if (prev.length === 1) return prev;
        return prev.filter((item) => item !== id);
      }
      return [...prev, id];
    });
  };

  return (
    <div className="mx-auto flex min-h-screen max-w-[1200px] flex-col gap-8 p-6 pb-16 sm:p-8">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-indigo-600">
            Laboratorio de complejidad
          </p>
          <h1 className="text-4xl font-bold tracking-tight text-slate-900">
            ¿Qué es el tiempo polinómico?
          </h1>
          <p className="mt-2 max-w-2xl text-slate-600">
            Un algoritmo es de tiempo polinómico si, al crecer el tamaño del
            problema n, el trabajo crece como n, n², n³… (n elevado a un número
            fijo). No como 2ⁿ, que se desborda.
          </p>
        </div>
        <Link
          href="/"
          className="text-sm text-slate-500 underline-offset-4 hover:text-slate-900 hover:underline"
        >
          ← Volver al tokenizer
        </Link>
      </header>

      <section className="overflow-hidden rounded-3xl bg-slate-900 p-6 text-white shadow-lg">
        <div className="grid gap-6 md:grid-cols-[1.2fr_0.8fr] md:items-center">
          <div>
            <p className="text-sm font-medium text-emerald-300">
              Definición para el aula
            </p>
            <p className="mt-2 text-2xl font-semibold leading-snug sm:text-3xl">
              Tiempo polinómico: existen constantes c y k tales que el algoritmo
              termina en como mucho{" "}
              <span className="poly-formula text-emerald-300">c · nᵏ</span>{" "}
              pasos.
            </p>
            <p className="mt-3 text-slate-300">
              O(n), O(n²) y O(n³) están en P. O(2ⁿ) no. La k no puede depender
              de n: si k crece con n, ya no es polinomio.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {FAMILIES.filter((f) => f.id !== "constant").map((family) => (
              <div
                key={family.id}
                className="rounded-2xl border border-white/10 bg-white/5 p-3"
              >
                <div className="flex items-center gap-2">
                  <span
                    className="h-2.5 w-2.5 rounded-full"
                    style={{ background: family.color }}
                  />
                  <span className="font-semibold">{family.shortLabel}</span>
                </div>
                <p className="mt-1 text-slate-300">
                  {family.polynomial
                    ? "Polinómico · clase P"
                    : "Exponencial · se sale de P"}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">
              1. Simulación con movimiento
            </h2>
            <p className="mt-1 max-w-2xl text-sm text-slate-600">
              El reloj global avanza a la misma velocidad de operaciones para
              todos. El lineal termina casi al instante; el exponencial sigue
              corriendo. n es el número de alumnos / datos.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button onClick={() => setPlaying((value) => !value)}>
              {playing ? (
                <Pause className="mr-2 h-4 w-4" />
              ) : (
                <Play className="mr-2 h-4 w-4" />
              )}
              {playing ? "Pausa" : "Play"}
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setPlaying(false);
                setGlobalOps(0);
              }}
            >
              <RotateCcw className="mr-2 h-4 w-4" />
              Reiniciar
            </Button>
          </div>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-[1fr_220px]">
          <label className="block">
            <div className="mb-1 flex justify-between text-sm">
              <span className="font-medium text-slate-700">
                Tamaño del problema n = {n}
              </span>
              <span className="tabular-nums text-slate-500">
                {formatOps(globalOps)} / {formatOps(maxOps)} ops
              </span>
            </div>
            <input
              type="range"
              min={N_MIN}
              max={N_MAX}
              value={n}
              onChange={(event) => setN(Number(event.target.value))}
              className="w-full accent-indigo-600"
            />
            <div className="mt-1 flex justify-between text-xs text-slate-400">
              <span>n = {N_MIN} (se parecen)</span>
              <span>n = {N_MAX} (el 2ⁿ explota)</span>
            </div>
          </label>
          <label className="block">
            <div className="mb-1 text-sm font-medium text-slate-700">
              Velocidad ×{speed.toFixed(1)}
            </div>
            <input
              type="range"
              min={0.4}
              max={4}
              step={0.1}
              value={speed}
              onChange={(event) => setSpeed(Number(event.target.value))}
              className="w-full accent-indigo-600"
            />
          </label>
        </div>

        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          {RACE_FAMILIES.map((family) => (
            <WorkLane
              key={family.id}
              family={family}
              n={n}
              globalOps={globalOps}
            >
              {n <= 10 ? (
                <ClassroomScene
                  n={classroomN}
                  globalOps={globalOps}
                  activeId={family.id}
                />
              ) : (
                <OperationGrid
                  n={n}
                  globalOps={globalOps}
                  id={family.id}
                  color={family.color}
                />
              )}
            </WorkLane>
          ))}
        </div>
        <p className="mt-3 text-xs text-slate-500">
          Con n ≤ 10 ves el aula (lista, saludos, tríos, subconjuntos). Con n
          mayor las celdas representan operaciones: cada cuadrito es un paso de
          trabajo.
        </p>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">
              2. Gráfico que crece
            </h2>
            <p className="mt-1 max-w-2xl text-sm text-slate-600">
              Pulsa play y mira la línea vertical avanzar. En escala lineal el
              exponencial se come la pantalla; en logarítmica se ve cómo los
              polinomios siguen siendo rectas suaves.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              onClick={() => {
                if (chartN >= CHART_MAX) setChartN(1);
                setChartPlaying((value) => !value);
              }}
            >
              {chartPlaying ? (
                <Pause className="mr-2 h-4 w-4" />
              ) : (
                <Play className="mr-2 h-4 w-4" />
              )}
              Animar n
            </Button>
            <Button
              variant={logScale ? "default" : "outline"}
              onClick={() => setLogScale(true)}
            >
              Eje log
            </Button>
            <Button
              variant={!logScale ? "default" : "outline"}
              onClick={() => setLogScale(false)}
            >
              Eje lineal
            </Button>
          </div>
        </div>
        <div className="mb-3 flex flex-wrap gap-2">
          {FAMILIES.map((family) => (
            <button
              key={family.id}
              onClick={() => toggleFamily(family.id)}
              className={cn(
                "rounded-full border px-3 py-1 text-sm",
                visible.includes(family.id)
                  ? "text-white"
                  : "border-slate-200 bg-white text-slate-500"
              )}
              style={{
                background: visible.includes(family.id)
                  ? family.color
                  : undefined,
                borderColor: family.color,
              }}
            >
              {family.shortLabel}
            </button>
          ))}
        </div>
        <GrowthChart
          n={Math.round(chartN)}
          nMax={CHART_MAX}
          visible={visible}
          logScale={logScale}
        />
        <label className="mt-3 block">
          <div className="mb-1 text-sm text-slate-600">
            n del gráfico = {Math.round(chartN)} · O(2ⁿ) ={" "}
            {formatOps(operations("exponential", Math.round(chartN)))} · O(n³) ={" "}
            {formatOps(operations("cubic", Math.round(chartN)))}
          </div>
          <input
            type="range"
            min={1}
            max={CHART_MAX}
            value={Math.round(chartN)}
            onChange={(event) => {
              setChartPlaying(false);
              setChartN(Number(event.target.value));
            }}
            className="w-full accent-indigo-600"
          />
        </label>
      </section>

      <RealStopwatch n={n} />

      <DoublingDemo opsPerSec={opsPerSec} />

      <UniverseTable opsPerSec={opsPerSec || 1_000_000_000} highlightN={n} />

      <section className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
        <div className="flex items-start gap-3">
          <BookOpen className="mt-1 h-6 w-6 text-amber-700" />
          <div>
            <h2 className="text-2xl font-bold text-slate-900">
              Cómo explicarlo en 5 minutos
            </h2>
            <ol className="mt-3 list-decimal space-y-2 pl-5 text-slate-700">
              <li>
                Enseña n = 6 en el aula: pasar lista (n), saludos (n²), tríos
                (n³) y todos los grupos posibles (2ⁿ).
              </li>
              <li>
                Sube n hasta 12–16 y dale a Play. Pregunta: ¿quién termina
                primero y por qué?
              </li>
              <li>
                Abre el gráfico en eje lineal y luego en log. El truco: un
                polinomio en log-log es casi una recta; 2ⁿ se pone vertical.
              </li>
              <li>
                Corre el cronómetro real. Aunque los n no sean idénticos, se
                siente que 2ⁿ obliga a bajar n para no congelar el ordenador.
              </li>
              <li>
                Cierra con la tabla: a n = 60, n³ cabe en una clase; 2⁶⁰ no cabe
                en la historia del universo.
              </li>
            </ol>
            <p className="mt-3 text-sm text-slate-600">
              Frase para llevar:{" "}
              <strong>polinómico significa tratable cuando n crece</strong>. No
              significa “siempre instantáneo”, ni que n¹⁰⁰ sea práctico, pero sí
              que no explota como 2ⁿ.
            </p>
          </div>
        </div>
      </section>

      <p className="flex items-center gap-2 text-xs text-slate-400">
        <Clock className="h-4 w-4" />
        Calibración de este navegador: {formatOps(opsPerSec)} operaciones/s
        aproximadas. Un CPU real hace más trabajo útil por ciclo; aquí medimos
        bucles de JavaScript, que es lo que tus alumnos pueden tocar.
      </p>
    </div>
  );
}

function DoublingDemo({ opsPerSec }: { opsPerSec: number }) {
  const samples: { id: ComplexityId; a: number; b: number; note: string }[] = [
    { id: "linear", a: 1_000_000, b: 2_000_000, note: "n → 2n, se espera ×2" },
    { id: "quadratic", a: 800, b: 1600, note: "n → 2n, se espera ×4" },
    { id: "cubic", a: 80, b: 160, note: "n → 2n, se espera ×8" },
    { id: "exponential", a: 22, b: 23, note: "n → n+1, se espera ×2" },
  ];

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-2xl font-bold text-slate-900">
        3. El truco de duplicar n
      </h2>
      <p className="mt-1 max-w-3xl text-sm text-slate-600">
        En un polinomio de grado k, duplicar n multiplica el tiempo por 2ᵏ. En
        un exponencial, <em>sumar 1</em> a n ya duplica el trabajo. Esta tabla
        usa la velocidad medida de tu navegador.
      </p>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[720px] text-sm">
          <thead>
            <tr className="border-b text-left text-slate-500">
              <th className="py-2 pr-3 font-medium">Familia</th>
              <th className="py-2 pr-3 font-medium">De n</th>
              <th className="py-2 pr-3 font-medium">A</th>
              <th className="py-2 pr-3 font-medium">Tiempo estimado</th>
              <th className="py-2 pr-3 font-medium">Factor</th>
            </tr>
          </thead>
          <tbody>
            {samples.map((sample) => {
              const family = FAMILIES.find((item) => item.id === sample.id)!;
              const ta =
                operations(sample.id, sample.a) / Math.max(1, opsPerSec);
              const tb =
                operations(sample.id, sample.b) / Math.max(1, opsPerSec);
              const factor = tb / Math.max(ta, 1e-12);
              return (
                <tr key={sample.id} className="border-b border-slate-100">
                  <td
                    className="py-2.5 pr-3 font-semibold"
                    style={{ color: family.color }}
                  >
                    {family.shortLabel}
                  </td>
                  <td className="py-2.5 pr-3 tabular-nums">
                    {sample.a.toLocaleString("es-ES")}
                  </td>
                  <td className="py-2.5 pr-3 tabular-nums">
                    {sample.b.toLocaleString("es-ES")}
                  </td>
                  <td className="py-2.5 pr-3 tabular-nums">
                    {formatDuration(ta)} → {formatDuration(tb)}
                  </td>
                  <td className="py-2.5 pr-3">
                    ×{factor.toFixed(1)}{" "}
                    <span className="text-slate-500">({sample.note})</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
