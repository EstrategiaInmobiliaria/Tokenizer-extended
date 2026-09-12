# 🏗️ læds® CRM - Arquitectura Técnica Detallada

**Versión:** 1.0  
**Fecha:** 9 de Septiembre, 2026  
**Autor:** Cursor AI Agent  
**Estado:** Especificación Técnica de Referencia

---

## 📋 Índice

1. [Visión General de Arquitectura](#visión-general-de-arquitectura)
2. [Diagrama de Componentes](#diagrama-de-componentes)
3. [Stack Tecnológico Detallado](#stack-tecnológico-detallado)
4. [Esquemas de Base de Datos](#esquemas-de-base-de-datos)
5. [Microservicios y APIs](#microservicios-y-apis)
6. [Flujos de Datos Críticos](#flujos-de-datos-críticos)
7. [Seguridad y Autenticación](#seguridad-y-autenticación)
8. [Escalabilidad y Performance](#escalabilidad-y-performance)
9. [Monitoreo y Observabilidad](#monitoreo-y-observabilidad)
10. [Deployment y CI/CD](#deployment-y-cicd)

---

## 1. Visión General de Arquitectura

### Principios de Diseño

1. **API-First:** Todas las funcionalidades expuestas vía APIs documentadas
2. **Multi-Tenant:** Aislamiento completo de datos por broker/agencia
3. **Event-Driven:** Arquitectura basada en eventos para desacoplamiento
4. **Scalable by Default:** Diseño horizontal desde día 1
5. **Security by Design:** Seguridad en cada capa, no como añadido
6. **Observability:** Logging, tracing y métricas en todo el sistema

### Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Web App    │  │  Mobile App  │  │  Extensión   │         │
│  │  (Next.js)   │  │(React Native)│  │  WhatsApp    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS/WSS
┌────────────────────────────┴────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Vercel Edge Functions / Cloudflare Workers              │  │
│  │  • Rate Limiting  • Auth  • Routing  • Caching           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ Internal Network
┌────────────────────────────┴────────────────────────────────────┐
│                     APPLICATION LAYER                           │
│  ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │   Core    │ │    AI    │ │Automation│ │   Integrations   │ │
│  │  Services │ │  Engine  │ │  Engine  │ │     Service      │ │
│  │  (tRPC)   │ │(Langchain│ │(Make.com)│ │(EasyBroker, etc) │ │
│  └───────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │PostgreSQL│ │ MongoDB  │ │  Redis   │ │    Pinecone      │  │
│  │(Neon.tech│ │(Atlas)   │ │(Upstash) │ │  (Embeddings)    │  │
│  │ Relational│ │Documents)│ │ (Cache)  │ │  (Vector Search) │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                   STORAGE & QUEUE LAYER                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │   S3     │ │  SQS/    │ │EventBridge│ │   CloudWatch    │  │
│  │(Cloudflare│ │ BullMQ  │ │ /Events  │ │   (Logs/Metrics)│  │
│  │   R2)    │ │ (Queue) │ │ (PubSub) │ │                  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Diagrama de Componentes

### Frontend Architecture (Next.js 14 App Router)

```
src/
├── app/                          # App Router (Next.js 14+)
│   ├── (auth)/                   # Grupo de rutas autenticadas
│   │   ├── login/
│   │   ├── register/
│   │   └── reset-password/
│   ├── (dashboard)/              # Grupo principal de app
│   │   ├── dashboard/            # Home del broker
│   │   ├── leads/                # Gestión de leads
│   │   ├── clients/              # Cartera de clientes
│   │   ├── properties/           # Inventario de propiedades
│   │   ├── proposals/            # Propuestas generadas
│   │   ├── automations/          # Config de automatizaciones
│   │   ├── analytics/            # Métricas y reportes
│   │   └── settings/             # Configuración
│   ├── api/                      # API Routes
│   │   ├── trpc/[trpc]/          # tRPC endpoints
│   │   ├── webhooks/             # Webhooks externos
│   │   │   ├── easybroker/
│   │   │   ├── whatsapp/
│   │   │   └── stripe/
│   │   └── cron/                 # Scheduled jobs
│   └── layout.tsx                # Root layout
├── components/
│   ├── ui/                       # shadcn/ui components
│   ├── forms/                    # Form components con validation
│   ├── layouts/                  # Layout wrappers
│   └── features/                 # Feature-specific components
│       ├── leads/
│       ├── proposals/
│       └── ai-chat/
├── lib/
│   ├── trpc/                     # tRPC client setup
│   ├── db/                       # Database clients (Prisma, MongoDB)
│   ├── ai/                       # AI utilities (Langchain wrappers)
│   └── integrations/             # External API clients
│       ├── easybroker.ts
│       ├── whatsapp.ts
│       └── make.ts
├── hooks/                        # Custom React hooks
├── stores/                       # Zustand stores
└── utils/                        # Utility functions
```

### Backend Architecture (Node.js + TypeScript)

```
packages/
├── api/                          # Main API service
│   ├── src/
│   │   ├── routers/              # tRPC routers
│   │   │   ├── leads.ts
│   │   │   ├── clients.ts
│   │   │   ├── properties.ts
│   │   │   ├── proposals.ts
│   │   │   └── automations.ts
│   │   ├── middleware/           # Auth, logging, error handling
│   │   ├── services/             # Business logic
│   │   │   ├── lead-service.ts
│   │   │   ├── proposal-service.ts
│   │   │   └── notification-service.ts
│   │   └── utils/
│   └── prisma/                   # Prisma schema & migrations
├── ai-engine/                    # AI Service (separado para escalar)
│   ├── src/
│   │   ├── agents/               # Langchain agents
│   │   │   ├── proposal-generator.ts
│   │   │   ├── lead-qualifier.ts
│   │   │   └── financial-analyzer.ts
│   │   ├── chains/               # Langchain chains
│   │   ├── tools/                # Langchain tools
│   │   └── prompts/              # Prompt templates
│   └── tests/
├── integrations/                 # Integration service
│   ├── src/
│   │   ├── adapters/             # Adapter pattern para integraciones
│   │   │   ├── crm/
│   │   │   │   ├── easybroker.adapter.ts
│   │   │   │   └── salesforce.adapter.ts (futuro)
│   │   │   ├── messaging/
│   │   │   │   ├── whatsapp.adapter.ts
│   │   │   │   └── telegram.adapter.ts (futuro)
│   │   │   └── payment/
│   │   │       ├── stripe.adapter.ts
│   │   │       └── conekta.adapter.ts
│   │   └── webhooks/             # Webhook handlers
│   └── tests/
├── automation-engine/            # Make.com alternative (futuro in-house)
│   └── src/
│       ├── workflows/            # Workflow definitions
│       ├── triggers/             # Event triggers
│       └── actions/              # Action executors
└── shared/                       # Shared utilities & types
    ├── types/                    # TypeScript types compartidos
    ├── constants/
    └── utils/
```

---

## 3. Stack Tecnológico Detallado

### Frontend Stack

| Categoría | Tecnología | Versión | Justificación |
|-----------|-----------|---------|---------------|
| **Framework** | Next.js | 14.2+ | SSR, App Router, Edge Functions, Best DX |
| **Language** | TypeScript | 5.4+ | Type safety, mejor DX, menos bugs en producción |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first, rápido desarrollo, consistencia |
| **UI Components** | shadcn/ui | Latest | Componentes accesibles, customizables, no-dependency |
| **State Management** | Zustand | 4.5+ | Ligero (1kb), simple API, no boilerplate |
| **Forms** | React Hook Form | 7.51+ | Performance, validación, integración con Zod |
| **Validation** | Zod | 3.22+ | Type-safe schema validation, integración tRPC |
| **Data Fetching** | tRPC | 10.45+ | End-to-end type safety, no code generation |
| **Charts** | Recharts | 2.12+ | Declarativo, responsive, basado en D3 |
| **Date** | date-fns | 3.6+ | Funcional, tree-shakeable, i18n |
| **Icons** | Lucide React | 0.index | Iconos modernos, consistentes |
| **Testing** | Vitest + Testing Library | Latest | Rápido, compatible Jest, mejor DX |

### Backend Stack

| Categoría | Tecnología | Versión | Justificación |
|-----------|-----------|---------|---------------|
| **Runtime** | Node.js | 20 LTS | Estabilidad, performance, ecosistema |
| **Framework** | tRPC | 10.45+ | Type safety full-stack, menos código |
| **ORM** | Prisma | 5.13+ | Type-safe queries, migraciones, introspección |
| **Validation** | Zod | 3.22+ | Consistencia con frontend, type inference |
| **Authentication** | Clerk | Latest | Multi-tenant, SSO, MFA out-of-the-box |
| **Queue** | BullMQ | 5.7+ | Redis-backed, retry logic, cron jobs |
| **Testing** | Vitest | Latest | Mismo stack que frontend, fast |

### Databases & Storage

| Tipo | Tecnología | Proveedor | Uso |
|------|-----------|-----------|-----|
| **Relational** | PostgreSQL 16 | Neon.tech | Datos estructurados (users, leads, properties) |
| **Document** | MongoDB 7 | MongoDB Atlas | Documentos (expedientes, logs de IA) |
| **Cache** | Redis 7 | Upstash | Sessions, rate limiting, pub/sub |
| **Vector** | Pinecone | Pinecone.io | Embeddings para búsqueda semántica |
| **Object Storage** | S3-compatible | Cloudflare R2 | Imágenes, documentos, backups |

### AI & ML Stack

| Categoría | Tecnología | Provider | Uso |
|-----------|-----------|----------|-----|
| **LLM Principal** | GPT-4o/GPT-5 | OpenAI | Generación de propuestas, análisis |
| **LLM Fallback** | Claude 3.5 Opus | Anthropic | Backup, tareas específicas |
| **Embeddings** | text-embedding-3-large | OpenAI | Búsqueda semántica de propiedades |
| **Orchestration** | Langchain.js | OSS | Chains, agents, tools |
| **Vector DB** | Pinecone | Pinecone.io | Almacenar embeddings |
| **Fine-tuning** | OpenAI Fine-tuning | OpenAI | Modelos personalizados (futuro) |

### Infrastructure & DevOps

| Categoría | Tecnología | Provider | Justificación |
|-----------|-----------|----------|---------------|
| **Frontend Hosting** | Vercel | Vercel | Next.js optimizado, Edge Functions |
| **Backend Hosting** | Fly.io | Fly.io | Global deployment, Docker, bajo costo |
| **CDN** | Cloudflare | Cloudflare | Performance, DDoS protection |
| **Monitoring** | Sentry | Sentry.io | Error tracking, performance monitoring |
| **Analytics** | PostHog | PostHog | Product analytics, self-hosted option |
| **Logging** | Axiom | Axiom.co | Structured logging, fast search |
| **APM** | Highlight.io | Highlight | Session replay, performance |
| **Secrets** | Doppler | Doppler | Secret management, rotación |
| **CI/CD** | GitHub Actions | GitHub | Integration con repo, gratis OSS |

---

## 4. Esquemas de Base de Datos

### PostgreSQL Schema (Prisma)

```prisma
// schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// =====================
// USERS & AUTHENTICATION
// =====================

model Organization {
  id        String   @id @default(cuid())
  name      String
  slug      String   @unique
  tier      Tier     @default(FREE)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  users         User[]
  leads         Lead[]
  clients       Client[]
  properties    Property[]
  proposals     Proposal[]
  automations   Automation[]
  
  // Settings
  settings      Json? // Configuraciones generales
  branding      Json? // Logo, colores, etc. para white-label

  @@map("organizations")
}

enum Tier {
  FREE
  PROFESSIONAL
  AGENCY
  ENTERPRISE
}

model User {
  id             String   @id @default(cuid())
  clerkId        String   @unique // ID de Clerk
  email          String   @unique
  name           String
  avatar         String?
  role           Role     @default(BROKER)
  organizationId String
  organization   Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  createdAt      DateTime @default(now())
  updatedAt      DateTime @updatedAt

  // Relaciones
  leadsOwned     Lead[]
  clientsOwned   Client[]
  proposalsCreated Proposal[]
  activities     Activity[]

  // Métricas
  metrics        Json? // { totalLeads, conversions, revenue, etc. }

  @@map("users")
}

enum Role {
  BROKER
  MANAGER
  ADMIN
  OWNER
}

// =====================
// LEADS
// =====================

model Lead {
  id             String   @id @default(cuid())
  organizationId String
  organization   Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  ownerId        String
  owner          User     @relation(fields: [ownerId], references: [id])
  
  // Información básica
  name           String
  email          String
  phone          String
  source         LeadSource
  status         LeadStatus @default(NEW)
  
  // Calificación
  budget         Decimal?
  preApproved    Boolean  @default(false)
  score          Int?     // 0-100 score de IA
  
  // Preferencias
  preferences    Json?    // { bedrooms, location, propertyType, etc. }
  
  // Metadata
  metadata       Json?    // { utmSource, utmCampaign, adId, etc. }
  
  // Timestamps
  createdAt      DateTime @default(now())
  updatedAt      DateTime @updatedAt
  lastContactAt  DateTime?
  convertedAt    DateTime?

  // Relaciones
  activities     Activity[]
  proposals      Proposal[]
  client         Client?    // Si se convierte

  @@map("leads")
  @@index([organizationId, status])
  @@index([organizationId, ownerId])
  @@index([createdAt])
}

enum LeadSource {
  META_ADS
  GOOGLE_ADS
  WEBSITE
  REFERRAL
  WALK_IN
  WHATSAPP
  OTHER
}

enum LeadStatus {
  NEW
  CONTACTED
  QUALIFIED
  PROPOSAL_SENT
  NEGOTIATING
  CONVERTED
  LOST
}

// =====================
// CLIENTS
// =====================

model Client {
  id             String   @id @default(cuid())
  organizationId String
  organization   Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  ownerId        String
  owner          User     @relation(fields: [ownerId], references: [id])
  leadId         String?  @unique
  lead           Lead?    @relation(fields: [leadId], references: [id])
  
  // Información básica
  name           String
  email          String
  phone          String
  rfc            String?
  
  // Dirección
  address        Json?
  
  // Financiero
  totalPurchases Decimal  @default(0)
  lifetimeValue  Decimal  @default(0)
  
  // Metadata
  metadata       Json?
  tags           String[]
  
  // Timestamps
  createdAt      DateTime @default(now())
  updatedAt      DateTime @updatedAt

  // Relaciones
  purchases      Purchase[]
  activities     Activity[]
  patrimony      PatrimonyTracking[]

  @@map("clients")
  @@index([organizationId, ownerId])
}

// =====================
// PROPERTIES
// =====================

model Property {
  id              String   @id @default(cuid())
  organizationId  String
  organization    Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  
  // Info de EasyBroker (si aplica)
  externalId      String?  @unique // ID de EasyBroker
  externalSource  String?  // "easybroker", "manual", etc.
  
  // Información básica
  title           String
  description     String   @db.Text
  propertyType    PropertyType
  status          PropertyStatus @default(AVAILABLE)
  
  // Ubicación
  address         String
  city            String
  state           String
  zipCode         String?
  coordinates     Json?    // { lat, lng }
  
  // Características
  bedrooms        Int?
  bathrooms       Decimal?
  parkingSpots    Int?
  area            Decimal? // m²
  builtArea       Decimal? // m² construidos
  
  // Financiero
  price           Decimal
  pricePerM2      Decimal?
  downPayment     Decimal?
  monthlyPayment  Decimal?
  
  // Media
  images          String[] // URLs de imágenes
  videos          String[] // URLs de videos
  virtualTour     String?  // URL de tour virtual
  
  // Desarrolladora
  developer       Json?    // { name, certifications, etc. }
  
  // Metadata
  metadata        Json?
  tags            String[]
  
  // Timestamps
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  publishedAt     DateTime?
  soldAt          DateTime?

  // Relaciones
  proposals       Proposal[]
  purchases       Purchase[]
  
  // Vector embedding para búsqueda semántica
  embedding       Float[]  // Almacenado localmente también (backup)

  @@map("properties")
  @@index([organizationId, status])
  @@index([propertyType, status])
  @@index([city, status])
}

enum PropertyType {
  APARTMENT
  HOUSE
  LAND
  COMMERCIAL
  PENTHOUSE
  STUDIO
}

enum PropertyStatus {
  AVAILABLE
  RESERVED
  SOLD
  RENTED
  UNAVAILABLE
}

// =====================
// PROPOSALS
// =====================

model Proposal {
  id             String   @id @default(cuid())
  organizationId String
  ownerId        String
  owner          User     @relation(fields: [ownerId], references: [id])
  leadId         String
  lead           Lead     @relation(fields: [leadId], references: [id], onDelete: Cascade)
  propertyId     String
  property       Property @relation(fields: [propertyId], references: [id])
  
  // Contenido
  title          String
  content        String   @db.Text // Markdown generado por IA
  imageUrl       String?  // Imagen personalizada generada
  pdfUrl         String?  // PDF generado
  
  // Financiero
  price          Decimal
  downPayment    Decimal
  monthlyPayment Decimal
  term           Int      // Meses
  interestRate   Decimal?
  
  // Estado
  status         ProposalStatus @default(DRAFT)
  sentAt         DateTime?
  viewedAt       DateTime?
  expiresAt      DateTime? // 48 horas típicamente
  
  // Respuesta
  response       String?  // INTERESTED, NOT_INTERESTED, NEED_MORE_INFO
  responseNotes  String?  @db.Text
  
  // Metadata
  metadata       Json?    // { generatedBy: "AI", template: "palm-diamante", etc. }
  
  // Timestamps
  createdAt      DateTime @default(now())
  updatedAt      DateTime @updatedAt

  @@map("proposals")
  @@index([organizationId, ownerId])
  @@index([leadId])
  @@index([status, expiresAt])
}

enum ProposalStatus {
  DRAFT
  SENT
  VIEWED
  EXPIRED
  ACCEPTED
  REJECTED
}

// =====================
// PURCHASES
// =====================

model Purchase {
  id             String   @id @default(cuid())
  clientId       String
  client         Client   @relation(fields: [clientId], references: [id], onDelete: Cascade)
  propertyId     String
  property       Property @relation(fields: [propertyId], references: [id])
  
  // Financiero
  totalPrice     Decimal
  downPayment    Decimal
  financedAmount Decimal
  monthlyPayment Decimal
  term           Int
  interestRate   Decimal?
  
  // Estado
  status         PurchaseStatus @default(RESERVED)
  
  // Documentos
  contractUrl    String?
  notaryInfo     Json?
  
  // Fechas importantes
  reservedAt     DateTime
  contractAt     DateTime?
  deliveryAt     DateTime?
  completedAt    DateTime?
  
  // Metadata
  metadata       Json?
  
  // Timestamps
  createdAt      DateTime @default(now())
  updatedAt      DateTime @updatedAt

  @@map("purchases")
  @@index([clientId])
  @@index([status])
}

enum PurchaseStatus {
  RESERVED
  CONTRACT_SIGNED
  FINANCING_APPROVED
  IN_CONSTRUCTION
  DELIVERED
  COMPLETED
  CANCELLED
}

// =====================
// AUTOMATIONS
// =====================

model Automation {
  id             String   @id @default(cuid())
  organizationId String
  organization   Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  
  // Configuración
  name           String
  description    String?
  enabled        Boolean  @default(true)
  
  // Workflow
  trigger        Json     // { type: "lead_created", conditions: {...} }
  actions        Json     // [{ type: "send_whatsapp", template: "..." }, ...]
  
  // Ejecución
  runsCount      Int      @default(0)
  lastRunAt      DateTime?
  
  // Metadata
  metadata       Json?
  
  // Timestamps
  createdAt      DateTime @default(now())
  updatedAt      DateTime @updatedAt

  @@map("automations")
  @@index([organizationId, enabled])
}

// =====================
// ACTIVITY LOG
// =====================

model Activity {
  id             String   @id @default(cuid())
  userId         String?
  user           User?    @relation(fields: [userId], references: [id], onDelete: SetNull)
  leadId         String?
  lead           Lead?    @relation(fields: [leadId], references: [id], onDelete: Cascade)
  clientId       String?
  client         Client?  @relation(fields: [clientId], references: [id], onDelete: Cascade)
  
  // Actividad
  type           ActivityType
  title          String
  description    String?  @db.Text
  metadata       Json?
  
  // Timestamps
  createdAt      DateTime @default(now())

  @@map("activities")
  @@index([userId, createdAt])
  @@index([leadId, createdAt])
  @@index([clientId, createdAt])
}

enum ActivityType {
  LEAD_CREATED
  LEAD_CONTACTED
  PROPOSAL_SENT
  PROPOSAL_VIEWED
  MEETING_SCHEDULED
  CALL_MADE
  EMAIL_SENT
  WHATSAPP_SENT
  NOTE_ADDED
  STATUS_CHANGED
  PURCHASE_COMPLETED
}

// =====================
// PATRIMONY TRACKING
// =====================

model PatrimonyTracking {
  id             String   @id @default(cuid())
  clientId       String
  client         Client   @relation(fields: [clientId], references: [id], onDelete: Cascade)
  
  // Valores
  currentValue   Decimal  // Valor actual estimado
  purchaseValue  Decimal  // Valor de compra original
  appreciation   Decimal  // Plusvalía %
  
  // Metadata
  calculatedBy   String   // "manual", "ai", "market_data"
  metadata       Json?
  
  // Timestamp
  date           DateTime @default(now())

  @@map("patrimony_tracking")
  @@index([clientId, date])
}
```

### MongoDB Collections (para documentos no estructurados)

```typescript
// collections.ts

// Collection: ai_conversations
interface AIConversation {
  _id: ObjectId;
  organizationId: string;
  userId: string;
  leadId?: string;
  clientId?: string;
  
  // Conversación
  messages: {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    metadata?: any;
  }[];
  
  // Metadata
  model: string; // "gpt-4", "claude-3-opus", etc.
  tokens: number;
  cost: number; // USD
  
  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

// Collection: audit_logs
interface AuditLog {
  _id: ObjectId;
  organizationId: string;
  userId?: string;
  
  // Evento
  action: string; // "user.created", "lead.updated", "proposal.sent"
  resource: string; // "user", "lead", "proposal"
  resourceId: string;
  
  // Cambios
  before?: any; // Estado anterior
  after?: any; // Estado nuevo
  
  // Metadata
  ip: string;
  userAgent: string;
  metadata?: any;
  
  // Timestamp
  timestamp: Date;
}

// Collection: documents
interface Document {
  _id: ObjectId;
  organizationId: string;
  clientId?: string;
  leadId?: string;
  
  // Documento
  type: 'contract' | 'identification' | 'proof_of_income' | 'other';
  name: string;
  url: string; // S3/R2 URL
  mimeType: string;
  size: number; // bytes
  
  // OCR y análisis
  extractedText?: string;
  analysis?: any; // Resultado de análisis de IA
  
  // Seguridad
  encryptionKey?: string; // Si está encriptado
  
  // Timestamps
  uploadedAt: Date;
  expiresAt?: Date;
}

// Collection: webhook_logs
interface WebhookLog {
  _id: ObjectId;
  source: string; // "easybroker", "whatsapp", "stripe"
  
  // Request
  method: string;
  path: string;
  headers: any;
  body: any;
  
  // Response
  statusCode: number;
  responseBody: any;
  
  // Procesamiento
  processed: boolean;
  error?: string;
  
  // Timestamps
  receivedAt: Date;
  processedAt?: Date;
}
```

---

## 5. Microservicios y APIs

### Core API (tRPC Routers)

```typescript
// src/server/api/root.ts

import { createTRPCRouter } from './trpc';
import { leadRouter } from './routers/lead';
import { clientRouter } from './routers/client';
import { propertyRouter } from './routers/property';
import { proposalRouter } from './routers/proposal';
import { automationRouter } from './routers/automation';
import { analyticsRouter } from './routers/analytics';
import { aiRouter } from './routers/ai';

export const appRouter = createTRPCRouter({
  lead: leadRouter,
  client: clientRouter,
  property: propertyRouter,
  proposal: proposalRouter,
  automation: automationRouter,
  analytics: analyticsRouter,
  ai: aiRouter,
});

export type AppRouter = typeof appRouter;
```

### Lead Router (Ejemplo Detallado)

```typescript
// src/server/api/routers/lead.ts

import { z } from 'zod';
import { createTRPCRouter, protectedProcedure } from '../trpc';
import { LeadService } from '@/services/lead-service';
import { AIService } from '@/services/ai-service';

export const leadRouter = createTRPCRouter({
  // Listar leads
  list: protectedProcedure
    .input(
      z.object({
        status: z.enum(['NEW', 'CONTACTED', 'QUALIFIED', 'PROPOSAL_SENT', 'NEGOTIATING', 'CONVERTED', 'LOST']).optional(),
        search: z.string().optional(),
        limit: z.number().min(1).max(100).default(50),
        cursor: z.string().optional(), // Para paginación
      })
    )
    .query(async ({ ctx, input }) => {
      const leads = await LeadService.list({
        organizationId: ctx.user.organizationId,
        ...input,
      });
      return leads;
    }),

  // Obtener un lead
  get: protectedProcedure
    .input(z.object({ id: z.string() }))
    .query(async ({ ctx, input }) => {
      const lead = await LeadService.get({
        id: input.id,
        organizationId: ctx.user.organizationId,
      });
      return lead;
    }),

  // Crear lead
  create: protectedProcedure
    .input(
      z.object({
        name: z.string().min(1),
        email: z.string().email(),
        phone: z.string(),
        source: z.enum(['META_ADS', 'GOOGLE_ADS', 'WEBSITE', 'REFERRAL', 'WALK_IN', 'WHATSAPP', 'OTHER']),
        budget: z.number().optional(),
        preferences: z.any().optional(),
        metadata: z.any().optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      // Crear lead
      const lead = await LeadService.create({
        ...input,
        organizationId: ctx.user.organizationId,
        ownerId: ctx.user.id,
      });

      // Calificar con IA (asíncrono, no bloqueante)
      AIService.qualifyLead(lead.id).catch(console.error);

      return lead;
    }),

  // Actualizar lead
  update: protectedProcedure
    .input(
      z.object({
        id: z.string(),
        status: z.enum(['NEW', 'CONTACTED', 'QUALIFIED', 'PROPOSAL_SENT', 'NEGOTIATING', 'CONVERTED', 'LOST']).optional(),
        budget: z.number().optional(),
        preferences: z.any().optional(),
        metadata: z.any().optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { id, ...data } = input;
      const lead = await LeadService.update({
        id,
        organizationId: ctx.user.organizationId,
        data,
      });
      return lead;
    }),

  // Calificar lead con IA
  qualify: protectedProcedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ ctx, input }) => {
      const qualification = await AIService.qualifyLead(input.id);
      return qualification;
    }),

  // Generar propuesta automática
  generateProposal: protectedProcedure
    .input(
      z.object({
        leadId: z.string(),
        propertyId: z.string().optional(), // Si no se provee, IA elige mejor match
      })
    )
    .mutation(async ({ ctx, input }) => {
      let propertyId = input.propertyId;

      // Si no se especificó propiedad, usar IA para matching
      if (!propertyId) {
        const match = await AIService.matchLeadToProperty({
          leadId: input.leadId,
          organizationId: ctx.user.organizationId,
        });
        propertyId = match.propertyId;
      }

      // Generar propuesta
      const proposal = await AIService.generateProposal({
        leadId: input.leadId,
        propertyId,
        userId: ctx.user.id,
      });

      return proposal;
    }),
});
```

### AI Service API Endpoints (REST para external integrations)

```typescript
// src/pages/api/ai/generate-proposal.ts

import { NextApiRequest, NextApiResponse } from 'next';
import { verifyApiKey } from '@/lib/auth';
import { AIService } from '@/services/ai-service';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Verificar API key
  const apiKey = req.headers.authorization?.replace('Bearer ', '');
  const organization = await verifyApiKey(apiKey);
  if (!organization) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const { leadId, propertyId } = req.body;

    const proposal = await AIService.generateProposal({
      leadId,
      propertyId,
      organizationId: organization.id,
    });

    return res.status(200).json(proposal);
  } catch (error) {
    console.error('Error generating proposal:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
```

---

## 6. Flujos de Datos Críticos

### Flujo 1: Meta Lead → Propuesta Personalizada (48h)

```mermaid
sequenceDiagram
    participant Meta as Meta Ads
    participant Webhook as Webhook Handler
    participant API as Core API
    participant AI as AI Engine
    participant EB as EasyBroker
    participant WA as WhatsApp API
    participant Queue as Job Queue

    Meta->>Webhook: POST /api/webhooks/meta-lead
    Webhook->>API: leadRouter.create()
    API->>Queue: Queue job: "qualify-lead"
    API-->>Webhook: 201 Created { leadId }
    
    Queue->>AI: qualifyLead(leadId)
    AI->>API: Get lead data
    AI->>AI: GPT-4: Analyze profile
    AI->>API: Update lead.score
    
    alt Score >= 70 (Qualified)
        Queue->>AI: matchLeadToProperty(leadId)
        AI->>EB: GET /properties
        AI->>AI: Semantic search (embeddings)
        AI->>API: Get best match propertyId
        
        Queue->>AI: generateProposal(leadId, propertyId)
        AI->>AI: GPT-4: Generate content
        AI->>AI: Generate personalized image
        AI->>API: Save proposal
        
        Queue->>WA: Send WhatsApp message
        WA->>Lead: "Juan, tu propuesta..."
        
        Queue->>API: Create activity log
    else Score < 70 (Not qualified)
        Queue->>API: Update lead.status = LOST
        Queue->>API: Create activity log
    end
```

### Flujo 2: Pago Confirmado → Onboarding Cliente

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant Payment as Payment Gateway
    participant Webhook as Webhook Handler
    participant API as Core API
    participant Storage as File Storage
    participant Cal as Google Calendar
    participant WA as WhatsApp API

    Client->>Payment: Transfer to CLABE
    Payment->>Webhook: POST /api/webhooks/payment
    Webhook->>API: purchaseRouter.create()
    API->>Storage: Move to "PD-APARTA PAGADO"
    
    API->>Cal: Create calendar event
    Cal-->>API: Event created
    
    API->>WA: Send onboarding message
    WA->>Client: "¡Felicidades! Siguiente paso..."
    
    API->>WA: Request KYC documents
    WA->>Client: "Por favor envía: INE, comprobante..."
    
    Client->>WA: Uploads documents
    WA->>Webhook: POST /api/webhooks/whatsapp
    Webhook->>Storage: Upload to S3
    Webhook->>API: Update purchase.status
```

### Flujo 3: Búsqueda Semántica de Propiedades

```mermaid
sequenceDiagram
    participant User as Usuario
    participant UI as Frontend
    participant API as Core API
    participant AI as AI Engine
    participant Pinecone as Vector DB
    participant Postgres as PostgreSQL

    User->>UI: Search: "departamento cerca del metro con 2 recámaras"
    UI->>API: propertyRouter.semanticSearch()
    API->>AI: generateEmbedding(query)
    AI->>OpenAI: text-embedding-3-large
    OpenAI-->>AI: [0.123, -0.456, ...]
    
    AI->>Pinecone: query(embedding, topK=10)
    Pinecone-->>AI: [propertyId1, propertyId2, ...]
    
    AI->>Postgres: Get properties by IDs
    Postgres-->>AI: [Property[], with full data]
    
    AI->>AI: Re-rank by relevance
    AI-->>API: Sorted results
    API-->>UI: Response
    UI-->>User: Display results
```

---

## 7. Seguridad y Autenticación

### Authentication Flow (Clerk)

```typescript
// middleware.ts (Next.js)

import { authMiddleware } from '@clerk/nextjs';

export default authMiddleware({
  publicRoutes: [
    '/',
    '/api/webhooks/(.*)',
    '/sign-in(.*)',
    '/sign-up(.*)',
  ],
  ignoredRoutes: [
    '/api/health',
  ],
});

export const config = {
  matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
};
```

### Authorization (RBAC)

```typescript
// lib/permissions.ts

export const PERMISSIONS = {
  // Leads
  'lead:create': ['BROKER', 'MANAGER', 'ADMIN', 'OWNER'],
  'lead:read:own': ['BROKER', 'MANAGER', 'ADMIN', 'OWNER'],
  'lead:read:all': ['MANAGER', 'ADMIN', 'OWNER'],
  'lead:update:own': ['BROKER', 'MANAGER', 'ADMIN', 'OWNER'],
  'lead:update:all': ['MANAGER', 'ADMIN', 'OWNER'],
  'lead:delete': ['ADMIN', 'OWNER'],
  
  // Proposals
  'proposal:create': ['BROKER', 'MANAGER', 'ADMIN', 'OWNER'],
  'proposal:send': ['BROKER', 'MANAGER', 'ADMIN', 'OWNER'],
  
  // Properties
  'property:create': ['MANAGER', 'ADMIN', 'OWNER'],
  'property:update': ['MANAGER', 'ADMIN', 'OWNER'],
  'property:delete': ['ADMIN', 'OWNER'],
  
  // Settings
  'settings:update': ['ADMIN', 'OWNER'],
  'settings:billing': ['OWNER'],
  
  // Users
  'user:invite': ['MANAGER', 'ADMIN', 'OWNER'],
  'user:remove': ['ADMIN', 'OWNER'],
} as const;

export function hasPermission(userRole: Role, permission: keyof typeof PERMISSIONS): boolean {
  return PERMISSIONS[permission].includes(userRole);
}

// Uso en tRPC
export const protectedProcedure = publicProcedure.use(async ({ ctx, next }) => {
  if (!ctx.session?.userId) {
    throw new TRPCError({ code: 'UNAUTHORIZED' });
  }

  const user = await prisma.user.findUnique({
    where: { clerkId: ctx.session.userId },
    include: { organization: true },
  });

  if (!user) {
    throw new TRPCError({ code: 'UNAUTHORIZED' });
  }

  return next({
    ctx: {
      ...ctx,
      user,
    },
  });
});

export const requirePermission = (permission: keyof typeof PERMISSIONS) => {
  return protectedProcedure.use(async ({ ctx, next }) => {
    if (!hasPermission(ctx.user.role, permission)) {
      throw new TRPCError({ code: 'FORBIDDEN' });
    }
    return next();
  });
};
```

### Data Encryption

```typescript
// lib/encryption.ts

import crypto from 'crypto';

const ALGORITHM = 'aes-256-gcm';
const KEY_LENGTH = 32;
const IV_LENGTH = 16;
const TAG_LENGTH = 16;

// Derivar key desde master key + organizationId
function deriveKey(masterKey: string, organizationId: string): Buffer {
  return crypto.pbkdf2Sync(
    masterKey,
    organizationId,
    100000,
    KEY_LENGTH,
    'sha512'
  );
}

export function encrypt(plaintext: string, organizationId: string): {
  ciphertext: string;
  iv: string;
  tag: string;
} {
  const masterKey = process.env.ENCRYPTION_MASTER_KEY!;
  const key = deriveKey(masterKey, organizationId);
  
  const iv = crypto.randomBytes(IV_LENGTH);
  const cipher = crypto.createCipheriv(ALGORITHM, key, iv);
  
  let ciphertext = cipher.update(plaintext, 'utf8', 'hex');
  ciphertext += cipher.final('hex');
  
  const tag = cipher.getAuthTag();
  
  return {
    ciphertext,
    iv: iv.toString('hex'),
    tag: tag.toString('hex'),
  };
}

export function decrypt(
  ciphertext: string,
  iv: string,
  tag: string,
  organizationId: string
): string {
  const masterKey = process.env.ENCRYPTION_MASTER_KEY!;
  const key = deriveKey(masterKey, organizationId);
  
  const decipher = crypto.createDecipheriv(
    ALGORITHM,
    key,
    Buffer.from(iv, 'hex')
  );
  
  decipher.setAuthTag(Buffer.from(tag, 'hex'));
  
  let plaintext = decipher.update(ciphertext, 'hex', 'utf8');
  plaintext += decipher.final('utf8');
  
  return plaintext;
}

// Uso para documentos sensibles
async function uploadSensitiveDocument(file: File, organizationId: string) {
  const plaintext = await file.text();
  const { ciphertext, iv, tag } = encrypt(plaintext, organizationId);
  
  // Guardar en MongoDB
  await documentsCollection.insertOne({
    organizationId,
    ciphertext,
    iv,
    tag,
    mimeType: file.type,
    createdAt: new Date(),
  });
}
```

---

## 8. Escalabilidad y Performance

### Caching Strategy

```typescript
// lib/cache.ts

import { Redis } from '@upstash/redis';

const redis = Redis.fromEnv();

export const cache = {
  // Cache simple
  async get<T>(key: string): Promise<T | null> {
    return await redis.get<T>(key);
  },

  async set<T>(key: string, value: T, ttlSeconds?: number): Promise<void> {
    if (ttlSeconds) {
      await redis.setex(key, ttlSeconds, JSON.stringify(value));
    } else {
      await redis.set(key, JSON.stringify(value));
    }
  },

  async del(key: string): Promise<void> {
    await redis.del(key);
  },

  // Cache con patron aside
  async getOrCompute<T>(
    key: string,
    computeFn: () => Promise<T>,
    ttlSeconds: number = 300
  ): Promise<T> {
    const cached = await this.get<T>(key);
    if (cached) return cached;

    const computed = await computeFn();
    await this.set(key, computed, ttlSeconds);
    return computed;
  },

  // Invalidación por patrón
  async invalidatePattern(pattern: string): Promise<void> {
    const keys = await redis.keys(pattern);
    if (keys.length > 0) {
      await redis.del(...keys);
    }
  },
};

// Ejemplo de uso en API
export async function getProperties(organizationId: string) {
  return cache.getOrCompute(
    `properties:${organizationId}`,
    async () => {
      return await prisma.property.findMany({
        where: { organizationId, status: 'AVAILABLE' },
      });
    },
    600 // 10 minutos
  );
}

// Invalidar al actualizar
export async function updateProperty(id: string, organizationId: string, data: any) {
  const updated = await prisma.property.update({ where: { id }, data });
  
  // Invalidar caché
  await cache.invalidatePattern(`properties:${organizationId}*`);
  await cache.invalidatePattern(`property:${id}`);
  
  return updated;
}
```

### Rate Limiting

```typescript
// lib/rate-limit.ts

import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const redis = Redis.fromEnv();

// Rate limiters por tier
export const rateLimiters = {
  free: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(100, '1 h'), // 100 requests/hora
    analytics: true,
  }),
  
  professional: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(1000, '1 h'), // 1000 requests/hora
    analytics: true,
  }),
  
  agency: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(10000, '1 h'), // 10k requests/hora
    analytics: true,
  }),
  
  enterprise: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(100000, '1 h'), // 100k requests/hora
    analytics: true,
  }),
};

// Middleware para tRPC
export const rateLimitMiddleware = t.middleware(async ({ ctx, next }) => {
  if (!ctx.user) return next(); // Public routes sin rate limit (hay otros mecanismos)

  const limiter = rateLimiters[ctx.user.organization.tier.toLowerCase()];
  const identifier = `${ctx.user.organizationId}:${ctx.user.id}`;
  
  const { success, limit, remaining, reset } = await limiter.limit(identifier);
  
  if (!success) {
    throw new TRPCError({
      code: 'TOO_MANY_REQUESTS',
      message: `Rate limit exceeded. Try again in ${Math.ceil((reset - Date.now()) / 1000)} seconds.`,
    });
  }
  
  // Agregar headers informativos
  ctx.res?.setHeader('X-RateLimit-Limit', limit.toString());
  ctx.res?.setHeader('X-RateLimit-Remaining', remaining.toString());
  ctx.res?.setHeader('X-RateLimit-Reset', reset.toString());
  
  return next();
});
```

### Database Connection Pooling

```typescript
// lib/db.ts

import { PrismaClient } from '@prisma/client';

const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
    datasources: {
      db: {
        url: process.env.DATABASE_URL,
      },
    },
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

// Connection pool config (en DATABASE_URL)
// postgresql://user:pass@host:5432/db?
//   connection_limit=10&
//   pool_timeout=10&
//   connect_timeout=10&
//   pgbouncer=true
```

### Background Jobs (BullMQ)

```typescript
// lib/queue.ts

import { Queue, Worker } from 'bullmq';
import { Redis } from 'ioredis';

const connection = new Redis(process.env.REDIS_URL!, {
  maxRetriesPerRequest: null,
});

// Definir colas
export const queues = {
  leads: new Queue('leads', { connection }),
  proposals: new Queue('proposals', { connection }),
  notifications: new Queue('notifications', { connection }),
  ai: new Queue('ai', { connection }),
};

// Workers
export function startWorkers() {
  // Lead qualification worker
  new Worker(
    'leads',
    async (job) => {
      switch (job.name) {
        case 'qualify':
          return await AIService.qualifyLead(job.data.leadId);
        case 'match-property':
          return await AIService.matchLeadToProperty(job.data.leadId);
        default:
          throw new Error(`Unknown job: ${job.name}`);
      }
    },
    { connection, concurrency: 10 }
  );

  // Proposal generation worker
  new Worker(
    'proposals',
    async (job) => {
      switch (job.name) {
        case 'generate':
          return await AIService.generateProposal(job.data);
        case 'send':
          return await NotificationService.sendProposal(job.data.proposalId);
        default:
          throw new Error(`Unknown job: ${job.name}`);
      }
    },
    { connection, concurrency: 5 } // Menor concurrency por llamadas a IA
  );

  // Notification worker
  new Worker(
    'notifications',
    async (job) => {
      switch (job.name) {
        case 'whatsapp':
          return await WhatsAppService.send(job.data);
        case 'email':
          return await EmailService.send(job.data);
        default:
          throw new Error(`Unknown job: ${job.name}`);
      }
    },
    { connection, concurrency: 20 }
  );
}

// Ejemplo de uso
export async function qualifyLeadAsync(leadId: string) {
  await queues.leads.add('qualify', { leadId }, {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000,
    },
  });
}
```

---

## 9. Monitoreo y Observabilidad

### Logging Structure

```typescript
// lib/logger.ts

import { Axiom } from '@axiomhq/js';

const axiom = new Axiom({
  token: process.env.AXIOM_TOKEN!,
  orgId: process.env.AXIOM_ORG_ID!,
});

interface LogContext {
  userId?: string;
  organizationId?: string;
  leadId?: string;
  [key: string]: any;
}

export const logger = {
  info(message: string, context?: LogContext) {
    axiom.ingest('laeds-logs', [{
      _time: new Date().toISOString(),
      level: 'info',
      message,
      ...context,
    }]);
  },

  error(message: string, error: Error, context?: LogContext) {
    axiom.ingest('laeds-logs', [{
      _time: new Date().toISOString(),
      level: 'error',
      message,
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack,
      },
      ...context,
    }]);
  },

  warn(message: string, context?: LogContext) {
    axiom.ingest('laeds-logs', [{
      _time: new Date().toISOString(),
      level: 'warn',
      message,
      ...context,
    }]);
  },

  async flush() {
    await axiom.flush();
  },
};

// Middleware para auto-logging
export const loggingMiddleware = t.middleware(async ({ ctx, next, path, type }) => {
  const start = Date.now();
  
  try {
    const result = await next();
    const duration = Date.now() - start;
    
    logger.info(`${type} ${path} completed`, {
      userId: ctx.user?.id,
      organizationId: ctx.user?.organizationId,
      duration,
      type,
      path,
    });
    
    return result;
  } catch (error) {
    const duration = Date.now() - start;
    
    logger.error(`${type} ${path} failed`, error as Error, {
      userId: ctx.user?.id,
      organizationId: ctx.user?.organizationId,
      duration,
      type,
      path,
    });
    
    throw error;
  }
});
```

### Metrics (Custom)

```typescript
// lib/metrics.ts

import { Redis } from '@upstash/redis';

const redis = Redis.fromEnv();

export const metrics = {
  // Incrementar contador
  async increment(key: string, amount: number = 1): Promise<void> {
    await redis.incrby(key, amount);
  },

  // Medir duración
  async timing(key: string, durationMs: number): Promise<void> {
    await redis.zadd(key, {
      score: Date.now(),
      member: durationMs.toString(),
    });
    
    // Mantener solo últimas 1000 mediciones
    await redis.zremrangebyrank(key, 0, -1001);
  },

  // Obtener métricas
  async get(key: string): Promise<number> {
    return (await redis.get<number>(key)) || 0;
  },

  // Resetear
  async reset(key: string): Promise<void> {
    await redis.del(key);
  },
};

// Wrapper para medir funciones
export function measure<T>(fn: () => Promise<T>, metricName: string): Promise<T> {
  return async function wrapped(...args: any[]) {
    const start = Date.now();
    try {
      const result = await fn(...args);
      const duration = Date.now() - start;
      await metrics.timing(metricName, duration);
      return result;
    } catch (error) {
      await metrics.increment(`${metricName}:errors`);
      throw error;
    }
  };
}

// Ejemplo
export const generateProposal = measure(
  async (leadId: string, propertyId: string) => {
    // ... lógica
  },
  'ai:generate_proposal'
);
```

### Health Checks

```typescript
// pages/api/health.ts

import { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '@/lib/db';
import { redis } from '@/lib/redis';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const checks = {
    timestamp: new Date().toISOString(),
    status: 'healthy',
    checks: {
      database: 'unknown',
      redis: 'unknown',
      ai: 'unknown',
    },
  };

  try {
    // Check PostgreSQL
    await prisma.$queryRaw`SELECT 1`;
    checks.checks.database = 'healthy';
  } catch (error) {
    checks.checks.database = 'unhealthy';
    checks.status = 'degraded';
  }

  try {
    // Check Redis
    await redis.ping();
    checks.checks.redis = 'healthy';
  } catch (error) {
    checks.checks.redis = 'unhealthy';
    checks.status = 'degraded';
  }

  try {
    // Check OpenAI API
    const response = await fetch('https://api.openai.com/v1/models', {
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
      },
    });
    checks.checks.ai = response.ok ? 'healthy' : 'unhealthy';
  } catch (error) {
    checks.checks.ai = 'unhealthy';
    checks.status = 'degraded';
  }

  const statusCode = checks.status === 'healthy' ? 200 : 503;
  return res.status(statusCode).json(checks);
}
```

---

## 10. Deployment y CI/CD

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml

name: Deploy

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '20'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'yarn'
      
      - name: Install dependencies
        run: yarn install --frozen-lockfile
      
      - name: Run linter
        run: yarn lint
      
      - name: Run type check
        run: yarn type-check
      
      - name: Run tests
        run: yarn test:ci
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'yarn'
      
      - name: Install dependencies
        run: yarn install --frozen-lockfile
      
      - name: Build
        run: yarn build
        env:
          SKIP_ENV_VALIDATION: true
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build
          path: .next

  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/staging'
    environment:
      name: staging
      url: https://staging.laeds.ai
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Vercel (Staging)
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          scope: ${{ secrets.VERCEL_ORG_ID }}

  deploy-production:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://app.laeds.ai
    steps:
      - uses: actions/checkout@v4
      
      - name: Run database migrations
        run: npx prisma migrate deploy
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
      
      - name: Deploy to Vercel (Production)
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
          scope: ${{ secrets.VERCEL_ORG_ID }}
      
      - name: Notify Sentry of deployment
        run: |
          curl -X POST https://sentry.io/api/0/organizations/${{ secrets.SENTRY_ORG }}/releases/ \
            -H "Authorization: Bearer ${{ secrets.SENTRY_AUTH_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{
              "version": "${{ github.sha }}",
              "projects": ["laeds"]
            }'
```

### Environment Configuration

```bash
# .env.example

# Database
DATABASE_URL="postgresql://user:pass@host:5432/laeds?pgbouncer=true&connection_limit=10"
MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/laeds"

# Redis
REDIS_URL="redis://default:pass@redis.upstash.io:6379"

# Authentication (Clerk)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="pk_test_..."
CLERK_SECRET_KEY="sk_test_..."
CLERK_WEBHOOK_SECRET="whsec_..."

# AI (OpenAI)
OPENAI_API_KEY="sk-..."
OPENAI_ORG_ID="org-..."

# AI (Anthropic - Backup)
ANTHROPIC_API_KEY="sk-ant-..."

# Vector DB (Pinecone)
PINECONE_API_KEY="..."
PINECONE_ENVIRONMENT="us-west1-gcp"
PINECONE_INDEX="laeds-properties"

# Integrations
EASYBROKER_API_KEY="..."
WHATSAPP_API_KEY="..."
WHATSAPP_PHONE_NUMBER_ID="..."
GOOGLE_CALENDAR_CLIENT_ID="..."
GOOGLE_CALENDAR_CLIENT_SECRET="..."

# Storage (Cloudflare R2)
R2_ACCOUNT_ID="..."
R2_ACCESS_KEY_ID="..."
R2_SECRET_ACCESS_KEY="..."
R2_BUCKET_NAME="laeds-documents"

# Payments
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

# Monitoring
SENTRY_DSN="https://...@sentry.io/..."
AXIOM_TOKEN="..."
AXIOM_ORG_ID="..."

# Encryption
ENCRYPTION_MASTER_KEY="..." # 32-byte base64 encoded key

# Feature Flags
NEXT_PUBLIC_ENABLE_AI_CHAT="true"
NEXT_PUBLIC_ENABLE_SEMANTIC_SEARCH="true"

# Misc
NEXT_PUBLIC_APP_URL="https://app.laeds.ai"
NEXT_PUBLIC_API_URL="https://api.laeds.ai"
```

---

## Resumen y Próximos Pasos

Este documento define la arquitectura técnica completa de læds® CRM, incluyendo:

✅ Arquitectura de componentes frontend y backend  
✅ Stack tecnológico detallado con justificaciones  
✅ Esquemas de base de datos (PostgreSQL con Prisma + MongoDB)  
✅ APIs y routers tRPC con ejemplos  
✅ Flujos de datos críticos con diagramas de secuencia  
✅ Seguridad (autenticación, autorización, encriptación)  
✅ Escalabilidad (caching, rate limiting, queues)  
✅ Observabilidad (logging, metrics, health checks)  
✅ CI/CD y deployment strategy  

**Siguiente fase:** Implementación de MVP siguiendo esta arquitectura.

---

**Documento preparado por:** Cursor AI Agent  
**Fecha:** 9 de Septiembre, 2026  
**Versión:** 1.0  
**Estado:** Especificación Técnica de Referencia
