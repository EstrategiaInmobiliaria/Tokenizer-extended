import { type ReactNode } from "react";
import {
  ASME_SYMBOLS,
  INVESTMENT_STEPS,
  METHODS_STEPS,
  PROJECT_STEPS,
  SLP_STEPS,
} from "~/data/ieGuide";
import { cn } from "~/utils/cn";

function Node({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "rounded-lg border border-slate-300 bg-white px-3 py-2 text-center text-sm font-medium text-slate-800 shadow-sm",
        className
      )}
    >
      {children}
    </div>
  );
}

function Arrow({ label }: { label?: string }) {
  return (
    <div className="flex flex-col items-center py-1 text-slate-400" aria-hidden>
      <span className="text-lg leading-none">↓</span>
      {label ? (
        <span className="text-[10px] uppercase tracking-wide">{label}</span>
      ) : null}
    </div>
  );
}

function AsmeGlyph({ shape }: { shape: (typeof ASME_SYMBOLS)[number]["shape"] }) {
  if (shape === "circle") {
    return (
      <span className="inline-flex h-14 w-14 items-center justify-center rounded-full border-2 border-teal-700 bg-teal-50 text-xs font-bold text-teal-800">
        O
      </span>
    );
  }
  if (shape === "arrow") {
    return (
      <span className="inline-flex h-12 w-16 items-center justify-center text-3xl text-sky-700">
        →
      </span>
    );
  }
  if (shape === "square") {
    return (
      <span className="inline-flex h-14 w-14 items-center justify-center border-2 border-amber-600 bg-amber-50 text-xs font-bold text-amber-800">
        □
      </span>
    );
  }
  if (shape === "delay") {
    return (
      <span className="inline-flex h-14 w-12 items-center justify-center rounded-r-full border-2 border-rose-600 bg-rose-50 text-xl font-bold text-rose-800">
        D
      </span>
    );
  }
  return (
    <span
      className="inline-block h-0 w-0 border-l-[18px] border-r-[18px] border-t-[28px] border-l-transparent border-r-transparent border-t-indigo-700"
      aria-hidden
    />
  );
}

function CompanyFlows() {
  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <article className="rounded-xl border border-sky-200 bg-sky-50/60 p-4">
        <h4 className="font-semibold text-sky-900">Figura 1.1 · Información</h4>
        <p className="mb-3 text-xs text-sky-800">
          Rectángulos = áreas o entidades. Flechas = datos que circulan.
        </p>
        <div className="flex flex-col items-center">
          <Node className="bg-sky-100">Mercado / consumidores</Node>
          <Arrow />
          <Node>Investigación de mercado</Node>
          <Arrow />
          <Node className="bg-slate-900 text-white">
            Propietarios y dirección
          </Node>
          <Arrow />
          <Node>Áreas: RH, finanzas, operaciones, tecnología</Node>
          <Arrow />
          <Node>Almacén → Producción → PT → Distribución</Node>
          <Arrow />
          <Node className="bg-sky-100">Cliente (satisfacción)</Node>
          <Arrow label="retroalimentación" />
          <Node>Contabilidad / inventarios / gobierno</Node>
        </div>
      </article>

      <article className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-4">
        <h4 className="font-semibold text-emerald-900">Figura 1.2 · Dinero</h4>
        <p className="mb-3 text-xs text-emerald-800">
          Solo flujo monetario: de capital y ventas hacia costos y retorno.
        </p>
        <div className="flex flex-col items-center">
          <Node className="bg-emerald-100">Accionistas / crédito</Node>
          <Arrow />
          <Node>Finanzas y tesorería</Node>
          <Arrow />
          <div className="grid w-full grid-cols-2 gap-2">
            <Node>Compras MP</Node>
            <Node>Nómina y gastos</Node>
          </div>
          <Arrow />
          <Node>Producción (costo de transformación)</Node>
          <Arrow />
          <Node>Ventas al cliente</Node>
          <Arrow />
          <Node className="bg-emerald-100">Ingreso → utilidad / impuestos</Node>
        </div>
      </article>

      <article className="rounded-xl border border-amber-200 bg-amber-50/60 p-4">
        <h4 className="font-semibold text-amber-900">
          Figura 1.3 · Materias primas
        </h4>
        <p className="mb-3 text-xs text-amber-800">
          Flujo físico de insumos hasta el consumidor.
        </p>
        <div className="flex flex-col items-center">
          <Node className="bg-amber-100">Proveedores</Node>
          <Arrow />
          <Node>Almacén de materia prima</Node>
          <Arrow />
          <Node>Elaboración del producto</Node>
          <Arrow />
          <Node>Almacén de producto terminado</Node>
          <Arrow />
          <Node>Distribución</Node>
          <Arrow />
          <Node className="bg-amber-100">Consumidor</Node>
        </div>
      </article>
    </div>
  );
}

function IndustrialProcess() {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white p-4">
      <h4 className="mb-4 font-semibold text-slate-900">
        Figura 2.5 · Proceso industrial (entradas → transformación → salidas)
      </h4>
      <div className="flex min-w-[720px] items-stretch justify-center gap-4">
        <div className="flex w-40 flex-col justify-center gap-2">
          <p className="text-center text-xs font-bold uppercase text-slate-500">
            Entradas
          </p>
          {["A Materias primas", "B Agua", "C Aire", "D Combustibles"].map(
            (item) => (
              <Node key={item} className="bg-teal-50">
                {item}
              </Node>
            )
          )}
        </div>
        <div className="flex items-center text-2xl text-slate-400">→</div>
        <div className="flex flex-1 flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-400 bg-slate-50 p-4">
          <p className="text-xs font-bold uppercase text-slate-500">
            Proceso transformador
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            <Node className="bg-white">Operación unitaria (cambio físico)</Node>
            <Node className="bg-white">Proceso unitario (reacción química)</Node>
            <Node className="bg-white">Operación unitaria</Node>
          </div>
        </div>
        <div className="flex items-center text-2xl text-slate-400">→</div>
        <div className="flex w-44 flex-col justify-center gap-2">
          <p className="text-center text-xs font-bold uppercase text-slate-500">
            Salidas
          </p>
          <Node className="bg-emerald-100">P Producto</Node>
          <Node className="bg-emerald-50">S Subproducto</Node>
          <Node className="bg-rose-50">EG Emisiones</Node>
          <Node className="bg-sky-50">AR Aguas residuales</Node>
          <Node className="bg-slate-100">R Residuos</Node>
        </div>
      </div>
      <p className="mt-3 text-sm text-slate-600">
        El capítulo 12 se estudia como la gestión de EG, AR y R: cada salida no
        aprovechable exige prevención o tratamiento.
      </p>
    </div>
  );
}

function StepFlow({
  title,
  steps,
  caption,
}: {
  title: string;
  steps: readonly string[];
  caption: string;
}) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-4">
      <h4 className="font-semibold text-slate-900">{title}</h4>
      <p className="mb-4 text-sm text-slate-600">{caption}</p>
      <ol className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
        {steps.map((step, index) => (
          <li
            key={step}
            className="flex gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3"
          >
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-teal-700 text-sm font-bold text-white">
              {index + 1}
            </span>
            <span className="text-sm text-slate-800">{step}</span>
          </li>
        ))}
      </ol>
    </article>
  );
}

export function IeFlowcharts() {
  return (
    <section id="flujos" className="scroll-mt-24 space-y-10">
      <header>
        <p className="text-sm font-semibold uppercase tracking-widest text-teal-700">
          Pilar II · Capítulos 1, 2, 4, 6, 7, 8 y 10
        </p>
        <h2 className="mt-1 text-3xl font-bold text-slate-900">
          Diagramas de flujo de los procesos del libro
        </h2>
        <p className="mt-2 max-w-3xl text-slate-600">
          La empresa se estudia como un conjunto de procesos interrelacionados.
          Usa la simbología ASME al registrar métodos (cap. 7) y diagramas de
          bloques para los flujos de negocio.
        </p>
      </header>

      <div>
        <h3 className="mb-4 text-xl font-semibold">Simbología ASME</h3>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {ASME_SYMBOLS.map((symbol) => (
            <div
              key={symbol.id}
              className="flex flex-col items-center rounded-xl border border-slate-200 bg-white p-4 text-center"
            >
              <AsmeGlyph shape={symbol.shape} />
              <h4 className="mt-3 font-semibold text-slate-900">{symbol.name}</h4>
              <p className="mt-1 text-sm text-slate-600">{symbol.meaning}</p>
            </div>
          ))}
        </div>
        <p className="mt-3 text-sm text-slate-500">
          Recuerda: operación agrega valor; inspección verifica; transporte
          mueve; demora espera sin control; almacén espera con control.
        </p>
      </div>

      <div>
        <h3 className="mb-4 text-xl font-semibold">
          Tres flujos que mantienen viva a la empresa (cap. 1)
        </h3>
        <p className="mb-4 max-w-3xl text-slate-600">
          Analogía del texto: así como el cuerpo necesita información genética,
          gases y nutrientes, la industria necesita información, dinero y
          materia prima en circulación continua.
        </p>
        <CompanyFlows />
      </div>

      <IndustrialProcess />

      <StepFlow
        title="Figura 6.8 · Administración de proyectos (8 pasos)"
        caption="Ciclo del líder de proyecto: de identificar tareas a capitalizar la experiencia."
        steps={PROJECT_STEPS}
      />

      <article className="rounded-xl border border-slate-200 bg-white p-4">
        <h4 className="font-semibold text-slate-900">
          Capítulo 7 · Seis fases del estudio de métodos
        </h4>
        <p className="mb-4 text-sm text-slate-600">
          Flujo metodológico para mejorar el trabajo. En el paso 2 (Registrar)
          aplicas los símbolos ASME.
        </p>
        <ol className="grid gap-3 md:grid-cols-3 lg:grid-cols-6">
          {METHODS_STEPS.map((step, index) => (
            <li
              key={step.name}
              className="rounded-lg border border-teal-200 bg-teal-50 p-3"
            >
              <p className="text-xs font-bold uppercase text-teal-700">
                {index + 1}. {step.name}
              </p>
              <p className="mt-1 text-sm text-slate-700">{step.detail}</p>
            </li>
          ))}
        </ol>
      </article>

      <StepFlow
        title="Capítulo 8 · Planeación sistemática de la distribución (SLP)"
        caption="Del análisis de flujos al layout detallado."
        steps={SLP_STEPS}
      />

      <StepFlow
        title="Capítulo 10 · Decisiones de inversión"
        caption="De la necesidad de mercado a la planeación financiera. Distingue evaluación de proyectos (idealizada) y planeación estratégica (no idealizada)."
        steps={INVESTMENT_STEPS}
      />

      <article className="rounded-xl border border-slate-200 bg-white p-4">
        <h4 className="font-semibold text-slate-900">
          Capítulo 4 · Momentos de un proceso que se mejora
        </h4>
        <div className="mt-4 flex flex-col items-center sm:flex-row sm:justify-center sm:gap-4">
          <Node className="bg-indigo-50">Diseño del proceso</Node>
          <span className="text-slate-400">→</span>
          <Node className="bg-indigo-50">Operación</Node>
          <span className="text-slate-400">→</span>
          <Node className="bg-indigo-50">Control</Node>
          <span className="text-slate-400">↩</span>
          <Node className="bg-indigo-100">Mejora incremental o de rediseño</Node>
        </div>
        <p className="mt-3 text-sm text-slate-600">
          Productividad mira resultados; mejora continua mira el proceso. El
          círculo de Shewhart/Deming del capítulo 5 (Planear-Hacer-Verificar-Actuar)
          es el mismo pulso con lenguaje de calidad.
        </p>
      </article>
    </section>
  );
}
