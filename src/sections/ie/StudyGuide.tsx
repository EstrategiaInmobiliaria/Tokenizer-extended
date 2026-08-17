import Link from "next/link";
import { BOOK } from "~/data/ieGuide";
import { IeChapterMap } from "~/sections/ie/IeChapterMap";
import { IeFlowcharts } from "~/sections/ie/IeFlowcharts";
import { IeOrgCharts } from "~/sections/ie/IeOrgCharts";
import { IeQuiz } from "~/sections/ie/IeQuiz";
import { IeSystemsMap } from "~/sections/ie/IeSystemsMap";
import { IeTimeline } from "~/sections/ie/IeTimeline";

const NAV = [
  { href: "#mapa", label: "Cómo estudiar" },
  { href: "#capitulos", label: "13 capítulos" },
  { href: "#cronologia", label: "Cronología" },
  { href: "#flujos", label: "Diagramas de flujo" },
  { href: "#organigramas", label: "Organigramas" },
  { href: "#sistemas", label: "Mapa de sistemas" },
  { href: "#cuestionario", label: "Cuestionario" },
] as const;

export function StudyGuide() {
  return (
    <div className="min-h-screen bg-[#f6f1e8] text-slate-800">
      <header className="border-b border-slate-800 bg-[#0f2744] text-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-6 sm:px-8">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <Link href="/" className="text-sm text-slate-300 hover:text-white">
              ← Tiktokenizer
            </Link>
            <p className="text-xs uppercase tracking-[0.2em] text-teal-300">
              Guía de estudio referenciada
            </p>
          </div>
          <div>
            <h1 className="text-3xl font-bold leading-tight sm:text-4xl">
              {BOOK.title}
            </h1>
            <p className="mt-2 max-w-3xl text-slate-300">
              {BOOK.edition} · {BOOK.authors} · {BOOK.publisher} ({BOOK.year}).
              Esquema original para cronología, procesos y organigramas — no
              reproduce el texto del libro.
            </p>
          </div>
        </div>
        <nav className="sticky top-0 z-20 overflow-x-auto border-t border-slate-700 bg-[#0f2744]/95 backdrop-blur">
          <ul className="mx-auto flex max-w-6xl gap-1 px-4 py-2 sm:px-8">
            {NAV.map((item) => (
              <li key={item.href}>
                <a
                  href={item.href}
                  className="block whitespace-nowrap rounded-md px-3 py-1.5 text-sm text-slate-200 hover:bg-white/10 hover:text-white"
                >
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-16 px-4 py-10 sm:px-8">
        <section
          id="mapa"
          className="scroll-mt-24 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <h2 className="text-2xl font-bold text-slate-900">
            Tres pilares para mapear todo el texto
          </h2>
          <p className="mt-2 text-slate-600">
            El propio libro invita a ver la industria como historia, como
            procesos y como estructura. Estudia en ese orden: primero el
            <em> cuándo</em>, luego el <em>cómo fluye</em>, después el{" "}
            <em>quién reporta a quién</em>. El capítulo 11 cierra el sistema.
          </p>
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            <a
              href="#cronologia"
              className="rounded-xl border border-amber-200 bg-amber-50 p-4 hover:border-amber-400"
            >
              <p className="text-xs font-bold uppercase tracking-wide text-amber-700">
                I. Cronología
              </p>
              <p className="mt-1 font-semibold text-slate-900">Cinco eras</p>
              <p className="mt-1 text-sm text-slate-600">
                De Agrícola y Napoleón hasta ERP, ISO y ergonomía. Ancla cada
                autor a un capítulo.
              </p>
            </a>
            <a
              href="#flujos"
              className="rounded-xl border border-sky-200 bg-sky-50 p-4 hover:border-sky-400"
            >
              <p className="text-xs font-bold uppercase tracking-wide text-sky-700">
                II. Diagramas de flujo
              </p>
              <p className="mt-1 font-semibold text-slate-900">
                ASME + procesos clave
              </p>
              <p className="mt-1 text-sm text-slate-600">
                Información, dinero, materiales, proceso industrial, proyectos,
                métodos, SLP e inversión.
              </p>
            </a>
            <a
              href="#organigramas"
              className="rounded-xl border border-violet-200 bg-violet-50 p-4 hover:border-violet-400"
            >
              <p className="text-xs font-bold uppercase tracking-wide text-violet-700">
                III. Organigramas
              </p>
              <p className="mt-1 font-semibold text-slate-900">
                Empresa y proyectos
              </p>
              <p className="mt-1 text-sm text-slate-600">
                Seis formas clásicas de organigrama y las tres de proyecto
                (puro, funcional, matriz).
              </p>
            </a>
          </div>
          <ol className="mt-6 grid gap-2 text-sm text-slate-700 md:grid-cols-2">
            <li>
              <span className="font-semibold">1. </span>
              Recorre la cronología y marca en el índice del libro cada nombre
              (Watt, Taylor, Ford, Deming).
            </li>
            <li>
              <span className="font-semibold">2. </span>
              Copia a mano los tres flujos del capítulo 1 y el proceso 2.5
              antes de leer los capítulos técnicos.
            </li>
            <li>
              <span className="font-semibold">3. </span>
              Al llegar al 6 y al 9, redibuja organigramas con puestos de una
              empresa que conozcas.
            </li>
            <li>
              <span className="font-semibold">4. </span>
              Cierra con el mapa de sistemas (11): un recuadro por subsistema
              con KPI. Eso integra el curso.
            </li>
          </ol>
        </section>

        <IeChapterMap />
        <IeTimeline />
        <IeFlowcharts />
        <IeOrgCharts />
        <IeSystemsMap />
        <IeQuiz />

        <aside className="rounded-xl border border-dashed border-slate-400 bg-white/70 p-4 text-sm text-slate-600">
          <p>
            ISBN ebook {BOOK.isbnEbook}. Esta guía es un mapa de estudio
            original: títulos de capítulo y números de figura se usan como
            referencia; el desarrollo es para aprender, no para sustituir la
            lectura del texto.
          </p>
        </aside>
      </main>
    </div>
  );
}
