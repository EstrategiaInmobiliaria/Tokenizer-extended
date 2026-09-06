import { useState } from 'react';
import Head from 'next/head';
import { api } from '~/utils/api';
import type { LeadInput, LeadScore } from '~/models/lead-scoring';
import { LeadForm } from '~/components/LeadForm';
import { LeadCard } from '~/components/LeadCard';
import { Button } from '~/components/Button';

export default function LeadScoringPage() {
  const [showForm, setShowForm] = useState(false);
  const [scoredLeads, setScoredLeads] = useState<LeadScore[]>([]);
  const [selectedLead, setSelectedLead] = useState<LeadScore | null>(null);
  const [filter, setFilter] = useState<'all' | 'hot' | 'warm' | 'cold'>('all');

  const scoreLeadMutation = api.leadScoring.scoreLead.useMutation({
    onSuccess: (data) => {
      setScoredLeads(prev => [data, ...prev]);
      setShowForm(false);
    },
  });

  const handleSubmitLead = (lead: LeadInput) => {
    scoreLeadMutation.mutate(lead);
  };

  const filteredLeads = scoredLeads.filter(lead => {
    if (filter === 'all') return lead.category !== 'disqualified';
    return lead.category === filter;
  });

  const stats = {
    total: scoredLeads.length,
    hot: scoredLeads.filter(l => l.category === 'hot').length,
    warm: scoredLeads.filter(l => l.category === 'warm').length,
    cold: scoredLeads.filter(l => l.category === 'cold').length,
    disqualified: scoredLeads.filter(l => l.category === 'disqualified').length,
    avgScore: scoredLeads.length > 0
      ? Math.round(scoredLeads.reduce((sum, l) => sum + l.overallScore, 0) / scoredLeads.length)
      : 0,
    totalValue: scoredLeads.reduce((sum, l) => sum + (l.estimatedROI.estimatedValue ?? 0), 0),
  };

  return (
    <>
      <Head>
        <title>Sistema de Calificación de Leads Inmobiliarios con IA</title>
        <meta name="description" content="Califica leads de propiedades con inteligencia artificial" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="container mx-auto px-4 py-8">
          <header className="mb-8">
            <h1 className="mb-2 text-4xl font-bold text-gray-900">
              🏢 Sistema de Calificación de Leads Inmobiliarios
            </h1>
            <p className="text-lg text-gray-600">
              Inteligencia Artificial para filtrar leads de calidad y maximizar tu ROI
            </p>
          </header>

          <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-7">
            <div className="rounded-lg bg-white p-4 shadow">
              <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
              <div className="text-sm text-gray-600">Total Leads</div>
            </div>
            <div className="rounded-lg bg-red-100 p-4 shadow">
              <div className="text-2xl font-bold text-red-800">🔥 {stats.hot}</div>
              <div className="text-sm text-red-700">Hot Leads</div>
            </div>
            <div className="rounded-lg bg-orange-100 p-4 shadow">
              <div className="text-2xl font-bold text-orange-800">⚡ {stats.warm}</div>
              <div className="text-sm text-orange-700">Tibios</div>
            </div>
            <div className="rounded-lg bg-blue-100 p-4 shadow">
              <div className="text-2xl font-bold text-blue-800">❄️ {stats.cold}</div>
              <div className="text-sm text-blue-700">Fríos</div>
            </div>
            <div className="rounded-lg bg-gray-100 p-4 shadow">
              <div className="text-2xl font-bold text-gray-800">🚫 {stats.disqualified}</div>
              <div className="text-sm text-gray-700">Descalificados</div>
            </div>
            <div className="rounded-lg bg-purple-100 p-4 shadow">
              <div className="text-2xl font-bold text-purple-800">{stats.avgScore}</div>
              <div className="text-sm text-purple-700">Score Promedio</div>
            </div>
            <div className="rounded-lg bg-green-100 p-4 shadow">
              <div className="text-xl font-bold text-green-800">
                ${Math.round(stats.totalValue).toLocaleString('es-MX')}
              </div>
              <div className="text-sm text-green-700">Valor Estimado</div>
            </div>
          </div>

          <div className="mb-6 flex flex-wrap items-center gap-4">
            <Button
              onClick={() => setShowForm(!showForm)}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              {showForm ? '❌ Cerrar Formulario' : '➕ Nuevo Lead'}
            </Button>

            <div className="flex gap-2">
              <button
                onClick={() => setFilter('all')}
                className={`rounded px-4 py-2 text-sm font-semibold transition ${
                  filter === 'all' ? 'bg-gray-800 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                }`}
              >
                Todos
              </button>
              <button
                onClick={() => setFilter('hot')}
                className={`rounded px-4 py-2 text-sm font-semibold transition ${
                  filter === 'hot' ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800 hover:bg-red-200'
                }`}
              >
                🔥 Hot
              </button>
              <button
                onClick={() => setFilter('warm')}
                className={`rounded px-4 py-2 text-sm font-semibold transition ${
                  filter === 'warm' ? 'bg-orange-600 text-white' : 'bg-orange-100 text-orange-800 hover:bg-orange-200'
                }`}
              >
                ⚡ Tibio
              </button>
              <button
                onClick={() => setFilter('cold')}
                className={`rounded px-4 py-2 text-sm font-semibold transition ${
                  filter === 'cold' ? 'bg-blue-600 text-white' : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
                }`}
              >
                ❄️ Frío
              </button>
            </div>
          </div>

          {showForm && (
            <div className="mb-8">
              <LeadForm
                onSubmit={handleSubmitLead}
                onCancel={() => setShowForm(false)}
              />
            </div>
          )}

          {scoreLeadMutation.isLoading && (
            <div className="mb-6 rounded-lg bg-blue-100 p-4 text-center">
              <div className="text-lg font-semibold">🤖 Analizando lead con IA...</div>
            </div>
          )}

          {filteredLeads.length === 0 && !showForm ? (
            <div className="rounded-lg bg-white p-12 text-center shadow-lg">
              <div className="mb-4 text-6xl">🎯</div>
              <h2 className="mb-2 text-2xl font-bold">No hay leads calificados aún</h2>
              <p className="mb-6 text-gray-600">
                Comienza agregando tu primer lead para calificarlo con IA
              </p>
              <Button
                onClick={() => setShowForm(true)}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                ➕ Agregar Primer Lead
              </Button>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredLeads.map((lead) => (
                <LeadCard
                  key={lead.leadId}
                  score={lead}
                  onViewDetails={() => setSelectedLead(lead)}
                />
              ))}
            </div>
          )}

          {selectedLead && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
              <div className="max-h-[90vh] w-full max-w-3xl overflow-auto rounded-lg bg-white p-6 shadow-2xl">
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-2xl font-bold">Detalles Completos del Lead</h2>
                  <button
                    onClick={() => setSelectedLead(null)}
                    className="rounded-full bg-gray-200 px-4 py-2 font-semibold hover:bg-gray-300"
                  >
                    ✕ Cerrar
                  </button>
                </div>

                <LeadCard score={selectedLead} />

                <div className="mt-6 space-y-4">
                  <div>
                    <h3 className="mb-2 text-lg font-bold">📊 Scores Detallados</h3>
                    <div className="space-y-2">
                      {Object.entries(selectedLead.scores).map(([key, value]) => (
                        <div key={key} className="flex items-center gap-2">
                          <div className="w-48 text-sm font-semibold capitalize">
                            {key.replace(/([A-Z])/g, ' $1').trim()}
                          </div>
                          <div className="h-4 flex-1 rounded-full bg-gray-200">
                            <div
                              className="h-full rounded-full bg-gradient-to-r from-blue-500 to-purple-500"
                              style={{ width: `${value}%` }}
                            />
                          </div>
                          <div className="w-12 text-right text-sm font-bold">{value}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="mb-2 text-lg font-bold">💡 Todas las Recomendaciones</h3>
                    <ul className="space-y-2">
                      {selectedLead.recommendations.map((rec, idx) => (
                        <li key={idx} className="rounded bg-gray-50 p-2 text-sm">
                          • {rec}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h3 className="mb-2 text-lg font-bold">🎯 Acciones Recomendadas</h3>
                    <ul className="space-y-2">
                      {selectedLead.estimatedROI.recommendedActions.map((action, idx) => (
                        <li key={idx} className="rounded bg-blue-50 p-2 text-sm">
                          • {action}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
