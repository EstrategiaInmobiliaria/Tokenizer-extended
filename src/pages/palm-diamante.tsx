import type { NextPage } from "next";
import Head from "next/head";
import { PalmDiamanteCalculator } from "~/components/PalmDiamanteCalculator";
import { LeadQualificationForm } from "~/components/LeadQualificationForm";
import { InventoryTable } from "~/components/InventoryTable";
import { VideoScriptsLibrary } from "~/components/VideoScriptsLibrary";
import { INVENTORY_STATS } from "~/data/inventory";

const PalmDiamantePage: NextPage = () => {
  return (
    <>
      <Head>
        <title>Palm Diamante - Calculadora Financiera</title>
        <meta
          name="description"
          content="Aparta con $25k. Estructura financiera verificada: 7% firma + 13% mensualidades + 80% hipoteca. Jaime Wilk + Diana Ondarza."
        />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
        {/* Hero Section */}
        <section className="border-b border-slate-200 bg-gradient-to-r from-blue-600 to-blue-800 px-6 py-12 text-white shadow-lg">
          <div className="mx-auto max-w-[1400px]">
            <h1 className="mb-4 text-5xl font-bold">
              Palm Diamante Acapulco
            </h1>
            <p className="mb-6 text-xl">
              Aparta con <strong className="text-yellow-300">$25,000</strong>.
              No $5M completos. El banco pone el 80%.
            </p>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-md border border-blue-400 bg-blue-700/50 p-4 backdrop-blur">
                <div className="text-3xl font-bold text-yellow-300">
                  {INVENTORY_STATS.disponibles}
                </div>
                <div className="text-sm">Unidades Disponibles</div>
              </div>
              <div className="rounded-md border border-blue-400 bg-blue-700/50 p-4 backdrop-blur">
                <div className="text-3xl font-bold text-yellow-300">
                  {INVENTORY_STATS.vendidos}
                </div>
                <div className="text-sm">Ya Vendidas</div>
              </div>
              <div className="rounded-md border border-blue-400 bg-blue-700/50 p-4 backdrop-blur">
                <div className="text-3xl font-bold text-yellow-300">
                  {INVENTORY_STATS.torres["III"].disponibles}
                </div>
                <div className="text-sm">Torre III - 24 Meses</div>
              </div>
            </div>
            <p className="mt-6 text-sm">
              <strong>Jaime Wilk</strong> - Estrategia Inmobiliaria +{" "}
              <strong>Diana Ondarza</strong> - Agartha Bienes Raíces
            </p>
          </div>
        </section>

        {/* Main Content */}
        <div className="mx-auto max-w-[1400px] space-y-8 px-6 py-8">
          {/* Value Proposition */}
          <section className="rounded-lg border-2 border-blue-200 bg-blue-50 p-6">
            <h2 className="mb-4 text-2xl font-bold text-blue-900">
              🎯 La Estructura que Nadie Más Está Comunicando Bien
            </h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <h3 className="mb-2 font-bold text-blue-800">
                  Estructura Tradicional (lo que todos dicen):
                </h3>
                <p className="text-sm text-blue-700">
                  ❌ &ldquo;Departamentos desde $5M&rdquo;
                  <br />
                  ❌ Barrera de entrada: $5,000,000 completos
                  <br />
                  ❌ Filtra al inversionista curioso que solo pide &ldquo;info&rdquo;
                </p>
              </div>
              <div className="rounded-md bg-green-100 p-4">
                <h3 className="mb-2 font-bold text-green-800">
                  Nuestra Estructura con Diana (oro puro):
                </h3>
                <p className="text-sm text-green-700">
                  ✅ <strong>$25,000 aparta</strong> + 7% firma + 13% hasta
                  entrega + 80% crédito hipotecario
                  <br />
                  ✅ Barrera de entrada real: <strong>$353k</strong>, no $5M
                  <br />
                  ✅ Filtra al inversionista <strong>honesto y verificado</strong>
                </p>
              </div>
            </div>
          </section>

          {/* Calculadora */}
          <PalmDiamanteCalculator />

          {/* Lead Qualification Form */}
          <LeadQualificationForm />

          {/* Inventory Table */}
          <InventoryTable />

          {/* Video Scripts & Marketing */}
          <VideoScriptsLibrary />

          {/* Siguiente Paso CTA */}
          <section className="rounded-lg border-2 border-green-200 bg-green-50 p-6">
            <h2 className="mb-4 text-2xl font-bold text-green-900">
              🚀 Próximos Pasos
            </h2>
            <div className="space-y-4 text-sm text-green-800">
              <div className="flex gap-3">
                <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-green-600 font-bold text-white">
                  1
                </span>
                <div>
                  <h3 className="font-bold">
                    Exporta el inventario de las 210 disponibles
                  </h3>
                  <p>
                    Usa el botón &ldquo;Exportar a Excel/CSV&rdquo; en la tabla de arriba
                    para tener tu corrida lista para EasyBroker.
                  </p>
                </div>
              </div>

              <div className="flex gap-3">
                <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-green-600 font-bold text-white">
                  2
                </span>
                <div>
                  <h3 className="font-bold">
                    Usa los guiones de video para @palm.diamante
                  </h3>
                  <p>
                    Copia los scripts de 15 segundos de la sección &ldquo;Biblioteca
                    de Marketing&rdquo; y graba para Instagram/TikTok.
                  </p>
                </div>
              </div>

              <div className="flex gap-3">
                <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-green-600 font-bold text-white">
                  3
                </span>
                <div>
                  <h3 className="font-bold">
                    Actualiza tu formulario de Meta Ads
                  </h3>
                  <p>
                    Cambia las 3 preguntas del formulario de calificación para
                    filtrar liquidez real desde el primer contacto.
                  </p>
                </div>
              </div>

              <div className="flex gap-3">
                <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-green-600 font-bold text-white">
                  4
                </span>
                <div>
                  <h3 className="font-bold">
                    Conecta con EasyBroker para auto-apartar
                  </h3>
                  <p>
                    Cada lead que pague los $25k se marca como APARTADO
                    automáticamente y no lo vuelve a ofrecer tu bot.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Footer con datos de contacto */}
          <footer className="border-t border-slate-200 pt-6 text-center text-sm text-slate-600">
            <p className="mb-2">
              <strong>Jaime Wilk</strong> - Estrategia Inmobiliaria
            </p>
            <p className="mb-2">
              <strong>Diana Ondarza</strong> - Agartha Bienes Raíces
            </p>
            <p className="text-xs text-slate-500">
              Palm Diamante Acapulco - Frente a Princess Mundo Imperial
            </p>
          </footer>
        </div>
      </main>
    </>
  );
};

export default PalmDiamantePage;
