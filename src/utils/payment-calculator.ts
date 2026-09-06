import type { PaymentStructure, PalmDiamanteUnit, FinancingPlan } from "~/types/palm-diamante";
import { APARTA_FIJO, TORRE_FINANCING_MONTHS } from "~/types/palm-diamante";

/**
 * Calcula la estructura de pagos para una unidad de Palm Diamante
 * Fórmula: $25k aparta + 7% firma + 13% en mensualidades + 80% hipoteca
 */
export function calculatePaymentStructure(precioTotal: number): PaymentStructure {
  const aparta = APARTA_FIJO;
  const firma7Percent = precioTotal * 0.07;
  const restaFirma = firma7Percent - aparta;
  const percent13Total = precioTotal * 0.13;
  const mensualidad24Meses = percent13Total / 24;
  const percent80Hipoteca = precioTotal * 0.80;

  return {
    aparta,
    firma7Percent,
    restaFirma,
    percent13Total,
    mensualidad24Meses,
    percent80Hipoteca,
  };
}

/**
 * Calcula el plan de financiamiento completo para una unidad
 */
export function calculateFinancingPlan(unit: PalmDiamanteUnit): FinancingPlan {
  const paymentStructure = calculatePaymentStructure(unit.precioTotal);
  const mesesFinanciamiento = TORRE_FINANCING_MONTHS[unit.torre];

  // Recalcular mensualidad basada en los meses de financiamiento reales de la torre
  const mensualidadAjustada = paymentStructure.percent13Total / mesesFinanciamiento;

  return {
    ...paymentStructure,
    mensualidad24Meses: mensualidadAjustada,
    unit,
    mesesFinanciamiento,
  };
}

/**
 * Formatea una cantidad en pesos mexicanos
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Calcula el ROI potencial para renta vacacional
 * Basado en Garden House: renta $95k/mes en temporada
 */
export function calculateROI(
  precioTotal: number,
  rentaMensualEstimada: number,
  mesesTemporadaAlta: number = 6
): {
  inversionInicial: number;
  ingresoAnualEstimado: number;
  roiAnual: number;
} {
  const paymentStructure = calculatePaymentStructure(precioTotal);
  const inversionInicial = paymentStructure.firma7Percent;
  const ingresoAnualEstimado = rentaMensualEstimada * mesesTemporadaAlta;
  const roiAnual = (ingresoAnualEstimado / inversionInicial) * 100;

  return {
    inversionInicial,
    ingresoAnualEstimado,
    roiAnual,
  };
}

/**
 * Determina si un lead está calificado basado en liquidez
 */
export function isLeadQualified(
  tieneLiquidez: boolean,
  puedePagarMensualidad: boolean,
  quiereCreditoHipotecario: boolean
): boolean {
  return tieneLiquidez && puedePagarMensualidad && quiereCreditoHipotecario;
}
