import { cn } from "~/utils/cn";

function Box({
  children,
  className,
}: {
  children: string;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "rounded-md border border-slate-400 bg-white px-3 py-2 text-center text-sm font-medium text-slate-800 shadow-sm",
        className
      )}
    >
      {children}
    </div>
  );
}

function Hierarchical() {
  return (
    <div className="flex flex-col items-center gap-2">
      <Box className="bg-slate-900 text-white">Director general</Box>
      <span className="text-slate-400">│</span>
      <div className="flex gap-3">
        <Box>Gerente A</Box>
        <Box>Gerente B</Box>
        <Box>Gerente C</Box>
      </div>
      <span className="text-slate-400">│</span>
      <div className="flex gap-2">
        <Box className="text-xs">Mandos medios</Box>
        <Box className="text-xs">Mandos medios</Box>
        <Box className="text-xs">Mandos medios</Box>
      </div>
      <div className="mt-1 grid w-full grid-cols-4 gap-1">
        {["Op.", "Op.", "Op.", "Op."].map((label, index) => (
          <Box key={index} className="bg-slate-50 text-xs">
            {label}
          </Box>
        ))}
      </div>
      <p className="mt-2 text-xs text-slate-500">
        Pirámide: la autoridad desciende y la base se ensancha hacia los obreros.
      </p>
    </div>
  );
}

function Horizontal() {
  return (
    <div className="flex flex-wrap items-center justify-center gap-2">
      <Box className="bg-slate-900 text-white">Director</Box>
      <span className="text-slate-400">→</span>
      <Box>Subdirectores</Box>
      <span className="text-slate-400">→</span>
      <Box>Gerentes</Box>
      <span className="text-slate-400">→</span>
      <Box>Jefes</Box>
      <span className="text-slate-400">→</span>
      <Box>Operativos</Box>
    </div>
  );
}

function Ladder() {
  return (
    <div className="space-y-2">
      {[
        "Dirección",
        "Subdirección",
        "Gerencia",
        "Jefatura",
        "Supervisión",
        "Operación",
      ].map((level, index) => (
        <div key={level} style={{ marginLeft: `${index * 1.25}rem` }}>
          <Box className={index === 0 ? "bg-slate-900 text-white" : ""}>
            {level}
          </Box>
        </div>
      ))}
      <p className="text-xs text-slate-500">
        El nivel máximo está en el escalón más alto; cada peldaño es un nivel
        jerárquico.
      </p>
    </div>
  );
}

function PieChart() {
  return (
    <div className="flex flex-col items-center">
      <div className="relative flex h-56 w-56 items-center justify-center rounded-full border-[28px] border-slate-200">
        <div className="flex h-36 w-36 items-center justify-center rounded-full border-[24px] border-slate-400">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-900 text-center text-[10px] font-bold leading-tight text-white">
            Dirección
          </div>
        </div>
        <span className="absolute right-2 top-6 text-[10px] font-medium text-slate-600">
          Mandos
        </span>
        <span className="absolute bottom-3 text-[10px] font-medium text-slate-500">
          Operativos
        </span>
      </div>
      <p className="mt-3 max-w-xs text-center text-xs text-slate-500">
        Círculos concéntricos: el puesto directivo al centro; los operativos en
        el anillo exterior.
      </p>
    </div>
  );
}

function StaffChart() {
  return (
    <div className="flex flex-col items-center gap-3">
      <Box className="bg-slate-900 text-white">Director general</Box>
      <div className="flex items-start gap-8">
        <div className="flex flex-col items-center gap-1">
          <span className="text-xs italic text-amber-700">asesoría (staff)</span>
          <Box className="border-dashed border-amber-500 bg-amber-50">
            Jurídico / técnico
          </Box>
        </div>
        <div className="flex flex-col items-center gap-2">
          <span className="text-xs text-slate-500">línea</span>
          <div className="flex gap-2">
            <Box>Producción</Box>
            <Box>Ventas</Box>
            <Box>Finanzas</Box>
          </div>
        </div>
      </div>
      <p className="text-xs text-slate-500">
        El staff colabora con altos mandos pero no tiene autoridad de línea sobre
        los departamentos.
      </p>
    </div>
  );
}

function FunctionalChart() {
  return (
    <div className="flex flex-col items-center gap-2">
      <Box className="bg-slate-900 text-white">Director general</Box>
      <div className="mt-2 grid w-full grid-cols-2 gap-2 sm:grid-cols-4">
        <div className="space-y-1">
          <Box className="bg-teal-50">Producción</Box>
          <Box className="text-xs">Jefe de planta</Box>
          <Box className="text-xs">Supervisores</Box>
        </div>
        <div className="space-y-1">
          <Box className="bg-sky-50">Calidad</Box>
          <Box className="text-xs">Lab. metrología</Box>
          <Box className="text-xs">Inspectores</Box>
        </div>
        <div className="space-y-1">
          <Box className="bg-amber-50">Logística</Box>
          <Box className="text-xs">Almacenes</Box>
          <Box className="text-xs">Tráfico</Box>
        </div>
        <div className="space-y-1">
          <Box className="bg-rose-50">Finanzas</Box>
          <Box className="text-xs">Costos</Box>
          <Box className="text-xs">Tesorería</Box>
        </div>
      </div>
      <p className="text-xs text-slate-500">
        Mezcla militar y horizontal: cada columna detalla la función del puesto
        (figura tipo 10.8 / cap. 9).
      </p>
    </div>
  );
}

function ProjectOrgs() {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <article className="rounded-xl border border-slate-200 bg-white p-4">
        <h4 className="font-semibold text-slate-900">a) Proyecto puro</h4>
        <div className="mt-3 flex flex-col items-center gap-2">
          <Box className="bg-slate-900 text-white">Dirección general</Box>
          <div className="grid w-full grid-cols-2 gap-2">
            <Box className="text-xs">Finanzas</Box>
            <Box className="text-xs">Ingeniería</Box>
            <Box className="text-xs">Manufactura</Box>
            <Box className="bg-teal-100 text-xs">Proyectos (autónomo)</Box>
          </div>
          <div className="flex gap-1">
            <Box className="text-xs">A</Box>
            <Box className="text-xs">B</Box>
            <Box className="text-xs">C</Box>
            <Box className="text-xs">D</Box>
          </div>
        </div>
        <ul className="mt-3 list-disc pl-4 text-xs text-slate-600">
          <li>Equipo dedicado; gerente con autoridad plena.</li>
          <li>Riesgo: duplicidad, aislamiento, saltarse políticas.</li>
        </ul>
      </article>

      <article className="rounded-xl border border-slate-200 bg-white p-4">
        <h4 className="font-semibold text-slate-900">b) Funcional</h4>
        <div className="mt-3 flex flex-col items-center gap-2">
          <Box className="bg-slate-900 text-white">Dirección general</Box>
          <div className="grid w-full grid-cols-3 gap-1">
            <Box className="text-xs">Finanzas</Box>
            <Box className="bg-sky-100 text-xs">Ingeniería + proyectos</Box>
            <Box className="text-xs">Manufactura</Box>
          </div>
        </div>
        <ul className="mt-3 list-disc pl-4 text-xs text-slate-600">
          <li>El proyecto vive en un departamento.</li>
          <li>Pertenencia y especialización; menor visión transversal.</li>
        </ul>
      </article>

      <article className="rounded-xl border border-slate-200 bg-white p-4">
        <h4 className="font-semibold text-slate-900">c) Matriz</h4>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-center text-xs">
            <thead>
              <tr className="text-slate-500">
                <th className="p-1 text-left">Área</th>
                <th className="p-1">Finanzas</th>
                <th className="p-1">Ingeniería</th>
                <th className="p-1">Manufactura</th>
              </tr>
            </thead>
            <tbody>
              {["Proyecto A", "Proyecto B", "Proyecto C"].map((project) => (
                <tr key={project}>
                  <td className="p-1 text-left font-medium">{project}</td>
                  <td className="p-1">×</td>
                  <td className="p-1">×</td>
                  <td className="p-1">×</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <ul className="mt-3 list-disc pl-4 text-xs text-slate-600">
          <li>Integra áreas; menos duplicidad; se conserva pertenencia.</li>
          <li>Riesgo: varios jefes y subutilización si no hay control.</li>
        </ul>
      </article>
    </div>
  );
}

const CHARTS = [
  {
    id: "jerarquico",
    title: "Jerárquico o militar",
    body: <Hierarchical />,
  },
  {
    id: "horizontal",
    title: "Horizontal",
    body: <Horizontal />,
  },
  {
    id: "escalera",
    title: "De escalera",
    body: <Ladder />,
  },
  {
    id: "pastel",
    title: "De pastel (concéntrico)",
    body: <PieChart />,
  },
  {
    id: "staff",
    title: "De staff",
    body: <StaffChart />,
  },
  {
    id: "funcional",
    title: "Funcional (recomendado)",
    body: <FunctionalChart />,
  },
] as const;

export function IeOrgCharts() {
  return (
    <section id="organigramas" className="scroll-mt-24 space-y-8">
      <header>
        <p className="text-sm font-semibold uppercase tracking-widest text-teal-700">
          Pilar III · Capítulos 6 y 9
        </p>
        <h2 className="mt-1 text-3xl font-bold text-slate-900">
          Organigramas de las estructuras del libro
        </h2>
        <p className="mt-2 max-w-3xl text-slate-600">
          El capítulo 9 sitúa la organización dentro del proceso administrativo
          (planeación, organización, ejecución y control). El capítulo 6 aplica
          esas formas al recurso humano de un proyecto (figura 6.10).
        </p>
      </header>

      <div className="grid gap-6 md:grid-cols-2">
        {CHARTS.map((chart) => (
          <article
            key={chart.id}
            className="rounded-xl border border-slate-200 bg-slate-50 p-5"
          >
            <h3 className="mb-4 text-lg font-semibold text-slate-900">
              {chart.title}
            </h3>
            {chart.body}
          </article>
        ))}
      </div>

      <div>
        <h3 className="mb-4 text-xl font-semibold">
          Figura 6.10 · Organización de proyectos en AO
        </h3>
        <ProjectOrgs />
      </div>
    </section>
  );
}
