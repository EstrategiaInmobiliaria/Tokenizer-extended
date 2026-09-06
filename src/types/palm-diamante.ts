export type TorreType = "I-A" | "I-B" | "II-A" | "II-B" | "III-A" | "III-B";

export type ModelType = 
  | "B1"
  | "A1" 
  | "A2"
  | "Roof Garden"
  | "Garden House"
  | "Penthouse";

export type UnitStatus = "disponible" | "vendido" | "reservado" | "apartado";

export interface PalmDiamanteUnit {
  id: string;
  torre: TorreType;
  model: ModelType;
  metrosCuadrados: number;
  precioTotal: number;
  status: UnitStatus;
  nivel?: number;
  numeroUnidad?: string;
}

export interface PaymentStructure {
  aparta: number; // $25,000 fijo
  firma7Percent: number; // 7% del precio total
  restaFirma: number; // firma7Percent - aparta
  percent13Total: number; // 13% del precio total
  mensualidad24Meses: number; // percent13Total / 24
  percent80Hipoteca: number; // 80% del precio total
}

export interface FinancingPlan extends PaymentStructure {
  unit: PalmDiamanteUnit;
  mesesFinanciamiento: number; // 5, 9, o 24 según la torre
  fechaEntregaEstimada?: string;
}

export interface LeadQualification {
  tieneLiquidezFirma: boolean; // ¿Cuenta con $353k-$868k?
  puedePagarMensualidad: boolean; // ¿Puede pagar $27k-$67k mensuales?
  quiereCreditoHipotecario: "si_rfc" | "si_persona_fisica" | "no";
  nombre?: string;
  email?: string;
  telefono?: string;
  notas?: string;
}

export interface TorreInfo {
  torre: TorreType;
  mesesFinanciamiento: number;
  unidadesDisponibles: number;
  fechaEntregaEstimada?: string;
}

export const TORRE_FINANCING_MONTHS: Record<TorreType, number> = {
  "I-A": 21,
  "I-B": 21,
  "II-A": 26,
  "II-B": 26,
  "III-A": 42,
  "III-B": 42,
};

export const APARTA_FIJO = 25000;
