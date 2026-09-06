import type { LeadScore } from '~/models/lead-scoring';

interface LeadCardProps {
  score: LeadScore;
  onViewDetails?: () => void;
}

export const LeadCard = ({ score, onViewDetails }: LeadCardProps) => {
  const categoryColors = {
    hot: 'bg-red-100 border-red-500 text-red-800',
    warm: 'bg-orange-100 border-orange-500 text-orange-800',
    cold: 'bg-blue-100 border-blue-500 text-blue-800',
    disqualified: 'bg-gray-100 border-gray-500 text-gray-800',
  };

  const categoryEmojis = {
    hot: '🔥',
    warm: '⚡',
    cold: '❄️',
    disqualified: '🚫',
  };

  const categoryLabels = {
    hot: 'HOT LEAD',
    warm: 'TIBIO',
    cold: 'FRÍO',
    disqualified: 'DESCALIFICADO',
  };

  return (
    <div className={`rounded-lg border-2 p-4 shadow-md transition-all hover:shadow-lg ${categoryColors[score.category]}`}>
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{categoryEmojis[score.category]}</span>
          <span className="font-bold text-lg">{categoryLabels[score.category]}</span>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold">{score.overallScore}</div>
          <div className="text-xs">Score</div>
        </div>
      </div>

      <div className="mb-3 space-y-2">
        <div className="flex justify-between text-sm">
          <span>💰 Capacidad Financiera:</span>
          <span className="font-semibold">{score.scores.financialCapacity}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>🎯 Intención de Compra:</span>
          <span className="font-semibold">{score.scores.buyingIntent}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>✅ Autenticidad:</span>
          <span className="font-semibold">{score.scores.authenticity}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>📱 Engagement:</span>
          <span className="font-semibold">{score.scores.engagement}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>🌐 Credibilidad Social:</span>
          <span className="font-semibold">{score.scores.socialCredibility}</span>
        </div>
      </div>

      <div className="mb-3 rounded bg-white bg-opacity-50 p-2">
        <div className="text-xs font-semibold mb-1">🎲 Probabilidad de Conversión</div>
        <div className="text-2xl font-bold">{score.estimatedROI.conversionProbability}%</div>
        {score.estimatedROI.estimatedValue && (
          <div className="text-xs mt-1">
            Valor estimado: ${score.estimatedROI.estimatedValue.toLocaleString('es-MX')}
          </div>
        )}
      </div>

      {score.redFlags && score.redFlags.length > 0 && (
        <div className="mb-3 rounded bg-red-50 p-2">
          <div className="text-xs font-semibold mb-1 text-red-900">⚠️ Banderas Rojas</div>
          <ul className="text-xs space-y-1">
            {score.redFlags.slice(0, 2).map((flag, idx) => (
              <li key={idx} className="text-red-800">• {flag.description}</li>
            ))}
          </ul>
        </div>
      )}

      {score.greenFlags && score.greenFlags.length > 0 && (
        <div className="mb-3 rounded bg-green-50 p-2">
          <div className="text-xs font-semibold mb-1 text-green-900">✅ Banderas Verdes</div>
          <ul className="text-xs space-y-1">
            {score.greenFlags.slice(0, 2).map((flag, idx) => (
              <li key={idx} className="text-green-800">• {flag.description}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="mb-3 rounded bg-white bg-opacity-50 p-2">
        <div className="text-xs font-semibold mb-1">💡 Recomendaciones</div>
        <ul className="text-xs space-y-1">
          {score.recommendations.slice(0, 2).map((rec, idx) => (
            <li key={idx}>• {rec}</li>
          ))}
        </ul>
      </div>

      {onViewDetails && (
        <button
          onClick={onViewDetails}
          className="w-full rounded bg-black bg-opacity-10 px-4 py-2 text-sm font-semibold transition-colors hover:bg-opacity-20"
        >
          Ver Detalles Completos
        </button>
      )}
    </div>
  );
};
