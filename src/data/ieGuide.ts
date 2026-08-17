/**
 * Original study map for Introducción a la Ingeniería Industrial
 * (2.ª ed., Baca et al., Grupo Editorial Patria).
 * Chapter titles and figure numbers follow the book's table of contents.
 * Narratives are original syntheses for study — they do not reproduce the book text.
 */

export type Pillar = "cronologia" | "flujos" | "organigramas";

export type EraId =
  | "preindustrial"
  | "primera-revolucion"
  | "segunda-revolucion"
  | "admin-cientifica"
  | "sistemas-calidad";

export type TimelineEvent = {
  year: string;
  title: string;
  detail: string;
  chapter: string;
  era: EraId;
};

export type ChapterCard = {
  number: number;
  title: string;
  pages: string;
  pillars: Pillar[];
  figures: string[];
  studyFocus: string;
  howToMap: string;
};

export const BOOK = {
  title: "Introducción a la Ingeniería Industrial",
  edition: "2.ª edición",
  authors:
    "Gabriel Baca Urbina, Margarita Cruz Valderrama, I. Marco Antonio Cristóbal Vázquez y coautores",
  publisher: "Grupo Editorial Patria",
  year: "2014",
  isbnEbook: "978-607-438-919-7",
} as const;

export const ERAS: {
  id: EraId;
  label: string;
  period: string;
  summary: string;
}[] = [
  {
    id: "preindustrial",
    label: "Antecedentes preindustriales",
    period: "siglos XVI–XVIII",
    summary:
      "Tratados técnicos, caminos, minería y las primeras escuelas de ingeniería en Francia, impulsadas por necesidades de Estado y de guerra.",
  },
  {
    id: "primera-revolucion",
    label: "Primera Revolución Industrial",
    period: "1765 y fines del siglo XVIII",
    summary:
      "La máquina de vapor sustituye la fuerza humana y nace la producción en masa. El método científico pragmático (causa-efecto por experiencia) prepara el terreno industrial.",
  },
  {
    id: "segunda-revolucion",
    label: "Segunda Revolución Industrial y estandarización",
    period: "siglo XIX – 1908",
    summary:
      "Partes intercambiables, sociedades profesionales, administración general, acero y ferrocarril, y la línea de ensamble móvil del Ford T.",
  },
  {
    id: "admin-cientifica",
    label: "Administración científica",
    period: "principios del siglo XX",
    summary:
      "Taylor, los Gilbreth y Gantt convierten el trabajo en objeto de medición, diseño y programación. Nace la profesión de ingeniero industrial.",
  },
  {
    id: "sistemas-calidad",
    label: "Automatización, calidad y sistemas",
    period: "segunda mitad del siglo XX – siglo XXI",
    summary:
      "Institucionalización de la profesión, ergonomía, control estadístico y calidad total, computadoras, ERP, CAD y comercio electrónico.",
  },
];

export const TIMELINE: TimelineEvent[] = [
  {
    year: "1560",
    title: "De re metallica — Jorge Agrícola",
    detail:
      "Tratado de geología y minería. El libro lo usa como ejemplo de ingeniería escrita en el Renacimiento, antes de que existiera la profesión moderna.",
    chapter: "Cap. 1",
    era: "preindustrial",
  },
  {
    year: "1587",
    title: "Tratado de Guido Toglieta",
    detail:
      "Describe con detalle las técnicas de construcción de caminos: ingeniería civil práctica anterior a las escuelas formales.",
    chapter: "Cap. 1",
    era: "preindustrial",
  },
  {
    year: "1622",
    title: "Carreteras del imperio romano — Nicolás Bergier",
    detail:
      "Obra que documenta la red vial romana y refuerza la idea de que la infraestructura es un problema de ingeniería de Estado.",
    chapter: "Cap. 1",
    era: "preindustrial",
  },
  {
    year: "1646",
    title: "Cuerpo de ingenieros franceses (Colbert)",
    detail:
      "Cuerpo de carácter militar. El texto señala que la necesidad bélica anticipó la formación de ingenieros mucho antes de las escuelas napoleónicas.",
    chapter: "Cap. 1",
    era: "preindustrial",
  },
  {
    year: "1765",
    title: "Máquina de vapor — James Watt",
    detail:
      "Sustituye la fuerza del hombre por la presión de vapor. Con husillos y telares semiautomáticos inicia la producción en masa en Inglaterra.",
    chapter: "Cap. 1",
    era: "primera-revolucion",
  },
  {
    year: "1711–1776",
    title: "David Hume y el método científico pragmático",
    detail:
      "Propone que en los hechos hay relación causa-efecto y que ésta se descubre por la experiencia, no solo por la razón. Base del enfoque pragmático industrial.",
    chapter: "Cap. 1",
    era: "primera-revolucion",
  },
  {
    year: "1793",
    title: "Primera fábrica textil masiva en América (Pawtucket)",
    detail:
      "Samuel Slater lleva el secreto de la hiladora inglesa a Rhode Island. El libro lo marca como hito de la transferencia tecnológica hacia Estados Unidos.",
    chapter: "Cap. 1",
    era: "primera-revolucion",
  },
  {
    year: "1794",
    title: "École des Ponts et Chaussées",
    detail:
      "Escuela de Puentes y Pavimentos en Francia: antecesora de la ingeniería civil moderna (puentes, caminos, obras públicas).",
    chapter: "Cap. 1",
    era: "preindustrial",
  },
  {
    year: "1795",
    title: "École Polytechnique (París)",
    detail:
      "Fundada durante el mandato de Napoleón. El libro la presenta como la primera escuela de ingeniería del mundo, impulsada por necesidades de logística militar (entre ellas, conservar alimentos).",
    chapter: "Cap. 1",
    era: "preindustrial",
  },
  {
    year: "siglo XIX",
    title: "Sistema uniforme de producción — Whitney y North",
    detail:
      "Eli Whitney y Simeon North estandarizan partes intercambiables (armas). El obrero y las piezas se vuelven intercambiables: nace la Segunda Revolución Industrial según el texto.",
    chapter: "Cap. 1",
    era: "segunda-revolucion",
  },
  {
    year: "1852–1884",
    title: "Sociedades profesionales en EE. UU.",
    detail:
      "1852 ingenieros civiles, 1871 minas, 1880 ASME (foro clave para los primeros industriales), 1884 eléctricos. En 1908 se suma la sociedad de ingenieros químicos.",
    chapter: "Cap. 1",
    era: "segunda-revolucion",
  },
  {
    year: "1872–1902",
    title: "Andrew Carnegie y el acero",
    detail:
      "Mezcla técnicas de producción de acero con administración ferroviaria y contabilidad de costos. EE. UU. pasa de productor menor a líder mundial del acero.",
    chapter: "Cap. 1",
    era: "segunda-revolucion",
  },
  {
    year: "fines del s. XIX / 1916",
    title: "Henri Fayol — administración general",
    detail:
      "Ingeniero de minas. El texto le atribuye los conceptos vigentes de planeación, dirección, administración y control. Su libro clásico Administración industrial y general se publica en 1916.",
    chapter: "Caps. 1 y 9",
    era: "segunda-revolucion",
  },
  {
    year: "1908",
    title: "Línea de ensamble móvil — Henry Ford (Modelo T)",
    detail:
      "El auto va al obrero, no al revés. El precio del Ford T cae de ~850 USD (1908) hacia 290 USD (1920). Aporte central: velocidad de producción e inventarios bajos.",
    chapter: "Cap. 1",
    era: "segunda-revolucion",
  },
  {
    year: "1885–1903",
    title: "Frederick W. Taylor ante la ASME",
    detail:
      "Padre de la ingeniería industrial. Diseño del trabajo, cronómetro, estandarización de tiempos, programación de la producción y geometría de herramientas. Murió en 1915.",
    chapter: "Caps. 1 y 7",
    era: "admin-cientifica",
  },
  {
    year: "principios s. XX",
    title: "Frank y Lillian Gilbreth",
    detail:
      "Estudio de tiempos y micromovimientos con apoyo de video. Optimizan ensambles manuales; base del estudio de métodos del capítulo 7.",
    chapter: "Caps. 1 y 7",
    era: "admin-cientifica",
  },
  {
    year: "principios s. XX",
    title: "Lawrence Gantt — gráfica de control temporal",
    detail:
      "Barras de actividades contra el tiempo. El capítulo 6 la usa todavía para controlar proyectos (figura 6.11).",
    chapter: "Caps. 1 y 6",
    era: "admin-cientifica",
  },
  {
    year: "1917",
    title: "Primera Sociedad de Ingenieros Industriales (EE. UU.)",
    detail:
      "Foro dedicado a la administración de la producción, tema práctico de los primeros ingenieros industriales.",
    chapter: "Cap. 1",
    era: "admin-cientifica",
  },
  {
    year: "1927",
    title: "Lote económico — F. W. Harris",
    detail:
      "Modelo de inventario de diente de sierra (luego modelo de Wilson). El capítulo 6 retoma EOQ en la administración de inventarios.",
    chapter: "Caps. 1 y 6",
    era: "admin-cientifica",
  },
  {
    year: "1948 / 1981",
    title: "AIIE → IIE",
    detail:
      "1948: Instituto Norteamericano de Ingenieros Industriales. 1981: se convierte en el Instituto de Ingenieros Industriales (IIE), de alcance internacional.",
    chapter: "Cap. 1",
    era: "sistemas-calidad",
  },
  {
    year: "12 jul 1949",
    title: "Ergonomía como disciplina formal",
    detail:
      "Fundación de la Sociedad de Investigación Ergonómica en Inglaterra. El capítulo 13 desarrolla los tres pilares: sistema hombre, máquina y entorno.",
    chapter: "Cap. 13",
    era: "sistemas-calidad",
  },
  {
    year: "años 1950",
    title: "Deming, Juran, Ishikawa y normas ISO",
    detail:
      "W. Edwards Deming introduce el control estadístico de la calidad en Japón. El capítulo 5 articula pensadores de la calidad y el camino hacia ISO 9000 / ISO 14000.",
    chapter: "Cap. 5",
    era: "sistemas-calidad",
  },
  {
    year: "siglo XXI",
    title: "Tercera Revolución Industrial (Forrester) y TIC",
    detail:
      "Computadoras, automatización, ERP, CAD, robots, e-commerce y velocidad de la información. Los principios de la II cambian poco; cambia la velocidad de ejecución.",
    chapter: "Caps. 1 y 3",
    era: "sistemas-calidad",
  },
];

export const CHAPTERS: ChapterCard[] = [
  {
    number: 1,
    title: "Generalidades de la ingeniería industrial",
    pages: "1–23",
    pillars: ["cronologia", "flujos"],
    figures: ["1.1 información", "1.2 dinero", "1.3 materias primas"],
    studyFocus:
      "Definición de ingeniería, historia mundial, papel del II, empresa como procesos y tendencias.",
    howToMap:
      "Traza la cronología completa y dibuja los tres flujos de la empresa (información, dinero, materiales) uniendo departamentos.",
  },
  {
    number: 2,
    title: "Naturaleza de los procesos industriales",
    pages: "25–52",
    pillars: ["flujos"],
    figures: ["2.5 proceso industrial", "2.1–2.4 clasificaciones"],
    studyFocus:
      "Sectores y cadenas productivas, operaciones unitarias (cambios físicos) y procesos unitarios (reacciones químicas).",
    howToMap:
      "Diagrama de bloques: entradas → transformación → salidas (producto, subproducto, emisiones, aguas residuales, residuos).",
  },
  {
    number: 3,
    title: "Logística y sistemas de información",
    pages: "53–71",
    pillars: ["cronologia", "flujos"],
    figures: ["3.2 flujos físicos/info/financieros", "3.5 cadena de suministro"],
    studyFocus:
      "De la logística militar a la empresarial: servicio al cliente, inventarios, transporte, localización y sistemas de información.",
    howToMap:
      "Tres visiones: departamentos, empresa completa y cadena de suministro. Añade logística inversa.",
  },
  {
    number: 4,
    title: "Productividad y mejora continua",
    pages: "73–98",
    pillars: ["flujos"],
    figures: ["4.2 mejora continua", "4.3 diseño-operación-control", "4.7 espiral"],
    studyFocus:
      "Productividad (resultados) vs mejora continua (procesos). Metodología y dimensiones política/macroeconómica.",
    howToMap:
      "Ciclo diseño → operación → control, y la espiral de productividad como diagrama de realimentación.",
  },
  {
    number: 5,
    title: "Calidad: concepto, gestión y control estadístico",
    pages: "99–132",
    pillars: ["cronologia", "flujos"],
    figures: ["5.4 círculo de Shewhart/Deming", "5.7 trilogía de Juran", "7 herramientas"],
    studyFocus:
      "Pensadores de la calidad, SGC, ISO, y las siete herramientas estadísticas.",
    howToMap:
      "Línea de pensadores + PDCA + diagrama de Ishikawa y Pareto como flujos de análisis.",
  },
  {
    number: 6,
    title: "La administración de las operaciones",
    pages: "133–173",
    pillars: ["flujos", "organigramas"],
    figures: ["6.8 proceso de AP", "6.10 puro/funcional/matriz", "6.11 Gantt"],
    studyFocus:
      "AO como estrategia, administración de proyectos (CPM), pronósticos, planeación agregada e inventarios.",
    howToMap:
      "Flujo de 8 pasos de un proyecto y organigramas de equipo puro, funcional y matricial.",
  },
  {
    number: 7,
    title: "Estudio y diseño del trabajo",
    pages: "175–214",
    pillars: ["flujos"],
    figures: ["estudio de métodos", "estudio de tiempos", "MOST"],
    studyFocus:
      "Estudio de métodos, medición del trabajo (cronómetro, muestreo, tiempos predeterminados), higiene y seguridad (OSHA).",
    howToMap:
      "Simbología ASME y las 6 fases: seleccionar, registrar, examinar, establecer, definir e implantar.",
  },
  {
    number: 8,
    title: "Diseño de instalaciones",
    pages: "215–237",
    pillars: ["flujos"],
    figures: ["SLP", "diagrama de relación de actividades", "tipos de distribución"],
    studyFocus:
      "Localización (continua/discreta) y distribución de planta: SLP, flujos y layouts (producto, proceso, posición fija, celular).",
    howToMap:
      "Flujo SLP: análisis de flujos → relaciones → espacios → plano por bloques → detalle.",
  },
  {
    number: 9,
    title: "Administración de la empresa",
    pages: "239–262",
    pillars: ["organigramas"],
    figures: ["proceso administrativo", "estilos de liderazgo"],
    studyFocus:
      "Historia de la administración, planeación-organización-ejecución-control, liderazgo, ética y visión estratégica.",
    howToMap:
      "Organigramas jerárquico, horizontal, de escalera, de pastel, de staff y funcional.",
  },
  {
    number: 10,
    title: "La planeación y las decisiones de inversión",
    pages: "263–289",
    pillars: ["flujos"],
    figures: ["estudio de mercado", "estudio técnico", "evaluación económica"],
    studyFocus:
      "Evaluación de proyectos vs planeación estratégica. Mercado, ingeniería, análisis económico y riesgo.",
    howToMap:
      "Secuencia: necesidad/mercado → técnico → económico → riesgo → planeación financiera.",
  },
  {
    number: 11,
    title: "La empresa vista como un conjunto de sistemas",
    pages: "291–311",
    pillars: ["organigramas", "flujos"],
    figures: ["subsistemas: ventas, distribución, almacenes, producción, etc."],
    studyFocus:
      "Teoría de sistemas aplicada a la empresa. Dirección general como cerebro; cada subsistema con objetivo, entradas, salidas e índices.",
    howToMap:
      "Mapa de sistemas con flechas bidireccionales de información alrededor de la Dirección General.",
  },
  {
    number: 12,
    title: "Contaminación y gestión de la contaminación",
    pages: "313–337",
    pillars: ["flujos"],
    figures: ["agua", "suelo", "aire", "gestión en procesos"],
    studyFocus:
      "Prevención y tratamiento de contaminantes de agua, suelo y aire, y gestión ambiental del proceso industrial.",
    howToMap:
      "Extiende el diagrama 2.5: cada salida residual tiene un tratamiento y un indicador de gestión.",
  },
  {
    number: 13,
    title: "Ergonomía",
    pages: "339–371",
    pillars: ["cronologia", "flujos"],
    figures: ["sistema hombre", "sistema máquina", "sistema entorno"],
    studyFocus:
      "Antecedentes históricos y los tres pilares: persona, máquina y entorno (iluminación, ruido, temperatura, vibración, presión).",
    howToMap:
      "Diagrama de interacción H-M-E. Relaciónalo con el capítulo 7 (diseño del trabajo).",
  },
];

export const ASME_SYMBOLS = [
  {
    id: "operacion",
    name: "Operación",
    shape: "circle" as const,
    meaning:
      "Cambio físico de materiales o tarea administrativa que agrega valor (barrenar una placa, teclear un informe).",
  },
  {
    id: "transporte",
    name: "Transporte",
    shape: "arrow" as const,
    meaning:
      "Traslado físico de personas, materiales o equipos de un punto a otro.",
  },
  {
    id: "inspeccion",
    name: "Inspección",
    shape: "square" as const,
    meaning:
      "Verificación de calidad, cantidad o lectura de indicadores; no transforma el producto.",
  },
  {
    id: "demora",
    name: "Demora o espera",
    shape: "delay" as const,
    meaning:
      "Cuello de botella, interferencia en el flujo o abandono temporal del trabajo. Se dibuja como una D.",
  },
  {
    id: "almacen",
    name: "Almacenamiento",
    shape: "triangle" as const,
    meaning:
      "Resguardo controlado de materiales o productos (requiere autorización para entrar o salir).",
  },
] as const;

export const PROJECT_STEPS = [
  "Identificar las operaciones (tareas) básicas del proyecto",
  "Estimar la duración de cada operación",
  "Estimar los requerimientos de recursos",
  "Preparar presupuestos",
  "Supervisar el progreso (tiempo y dinero)",
  "Realizar ajustes a los planes si es necesario",
  "Finalizar el proyecto y evaluar los resultados",
  "Consolidar conocimientos para proyectos futuros",
] as const;

export const METHODS_STEPS = [
  {
    name: "Seleccionar",
    detail: "Elige el trabajo, proceso o cuello de botella con mayor potencial de mejora.",
  },
  {
    name: "Registrar",
    detail: "Documenta el método actual con diagramas de flujo, recorrido y simbología ASME.",
  },
  {
    name: "Examinar",
    detail: "Cuestiona propósito, lugar, sucesión, persona y medios (las preguntas clásicas del estudio de métodos).",
  },
  {
    name: "Establecer",
    detail: "Diseña el método propuesto: elimina, combina, reordena y simplifica operaciones.",
  },
  {
    name: "Definir",
    detail: "Especifica el estándar: instrucciones, tiempos y condiciones de operación.",
  },
  {
    name: "Implantar",
    detail: "Capacita, pone en marcha y sostiene el nuevo método (control y seguimiento).",
  },
] as const;

export const SLP_STEPS = [
  "Analizar flujos de materiales y personas",
  "Analizar relaciones entre actividades",
  "Diagrama de relación de actividades",
  "Diagrama de relación de espacios",
  "Plano por bloques",
  "Distribución detallada",
] as const;

export const INVESTMENT_STEPS = [
  "Cuantificar la necesidad (estudio de mercado)",
  "Estudio técnico o ingeniería del proyecto",
  "Análisis económico",
  "Evaluación económica y análisis de riesgo",
  "Planeación financiera de la empresa",
] as const;

export const SUBSYSTEMS = [
  {
    name: "Dirección general",
    role: "Cerebro del suprasistema: integra objetivos, información y decisiones.",
    inputs: "Informes de todos los subsistemas, entorno (mercado, gobierno, macroeconomía).",
    outputs: "Políticas, metas, asignación de recursos, retroalimentación.",
    kpis: "Cumplimiento de estrategia, rentabilidad global, clima organizacional.",
  },
  {
    name: "Ventas",
    role: "Convertir demanda potencial en pedidos reales.",
    inputs: "Pronósticos, catálogo, precios, clientes.",
    outputs: "Pedidos, promesas de entrega, retroalimentación del mercado.",
    kpis: "Volumen de ventas, conversión, satisfacción del cliente.",
  },
  {
    name: "Distribución",
    role: "Entregar el producto en tiempo, lugar y costo adecuados.",
    inputs: "Producto terminado, rutas, pedidos.",
    outputs: "Entregas, devoluciones, costos logísticos.",
    kpis: "Fill rate, lead time, costo por entrega.",
  },
  {
    name: "Almacenes",
    role: "Resguardar MP y PT con control de existencias.",
    inputs: "Recepciones, órdenes de producción, despachos.",
    outputs: "Inventarios actualizados, materiales a planta, PT a distribución.",
    kpis: "Exactitud de inventario, rotación, merma.",
  },
  {
    name: "Producción",
    role: "Transformar materiales en productos de valor.",
    inputs: "MP, mano de obra, energía, programa maestro.",
    outputs: "PT, subproductos, residuos, datos de eficiencia.",
    kpis: "OEE, cumplimiento del programa, scrap.",
  },
  {
    name: "Mantenimiento",
    role: "Conservar la capacidad del equipo productivo.",
    inputs: "Historial de fallas, planes PM, refacciones.",
    outputs: "Máquinas disponibles, órdenes cerradas.",
    kpis: "MTBF, MTTR, disponibilidad.",
  },
  {
    name: "Control de calidad",
    role: "Asegurar que el producto cumpla especificaciones.",
    inputs: "Muestras, normas, quejas.",
    outputs: "Aceptación/rechazo, acciones correctivas.",
    kpis: "PPM, costos de calidad, quejas.",
  },
  {
    name: "Finanzas",
    role: "Registrar y controlar el flujo de dinero.",
    inputs: "Facturas, nómina, presupuestos, ventas.",
    outputs: "Estados financieros, liquidez, costos.",
    kpis: "Margen, flujo de caja, ROI.",
  },
  {
    name: "Recursos humanos",
    role: "Proveer, desarrollar y cuidar a las personas.",
    inputs: "Requisiciones, evaluaciones, marco legal.",
    outputs: "Plantilla capacitada, nómina, clima.",
    kpis: "Rotación, ausentismo, cobertura de capacitación.",
  },
] as const;

export const QUIZ = [
  {
    question: "Según la simbología ASME de procesos, el círculo representa…",
    options: ["Inspección", "Operación", "Almacenamiento", "Demora"],
    answer: 1,
    why: "El círculo es operación: cambio físico o tarea administrativa que transforma o agrega valor.",
  },
  {
    question: "El triángulo invertido en un diagrama de proceso indica…",
    options: ["Transporte", "Espera", "Almacenamiento controlado", "Inspección"],
    answer: 2,
    why: "El almacén es resguardo controlado; a diferencia de la demora (D), requiere autorización para entrar o salir.",
  },
  {
    question: "¿A quién considera el libro padre de la ingeniería industrial?",
    options: ["Henri Fayol", "Henry Ford", "Frederick W. Taylor", "Andrew Carnegie"],
    answer: 2,
    why: "Taylor sistematizó diseño del trabajo, medición con cronómetro y programación; Fayol es administración general y Ford la línea móvil.",
  },
  {
    question: "La figura 6.10 compara tres formas de organizar un proyecto. La matriz se caracteriza por…",
    options: [
      "Un equipo autónomo separado de la empresa",
      "El proyecto vive dentro de un solo departamento",
      "Integración interdepartamental: se reporta al área y al proyecto",
      "Solo asesores staff sin autoridad de línea",
    ],
    answer: 2,
    why: "La matriz combina fortalezas del puro y del funcional; el riesgo es la dualidad de jefes.",
  },
  {
    question: "En el mapa de sistemas del capítulo 11, la Dirección General se entiende como…",
    options: [
      "Un departamento más de staff",
      "El cerebro que conecta subsistemas con información bidireccional",
      "Únicamente el área de finanzas",
      "El almacén de producto terminado",
    ],
    answer: 1,
    why: "El texto analoga la empresa con un organismo: la dirección integra; los demás son órganos con entradas, salidas e índices.",
  },
  {
    question: "El orden de las seis fases del estudio de métodos es…",
    options: [
      "Implantar → Definir → Examinar → Registrar → Establecer → Seleccionar",
      "Seleccionar → Registrar → Examinar → Establecer → Definir → Implantar",
      "Registrar → Seleccionar → Implantar → Examinar → Definir → Establecer",
      "Examinar → Seleccionar → Definir → Registrar → Implantar → Establecer",
    ],
    answer: 1,
    why: "Primero se elige qué estudiar, luego se documenta lo actual, se cuestiona, se diseña, se estandariza y se pone en marcha.",
  },
] as const;
