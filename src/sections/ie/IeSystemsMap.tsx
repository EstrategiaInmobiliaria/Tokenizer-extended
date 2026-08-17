import { SUBSYSTEMS } from "~/data/ieGuide";
import { cn } from "~/utils/cn";

export function IeSystemsMap() {
  const direction = SUBSYSTEMS[0];
  const others = SUBSYSTEMS.slice(1);

  return (
    <section id="sistemas" className="scroll-mt-24">
      <header className="mb-6">
        <p className="text-sm font-semibold uppercase tracking-widest text-teal-700">
          Mapa integral · Capítulo 11
        </p>
        <h2 className="mt-1 text-3xl font-bold text-slate-900">
          La empresa como conjunto de sistemas
        </h2>
        <p className="mt-2 max-w-3xl text-slate-600">
          Dibuja un núcleo (Dirección General) y conéctalo con flechas
          bidireccionales de información. Junto a cada órgano anota objetivo,
          entradas, salidas e índices de desempeño — exactamente el método de
          estudio que propone el capítulo 11.
        </p>
      </header>

      <div className="mb-8 rounded-2xl border border-slate-200 bg-gradient-to-b from-slate-50 to-white p-6">
        <div className="mx-auto mb-6 max-w-md rounded-2xl border-2 border-slate-900 bg-slate-900 p-4 text-center text-white shadow-lg">
          <p className="text-xs uppercase tracking-widest text-teal-300">
            Cerebro
          </p>
          <h3 className="text-xl font-bold">{direction?.name}</h3>
          <p className="mt-1 text-sm text-slate-300">{direction?.role}</p>
        </div>
        <p className="mb-4 text-center text-xs font-medium uppercase tracking-wide text-slate-500">
          ↕ información bidireccional
        </p>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {others.map((system) => (
            <article
              key={system.name}
              className="rounded-xl border border-teal-200 bg-white p-3 shadow-sm"
            >
              <h4 className="font-semibold text-teal-900">{system.name}</h4>
              <p className="mt-1 text-xs text-slate-600">{system.role}</p>
            </article>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse text-sm">
          <thead>
            <tr className="bg-slate-900 text-left text-white">
              <th className="p-3">Subsistema</th>
              <th className="p-3">Objetivo</th>
              <th className="p-3">Entradas</th>
              <th className="p-3">Salidas</th>
              <th className="p-3">Índices</th>
            </tr>
          </thead>
          <tbody>
            {SUBSYSTEMS.map((system, index) => (
              <tr
                key={system.name}
                className={cn(index % 2 === 0 ? "bg-white" : "bg-slate-50")}
              >
                <td className="p-3 font-semibold text-slate-900">
                  {system.name}
                </td>
                <td className="p-3 text-slate-700">{system.role}</td>
                <td className="p-3 text-slate-600">{system.inputs}</td>
                <td className="p-3 text-slate-600">{system.outputs}</td>
                <td className="p-3 text-slate-600">{system.kpis}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
