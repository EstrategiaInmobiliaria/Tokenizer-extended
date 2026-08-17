import { CHAPTERS, type Pillar } from "~/data/ieGuide";
import { cn } from "~/utils/cn";

const PILLAR_STYLE: Record<Pillar, string> = {
  cronologia: "bg-amber-100 text-amber-800",
  flujos: "bg-sky-100 text-sky-800",
  organigramas: "bg-violet-100 text-violet-800",
};

const PILLAR_LABEL: Record<Pillar, string> = {
  cronologia: "Cronología",
  flujos: "Flujos",
  organigramas: "Organigramas",
};

export function IeChapterMap() {
  return (
    <section id="capitulos" className="scroll-mt-24">
      <header className="mb-6">
        <p className="text-sm font-semibold uppercase tracking-widest text-teal-700">
          Ruta de aprendizaje · 13 capítulos
        </p>
        <h2 className="mt-1 text-3xl font-bold text-slate-900">
          Cómo esquematizar cada capítulo
        </h2>
        <p className="mt-2 max-w-3xl text-slate-600">
          No leas el libro de corrido sin mapa. Por cada capítulo: (1) identifica
          el pilar, (2) dibuja la figura clave de memoria, (3) anota 5 palabras
          clave, (4) resuelve el caso del final como si fueras el egresado que
          el prefacio describe.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-2">
        {CHAPTERS.map((chapter) => (
          <article
            key={chapter.number}
            className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
          >
            <div className="flex items-start justify-between gap-2">
              <h3 className="text-lg font-semibold text-slate-900">
                <span className="mr-2 font-mono text-teal-700">
                  {String(chapter.number).padStart(2, "0")}
                </span>
                {chapter.title}
              </h3>
              <span className="shrink-0 text-xs text-slate-400">
                pp. {chapter.pages}
              </span>
            </div>
            <div className="mt-2 flex flex-wrap gap-1">
              {chapter.pillars.map((pillar) => (
                <span
                  key={pillar}
                  className={cn(
                    "rounded-full px-2 py-0.5 text-xs font-medium",
                    PILLAR_STYLE[pillar]
                  )}
                >
                  {PILLAR_LABEL[pillar]}
                </span>
              ))}
            </div>
            <p className="mt-3 text-sm text-slate-700">
              <span className="font-semibold">Enfoque: </span>
              {chapter.studyFocus}
            </p>
            <p className="mt-2 text-sm text-slate-600">
              <span className="font-semibold">Cómo mapearlo: </span>
              {chapter.howToMap}
            </p>
            <p className="mt-2 text-xs text-slate-500">
              Figuras ancla: {chapter.figures.join(" · ")}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
