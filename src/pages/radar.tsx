import type { NextPage } from "next";
import Head from "next/head";
import Link from "next/link";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import {
  ArrowLeft,
  Check,
  Clipboard,
  Download,
  ExternalLink,
  Link2,
  Plus,
  Trash2,
  Wand2,
} from "lucide-react";

type Signal = {
  id: string;
  url: string;
  platform: string;
  category: string;
  insight: string;
  status: "capturada" | "analizada" | "publicada";
  createdAt: string;
};

const STORAGE_KEY = "agartha-opportunity-radar";

const analysisPrompt = (signal?: Signal) => `Actúa como estratega de contenido y negocios para Agartha Bienes Raíces.

Analiza esta señal:
Enlace: ${signal?.url || "[PEGA AQUÍ EL ENLACE]"}
Plataforma: ${signal?.platform || "[PLATAFORMA]"}
Categoría: ${signal?.category || "[CATEGORÍA]"}
Observación: ${signal?.insight || "[POR QUÉ LLAMÓ MI ATENCIÓN]"}

Entrega:
1. Hook y mecanismo de retención.
2. Idea central, sin copiar frases del creador.
3. Relación legítima con inversión, patrimonio o estrategia inmobiliaria.
4. Tres guiones originales de 30 segundos para Instagram y TikTok.
5. Un carrusel de siete láminas.
6. CTA que lleve al formulario de Agartha.
7. Riesgos legales, afirmaciones que deban comprobarse y datos que no deben prometerse.

No garantices rendimientos, no inventes cifras y separa hechos de opiniones.`;

const Radar: NextPage = () => {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [selectedId, setSelectedId] = useState<string>("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        setSignals(JSON.parse(stored) as Signal[]);
      } catch {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    }
    setLoaded(true);
  }, []);

  useEffect(() => {
    if (loaded) {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(signals));
    }
  }, [signals, loaded]);

  const selected = useMemo(
    () => signals.find((signal) => signal.id === selectedId),
    [selectedId, signals]
  );

  const addSignal = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const signal: Signal = {
      id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      url: String(form.get("url") || ""),
      platform: String(form.get("platform") || "Instagram"),
      category: String(form.get("category") || "Contenido"),
      insight: String(form.get("insight") || ""),
      status: "capturada",
      createdAt: new Date().toISOString(),
    };
    setSignals((current) => [signal, ...current]);
    setSelectedId(signal.id);
    event.currentTarget.reset();
  };

  const updateStatus = (id: string, status: Signal["status"]) => {
    setSignals((current) =>
      current.map((signal) => (signal.id === id ? { ...signal, status } : signal))
    );
  };

  const copyPrompt = async () => {
    await navigator.clipboard.writeText(analysisPrompt(selected));
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  };

  const exportCsv = () => {
    const rows = [
      ["fecha", "plataforma", "categoria", "estado", "enlace", "observacion"],
      ...signals.map((signal) => [
        signal.createdAt,
        signal.platform,
        signal.category,
        signal.status,
        signal.url,
        signal.insight,
      ]),
    ];
    const csv = rows
      .map((row) =>
        row.map((value) => `"${value.replaceAll('"', '""')}"`).join(",")
      )
      .join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "radar-agartha.csv";
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <Head>
        <title>Radar de oportunidades | Agartha</title>
        <meta
          name="description"
          content="Captura y transforma señales digitales en contenido y oportunidades para Agartha."
        />
      </Head>
      <main className="min-h-screen bg-[#f2f0e9] text-[#17352b]">
        <header className="border-b border-[#17352b]/10 bg-[#17352b] px-6 py-5 text-white">
          <div className="mx-auto flex max-w-7xl items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <ArrowLeft size={18} />
              <span className="font-semibold tracking-[0.18em]">AGARTHA</span>
            </Link>
            <button
              onClick={exportCsv}
              disabled={!signals.length}
              className="flex items-center gap-2 rounded-full border border-white/20 px-4 py-2 text-sm disabled:opacity-40"
            >
              <Download size={16} /> Exportar CSV
            </button>
          </div>
        </header>

        <div className="mx-auto max-w-7xl px-6 py-12">
          <div className="mb-12 grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
            <div>
              <p className="section-label">Herramienta privada en tu navegador</p>
              <h1 className="max-w-3xl text-4xl font-medium tracking-tight sm:text-5xl">
                Convierte tu scrolling en un{" "}
                <span className="font-serif italic text-[#9a7d3c]">
                  inventario de oportunidades.
                </span>
              </h1>
            </div>
            <div className="flex gap-3">
              {(["capturada", "analizada", "publicada"] as const).map((status) => (
                <div key={status} className="rounded-2xl bg-white px-4 py-3 text-center">
                  <p className="text-xl font-semibold">
                    {signals.filter((signal) => signal.status === status).length}
                  </p>
                  <p className="mt-1 text-xs capitalize text-[#687a73]">{status}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-[0.88fr_1.12fr]">
            <section className="rounded-[28px] bg-white p-6 sm:p-8">
              <div className="mb-7 flex items-center gap-3">
                <span className="grid h-10 w-10 place-items-center rounded-full bg-[#e8eadf]">
                  <Plus size={19} />
                </span>
                <div>
                  <h2 className="text-xl font-medium">Capturar una señal</h2>
                  <p className="text-sm text-[#687a73]">Toma menos de un minuto.</p>
                </div>
              </div>
              <form onSubmit={addSignal} className="space-y-5">
                <label className="form-field">
                  <span>Enlace</span>
                  <input
                    name="url"
                    type="url"
                    required
                    placeholder="https://instagram.com/reel/..."
                  />
                </label>
                <div className="grid gap-4 sm:grid-cols-2">
                  <label className="form-field">
                    <span>Plataforma</span>
                    <select name="platform" defaultValue="Instagram">
                      <option>Instagram</option>
                      <option>TikTok</option>
                      <option>YouTube</option>
                      <option>LinkedIn</option>
                      <option>Otro</option>
                    </select>
                  </label>
                  <label className="form-field">
                    <span>Categoría</span>
                    <select name="category" defaultValue="Contenido">
                      <option>Contenido</option>
                      <option>Desarrollo</option>
                      <option>Mercado</option>
                      <option>Prospecto</option>
                      <option>IA y tecnología</option>
                    </select>
                  </label>
                </div>
                <label className="form-field">
                  <span>¿Por qué vale la pena?</span>
                  <textarea
                    name="insight"
                    rows={4}
                    required
                    className="rounded-xl border border-[#17352b]/15 bg-white px-4 py-3 font-normal outline-none focus:border-[#17352b]/50"
                    placeholder="Hook, dato, objeción, proyecto o señal que detectaste..."
                  />
                </label>
                <button className="button button-dark w-full justify-center">
                  Guardar señal <Link2 size={17} />
                </button>
              </form>
              <p className="mt-5 text-xs leading-5 text-[#687a73]">
                La información se guarda únicamente en este navegador. No
                pegues datos bancarios, contraseñas ni información confidencial
                de clientes.
              </p>
            </section>

            <section className="rounded-[28px] bg-[#17352b] p-6 text-white sm:p-8">
              <div className="mb-7 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-[#d7c69a]">
                    Biblioteca
                  </p>
                  <h2 className="mt-2 text-2xl font-medium">
                    {signals.length} señales guardadas
                  </h2>
                </div>
                <button onClick={copyPrompt} className="button button-light">
                  {copied ? <Check size={17} /> : <Clipboard size={17} />}
                  {copied ? "Copiado" : "Copiar prompt de análisis"}
                </button>
              </div>

              {!signals.length ? (
                <div className="grid min-h-[390px] place-items-center rounded-2xl border border-dashed border-white/20 text-center">
                  <div>
                    <Wand2 className="mx-auto text-[#d7c69a]" />
                    <p className="mt-4 font-medium">Tu radar está listo.</p>
                    <p className="mt-2 max-w-xs text-sm text-white/55">
                      Guarda el primer enlace y conviértelo en contenido original.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="max-h-[580px] space-y-3 overflow-y-auto pr-1">
                  {signals.map((signal) => (
                    <article
                      key={signal.id}
                      onClick={() => setSelectedId(signal.id)}
                      className={`cursor-pointer rounded-2xl border p-5 transition ${
                        selectedId === signal.id
                          ? "border-[#d7c69a] bg-white/10"
                          : "border-white/10 bg-white/[0.04] hover:bg-white/[0.07]"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="text-xs uppercase tracking-wider text-[#d7c69a]">
                            {signal.platform} · {signal.category}
                          </p>
                          <p className="mt-2 line-clamp-2 text-sm leading-6 text-white/75">
                            {signal.insight}
                          </p>
                        </div>
                        <a
                          href={signal.url}
                          target="_blank"
                          rel="noreferrer"
                          onClick={(event) => event.stopPropagation()}
                          aria-label="Abrir enlace"
                        >
                          <ExternalLink size={17} />
                        </a>
                      </div>
                      <div className="mt-4 flex items-center justify-between gap-3">
                        <select
                          value={signal.status}
                          onClick={(event) => event.stopPropagation()}
                          onChange={(event) =>
                            updateStatus(signal.id, event.target.value as Signal["status"])
                          }
                          className="rounded-full border border-white/15 bg-[#17352b] px-3 py-1.5 text-xs capitalize"
                        >
                          <option value="capturada">Capturada</option>
                          <option value="analizada">Analizada</option>
                          <option value="publicada">Publicada</option>
                        </select>
                        <button
                          onClick={(event) => {
                            event.stopPropagation();
                            setSignals((current) =>
                              current.filter((item) => item.id !== signal.id)
                            );
                          }}
                          aria-label="Eliminar señal"
                          className="text-white/40 hover:text-white"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </section>
          </div>
        </div>
      </main>
    </>
  );
};

export default Radar;
