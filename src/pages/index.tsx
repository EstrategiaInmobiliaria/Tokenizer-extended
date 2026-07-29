import type { NextPage } from "next";
import Head from "next/head";
import Link from "next/link";
import { useState, type FormEvent } from "react";
import {
  ArrowRight,
  BarChart3,
  Building2,
  Check,
  Instagram,
  Link2,
  Menu,
  MessageCircle,
  ShieldCheck,
  TrendingUp,
  Wand2,
  X,
} from "lucide-react";

const links = {
  instagram: process.env.NEXT_PUBLIC_INSTAGRAM_URL || "#contacto",
  tiktok: process.env.NEXT_PUBLIC_TIKTOK_URL || "#contacto",
  whatsapp: process.env.NEXT_PUBLIC_WHATSAPP_URL || "",
  email: process.env.NEXT_PUBLIC_CONTACT_EMAIL || "",
  prompts: process.env.NEXT_PUBLIC_PROMPTS_CHECKOUT_URL || "#contacto",
  strategy: process.env.NEXT_PUBLIC_STRATEGY_BOOKING_URL || "#contacto",
};

const incomeLines = [
  {
    icon: Building2,
    eyebrow: "Patrimonio",
    title: "Desarrollos inmobiliarios",
    description:
      "Oportunidades seleccionadas y acompañamiento para decidir con estrategia, datos y atención personal.",
    cta: "Ver oportunidades",
    href: "#desarrollos",
  },
  {
    icon: BarChart3,
    eyebrow: "Consultoría",
    title: "Estrategia inmobiliaria",
    description:
      "Diagnóstico para propietarios, compradores e inversionistas que buscan claridad antes de comprometer capital.",
    cta: "Agendar diagnóstico",
    href: links.strategy,
  },
  {
    icon: Wand2,
    eyebrow: "Producto digital",
    title: "Sistemas y prompts de IA",
    description:
      "Métodos para investigar mercados, crear contenido y convertir señales digitales en oportunidades comerciales.",
    cta: "Obtener el sistema",
    href: links.prompts,
  },
];

const processSteps = [
  ["01", "Detectamos", "Convertimos tendencias, enlaces y conversaciones en señales útiles."],
  ["02", "Validamos", "Contrastamos demanda, ubicación, números y contexto antes de recomendar."],
  ["03", "Ejecutamos", "Conectamos la oportunidad con contenido, asesoría o inversión."],
];

const Home: NextPage = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const submitLead = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const message = encodeURIComponent(
      `Hola, soy ${String(form.get("name") || "")}. Me interesa: ${String(
        form.get("interest") || ""
      )}. Mi contacto es ${String(form.get("contact") || "")}. Quiero recibir información de Agartha.`
    );

    setSubmitted(true);
    if (links.whatsapp) {
      const separator = links.whatsapp.includes("?") ? "&" : "?";
      window.open(`${links.whatsapp}${separator}text=${message}`, "_blank");
    } else if (links.email) {
      window.location.href = `mailto:${links.email}?subject=Nuevo contacto Agartha&body=${message}`;
    }
  };

  return (
    <>
      <Head>
        <title>Agartha | Estrategia inmobiliaria con visión</title>
        <meta
          name="description"
          content="Estrategia inmobiliaria, desarrollos seleccionados y sistemas de IA para tomar mejores decisiones."
        />
        <meta property="og:title" content="Agartha Bienes Raíces" />
        <meta
          property="og:description"
          content="Detectamos oportunidades. Diseñamos estrategia. Construimos patrimonio."
        />
      </Head>
      <div className="min-h-screen overflow-hidden bg-stone-50 text-[#17352b]">
        <header className="absolute inset-x-0 top-0 z-50">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
            <a href="#" className="flex items-center gap-3" aria-label="Agartha">
              <span className="grid h-10 w-10 place-items-center rounded-full border border-white/30 text-lg font-semibold text-white">
                A
              </span>
              <span className="text-lg font-semibold tracking-[0.2em] text-white">
                AGARTHA
              </span>
            </a>
            <nav className="hidden items-center gap-8 text-sm text-white/80 lg:flex">
              <a href="#servicios">Soluciones</a>
              <a href="#desarrollos">Desarrollos</a>
              <a href="#metodo">Método</a>
              <a className="nav-cta" href="#contacto">
                Hablemos
              </a>
            </nav>
            <button
              className="text-white lg:hidden"
              onClick={() => setMenuOpen(!menuOpen)}
              aria-label="Abrir menú"
            >
              {menuOpen ? <X /> : <Menu />}
            </button>
          </div>
          {menuOpen && (
            <nav className="mx-4 flex flex-col gap-4 rounded-2xl bg-white p-6 text-sm shadow-xl lg:hidden">
              {[
                ["Soluciones", "#servicios"],
                ["Desarrollos", "#desarrollos"],
                ["Método", "#metodo"],
                ["Contacto", "#contacto"],
              ].map(([label, href]) => (
                <a key={href} href={href} onClick={() => setMenuOpen(false)}>
                  {label}
                </a>
              ))}
            </nav>
          )}
        </header>

        <main>
          <section className="hero-grid relative flex min-h-[820px] items-end bg-[#17352b] px-6 pb-24 pt-36 text-white lg:px-10 lg:pb-28">
            <div className="hero-orb hero-orb-one" />
            <div className="hero-orb hero-orb-two" />
            <div className="relative mx-auto grid w-full max-w-7xl gap-16 lg:grid-cols-[1.25fr_0.75fr] lg:items-end">
              <div>
                <p className="eyebrow-light">
                  <span />
                  Estrategia inmobiliaria + inteligencia
                </p>
                <h1 className="max-w-4xl text-5xl font-medium leading-[0.98] tracking-[-0.045em] sm:text-7xl lg:text-[92px]">
                  Convertimos señales en{" "}
                  <em className="font-serif text-[#d7c69a]">patrimonio.</em>
                </h1>
                <p className="mt-8 max-w-2xl text-lg leading-8 text-white/70">
                  Agartha une criterio inmobiliario, tecnología y una red
                  comercial para detectar oportunidades y llevarlas a una
                  decisión concreta.
                </p>
                <div className="mt-10 flex flex-wrap gap-4">
                  <a className="button button-light" href="#desarrollos">
                    Explorar oportunidades <ArrowRight size={17} />
                  </a>
                  <a className="button button-ghost" href="#contacto">
                    Hablar con un asesor
                  </a>
                </div>
              </div>
              <div className="glass-panel">
                <div className="mb-8 flex items-start justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-[0.24em] text-white/50">
                      Ecosistema Agartha
                    </p>
                    <p className="mt-2 text-2xl font-medium">
                      Una señal. Tres vías de valor.
                    </p>
                  </div>
                  <TrendingUp className="text-[#d7c69a]" />
                </div>
                {[
                  "Inversión inmobiliaria",
                  "Estrategia personalizada",
                  "Sistemas digitales con IA",
                ].map((item) => (
                  <div
                    key={item}
                    className="flex items-center justify-between border-t border-white/10 py-4 text-sm text-white/70"
                  >
                    <span>{item}</span>
                    <Check size={17} className="text-[#d7c69a]" />
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section id="servicios" className="px-6 py-24 lg:px-10 lg:py-32">
            <div className="mx-auto max-w-7xl">
              <div className="mb-14 grid gap-8 lg:grid-cols-2 lg:items-end">
                <div>
                  <p className="section-label">Un sistema, no publicaciones aisladas</p>
                  <h2 className="section-title">
                    Cada interacción puede acercarte a una{" "}
                    <span>decisión de valor.</span>
                  </h2>
                </div>
                <p className="max-w-xl justify-self-end leading-7 text-[#587067]">
                  El scrolling y la IA no producen dinero por sí solos. El
                  modelo los convierte en investigación, contenido, prospectos
                  y productos que sí pueden venderse.
                </p>
              </div>
              <div className="grid gap-5 lg:grid-cols-3">
                {incomeLines.map((line) => {
                  const Icon = line.icon;
                  return (
                    <article key={line.title} className="income-card group">
                      <div className="mb-10 grid h-12 w-12 place-items-center rounded-full bg-[#eef0e8]">
                        <Icon size={21} />
                      </div>
                      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#9a7d3c]">
                        {line.eyebrow}
                      </p>
                      <h3 className="mt-4 text-3xl font-medium tracking-tight">
                        {line.title}
                      </h3>
                      <p className="mt-5 flex-1 leading-7 text-[#687a73]">
                        {line.description}
                      </p>
                      <a href={line.href} className="mt-8 flex items-center gap-2 font-semibold">
                        {line.cta}
                        <ArrowRight size={17} className="transition group-hover:translate-x-1" />
                      </a>
                    </article>
                  );
                })}
              </div>
            </div>
          </section>

          <section id="desarrollos" className="bg-[#e8eadf] px-6 py-24 lg:px-10 lg:py-32">
            <div className="mx-auto grid max-w-7xl gap-14 lg:grid-cols-[0.85fr_1.15fr] lg:items-center">
              <div>
                <p className="section-label">Portafolio privado</p>
                <h2 className="section-title">
                  No vendemos metros cuadrados.{" "}
                  <span>Diseñamos decisiones.</span>
                </h2>
                <p className="mt-7 max-w-lg leading-7 text-[#587067]">
                  Recibe oportunidades de desarrollos comercializados por
                  Agartha según tu objetivo, horizonte y nivel de inversión.
                </p>
                <ul className="mt-9 space-y-4">
                  {[
                    "Selección según perfil y objetivo",
                    "Análisis comercial y financiero",
                    "Acompañamiento durante el proceso",
                  ].map((item) => (
                    <li key={item} className="flex items-center gap-3">
                      <span className="grid h-6 w-6 place-items-center rounded-full bg-[#17352b] text-white">
                        <Check size={14} />
                      </span>
                      {item}
                    </li>
                  ))}
                </ul>
                <a className="button button-dark mt-10" href="#contacto">
                  Solicitar portafolio <ArrowRight size={17} />
                </a>
              </div>
              <div className="property-card">
                <div className="property-lines" />
                <div className="relative flex min-h-[464px] flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="rounded-full border border-white/20 px-4 py-2 text-xs uppercase tracking-[0.18em]">
                      Selección Agartha
                    </span>
                    <Building2 className="text-[#d7c69a]" />
                  </div>
                  <div>
                    <p className="max-w-md font-serif text-4xl italic leading-tight text-[#d7c69a] sm:text-5xl">
                      La oportunidad correcta empieza con la pregunta correcta.
                    </p>
                    <div className="mt-10 grid grid-cols-2 gap-4 border-t border-white/10 pt-6 text-sm">
                      <div>
                        <p className="text-white/40">Enfoque</p>
                        <p className="mt-1">México · mercados selectos</p>
                      </div>
                      <div>
                        <p className="text-white/40">Acceso</p>
                        <p className="mt-1">Bajo perfil de inversión</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section id="metodo" className="bg-white px-6 py-24 lg:px-10 lg:py-32">
            <div className="mx-auto max-w-7xl">
              <div className="max-w-3xl">
                <p className="section-label">Método Agartha</p>
                <h2 className="section-title">
                  De un enlace guardado a una{" "}
                  <span>oportunidad accionable.</span>
                </h2>
              </div>
              <div className="mt-16 grid border-y border-[#17352b]/10 lg:grid-cols-3">
                {processSteps.map(([number, title, copy]) => (
                  <div key={number} className="process-step">
                    <p className="font-serif text-4xl italic text-[#b39a5c]">{number}</p>
                    <h3 className="mt-8 text-2xl font-medium">{title}</h3>
                    <p className="mt-3 max-w-sm leading-7 text-[#687a73]">{copy}</p>
                  </div>
                ))}
              </div>
              <div className="radar-callout">
                <div className="flex items-start gap-5">
                  <div className="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-[#17352b] text-white">
                    <Link2 size={20} />
                  </div>
                  <div>
                    <h3 className="text-xl font-medium">Radar de oportunidades</h3>
                    <p className="mt-2 text-[#687a73]">
                      Captura enlaces, clasifica señales y genera tu siguiente acción con IA.
                    </p>
                  </div>
                </div>
                <Link className="button button-dark shrink-0" href="/radar">
                  Abrir radar <ArrowRight size={17} />
                </Link>
              </div>
            </div>
          </section>

          <section id="contacto" className="bg-[#c6a96a] px-6 py-24 lg:px-10 lg:py-32">
            <div className="mx-auto grid max-w-7xl gap-14 lg:grid-cols-[0.9fr_1.1fr]">
              <div>
                <p className="mb-6 text-xs font-semibold uppercase tracking-[0.25em] text-[#17352b]/65">
                  Próximo paso
                </p>
                <h2 className="text-5xl font-medium leading-[1.02] tracking-[-0.04em] sm:text-6xl">
                  Cuéntanos qué quieres <em className="font-serif">construir.</em>
                </h2>
                <p className="mt-7 max-w-lg leading-7 text-[#17352b]/70">
                  Comparte tu objetivo y te contactaremos con el siguiente paso
                  más útil, sin promesas de rentabilidad ni presión comercial.
                </p>
                <div className="mt-10 flex gap-3">
                  <a href={links.instagram} aria-label="Instagram" className="social-button">
                    <Instagram size={19} />
                  </a>
                  <a href={links.tiktok} aria-label="TikTok" className="social-button text-sm font-bold">
                    TT
                  </a>
                  {links.whatsapp && (
                    <a href={links.whatsapp} aria-label="WhatsApp" className="social-button">
                      <MessageCircle size={19} />
                    </a>
                  )}
                </div>
              </div>
              <form onSubmit={submitLead} className="lead-form">
                <div className="grid gap-5 sm:grid-cols-2">
                  <label className="form-field">
                    <span>Nombre</span>
                    <input name="name" required placeholder="Tu nombre" />
                  </label>
                  <label className="form-field">
                    <span>WhatsApp o email</span>
                    <input name="contact" required placeholder="Tu medio de contacto" />
                  </label>
                </div>
                <label className="form-field mt-5">
                  <span>¿Qué te interesa?</span>
                  <select name="interest" required defaultValue="">
                    <option value="" disabled>Selecciona una opción</option>
                    <option>Comprar o invertir en un desarrollo</option>
                    <option>Vender o estructurar un proyecto</option>
                    <option>Contratar estrategia inmobiliaria</option>
                    <option>Adquirir sistemas y prompts de IA</option>
                  </select>
                </label>
                <button className="button button-dark mt-7 w-full justify-center">
                  Solicitar información <ArrowRight size={17} />
                </button>
                {submitted && !links.whatsapp && !links.email && (
                  <p className="mt-4 text-center text-sm text-[#856b30]">
                    El formulario está listo. Falta conectar el WhatsApp o correo oficial.
                  </p>
                )}
                <p className="mt-5 flex items-start gap-2 text-xs leading-5 text-[#687a73]">
                  <ShieldCheck size={15} className="mt-0.5 shrink-0" />
                  Tus datos se usarán únicamente para responder esta solicitud.
                  Agartha no garantiza rendimientos de inversión.
                </p>
              </form>
            </div>
          </section>
        </main>

        <footer className="bg-[#102820] px-6 py-10 text-white/50 lg:px-10">
          <div className="mx-auto flex max-w-7xl flex-col gap-6 text-sm sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="font-semibold tracking-[0.18em] text-white">AGARTHA</p>
              <p className="mt-2">Bienes raíces · estrategia · inteligencia</p>
            </div>
            <div className="flex flex-wrap gap-6">
              <a href="#servicios">Soluciones</a>
              <a href="#desarrollos">Desarrollos</a>
              <a href="#contacto">Contacto</a>
            </div>
            <p>© {new Date().getFullYear()} Agartha Bienes Raíces</p>
          </div>
        </footer>
      </div>
    </>
  );
};

export default Home;
