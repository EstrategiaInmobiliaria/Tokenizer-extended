import { BOOK, ERAS, TIMELINE, type EraId } from "~/data/ieGuide";
import { cn } from "~/utils/cn";

const ERA_COLORS: Record<EraId, string> = {
  preindustrial: "border-amber-400 bg-amber-50",
  "primera-revolucion": "border-orange-500 bg-orange-50",
  "segunda-revolucion": "border-rose-500 bg-rose-50",
  "admin-cientifica": "border-teal-500 bg-teal-50",
  "sistemas-calidad": "border-indigo-500 bg-indigo-50",
};

const ERA_DOT: Record<EraId, string> = {
  preindustrial: "bg-amber-500",
  "primera-revolucion": "bg-orange-500",
  "segunda-revolucion": "bg-rose-500",
  "admin-cientifica": "bg-teal-500",
  "sistemas-calidad": "bg-indigo-500",
};

export function IeTimeline() {
  return (
    <section id="cronologia" className="scroll-mt-24">
      <header className="mb-6">
        <p className="text-sm font-semibold uppercase tracking-widest text-teal-700">
          Pilar I · Capítulo 1 (y vínculos a 5, 6, 7 y 13)
        </p>
        <h2 className="mt-1 text-3xl font-bold text-slate-900">
          Cronología de la ingeniería industrial
        </h2>
        <p className="mt-2 max-w-3xl text-slate-600">
          Cinco eras según {BOOK.authors.split(",")[0]} et al. Cada hito apunta
          al capítulo donde el libro lo desarrolla, para que leas el texto con
          un mapa mental ya armado.
        </p>
      </header>

      <div className="mb-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {ERAS.map((era, index) => (
          <div
            key={era.id}
            className={cn(
              "rounded-xl border-l-4 p-3 shadow-sm",
              ERA_COLORS[era.id]
            )}
          >
            <p className="text-xs font-bold uppercase tracking-wide text-slate-500">
              Era {index + 1}
            </p>
            <h3 className="font-semibold text-slate-900">{era.label}</h3>
            <p className="text-xs text-slate-500">{era.period}</p>
            <p className="mt-2 text-sm text-slate-700">{era.summary}</p>
          </div>
        ))}
      </div>

      <ol className="relative ml-3 border-l-2 border-slate-200 pl-8">
        {TIMELINE.map((event) => (
          <li key={`${event.year}-${event.title}`} className="mb-8 last:mb-0">
            <span
              className={cn(
                "absolute -left-[9px] mt-1.5 h-4 w-4 rounded-full ring-4 ring-white",
                ERA_DOT[event.era]
              )}
            />
            <div className="flex flex-wrap items-baseline gap-2">
              <time className="font-mono text-sm font-bold text-slate-800">
                {event.year}
              </time>
              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                {event.chapter}
              </span>
            </div>
            <h3 className="mt-1 text-lg font-semibold text-slate-900">
              {event.title}
            </h3>
            <p className="mt-1 text-slate-600">{event.detail}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
