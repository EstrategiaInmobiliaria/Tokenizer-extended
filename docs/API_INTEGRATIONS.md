# 🔌 læds® - API Integration Strategy

**Versión:** 1.0  
**Fecha:** 9 de Septiembre, 2026  
**Estado:** Production Ready

---

## 📋 Índice

1. [Visión General de Integraciones](#visión-general-de-integraciones)
2. [EasyBroker CRM Integration](#easybroker-crm-integration)
3. [WhatsApp Business API](#whatsapp-business-api)
4. [Google Calendar Integration](#google-calendar-integration)
5. [Payment Gateways](#payment-gateways)
6. [Notary & Banking APIs](#notary--banking-apis)
7. [AI Services Integration](#ai-services-integration)
8. [Adapter Pattern Implementation](#adapter-pattern-implementation)
9. [Webhook Management](#webhook-management)
10. [Rate Limiting & Error Handling](#rate-limiting--error-handling)

---

## 1. Visión General de Integraciones

### Arquitectura de Integración

```
┌─────────────────────────────────────────────────────────────────┐
│                      læds® CORE SYSTEM                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               Integration Service                         │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │  Adapter   │  │  Adapter   │  │  Adapter   │         │  │
│  │  │  Registry  │  │   Queue    │  │   Cache    │         │  │
│  │  └────────────┘  └────────────┘  └────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────┬────────────────────────────────────────┘
                       │
       ┌───────────────┴──────────────────┐
       │                                  │
   ┌───▼────┐  ┌────────┐  ┌──────────┐  ▼
   │  CRM   │  │Messaging│  │Scheduling│ ...
   │        │  │         │  │          │
┌──┴────┬───┴──┴────┬───┴──┴────┬─────┴─────┬──────────────┐
│Easy   │WhatsApp   │Google     │Stripe     │AI Services  │
│Broker │Business   │Calendar   │Conekta    │OpenAI       │
│       │Twilio     │Calendly   │           │Anthropic    │
└───────┴───────────┴───────────┴───────────┴─────────────┘
```

### Principios de Diseño

1. **Adapter Pattern**: Cada integración aislada, fácil reemplazo
2. **Resilience**: Retry logic, circuit breakers, fallbacks
3. **Observability**: Logging detallado, métricas, alertas
4. **Rate Limiting**: Respetar límites de APIs externas
5. **Security**: Secrets management, request signing
6. **Testability**: Mocks para testing, sandbox environments

---

## 2. EasyBroker CRM Integration

### Overview

**Propósito:** Sincronizar inventario de propiedades, leads y contactos

**Frecuencia de Sync:**
- Propiedades: Cada 6 horas (webhook + polling fallback)
- Leads: Real-time vía webhook
- Contactos: On-demand

### API Endpoints

```typescript
// lib/integrations/easybroker/client.ts

import axios, { AxiosInstance } from 'axios';
import { cache } from '@/lib/cache';
import { logger } from '@/lib/logger';
import { rateLimiters } from '@/lib/rate-limit';

interface EasyBrokerConfig {
  apiKey: string;
  baseURL?: string;
}

interface Property {
  id: string;
  title: string;
  description: string;
  property_type: string;
  bedrooms: number;
  bathrooms: number;
  parking_spaces: number;
  construction_size: number;
  lot_size: number;
  price: number;
  public_url: string;
  location: {
    name: string;
    latitude: number;
    longitude: number;
  };
  photos: Array<{
    url: string;
    title: string;
  }>;
}

interface PropertySearchParams {
  page?: number;
  limit?: number;
  search?: string;
  property_type?: string;
  min_price?: number;
  max_price?: number;
  bedrooms?: number;
}

export class EasyBrokerClient {
  private client: AxiosInstance;
  private apiKey: string;

  constructor(config: EasyBrokerConfig) {
    this.apiKey = config.apiKey;
    this.client = axios.create({
      baseURL: config.baseURL || 'https://api.easybroker.com/v1',
      headers: {
        'X-Authorization': config.apiKey,
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });

    // Request interceptor para logging
    this.client.interceptors.request.use(
      (config) => {
        logger.info('EasyBroker API Request', {
          method: config.method,
          url: config.url,
          params: config.params,
        });
        return config;
      },
      (error) => {
        logger.error('EasyBroker API Request Error', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor para error handling
    this.client.interceptors.response.use(
      (response) => {
        logger.info('EasyBroker API Response', {
          status: response.status,
          url: response.config.url,
        });
        return response;
      },
      async (error) => {
        if (error.response) {
          logger.error('EasyBroker API Error Response', {
            status: error.response.status,
            data: error.response.data,
            url: error.config.url,
          });

          // Retry en caso de rate limit (429)
          if (error.response.status === 429) {
            const retryAfter = parseInt(error.response.headers['retry-after'] || '60');
            logger.warn(`Rate limited by EasyBroker. Retrying after ${retryAfter}s`);
            await new Promise((resolve) => setTimeout(resolve, retryAfter * 1000));
            return this.client.request(error.config);
          }
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Obtener todas las propiedades con paginación
   */
  async getProperties(params: PropertySearchParams = {}): Promise<Property[]> {
    const cacheKey = `easybroker:properties:${JSON.stringify(params)}`;
    
    // Intentar desde caché (6 horas)
    const cached = await cache.get<Property[]>(cacheKey);
    if (cached) {
      logger.info('EasyBroker properties from cache');
      return cached;
    }

    const response = await this.client.get<{
      content: Property[];
      pagination: {
        page: number;
        per_page: number;
        total: number;
        total_pages: number;
      };
    }>('/properties', {
      params: {
        page: params.page || 1,
        limit: params.limit || 50,
        search: params.search,
        property_type: params.property_type,
        min_price: params.min_price,
        max_price: params.max_price,
        bedrooms: params.bedrooms,
      },
    });

    const properties = response.data.content;

    // Guardar en caché
    await cache.set(cacheKey, properties, 21600); // 6 horas

    return properties;
  }

  /**
   * Obtener una propiedad específica
   */
  async getProperty(propertyId: string): Promise<Property> {
    const cacheKey = `easybroker:property:${propertyId}`;
    
    const cached = await cache.get<Property>(cacheKey);
    if (cached) return cached;

    const response = await this.client.get<Property>(`/properties/${propertyId}`);
    const property = response.data;

    await cache.set(cacheKey, property, 3600); // 1 hora

    return property;
  }

  /**
   * Crear solicitud de contacto (lead)
   */
  async createContactRequest(data: {
    property_id: string;
    name: string;
    email: string;
    phone: string;
    message?: string;
    source?: string;
  }): Promise<{ id: string }> {
    const response = await this.client.post('/contact_requests', data);
    return response.data;
  }

  /**
   * Webhook signature validation
   */
  static validateWebhook(payload: string, signature: string, secret: string): boolean {
    const crypto = require('crypto');
    const hmac = crypto.createHmac('sha256', secret);
    hmac.update(payload);
    const digest = hmac.digest('hex');
    return digest === signature;
  }
}

// Singleton instance
let easybrokerClient: EasyBrokerClient | null = null;

export function getEasyBrokerClient(): EasyBrokerClient {
  if (!easybrokerClient) {
    easybrokerClient = new EasyBrokerClient({
      apiKey: process.env.EASYBROKER_API_KEY!,
    });
  }
  return easybrokerClient;
}
```

### Sync Service

```typescript
// lib/integrations/easybroker/sync.ts

import { getEasyBrokerClient } from './client';
import { prisma } from '@/lib/db';
import { generateEmbedding } from '@/lib/ai/embeddings';
import { pinecone } from '@/lib/pinecone';

export class EasyBrokerSyncService {
  /**
   * Sincronizar todas las propiedades
   */
  static async syncProperties(organizationId: string): Promise<{
    created: number;
    updated: number;
    deleted: number;
  }> {
    const client = getEasyBrokerClient();
    const properties = await client.getProperties({ limit: 1000 });

    let created = 0;
    let updated = 0;

    for (const ebProperty of properties) {
      // Buscar si ya existe
      const existing = await prisma.property.findUnique({
        where: {
          externalId: ebProperty.id,
        },
      });

      // Generar embedding para búsqueda semántica
      const embeddingText = `${ebProperty.title} ${ebProperty.description} ${ebProperty.location.name} ${ebProperty.bedrooms} bedrooms ${ebProperty.bathrooms} bathrooms`;
      const embedding = await generateEmbedding(embeddingText);

      const propertyData = {
        organizationId,
        externalId: ebProperty.id,
        externalSource: 'easybroker',
        title: ebProperty.title,
        description: ebProperty.description,
        propertyType: ebProperty.property_type.toUpperCase() as any,
        address: ebProperty.location.name,
        city: this.extractCity(ebProperty.location.name),
        state: this.extractState(ebProperty.location.name),
        coordinates: {
          lat: ebProperty.location.latitude,
          lng: ebProperty.location.longitude,
        },
        bedrooms: ebProperty.bedrooms,
        bathrooms: ebProperty.bathrooms,
        parkingSpots: ebProperty.parking_spaces,
        area: ebProperty.lot_size,
        builtArea: ebProperty.construction_size,
        price: ebProperty.price,
        pricePerM2: ebProperty.construction_size > 0 ? ebProperty.price / ebProperty.construction_size : null,
        images: ebProperty.photos.map((p) => p.url),
        status: 'AVAILABLE',
        embedding: embedding,
      };

      if (existing) {
        await prisma.property.update({
          where: { id: existing.id },
          data: propertyData,
        });
        updated++;
      } else {
        const newProperty = await prisma.property.create({
          data: propertyData,
        });
        created++;

        // Agregar a Pinecone
        await pinecone.index('laeds-properties').upsert([
          {
            id: newProperty.id,
            values: embedding,
            metadata: {
              organizationId,
              title: newProperty.title,
              price: newProperty.price.toNumber(),
              bedrooms: newProperty.bedrooms || 0,
              city: newProperty.city,
            },
          },
        ]);
      }
    }

    // Marcar como no disponibles las que ya no están en EasyBroker
    const ebPropertyIds = properties.map((p) => p.id);
    const deleted = await prisma.property.updateMany({
      where: {
        organizationId,
        externalSource: 'easybroker',
        externalId: {
          notIn: ebPropertyIds,
        },
        status: 'AVAILABLE',
      },
      data: {
        status: 'UNAVAILABLE',
      },
    });

    return {
      created,
      updated,
      deleted: deleted.count,
    };
  }

  private static extractCity(locationName: string): string {
    // Lógica para extraer ciudad del nombre de ubicación
    // Ejemplo: "Av. Revolución 1234, Col. Roma, Ciudad de México, CDMX" → "Ciudad de México"
    const parts = locationName.split(',');
    return parts[parts.length - 2]?.trim() || 'Unknown';
  }

  private static extractState(locationName: string): string {
    const parts = locationName.split(',');
    return parts[parts.length - 1]?.trim() || 'Unknown';
  }
}
```

### Webhook Handler

```typescript
// pages/api/webhooks/easybroker.ts

import { NextApiRequest, NextApiResponse } from 'next';
import { EasyBrokerClient } from '@/lib/integrations/easybroker/client';
import { EasyBrokerSyncService } from '@/lib/integrations/easybroker/sync';
import { logger } from '@/lib/logger';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Validar signature
  const signature = req.headers['x-easybroker-signature'] as string;
  const payload = JSON.stringify(req.body);
  const secret = process.env.EASYBROKER_WEBHOOK_SECRET!;

  if (!EasyBrokerClient.validateWebhook(payload, signature, secret)) {
    logger.warn('Invalid EasyBroker webhook signature');
    return res.status(401).json({ error: 'Invalid signature' });
  }

  try {
    const { event, data } = req.body;

    logger.info('EasyBroker webhook received', { event, propertyId: data.id });

    switch (event) {
      case 'property.created':
      case 'property.updated':
        // Sincronizar solo esta propiedad
        await EasyBrokerSyncService.syncProperties('org_default'); // TODO: obtener de webhook
        break;

      case 'property.deleted':
        // Marcar como no disponible
        await prisma.property.updateMany({
          where: { externalId: data.id },
          data: { status: 'UNAVAILABLE' },
        });
        break;

      default:
        logger.warn('Unknown EasyBroker webhook event', { event });
    }

    return res.status(200).json({ received: true });
  } catch (error) {
    logger.error('Error processing EasyBroker webhook', error as Error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
```

---

## 3. WhatsApp Business API

### Overview

**Propósito:** Comunicación bidireccional con leads y clientes

**Límites de Rate:**
- Cloud API: 1,000 mensajes/segundo (tier standard)
- Templates: Ilimitado (pre-aprobados)
- Session messages: 24 horas desde última interacción del usuario

### Client Implementation

```typescript
// lib/integrations/whatsapp/client.ts

import axios, { AxiosInstance } from 'axios';
import { logger } from '@/lib/logger';
import { metrics } from '@/lib/metrics';

interface WhatsAppConfig {
  accessToken: string;
  phoneNumberId: string;
  apiVersion?: string;
}

interface SendTemplateParams {
  to: string;
  templateName: string;
  languageCode: string;
  components?: Array<{
    type: 'header' | 'body' | 'button';
    parameters: Array<{
      type: 'text' | 'image' | 'document' | 'video';
      text?: string;
      image?: { link: string };
      document?: { link: string; filename: string };
      video?: { link: string };
    }>;
  }>;
}

interface SendTextParams {
  to: string;
  text: string;
  previewUrl?: boolean;
}

export class WhatsAppClient {
  private client: AxiosInstance;
  private phoneNumberId: string;

  constructor(config: WhatsAppConfig) {
    this.phoneNumberId = config.phoneNumberId;
    this.client = axios.create({
      baseURL: `https://graph.facebook.com/${config.apiVersion || 'v18.0'}`,
      headers: {
        'Authorization': `Bearer ${config.accessToken}`,
        'Content-Type': 'application/json',
      },
      timeout: 15000,
    });

    this.client.interceptors.request.use((config) => {
      logger.info('WhatsApp API Request', {
        method: config.method,
        url: config.url,
      });
      return config;
    });

    this.client.interceptors.response.use(
      (response) => {
        metrics.increment('whatsapp:api:success');
        return response;
      },
      async (error) => {
        metrics.increment('whatsapp:api:error');
        
        if (error.response) {
          logger.error('WhatsApp API Error', {
            status: error.response.status,
            data: error.response.data,
          });

          // Casos específicos de error
          const errorCode = error.response.data?.error?.code;
          
          if (errorCode === 131047) {
            // Re-engagement message needed (24h window expired)
            throw new Error('WHATSAPP_SESSION_EXPIRED');
          }
          
          if (errorCode === 131026) {
            // Message undeliverable (número inválido)
            throw new Error('WHATSAPP_INVALID_NUMBER');
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  /**
   * Enviar mensaje usando template pre-aprobado
   */
  async sendTemplate(params: SendTemplateParams): Promise<{
    messageId: string;
    status: string;
  }> {
    const response = await this.client.post(
      `/${this.phoneNumberId}/messages`,
      {
        messaging_product: 'whatsapp',
        to: this.formatPhoneNumber(params.to),
        type: 'template',
        template: {
          name: params.templateName,
          language: {
            code: params.languageCode,
          },
          components: params.components || [],
        },
      }
    );

    const messageId = response.data.messages[0].id;
    
    logger.info('WhatsApp template sent', {
      to: params.to,
      templateName: params.templateName,
      messageId,
    });

    return {
      messageId,
      status: 'sent',
    };
  }

  /**
   * Enviar mensaje de texto (solo dentro de ventana de 24h)
   */
  async sendText(params: SendTextParams): Promise<{
    messageId: string;
    status: string;
  }> {
    const response = await this.client.post(
      `/${this.phoneNumberId}/messages`,
      {
        messaging_product: 'whatsapp',
        to: this.formatPhoneNumber(params.to),
        type: 'text',
        text: {
          preview_url: params.previewUrl ?? false,
          body: params.text,
        },
      }
    );

    const messageId = response.data.messages[0].id;
    
    logger.info('WhatsApp text sent', {
      to: params.to,
      messageId,
    });

    return {
      messageId,
      status: 'sent',
    };
  }

  /**
   * Enviar imagen
   */
  async sendImage(params: {
    to: string;
    imageUrl: string;
    caption?: string;
  }): Promise<{
    messageId: string;
    status: string;
  }> {
    const response = await this.client.post(
      `/${this.phoneNumberId}/messages`,
      {
        messaging_product: 'whatsapp',
        to: this.formatPhoneNumber(params.to),
        type: 'image',
        image: {
          link: params.imageUrl,
          caption: params.caption,
        },
      }
    );

    return {
      messageId: response.data.messages[0].id,
      status: 'sent',
    };
  }

  /**
   * Enviar documento (PDF, etc.)
   */
  async sendDocument(params: {
    to: string;
    documentUrl: string;
    filename: string;
    caption?: string;
  }): Promise<{
    messageId: string;
    status: string;
  }> {
    const response = await this.client.post(
      `/${this.phoneNumberId}/messages`,
      {
        messaging_product: 'whatsapp',
        to: this.formatPhoneNumber(params.to),
        type: 'document',
        document: {
          link: params.documentUrl,
          filename: params.filename,
          caption: params.caption,
        },
      }
    );

    return {
      messageId: response.data.messages[0].id,
      status: 'sent',
    };
  }

  /**
   * Marcar mensaje como leído
   */
  async markAsRead(messageId: string): Promise<void> {
    await this.client.post(
      `/${this.phoneNumberId}/messages`,
      {
        messaging_product: 'whatsapp',
        status: 'read',
        message_id: messageId,
      }
    );
  }

  /**
   * Formatear número de teléfono (remover +, espacios, guiones)
   */
  private formatPhoneNumber(phone: string): string {
    return phone.replace(/[\s\-\+]/g, '');
  }

  /**
   * Validar webhook signature
   */
  static validateSignature(payload: string, signature: string, appSecret: string): boolean {
    const crypto = require('crypto');
    const expectedSignature = crypto
      .createHmac('sha256', appSecret)
      .update(payload)
      .digest('hex');
    return `sha256=${expectedSignature}` === signature;
  }
}

// Singleton
let whatsappClient: WhatsAppClient | null = null;

export function getWhatsAppClient(): WhatsAppClient {
  if (!whatsappClient) {
    whatsappClient = new WhatsAppClient({
      accessToken: process.env.WHATSAPP_ACCESS_TOKEN!,
      phoneNumberId: process.env.WHATSAPP_PHONE_NUMBER_ID!,
    });
  }
  return whatsappClient;
}
```

### Template Service

```typescript
// lib/integrations/whatsapp/templates.ts

import { getWhatsAppClient } from './client';

export interface ProposalTemplateData {
  clientName: string;
  propertyTitle: string;
  propertyArea: string;
  downPayment: string;
  term: string;
  monthlyPayment: string;
  deadline: string;
  imageUrl: string;
}

export class WhatsAppTemplateService {
  /**
   * Enviar propuesta personalizada
   */
  static async sendProposal(
    phone: string,
    data: ProposalTemplateData
  ): Promise<{ messageId: string }> {
    const client = getWhatsAppClient();
    
    const result = await client.sendTemplate({
      to: phone,
      templateName: 'propuesta_personalizada',
      languageCode: 'es_MX',
      components: [
        {
          type: 'header',
          parameters: [
            {
              type: 'image',
              image: { link: data.imageUrl },
            },
          ],
        },
        {
          type: 'body',
          parameters: [
            { type: 'text', text: data.clientName },
            { type: 'text', text: data.propertyTitle },
            { type: 'text', text: data.propertyArea },
            { type: 'text', text: data.downPayment },
            { type: 'text', text: data.term },
            { type: 'text', text: data.monthlyPayment },
            { type: 'text', text: data.deadline },
          ],
        },
      ],
    });

    return { messageId: result.messageId };
  }

  /**
   * Enviar confirmación de pago
   */
  static async sendPaymentConfirmation(
    phone: string,
    data: {
      clientName: string;
      propertyTitle: string;
      appointmentDateTime: string;
    }
  ): Promise<{ messageId: string }> {
    const client = getWhatsAppClient();
    
    const result = await client.sendTemplate({
      to: phone,
      templateName: 'pago_confirmado_onboarding',
      languageCode: 'es_MX',
      components: [
        {
          type: 'body',
          parameters: [
            { type: 'text', text: data.clientName },
            { type: 'text', text: data.propertyTitle },
            { type: 'text', text: data.appointmentDateTime },
          ],
        },
      ],
    });

    return { messageId: result.messageId };
  }

  /**
   * Solicitar documentos KYC
   */
  static async requestKYCDocuments(
    phone: string,
    clientName: string
  ): Promise<{ messageId: string }> {
    const client = getWhatsAppClient();
    
    const result = await client.sendTemplate({
      to: phone,
      templateName: 'solicitud_documentos_kyc',
      languageCode: 'es_MX',
      components: [
        {
          type: 'body',
          parameters: [
            { type: 'text', text: clientName },
          ],
        },
      ],
    });

    return { messageId: result.messageId };
  }
}
```

### Webhook Handler

```typescript
// pages/api/webhooks/whatsapp.ts

import { NextApiRequest, NextApiResponse } from 'next';
import { WhatsAppClient } from '@/lib/integrations/whatsapp/client';
import { logger } from '@/lib/logger';
import { prisma } from '@/lib/db';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // GET para verification token (Meta requirement)
  if (req.method === 'GET') {
    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];

    if (mode === 'subscribe' && token === process.env.WHATSAPP_VERIFY_TOKEN) {
      logger.info('WhatsApp webhook verified');
      return res.status(200).send(challenge);
    }

    return res.status(403).send('Forbidden');
  }

  // POST para mensajes
  if (req.method === 'POST') {
    // Validar signature
    const signature = req.headers['x-hub-signature-256'] as string;
    const payload = JSON.stringify(req.body);
    
    if (!WhatsAppClient.validateSignature(
      payload,
      signature,
      process.env.WHATSAPP_APP_SECRET!
    )) {
      logger.warn('Invalid WhatsApp webhook signature');
      return res.status(401).json({ error: 'Invalid signature' });
    }

    try {
      const { entry } = req.body;

      for (const entryItem of entry) {
        const { changes } = entryItem;

        for (const change of changes) {
          const { value } = change;

          if (value.messages) {
            for (const message of value.messages) {
              await handleIncomingMessage(message, value.metadata.phone_number_id);
            }
          }

          if (value.statuses) {
            for (const status of value.statuses) {
              await handleMessageStatus(status);
            }
          }
        }
      }

      return res.status(200).json({ received: true });
    } catch (error) {
      logger.error('Error processing WhatsApp webhook', error as Error);
      return res.status(500).json({ error: 'Internal server error' });
    }
  }

  return res.status(405).json({ error: 'Method not allowed' });
}

async function handleIncomingMessage(message: any, phoneNumberId: string) {
  logger.info('WhatsApp incoming message', {
    from: message.from,
    type: message.type,
    messageId: message.id,
  });

  // Buscar lead/cliente por teléfono
  const lead = await prisma.lead.findFirst({
    where: {
      phone: {
        contains: message.from,
      },
    },
  });

  if (!lead) {
    logger.warn('No lead found for WhatsApp message', { from: message.from });
    return;
  }

  // Crear actividad
  await prisma.activity.create({
    data: {
      leadId: lead.id,
      type: 'WHATSAPP_RECEIVED',
      title: 'WhatsApp message received',
      description: message.text?.body || `[${message.type}]`,
      metadata: {
        messageId: message.id,
        messageType: message.type,
      },
    },
  });

  // Si es respuesta a propuesta, analizar con IA (futuro)
  if (message.type === 'text' && lead.status === 'PROPOSAL_SENT') {
    const response = message.text.body.toLowerCase();
    
    if (response.includes('sí') || response.includes('aparto') || response.includes('interesa')) {
      await prisma.lead.update({
        where: { id: lead.id },
        data: { status: 'NEGOTIATING' },
      });

      // Notificar al broker
      // TODO: Enviar notificación
    }
  }

  // Marcar como leído
  const client = getWhatsAppClient();
  await client.markAsRead(message.id);
}

async function handleMessageStatus(status: any) {
  logger.info('WhatsApp message status', {
    messageId: status.id,
    status: status.status,
  });

  // Actualizar estado en DB si es necesario
  // TODO: Implementar tracking de estado de mensajes
}
```

---

_[Documento continúa con secciones para Google Calendar, Payment Gateways, etc. - por límite de tokens, continuaré en próximo commit]_

---

**Documento preparado por:** Cursor AI Agent  
**Fecha:** 9 de Septiembre, 2026  
**Versión:** 1.0 (Parcial - Continúa)  
**Estado:** In Progress
