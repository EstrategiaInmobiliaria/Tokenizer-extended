import { useState } from "react";
import { calculatePaymentStructure, formatCurrency } from "~/utils/payment-calculator";
import { MODEL_PRICING } from "~/data/inventory";
import type { ModelType } from "~/types/palm-diamante";

interface CalculatorProps {
  onResultChange?: (result: ReturnType<typeof calculatePaymentStructure>) => void;
}

export function PalmDiamanteCalculator({ onResultChange }: CalculatorProps) {
  const [selectedModel, setSelectedModel] = useState<ModelType>("B1");
  const [customPrice, setCustomPrice] = useState<number | null>(null);

  const precioTotal = customPrice || MODEL_PRICING[selectedModel].precioBase;
  const result = calculatePaymentStructure(precioTotal);
  const modelInfo = MODEL_PRICING[selectedModel];

  return (
    <div className="flex flex-col gap-6 rounded-lg border-2 border-slate-200 bg-white p-6 shadow-lg">
      <div className="flex flex-col gap-4">
        <h2 className="text-2xl font-bold text-slate-900">
          Calculadora Palm Diamante
        </h2>
        <p className="text-sm text-slate-600">
          Estructura financiera: <strong>$25k aparta + 7% firma + 13% mensualidades + 80% hipoteca</strong>
        </p>
      </div>

      {/* Selector de Modelo */}
      <div className="flex flex-col gap-2">
        <label className="text-sm font-semibold text-slate-700">
          Modelo de Unidad
        </label>
        <select
          value={selectedModel}
          onChange={(e) => {
            setSelectedModel(e.target.value as ModelType);
            setCustomPrice(null);
          }}
          className="rounded-md border border-slate-300 bg-white px-4 py-2 text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {Object.entries(MODEL_PRICING).map(([model, info]) => (
            <option key={model} value={model}>
              {model} - {info.metrosCuadrados}m² - {formatCurrency(info.precioBase)}
            </option>
          ))}
        </select>
        <p className="text-xs text-slate-500">{modelInfo.descripcion}</p>
      </div>

      {/* Precio personalizado */}
      <div className="flex flex-col gap-2">
        <label className="text-sm font-semibold text-slate-700">
          Precio personalizado (opcional)
        </label>
        <input
          type="number"
          placeholder={formatCurrency(MODEL_PRICING[selectedModel].precioBase)}
          value={customPrice || ""}
          onChange={(e) => setCustomPrice(e.target.value ? Number(e.target.value) : null)}
          className="rounded-md border border-slate-300 px-4 py-2 text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Resultados */}
      <div className="flex flex-col gap-4 rounded-md border border-slate-200 bg-slate-50 p-4">
        <div className="grid gap-3">
          <ResultRow
            label="Precio Total"
            value={formatCurrency(precioTotal)}
            highlight
          />
          
          <div className="border-t border-slate-300 pt-3">
            <ResultRow
              label="1. Aparta (hoy)"
              value={formatCurrency(result.aparta)}
              description="Pago inicial para reservar"
              highlight
            />
          </div>

          <div className="border-t border-slate-300 pt-3">
            <ResultRow
              label="2. Firma Contrato (7%)"
              value={formatCurrency(result.firma7Percent)}
              description={`Incluye el aparta. Pagas ${formatCurrency(result.restaFirma)} adicional`}
            />
          </div>

          <div className="border-t border-slate-300 pt-3">
            <ResultRow
              label="3. Mensualidades (13% total)"
              value={formatCurrency(result.percent13Total)}
              description="Pagadero en 21, 26 o 42 meses según torre"
            />
            <div className="ml-4 mt-2 space-y-1 text-sm">
              <div className="flex justify-between text-slate-600">
                <span>42 meses (Torre III):</span>
                <span className="font-semibold text-green-700">
                  {formatCurrency(result.percent13Total / 42)}/mes
                </span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>26 meses (Torre II):</span>
                <span className="font-semibold">
                  {formatCurrency(result.percent13Total / 26)}/mes
                </span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>21 meses (Torre I):</span>
                <span className="font-semibold">
                  {formatCurrency(result.percent13Total / 21)}/mes
                </span>
              </div>
            </div>
          </div>

          <div className="border-t border-slate-300 pt-3">
            <ResultRow
              label="4. Crédito Hipotecario (80%)"
              value={formatCurrency(result.percent80Hipoteca)}
              description="Contra entrega - BBVA, Banorte, Santander"
              highlight
            />
          </div>
        </div>

        {/* Resumen de inversión inicial */}
        <div className="mt-4 rounded-md border-2 border-blue-500 bg-blue-50 p-4">
          <h3 className="mb-2 text-lg font-bold text-blue-900">
            💰 Inversión Inicial Real
          </h3>
          <div className="flex items-baseline justify-between">
            <span className="text-sm text-blue-700">
              Para asegurar {formatCurrency(precioTotal)}:
            </span>
            <span className="text-2xl font-bold text-blue-900">
              {formatCurrency(result.firma7Percent)}
            </span>
          </div>
          <p className="mt-2 text-xs text-blue-600">
            No necesitas {formatCurrency(precioTotal)} hoy. Solo {formatCurrency(result.firma7Percent)} para firma.
          </p>
        </div>
      </div>
    </div>
  );
}

interface ResultRowProps {
  label: string;
  value: string;
  description?: string;
  highlight?: boolean;
}

function ResultRow({ label, value, description, highlight }: ResultRowProps) {
  return (
    <div className={`flex flex-col gap-1 ${highlight ? "font-semibold" : ""}`}>
      <div className="flex items-baseline justify-between">
        <span className={highlight ? "text-slate-900" : "text-slate-700"}>
          {label}
        </span>
        <span className={highlight ? "text-xl text-blue-600" : "text-lg text-slate-900"}>
          {value}
        </span>
      </div>
      {description && (
        <p className="text-xs font-normal text-slate-500">{description}</p>
      )}
    </div>
  );
}
