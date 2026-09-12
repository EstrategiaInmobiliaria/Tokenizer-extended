export function VideoScriptsLibrary() {
  const scripts = [
    {
      id: 1,
      titulo: "Video 1 - Filtro $25k",
      duracion: "15 segundos",
      objetivo: "Filtrar curiosos vs inversionistas reales",
      audiencia: "Base de 41k contactos",
      script: `"¿Cuánto necesitas para apartar un depa de $5M frente a Princess? No $5M. $25,000. Yo soy Jaime Wilk, con Diana Ondarza te llevamos paso a paso: 7% a la firma, 13% en 42 meses de $16k, y 80% con crédito hipotecario a la entrega. Torre III, 150 lugares. ¿Te armo tu corrida?"`,
      cta: "WhatsApp / DM para corrida financiera",
      plataforma: "@palm.diamante Instagram/TikTok",
    },
    {
      id: 2,
      titulo: "Video 2 - ROI Garden House",
      duracion: "15 segundos",
      objetivo: "Demostrar rentabilidad inmediata",
      audiencia: "Inversionistas con experiencia en renta vacacional",
      script: `"Garden House 147m² en Diamante: inviertes $664k hoy + $53k al mes, rentas en $95k al mes en temporada. El banco pone el 80%. Nosotros te pre-aprobamos el crédito desde hoy. Palm Diamante."`,
      cta: "Link en bio para calculadora ROI",
      plataforma: "@palm.diamante Instagram/TikTok",
    },
    {
      id: 3,
      titulo: "Video 3 - Urgencia Torre III",
      duracion: "15 segundos",
      objetivo: "Crear FOMO (Fear of Missing Out)",
      audiencia: "Leads tibios que están comparando opciones",
      script: `"390 vendidos ya. Quedan 150 en Torre III con 42 meses para pagar. Torre I y II solo 21 y 26 meses. Si quieres mensualidad baja, es ahora. $25k aparta. Jaime Wilk + Diana Ondarza."`,
      cta: "Aparta ahora / Link en bio",
      plataforma: "@palm.diamante Instagram/TikTok/Facebook",
    },
  ];

  const emailTemplates = [
      {
        tipo: "Lead Calificado",
        asunto: "Tu corrida financiera Palm Diamante está lista",
        cuerpo: `Hola [NOMBRE],

Gracias por tu interés en Palm Diamante. Basado en tu perfil, aquí está tu corrida financiera personalizada:

🏢 Modelo: [MODELO]
💰 Precio Total: [PRECIO]

📋 Estructura de Pago:
1. Aparta hoy: $25,000
2. Firma contrato (7%): [7%] - Pagas [RESTA] adicional
3. Mensualidades 42m (13%): [MENSUALIDAD]/mes
4. Crédito hipotecario (80%): [80%] - Lo gestionamos nosotros

📞 Siguiente paso:
Agendar llamada con Jaime Wilk + Diana Ondarza para pre-aprobar tu crédito hipotecario.

[LINK A CALENDARIO]

Jaime Wilk - Estrategia Inmobiliaria
Diana Ondarza - Agartha Bienes Raíces`,
      },
    {
      tipo: "Lead para Nurturing",
      asunto: "Guía completa de inversión en Palm Diamante",
      cuerpo: `Hola [NOMBRE],

Entiendo que estás explorando opciones de inversión en Acapulco Diamante. Te comparto esta guía que te ayudará a tomar la mejor decisión:

📚 Contenido que te puede interesar:
- ✅ Cómo funciona el crédito hipotecario en preventa
- ✅ Comparativa: ¿Torre I, II o III?
- ✅ ROI de renta vacacional en Diamante
- ✅ Testimonios de inversionistas

Cuando estés listo para una corrida financiera personalizada, escríbeme.

Jaime Wilk - Estrategia Inmobiliaria`,
    },
  ];

  const metaAdsTemplates = [
    {
      nombre: "Carousel - 4 Modelos",
      formato: "Carousel (4 cards)",
      copy: `Aparta desde $25k. No $5M completos.

🏠 B1 Entry: $16k/mes x 42m
🏠 A1 Intermedio: $19k/mes x 42m  
🏠 Garden House: $30k/mes x 42m + ROI $95k/mes
🏠 Penthouse: $38k/mes x 42m frente a Princess

El banco pone el 80%. Tú solo la firma.

👉 Calculadora gratis en bio`,
      audiencia: "Lookalike de compradores de bienes raíces en Acapulco, CDMX, GDL",
    },
    {
      nombre: "Video - Torre III Urgencia",
      formato: "Video 15 seg",
      copy: `390 vendidos. 150 lugares Torre III.

¿Por qué Torre III?
✅ 42 meses para pagar (vs 21 o 26 meses)
✅ Mensualidad más baja
✅ 80% hipotecable a entrega

Aparta: $25,000

[CTA: Quiero mi corrida financiera]`,
      audiencia: "Retargeting de visitantes web + leads tibios",
    },
  ];

  return (
    <div className="flex flex-col gap-6 rounded-lg border-2 border-slate-200 bg-white p-6 shadow-lg">
      <div className="flex flex-col gap-2">
        <h2 className="text-2xl font-bold text-slate-900">
          Biblioteca de Marketing
        </h2>
        <p className="text-sm text-slate-600">
          Guiones de video, emails y ads listos para usar
        </p>
      </div>

      {/* Video Scripts */}
      <section className="flex flex-col gap-4">
        <h3 className="text-lg font-bold text-slate-800">
          📹 Guiones para Video (15 seg)
        </h3>
        <div className="grid gap-4 md:grid-cols-1">
          {scripts.map((script) => (
            <div
              key={script.id}
              className="rounded-md border border-slate-200 bg-slate-50 p-4"
            >
              <div className="mb-3 flex items-start justify-between">
                <div>
                  <h4 className="font-bold text-slate-900">{script.titulo}</h4>
                  <p className="text-xs text-slate-600">
                    {script.duracion} • {script.plataforma}
                  </p>
                </div>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(script.script);
                    alert("✅ Copiado al portapapeles");
                  }}
                  className="rounded-md bg-blue-600 px-3 py-1 text-xs font-semibold text-white hover:bg-blue-700"
                >
                  Copiar
                </button>
              </div>

              <div className="mb-2 space-y-1 text-xs">
                <p>
                  <span className="font-semibold">Objetivo:</span>{" "}
                  {script.objetivo}
                </p>
                <p>
                  <span className="font-semibold">Audiencia:</span>{" "}
                  {script.audiencia}
                </p>
              </div>

              <div className="rounded-md bg-white p-3 text-sm italic text-slate-700">
                {script.script}
              </div>

              <p className="mt-2 text-xs text-slate-600">
                <span className="font-semibold">CTA:</span> {script.cta}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Email Templates */}
      <section className="flex flex-col gap-4">
        <h3 className="text-lg font-bold text-slate-800">
          📧 Plantillas de Email
        </h3>
        <div className="grid gap-4 md:grid-cols-2">
          {emailTemplates.map((template, idx) => (
            <div
              key={idx}
              className="rounded-md border border-slate-200 bg-slate-50 p-4"
            >
              <div className="mb-3 flex items-start justify-between">
                <div>
                  <h4 className="font-bold text-slate-900">{template.tipo}</h4>
                  <p className="text-xs text-slate-600">{template.asunto}</p>
                </div>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(template.cuerpo);
                    alert("✅ Copiado al portapapeles");
                  }}
                  className="rounded-md bg-blue-600 px-3 py-1 text-xs font-semibold text-white hover:bg-blue-700"
                >
                  Copiar
                </button>
              </div>

              <pre className="whitespace-pre-wrap rounded-md bg-white p-3 text-xs text-slate-700">
                {template.cuerpo}
              </pre>
            </div>
          ))}
        </div>
      </section>

      {/* Meta Ads Templates */}
      <section className="flex flex-col gap-4">
        <h3 className="text-lg font-bold text-slate-800">
          📱 Templates Meta Ads
        </h3>
        <div className="grid gap-4 md:grid-cols-2">
          {metaAdsTemplates.map((ad, idx) => (
            <div
              key={idx}
              className="rounded-md border border-slate-200 bg-slate-50 p-4"
            >
              <div className="mb-3 flex items-start justify-between">
                <div>
                  <h4 className="font-bold text-slate-900">{ad.nombre}</h4>
                  <p className="text-xs text-slate-600">{ad.formato}</p>
                </div>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(ad.copy);
                    alert("✅ Copiado al portapapeles");
                  }}
                  className="rounded-md bg-blue-600 px-3 py-1 text-xs font-semibold text-white hover:bg-blue-700"
                >
                  Copiar
                </button>
              </div>

              <div className="mb-2 rounded-md bg-white p-3 text-sm text-slate-700 whitespace-pre-line">
                {ad.copy}
              </div>

              <p className="text-xs text-slate-600">
                <span className="font-semibold">Audiencia:</span> {ad.audiencia}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Tips de Prospección */}
      <section className="rounded-md border border-blue-200 bg-blue-50 p-4">
        <h3 className="mb-3 text-sm font-bold text-blue-900">
          💡 Tips para Maximizar Leads Verificados
        </h3>
        <ul className="space-y-2 text-xs text-blue-800">
          <li>
            ✅ <strong>$25k es tu barrera anti-curioso:</strong> El que sí
            tiene comportamiento de inversionista entiende que $16k/mes por 42
            meses es negocio.
          </li>
          <li>
            ✅ <strong>Torre III es tu máquina de volumen:</strong> 150
            unidades con 42 meses. Enfócate ahí.
          </li>
          <li>
            ✅ <strong>Pre-aprueba el crédito desde ahora:</strong> Tú y Diana
            gestionan la tasa hipotecaria, no esperen a la entrega.
          </li>
          <li>
            ✅ <strong>Busca historial de ahorro:</strong> RFC empresa, leads
            que interactuaron con contenido de ROI, los que ya preguntaron por
            crédito.
          </li>
        </ul>
      </section>
    </div>
  );
}
