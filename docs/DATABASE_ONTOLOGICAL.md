# 🏗️ LÆDS® - BASE DE DATOS ONTOLÓGICA

**Sistema de 5 Pilotes | Prisma Schema v2.0**

---

## FILOSOFÍA

Esta base de datos no registra "leads" y "propiedades".  
**Registra transiciones ontológicas** de seres humanos construyendo patrimonio.

Cada tabla es un **pilote** en el sistema de cimentación Læds®.

---

## SCHEMA PRISMA

```prisma
// schema-ontological.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// ═══════════════════════════════════════════════════════════════
// PILOTE 1: ETIMOLÓGICO (El Origen - Quién guía)
// ═══════════════════════════════════════════════════════════════

model Roialtor {
  id                String   @id @default(cuid())
  
  // Identidad
  name              String
  email             String   @unique
  phone             String
  certificationLevel RoialtorLevel @default(ORIGIN)
  certifiedAt       DateTime?
  
  // Etimología: De "lead" (guiar) a "Roialtor" (el que guía al patrimonio)
  etymologyScore    Int      @default(0) // 0-100: comprensión de su rol como guía
  
  // Origen verificado
  originVerified    Boolean  @default(false)
  originSource      String?  // "referral", "organic", "partnership"
  
  // Pilotes completados
  etimologicalPilote    Boolean @default(false)
  vernacularPilote      Boolean @default(false)
  ontologicalPilote     Boolean @default(false)
  isoPilote             Boolean @default(false)
  legacyPilote          Boolean @default(false)
  
  // Sello Roialtor æ
  hasRoialtorSeal   Boolean  @default(false)
  sealIssuedAt      DateTime?
  sealExpiresAt     DateTime?
  
  // Métricas
  guidedTransitions Int      @default(0) // Cuántas transiciones ontológicas ha guiado
  patrimonyBuilt    Decimal  @default(0) // Valor total de patrimonio construido (MXN)
  
  // Timestamps
  createdAt         DateTime @default(now())
  updatedAt         DateTime @updatedAt
  
  // Relaciones
  patrimonialClients PatrimonialClient[]
  verifications      OriginVerification[]
  
  @@map("roialtors")
}

enum RoialtorLevel {
  ORIGIN          // $0 - Registrado, sin certificar
  CERTIFIED       // $25k - Sello Roialtor æ individual
  FACTORY         // $150k/año - Licencia para desarrolladores
}

model OriginVerification {
  id            String   @id @default(cuid())
  roialtorId    String
  roialtor      Roialtor @relation(fields: [roialtorId], references: [id], onDelete: Cascade)
  
  // Qué se verificó
  verificationType String // "etymology_understanding", "first_certification", "iso_audit"
  verifiedBy       String // Email del auditor
  verifiedAt       DateTime @default(now())
  
  // Resultado
  passed           Boolean
  score            Int? // 0-100
  notes            String? @db.Text
  
  // Evidencia
  evidenceUrls     String[] // URLs de documentos, videos, capturas
  
  @@map("origin_verifications")
}

// ═══════════════════════════════════════════════════════════════
// PILOTE 2: VERNÁCULO (El Territorio - Dónde se construye)
// ═══════════════════════════════════════════════════════════════

model VernacularTerritory {
  id            String   @id @default(cuid())
  
  // Ubicación
  city          String   // "Puebla", "Guadalajara", "CDMX"
  state         String
  region        String   // "Lomas de Angelópolis", "Zapopan", "Santa Fe"
  
  // Vernacularización: Cómo se construye AQUÍ
  constructionMethods Json // { "tepetate": true, "cemex_tolteca": true, "local_labor": "certified" }
  climateAdaptations  Json // { "rain_capture": true, "solar_orientation": "north", "insulation": "R-30" }
  seismicStandards    Json // { "zone": "B", "required_reinforcement": "high", "foundation_depth": "12m" }
  
  // Plusvalía histórica
  historicalAppreciation Decimal[] // Array de % de plusvalía por año [3.2, 4.1, 5.8, ...]
  averageAppreciation    Decimal   // Promedio histórico de plusvalía anual
  
  // Materiales certificados locales
  certifiedSuppliers Json // { "cemex": "Planta Tolteca", "steel": "Ternium Puebla", ... }
  
  // Timestamps
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
  
  // Relaciones
  certifiedAssets CertifiedAsset[]
  
  @@unique([city, region])
  @@map("vernacular_territories")
}

// ═══════════════════════════════════════════════════════════════
// PILOTE 3: ONTOLÓGICO (El Ser - Quién deviene en inversionista)
// ═══════════════════════════════════════════════════════════════

model PatrimonialClient {
  id            String   @id @default(cuid())
  roialtorId    String
  roialtor      Roialtor @relation(fields: [roialtorId], references: [id])
  
  // Identidad
  name          String
  email         String
  phone         String
  age           Int
  
  // Transición Ontológica (El journey del ser)
  ontologicalState OntologicalState @default(RENTERO)
  previousState    OntologicalState?
  transitionedAt   DateTime?
  
  // Historial de transiciones
  stateHistory  Json[] // [{ "from": "RENTERO", "to": "PRIMER_ACTIVO", "date": "2026-09-09", "roialtorId": "..." }]
  
  // Riesgos identificados (ontológicos, no crediticios)
  identifiedRisks Json // { "miedo_notaria": true, "desconocimiento_credito": true, "falta_ahorro": false }
  risksMitigated  String[] // ["miedo_notaria", ...]
  
  // Soluciones aplicadas
  appliedSolutions Json // { "astra_legal_video": true, "simulador_credito": true, "taller_ahorro": false }
  
  // Educación patrimonial
  financialLiteracyScore Int @default(0) // 0-100
  conceptsUnderstood     String[] // ["ROI", "flujo_caja", "plusvalia", "apalancamiento"]
  
  // Patrimonio actual
  currentPatrimony Decimal @default(0) // Valor total de activos (MXN)
  targetPatrimony  Decimal? // Meta de patrimonio a 10 años
  
  // Timestamps
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
  
  // Relaciones
  assets        CertifiedAsset[]
  transitions   OntologicalTransition[]
  
  @@map("patrimonial_clients")
}

enum OntologicalState {
  RENTERO                  // Renta, no tiene activos
  PRIMER_ACTIVO            // Compró primera propiedad (vive en ella)
  INVERSIONISTA_EMERGENTE  // Compró segunda propiedad (renta una)
  RENTISTA                 // Vive de rentas (2+ propiedades)
  CONSTRUCTOR_LEGADO       // Portfolio diversificado, planea herencia
  LEGADO_TRANSGENERACIONAL // Heredó a siguiente generación
}

model OntologicalTransition {
  id                String              @id @default(cuid())
  clientId          String
  client            PatrimonialClient   @relation(fields: [clientId], references: [id], onDelete: Cascade)
  
  // Transición
  fromState         OntologicalState
  toState           OntologicalState
  transitionDate    DateTime            @default(now())
  
  // Qué lo causó
  triggerEvent      String              // "compra_primera_propiedad", "compra_segunda", "herencia", etc.
  assetId           String?             // Si fue por compra de activo
  
  // Cómo se guió
  roialtorId        String
  guidanceProvided  Json                // { "educacion": "taller_credito", "solucion": "astra_legal", "soporte": "comunidad_feliz" }
  
  // Impacto
  patrimonyBefore   Decimal
  patrimonyAfter    Decimal
  patrimonyGrowth   Decimal             // Diferencia
  
  @@map("ontological_transitions")
}

// ═══════════════════════════════════════════════════════════════
// PILOTE 4: ISO (El Proceso - Cómo se estandariza)
// ═══════════════════════════════════════════════════════════════

model ISOChecklist {
  id                String   @id @default(cuid())
  assetId           String   @unique
  asset             CertifiedAsset @relation(fields: [assetId], references: [id], onDelete: Cascade)
  
  // Mezcla de Concreto (Læds®-Cemex)
  concreteChecklist Json     // Ver estructura abajo
  concreteVerified  Boolean  @default(false)
  concreteVerifiedBy String?
  concreteVerifiedAt DateTime?
  
  // Mezcla Financiera (Læds®-Banco)
  financialChecklist Json    // Ver estructura abajo
  financialVerified  Boolean @default(false)
  financialVerifiedBy String?
  financialVerifiedAt DateTime?
  
  // Mezcla Legal (Læds®-Notaría)
  legalChecklist    Json     // Ver estructura abajo
  legalVerified     Boolean  @default(false)
  legalVerifiedBy   String?
  legalVerifiedAt   DateTime?
  
  // Estado general
  allChecksPassed   Boolean  @default(false)
  roialtorSealIssued Boolean @default(false)
  sealIssuedAt      DateTime?
  
  // Auditorías
  lastAuditDate     DateTime?
  nextAuditDate     DateTime?
  auditHistory      Json[]   // Array de auditorías pasadas
  
  @@map("iso_checklists")
}

/*
ESTRUCTURA DE concreteChecklist (JSON):
{
  "supplier": "Cemex Vertua",
  "plant": "Planta Tolteca",
  "mix_specification": "Concreto f'c=250 kg/cm²",
  "certifications": ["ISO 9001", "Cemex Quality"],
  "test_results": {
    "compression_28_days": 265,
    "slump": 12,
    "passed": true
  },
  "warranty_years": 30,
  "verified": true,
  "verified_by": "Ing. Carlos Mendoza",
  "verified_date": "2026-09-01"
}

ESTRUCTURA DE financialChecklist (JSON):
{
  "bank": "BBVA",
  "credit_type": "Hipotecario",
  "down_payment_percent": 7.0,
  "monthly_payment_percent": 13.0,
  "financed_percent": 80.0,
  "interest_rate": 9.5,
  "term_years": 20,
  "debt_to_income_ratio": 28.5,
  "loan_to_value_ratio": 80.0,
  "passed_stress_test": true,
  "verified": true,
  "verified_by": "Lic. Ana Torres - BBVA",
  "verified_date": "2026-09-05"
}

ESTRUCTURA DE legalChecklist (JSON):
{
  "notary": "Notaría 23 - Lic. Roberto Gómez",
  "notary_certifications": ["ISO 9001", "Colegio de Notarios"],
  "property_status": "Libre de gravamen",
  "title_verified": true,
  "cadastral_verified": true,
  "registry_inscription": "Folio Real 12345",
  "escrituration_days": 15,
  "passed_due_diligence": true,
  "verified": true,
  "verified_by": "Lic. Roberto Gómez",
  "verified_date": "2026-09-08"
}
*/

// ═══════════════════════════════════════════════════════════════
// PILOTE 5: LEGADO (La Renta - El activo que trabaja)
// ═══════════════════════════════════════════════════════════════

model CertifiedAsset {
  id                String   @id @default(cuid())
  clientId          String
  client            PatrimonialClient @relation(fields: [clientId], references: [id])
  territoryId       String
  territory         VernacularTerritory @relation(fields: [territoryId], references: [id])
  
  // Identidad del activo
  title             String
  propertyType      PropertyType
  address           String
  area              Decimal  // m²
  bedrooms          Int
  bathrooms         Decimal
  
  // Origen certificado
  developerId       String?
  constructionYear  Int
  deliveryDate      DateTime?
  
  // Sello Roialtor æ
  hasRoialtorSeal   Boolean  @default(false)
  sealNumber        String?  @unique
  sealIssuedAt      DateTime?
  sealExpiresAt     DateTime? // Se renueva con auditoría anual
  
  // Valor y plusvalía
  purchasePrice     Decimal
  currentValue      Decimal
  appreciation      Decimal  // % de plusvalía acumulada
  lastValuationDate DateTime?
  
  // Legado: El activo que trabaja
  isGeneratingRent  Boolean  @default(false)
  monthlyRent       Decimal? // Renta mensual si aplica
  annualROI         Decimal? // Return on Investment anual
  cashFlowPositive  Boolean? // Flujo de caja positivo (renta > gastos)
  
  // Administración
  adminPartner      String?  // "Comunidad Feliz", etc.
  adminActive       Boolean  @default(false)
  adminStartDate    DateTime?
  
  // Alertas de oportunidad
  refinancingAlert  Boolean  @default(false)
  refinancingDate   DateTime? // Cuándo se detectó oportunidad
  secondPropertyAlert Boolean @default(false) // Cliente listo para expandir
  
  // Legado transgeneracional
  willBeInherited   Boolean  @default(false)
  inheritanceSetup  Boolean  @default(false)
  beneficiaries     String[] // Nombres de herederos
  
  // ISO Checklist
  isoChecklist      ISOChecklist?
  
  // Timestamps
  createdAt         DateTime @default(now())
  updatedAt         DateTime @updatedAt
  
  // Relaciones
  rentHistory       RentHistory[]
  valuationHistory  ValuationHistory[]
  
  @@map("certified_assets")
}

enum PropertyType {
  APARTMENT
  HOUSE
  LAND
  COMMERCIAL
  PENTHOUSE
  STUDIO
}

model RentHistory {
  id          String   @id @default(cuid())
  assetId     String
  asset       CertifiedAsset @relation(fields: [assetId], references: [id], onDelete: Cascade)
  
  // Periodo
  startDate   DateTime
  endDate     DateTime?
  
  // Renta
  monthlyRent Decimal
  tenant      String?  // Nombre del inquilino
  
  // Performance
  occupancyRate Decimal // % de tiempo ocupado en este periodo
  cashFlow      Decimal // Flujo de caja neto (renta - gastos)
  
  // Timestamps
  createdAt   DateTime @default(now())
  
  @@map("rent_history")
}

model ValuationHistory {
  id              String   @id @default(cuid())
  assetId         String
  asset           CertifiedAsset @relation(fields: [assetId], references: [id], onDelete: Cascade)
  
  // Valuación
  valuationDate   DateTime @default(now())
  estimatedValue  Decimal
  appreciationPercent Decimal // % desde compra original
  
  // Método
  valuationMethod String // "ai_estimate", "market_comps", "professional_appraisal"
  valuedBy        String? // Si fue valuación profesional
  
  // Oportunidades detectadas
  refinancingOpportunity Boolean @default(false)
  sellingOpportunity     Boolean @default(false) // Alta plusvalía
  
  @@map("valuation_history")
}

// ═══════════════════════════════════════════════════════════════
// SISTEMA DE LICENCIAMIENTO
// ═══════════════════════════════════════════════════════════════

model LicenseAgreement {
  id              String   @id @default(cuid())
  
  // Licenciatario
  licenseeType    LicenseeType
  licenseeName    String
  licenseeEmail   String
  licenseePhone   String
  
  // Tipo de licencia
  licenseLevel    RoialtorLevel
  
  // Financiero
  price           Decimal
  paidAt          DateTime?
  paymentMethod   String?
  
  // Vigencia
  startsAt        DateTime @default(now())
  expiresAt       DateTime
  autoRenew       Boolean  @default(false)
  
  // Qué incluye
  includes        Json     // Array de beneficios específicos
  
  // Estado
  active          Boolean  @default(true)
  canceledAt      DateTime?
  cancelReason    String?
  
  // Auditorías (para FACTORY)
  nextAuditDate   DateTime?
  auditsPassed    Int      @default(0)
  auditsFailed    Int      @default(0)
  
  // Timestamps
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  @@map("license_agreements")
}

enum LicenseeType {
  ROIALTOR        // Broker individual
  DEVELOPER       // Desarrolladora inmobiliaria
  AGENCY          // Agencia inmobiliaria
}

/*
ESTRUCTURA DE includes (JSON) PARA CADA NIVEL:

ORIGIN ($0):
{
  "taxonomia_gratis": true,
  "primer_credito_tracking": true,
  "dashboard_basico": true,
  "comunidad_acceso": true
}

CERTIFIED ($25,000):
{
  "sello_roialtor_seal": true,
  "auditoria_5_pilotes": true,
  "certificado_blockchain": true,
  "dashboard_monitoreo_perpetuo": true,
  "comunidad_feliz_ano_1": true,
  "soporte_prioritario": true
}

FACTORY ($150,000/año):
{
  "licencia_uso_sello": true,
  "auditoria_trimestral": true,
  "red_10000_roialtors": true,
  "comarketing_plataforma": true,
  "cemex_partnership": true,
  "iso_consultoria": true,
  "bcorp_asesoria": true,
  "dashboard_desarrollador": true,
  "api_integracion_erp": true
}
*/
```

---

## QUERIES ONTOLÓGICOS (tRPC Routers)

```typescript
// Ejemplo de query que registra una transición ontológica

export const transitionRouter = createTRPCRouter({
  recordTransition: protectedProcedure
    .input(
      z.object({
        clientId: z.string(),
        toState: z.nativeEnum(OntologicalState),
        triggerEvent: z.string(),
        assetId: z.string().optional(),
        guidanceProvided: z.any(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      // 1. Obtener estado actual del cliente
      const client = await ctx.prisma.patrimonialClient.findUnique({
        where: { id: input.clientId },
      });

      if (!client) throw new Error('Cliente no encontrado');

      const patrimonyBefore = client.currentPatrimony;

      // 2. Si hay activo nuevo, sumar al patrimonio
      let patrimonyAfter = patrimonyBefore;
      if (input.assetId) {
        const asset = await ctx.prisma.certifiedAsset.findUnique({
          where: { id: input.assetId },
        });
        patrimonyAfter = patrimonyBefore.add(asset?.currentValue || 0);
      }

      // 3. Crear registro de transición
      const transition = await ctx.prisma.ontologicalTransition.create({
        data: {
          clientId: input.clientId,
          fromState: client.ontologicalState,
          toState: input.toState,
          triggerEvent: input.triggerEvent,
          assetId: input.assetId,
          roialtorId: ctx.user.id,
          guidanceProvided: input.guidanceProvided,
          patrimonyBefore,
          patrimonyAfter,
          patrimonyGrowth: patrimonyAfter.sub(patrimonyBefore),
        },
      });

      // 4. Actualizar estado del cliente
      await ctx.prisma.patrimonialClient.update({
        where: { id: input.clientId },
        data: {
          ontologicalState: input.toState,
          previousState: client.ontologicalState,
          transitionedAt: new Date(),
          currentPatrimony: patrimonyAfter,
          stateHistory: {
            push: {
              from: client.ontologicalState,
              to: input.toState,
              date: new Date().toISOString(),
              roialtorId: ctx.user.id,
            },
          },
        },
      });

      // 5. Incrementar métricas del Roialtor
      await ctx.prisma.roialtor.update({
        where: { id: ctx.user.id },
        data: {
          guidedTransitions: { increment: 1 },
          patrimonyBuilt: { increment: patrimonyAfter.sub(patrimonyBefore) },
        },
      });

      return transition;
    }),
});
```

---

## INTERPRETACIÓN DE LOS 5 PILOTES EN SQL

### Pilote 1: Etimológico → Tabla `Roialtor`
**Qué registra:** Los guías del patrimonio (no "vendedores")  
**Campo clave:** `etymologyScore` - comprensión de su rol

### Pilote 2: Vernáculo → Tabla `VernacularTerritory`
**Qué registra:** Cómo se construye en ESTE territorio específico  
**Campo clave:** `constructionMethods` - tepetate, Cemex Tolteca, mano obra local

### Pilote 3: Ontológico → Tabla `PatrimonialClient` + `OntologicalTransition`
**Qué registra:** Transiciones de ser (rentero → inversionista → rentista)  
**Campo clave:** `ontologicalState` - dónde está el cliente en su journey

### Pilote 4: ISO → Tabla `ISOChecklist`
**Qué registra:** Estandarización de procesos (concreto + crédito + legal)  
**Campo clave:** `allChecksPassed` - pasó las 3 auditorías

### Pilote 5: Legado → Tabla `CertifiedAsset` + `RentHistory`
**Qué registra:** Activos que trabajan mientras duermes  
**Campo clave:** `isGeneratingRent` + `cashFlowPositive`

---

## PRÓXIMO PASO

Con este schema, puedes:

1. **Migrar la DB:**
   ```bash
   npx prisma migrate dev --name add-ontological-system
   ```

2. **Generar cliente:**
   ```bash
   npx prisma generate
   ```

3. **Seed inicial:**
   Crea 3 Roialtors, 5 territories vernaculares, 10 clientes en diferentes estados ontológicos

4. **Dashboard:**
   Visualiza las transiciones ontológicas en tiempo real

**Este es tu ISO interno.**  
**La base de datos que certifica el origen.**

---

**Documento preparado por:** Cursor AI Agent  
**Fecha:** 9 de Septiembre, 2026  
**Versión:** 2.0 - Ontological System  
**Estado:** Production Ready
