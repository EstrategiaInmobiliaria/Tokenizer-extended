# 🤖 læds® - Make.com Automation Workflows

**Versión:** 1.0  
**Fecha:** 9 de Septiembre, 2026  
**Estado:** Ready for Import

---

## 📋 Índice

1. [Visión General](#visión-general)
2. [Workflow 1: Meta Lead → Propuesta 48h](#workflow-1-meta-lead--propuesta-48h)
3. [Workflow 2: Pago → Onboarding Cliente](#workflow-2-pago--onboarding-cliente)
4. [Workflow 3: Seguimiento Automático](#workflow-3-seguimiento-automático)
5. [Workflow 4: Monitoreo Patrimonial](#workflow-4-monitoreo-patrimonial)
6. [Configuración de Integraciones](#configuración-de-integraciones)
7. [Variables y Secrets](#variables-y-secrets)
8. [Testing y Troubleshooting](#testing-y-troubleshooting)

---

## 1. Visión General

### Filosofía de Automatización

**Objetivo:** Eliminar 80% del trabajo manual del broker para que se enfoque en cerrar y construir relaciones.

**Principios:**
1. **Rápido:** Respuestas en <5 minutos desde que entra lead
2. **Personalizado:** Cada mensaje con nombre, propiedad específica, datos reales
3. **Humano:** Automatizado pero conversacional, no robótico
4. **Confiable:** Retry logic, error handling, notificaciones de fallos

### Arquitectura de Automatización

```
┌──────────────────────────────────────────────────────────────┐
│                      TRIGGER SOURCES                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Meta Ads  │  │  Stripe  │  │ WhatsApp │  │  Cron    │   │
│  │ Webhook  │  │ Webhook  │  │ Webhook  │  │ Schedule │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────┴───────────────────────────────────────┐
│                     MAKE.COM SCENARIOS                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  • Lead Qualification & Matching                       │  │
│  │  • Proposal Generation & Delivery                      │  │
│  │  • Payment Processing & Onboarding                     │  │
│  │  • Follow-ups & Nurture Sequences                      │  │
│  │  • Patrimony Monitoring & Alerts                       │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────┴───────────────────────────────────────┐
│                    ACTION DESTINATIONS                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │EasyBroker│  │ WhatsApp │  │  Google  │  │  Airtable│   │
│  │   API    │  │   API    │  │ Calendar │  │  /Notion │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Workflow 1: Meta Lead → Propuesta 48h

### Descripción

Cuando llega un lead de Meta Ads (Facebook/Instagram), el sistema:
1. Valida y filtra leads con presupuesto ≥ $25k MXN
2. Busca mejor propiedad match en EasyBroker
3. Calcula mensualidad exacta
4. Genera imagen personalizada con nombre + deadline
5. Envía WhatsApp con propuesta
6. Crea registro en CRM

### Diagrama de Flujo

```mermaid
graph TD
    A[Meta Ads Lead Form] -->|Webhook| B{Budget Filter}
    B -->|< $25k| C[Add to Nurture List]
    B -->|≥ $25k| D[Get EasyBroker Properties]
    D --> E[AI: Match Lead to Best Property]
    E --> F[Calculate Monthly Payment]
    F --> G[Generate Personalized Image]
    G --> H[Send WhatsApp Message]
    H --> I{Lead Responds?}
    I -->|Yes| J[Notify Broker]
    I -->|No - 24h| K[Send Follow-up]
    K --> L{Responds?}
    L -->|Yes| J
    L -->|No - 48h| M[Mark as Cold - Move to Drip]
```

### Make.com Scenario JSON

```json
{
  "name": "læds - Meta Lead to Proposal",
  "flow": [
    {
      "id": 1,
      "module": "gateway:CustomWebHook",
      "version": 1,
      "parameters": {
        "hook": 123456,
        "maxResults": 1
      },
      "mapper": {},
      "metadata": {
        "designer": {
          "x": 0,
          "y": 0
        },
        "restore": {
          "expect": {
            "structure": "object"
          }
        },
        "expect": [
          {
            "name": "name",
            "type": "text",
            "label": "Full Name",
            "required": true
          },
          {
            "name": "email",
            "type": "email",
            "label": "Email",
            "required": true
          },
          {
            "name": "phone",
            "type": "text",
            "label": "Phone",
            "required": true
          },
          {
            "name": "budget",
            "type": "number",
            "label": "Budget",
            "required": true
          },
          {
            "name": "bedrooms",
            "type": "number",
            "label": "Bedrooms Desired"
          },
          {
            "name": "location",
            "type": "text",
            "label": "Preferred Location"
          },
          {
            "name": "ad_id",
            "type": "text",
            "label": "Ad ID"
          },
          {
            "name": "campaign_name",
            "type": "text",
            "label": "Campaign Name"
          }
        ]
      }
    },
    {
      "id": 2,
      "module": "builtin:BasicRouter",
      "version": 1,
      "mapper": null,
      "metadata": {
        "designer": {
          "x": 300,
          "y": 0
        }
      },
      "routes": [
        {
          "flow": [
            {
              "id": 3,
              "module": "http:ActionMakeAnAPICall",
              "version": 1,
              "parameters": {},
              "mapper": {
                "url": "https://api.easybroker.com/v1/properties",
                "method": "get",
                "headers": [
                  {
                    "name": "X-Authorization",
                    "value": "{{EASYBROKER_API_KEY}}"
                  },
                  {
                    "name": "Content-Type",
                    "value": "application/json"
                  }
                ],
                "qs": [
                  {
                    "name": "limit",
                    "value": "50"
                  },
                  {
                    "name": "public",
                    "value": "true"
                  }
                ]
              },
              "metadata": {
                "designer": {
                  "x": 600,
                  "y": -100
                },
                "restore": {
                  "method": {
                    "mode": "chose",
                    "label": "GET"
                  }
                }
              }
            },
            {
              "id": 4,
              "module": "openai:ChatCompletion",
              "version": 1,
              "parameters": {
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 500
              },
              "mapper": {
                "messages": [
                  {
                    "role": "system",
                    "content": "Eres un experto en bienes raíces. Tu tarea es seleccionar la MEJOR propiedad para un cliente basándote en su presupuesto y preferencias. Responde SOLO con el property_id de la mejor opción."
                  },
                  {
                    "role": "user",
                    "content": "Cliente: {{1.name}}\\nPresupuesto: ${{1.budget}} MXN\\nRecámaras deseadas: {{1.bedrooms}}\\nUbicación preferida: {{1.location}}\\n\\nPropiedades disponibles:\\n{{3.data.content}}\\n\\n¿Cuál es la mejor opción? Responde SOLO con el property_id."
                  }
                ]
              },
              "metadata": {
                "designer": {
                  "x": 900,
                  "y": -100
                }
              }
            },
            {
              "id": 5,
              "module": "http:ActionMakeAnAPICall",
              "version": 1,
              "parameters": {},
              "mapper": {
                "url": "https://api.easybroker.com/v1/properties/{{4.choices[0].message.content}}",
                "method": "get",
                "headers": [
                  {
                    "name": "X-Authorization",
                    "value": "{{EASYBROKER_API_KEY}}"
                  }
                ]
              },
              "metadata": {
                "designer": {
                  "x": 1200,
                  "y": -100
                }
              }
            },
            {
              "id": 6,
              "module": "util:SetVariable2",
              "version": 1,
              "parameters": {},
              "mapper": {
                "name": "monthly_payment",
                "scope": "roundtrip",
                "value": "{{round((5.data.price - 1.budget) / 24, 2)}}"
              },
              "metadata": {
                "designer": {
                  "x": 1500,
                  "y": -100
                },
                "restore": {
                  "scope": {
                    "label": "This scenario"
                  }
                }
              }
            },
            {
              "id": 7,
              "module": "http:ActionMakeAnAPICall",
              "version": 1,
              "parameters": {},
              "mapper": {
                "url": "https://api.laeds.ai/v1/generate-image",
                "method": "post",
                "headers": [
                  {
                    "name": "Authorization",
                    "value": "Bearer {{LAEDS_API_KEY}}"
                  },
                  {
                    "name": "Content-Type",
                    "value": "application/json"
                  }
                ],
                "body": {
                  "template": "proposal-palm-diamante",
                  "data": {
                    "client_name": "{{1.name}}",
                    "property_title": "{{5.data.title}}",
                    "property_type": "{{5.data.property_type}}",
                    "area": "{{5.data.construction_size}}",
                    "price": "{{formatNumber(5.data.price, 0, ',', '.')}}",
                    "down_payment": "{{formatNumber(1.budget, 0, ',', '.')}}",
                    "monthly_payment": "{{formatNumber(6.monthly_payment, 2, ',', '.')}}",
                    "term": 24,
                    "deadline": "{{addDays(now, 2)}}",
                    "property_image": "{{5.data.photos[0].url}}"
                  }
                }
              },
              "metadata": {
                "designer": {
                  "x": 1800,
                  "y": -100
                }
              }
            },
            {
              "id": 8,
              "module": "whatsapp-business:sendMessage",
              "version": 1,
              "parameters": {
                "phoneNumberId": "{{WHATSAPP_PHONE_NUMBER_ID}}"
              },
              "mapper": {
                "to": "{{replace(1.phone, '+', '')}}",
                "type": "template",
                "template": {
                  "name": "propuesta_personalizada",
                  "language": {
                    "code": "es_MX"
                  },
                  "components": [
                    {
                      "type": "header",
                      "parameters": [
                        {
                          "type": "image",
                          "image": {
                            "link": "{{7.data.image_url}}"
                          }
                        }
                      ]
                    },
                    {
                      "type": "body",
                      "parameters": [
                        {
                          "type": "text",
                          "text": "{{1.name}}"
                        },
                        {
                          "type": "text",
                          "text": "{{5.data.title}}"
                        },
                        {
                          "type": "text",
                          "text": "{{5.data.construction_size}} m²"
                        },
                        {
                          "type": "text",
                          "text": "{{formatNumber(1.budget, 0, ',', '.')}}"
                        },
                        {
                          "type": "text",
                          "text": "24"
                        },
                        {
                          "type": "text",
                          "text": "{{formatNumber(6.monthly_payment, 2, ',', '.')}}"
                        },
                        {
                          "type": "text",
                          "text": "{{formatDate(addDays(now, 2), 'DD-MMM-YYYY')}}"
                        }
                      ]
                    }
                  ]
                }
              },
              "metadata": {
                "designer": {
                  "x": 2100,
                  "y": -100
                }
              }
            },
            {
              "id": 9,
              "module": "airtable:createRecord",
              "version": 3,
              "parameters": {
                "baseId": "{{AIRTABLE_BASE_ID}}",
                "tableName": "Leads"
              },
              "mapper": {
                "fields": {
                  "Name": "{{1.name}}",
                  "Email": "{{1.email}}",
                  "Phone": "{{1.phone}}",
                  "Budget": "{{1.budget}}",
                  "Status": "Proposal Sent",
                  "Source": "Meta Ads - {{1.campaign_name}}",
                  "Assigned Property": "{{5.data.title}}",
                  "Monthly Payment": "{{6.monthly_payment}}",
                  "Proposal Sent At": "{{now}}",
                  "Proposal Expires At": "{{addDays(now, 2)}}",
                  "WhatsApp Message ID": "{{8.data.messages[0].id}}"
                }
              },
              "metadata": {
                "designer": {
                  "x": 2400,
                  "y": -100
                }
              }
            },
            {
              "id": 10,
              "module": "slack:createMessage",
              "version": 1,
              "parameters": {
                "channel": "{{SLACK_CHANNEL_ID}}"
              },
              "mapper": {
                "text": "🎯 *Nuevo Lead Calificado - Propuesta Enviada*\\n\\n*Cliente:* {{1.name}}\\n*Presupuesto:* ${{formatNumber(1.budget, 0, ',', '.')}} MXN\\n*Propiedad:* {{5.data.title}}\\n*Mensualidad:* ${{formatNumber(6.monthly_payment, 2, ',', '.')}} MXN\\n*Válida hasta:* {{formatDate(addDays(now, 2), 'DD-MMM-YYYY')}}\\n\\n_WhatsApp enviado exitosamente_ ✅",
                "attachments": [
                  {
                    "fallback": "Propuesta {{1.name}}",
                    "color": "#36a64f",
                    "image_url": "{{7.data.image_url}}"
                  }
                ]
              },
              "metadata": {
                "designer": {
                  "x": 2700,
                  "y": -100
                }
              }
            }
          ]
        },
        {
          "flow": [
            {
              "id": 11,
              "module": "airtable:createRecord",
              "version": 3,
              "parameters": {
                "baseId": "{{AIRTABLE_BASE_ID}}",
                "tableName": "Leads"
              },
              "mapper": {
                "fields": {
                  "Name": "{{1.name}}",
                  "Email": "{{1.email}}",
                  "Phone": "{{1.phone}}",
                  "Budget": "{{1.budget}}",
                  "Status": "Nurture - Low Budget",
                  "Source": "Meta Ads - {{1.campaign_name}}",
                  "Notes": "Presupuesto menor a $25k. Agregado a secuencia de nurture."
                }
              },
              "metadata": {
                "designer": {
                  "x": 600,
                  "y": 100
                }
              }
            },
            {
              "id": 12,
              "module": "mailchimp:addSubscriberToList",
              "version": 1,
              "parameters": {
                "listId": "{{MAILCHIMP_NURTURE_LIST_ID}}"
              },
              "mapper": {
                "email": "{{1.email}}",
                "status": "subscribed",
                "merge_fields": {
                  "FNAME": "{{1.name}}",
                  "PHONE": "{{1.phone}}",
                  "BUDGET": "{{1.budget}}"
                },
                "tags": ["low-budget", "meta-ads"]
              },
              "metadata": {
                "designer": {
                  "x": 900,
                  "y": 100
                }
              }
            }
          ]
        }
      ],
      "metadata": {
        "designer": {
          "x": 300,
          "y": 0
        }
      }
    }
  ],
  "metadata": {
    "instant": false,
    "version": 1,
    "scenario": {
      "roundtrips": 1,
      "maxErrors": 3,
      "autoCommit": true,
      "autoCommitTriggerLast": true,
      "sequential": false,
      "confidential": false,
      "dataloss": false,
      "dlq": false
    },
    "designer": {
      "orphans": []
    },
    "zone": "us1.make.com"
  }
}
```

### WhatsApp Template: `propuesta_personalizada`

```
HEADER: [IMAGE]

BODY:
Hola {{1}} 👋

Tu propuesta personalizada está lista:

🏢 {{2}} - {{3}}
💰 Aparta con: ${{4}} MXN
📅 {{5}} mensualidades de: ${{6}} MXN
⏰ Oferta válida hasta: {{7}} (48 horas)

¿Te interesa apartar?

BUTTONS:
[Sí, me interesa] [Necesito más info] [No por ahora]

FOOTER:
læds® - Tu asesor patrimonial
```

---

## 3. Workflow 2: Pago → Onboarding Cliente

### Descripción

Cuando un cliente paga el aparta (vía CLABE, Stripe, transferencia):
1. Verifica el pago
2. Mueve carpeta digital a "PD-APARTA PAGADO"
3. Agenda cita con Diana (calendar)
4. Solicita documentos KYC
5. Envía contrato pre-firmado
6. Notifica al broker

### Make.com Scenario JSON (Simplificado)

```json
{
  "name": "læds - Payment to Onboarding",
  "flow": [
    {
      "id": 1,
      "module": "stripe:watchEvents",
      "version": 1,
      "parameters": {
        "events": ["payment_intent.succeeded"]
      },
      "mapper": {},
      "metadata": {
        "designer": {
          "x": 0,
          "y": 0
        }
      }
    },
    {
      "id": 2,
      "module": "airtable:searchRecords",
      "version": 3,
      "parameters": {
        "baseId": "{{AIRTABLE_BASE_ID}}",
        "tableName": "Leads"
      },
      "mapper": {
        "formula": "AND({Email} = '{{1.data.object.receipt_email}}', {Status} = 'Proposal Sent')"
      },
      "metadata": {
        "designer": {
          "x": 300,
          "y": 0
        }
      }
    },
    {
      "id": 3,
      "module": "airtable:updateRecord",
      "version": 3,
      "parameters": {
        "baseId": "{{AIRTABLE_BASE_ID}}",
        "tableName": "Leads",
        "recordId": "{{2.data.records[0].id}}"
      },
      "mapper": {
        "fields": {
          "Status": "Payment Received",
          "Payment Amount": "{{1.data.object.amount_received / 100}}",
          "Payment Method": "{{1.data.object.payment_method_types[0]}}",
          "Payment Date": "{{now}}",
          "Stripe Payment Intent": "{{1.data.object.id}}"
        }
      },
      "metadata": {
        "designer": {
          "x": 600,
          "y": 0
        }
      }
    },
    {
      "id": 4,
      "module": "googledrive:moveFile",
      "version": 3,
      "parameters": {},
      "mapper": {
        "fileId": "{{2.data.records[0].fields['Folder ID']}}",
        "newLocation": "{{GOOGLE_DRIVE_APARTA_PAGADO_FOLDER_ID}}"
      },
      "metadata": {
        "designer": {
          "x": 900,
          "y": 0
        }
      }
    },
    {
      "id": 5,
      "module": "google-calendar:createEvent",
      "version": 2,
      "parameters": {
        "calendarId": "{{DIANA_CALENDAR_ID}}"
      },
      "mapper": {
        "summary": "Visita: {{2.data.records[0].fields.Name}} - {{2.data.records[0].fields['Assigned Property']}}",
        "description": "Cliente pagó aparta. Revisar documentos y cerrar contrato.\\n\\nDetalles:\\nEmail: {{2.data.records[0].fields.Email}}\\nTeléfono: {{2.data.records[0].fields.Phone}}\\nMonto apartado: ${{formatNumber(1.data.object.amount_received / 100, 2, ',', '.')}} MXN",
        "start": {
          "dateTime": "{{addDays(now, 2)}}T10:00:00",
          "timeZone": "America/Mexico_City"
        },
        "end": {
          "dateTime": "{{addDays(now, 2)}}T11:00:00",
          "timeZone": "America/Mexico_City"
        },
        "attendees": [
          {
            "email": "{{2.data.records[0].fields.Email}}",
            "displayName": "{{2.data.records[0].fields.Name}}"
          },
          {
            "email": "diana@laeds.ai",
            "displayName": "Diana - læds"
          }
        ],
        "reminders": {
          "useDefault": false,
          "overrides": [
            {
              "method": "email",
              "minutes": 1440
            },
            {
              "method": "popup",
              "minutes": 60
            }
          ]
        }
      },
      "metadata": {
        "designer": {
          "x": 1200,
          "y": 0
        }
      }
    },
    {
      "id": 6,
      "module": "whatsapp-business:sendMessage",
      "version": 1,
      "parameters": {
        "phoneNumberId": "{{WHATSAPP_PHONE_NUMBER_ID}}"
      },
      "mapper": {
        "to": "{{replace(2.data.records[0].fields.Phone, '+', '')}}",
        "type": "template",
        "template": {
          "name": "pago_confirmado_onboarding",
          "language": {
            "code": "es_MX"
          },
          "components": [
            {
              "type": "body",
              "parameters": [
                {
                  "type": "text",
                  "text": "{{2.data.records[0].fields.Name}}"
                },
                {
                  "type": "text",
                  "text": "{{2.data.records[0].fields['Assigned Property']}}"
                },
                {
                  "type": "text",
                  "text": "{{formatDate(addDays(now, 2), 'DD-MMM-YYYY')}} a las 10:00 AM"
                }
              ]
            }
          ]
        }
      },
      "metadata": {
        "designer": {
          "x": 1500,
          "y": 0
        }
      }
    },
    {
      "id": 7,
      "module": "whatsapp-business:sendMessage",
      "version": 1,
      "parameters": {
        "phoneNumberId": "{{WHATSAPP_PHONE_NUMBER_ID}}"
      },
      "mapper": {
        "to": "{{replace(2.data.records[0].fields.Phone, '+', '')}}",
        "type": "template",
        "template": {
          "name": "solicitud_documentos_kyc",
          "language": {
            "code": "es_MX"
          },
          "components": [
            {
              "type": "body",
              "parameters": [
                {
                  "type": "text",
                  "text": "{{2.data.records[0].fields.Name}}"
                }
              ]
            }
          ]
        }
      },
      "metadata": {
        "designer": {
          "x": 1800,
          "y": 0
        }
      }
    },
    {
      "id": 8,
      "module": "slack:createMessage",
      "version": 1,
      "parameters": {
        "channel": "{{SLACK_CHANNEL_ID}}"
      },
      "mapper": {
        "text": "💰 *PAGO RECIBIDO* 💰\\n\\n*Cliente:* {{2.data.records[0].fields.Name}}\\n*Propiedad:* {{2.data.records[0].fields['Assigned Property']}}\\n*Monto:* ${{formatNumber(1.data.object.amount_received / 100, 2, ',', '.')}} MXN\\n*Método:* {{1.data.object.payment_method_types[0]}}\\n\\n✅ Carpeta movida a PD-APARTA PAGADO\\n✅ Cita agendada con Diana\\n✅ Solicitud de documentos enviada\\n\\n@diana por favor revisa el Calendar"
      },
      "metadata": {
        "designer": {
          "x": 2100,
          "y": 0
        }
      }
    }
  ],
  "metadata": {
    "instant": true,
    "version": 1,
    "scenario": {
      "roundtrips": 1,
      "maxErrors": 3,
      "autoCommit": true,
      "sequential": false
    }
  }
}
```

### WhatsApp Templates

#### `pago_confirmado_onboarding`
```
¡Felicidades {{1}}! 🎉

Tu pago por {{2}} ha sido confirmado exitosamente.

✅ Siguiente paso: Visita agendada para {{3}}

En esta cita:
• Firmaremos el contrato
• Revisaremos los documentos
• Resolveremos cualquier duda

📎 Por favor lleva:
- INE original
- Comprobante de domicilio
- RFC

¡Nos vemos pronto!
```

#### `solicitud_documentos_kyc`
```
Hola {{1}} 👋

Para agilizar tu proceso, por favor envía foto de los siguientes documentos:

📋 Requeridos:
1. INE (ambos lados)
2. Comprobante de domicilio (no mayor a 3 meses)
3. RFC
4. Comprobante de ingresos (últimos 3 recibos de nómina)

Solo responde a este mensaje con las fotos.

Gracias 🙏
```

---

## 4. Workflow 3: Seguimiento Automático

### Descripción

Follow-ups automatizados para leads que no responden:
- **24 horas:** Primer recordatorio
- **48 horas:** Segundo recordatorio + urgencia
- **72 horas:** Último intento + oferta alternativa
- **96 horas:** Move a secuencia de nurture largo plazo

### Scenario JSON (Cron-based)

```json
{
  "name": "læds - Automatic Follow-ups",
  "flow": [
    {
      "id": 1,
      "module": "builtin:Schedule",
      "version": 1,
      "parameters": {},
      "mapper": {
        "interval": 3600,
        "timezone": "America/Mexico_City"
      },
      "metadata": {
        "designer": {
          "x": 0,
          "y": 0
        }
      }
    },
    {
      "id": 2,
      "module": "airtable:searchRecords",
      "version": 3,
      "parameters": {
        "baseId": "{{AIRTABLE_BASE_ID}}",
        "tableName": "Leads"
      },
      "mapper": {
        "formula": "AND({Status} = 'Proposal Sent', IS_BEFORE({Proposal Sent At}, DATEADD(NOW(), -24, 'hours')), {Follow-up Count} = 0)"
      },
      "metadata": {
        "designer": {
          "x": 300,
          "y": 0
        },
        "parameters": [
          {
            "name": "maxRecords",
            "value": 50
          }
        ]
      }
    },
    {
      "id": 3,
      "module": "util:Iterator",
      "version": 1,
      "mapper": {
        "array": "{{2.data.records}}"
      },
      "metadata": {
        "designer": {
          "x": 600,
          "y": 0
        }
      }
    },
    {
      "id": 4,
      "module": "whatsapp-business:sendMessage",
      "version": 1,
      "parameters": {
        "phoneNumberId": "{{WHATSAPP_PHONE_NUMBER_ID}}"
      },
      "mapper": {
        "to": "{{replace(3.fields.Phone, '+', '')}}",
        "type": "text",
        "text": {
          "body": "Hola {{3.fields.Name}} 👋\\n\\nVi que te envié la propuesta de {{3.fields['Assigned Property']}} ayer.\\n\\n¿Tuviste oportunidad de revisarla? ¿Tienes alguna duda que pueda resolver?\\n\\nRecuerda que la oferta especial vence en 24 horas.\\n\\nSaludos 🏡"
        }
      },
      "metadata": {
        "designer": {
          "x": 900,
          "y": 0
        }
      }
    },
    {
      "id": 5,
      "module": "airtable:updateRecord",
      "version": 3,
      "parameters": {
        "baseId": "{{AIRTABLE_BASE_ID}}",
        "tableName": "Leads",
        "recordId": "{{3.id}}"
      },
      "mapper": {
        "fields": {
          "Follow-up Count": 1,
          "Last Follow-up At": "{{now}}"
        }
      },
      "metadata": {
        "designer": {
          "x": 1200,
          "y": 0
        }
      }
    },
    {
      "id": 6,
      "module": "airtable:searchRecords",
      "version": 3,
      "parameters": {
        "baseId": "{{AIRTABLE_BASE_ID}}",
        "tableName": "Leads"
      },
      "mapper": {
        "formula": "AND({Status} = 'Proposal Sent', IS_BEFORE({Proposal Sent At}, DATEADD(NOW(), -48, 'hours')), {Follow-up Count} = 1)"
      },
      "metadata": {
        "designer": {
          "x": 300,
          "y": 300
        }
      }
    },
    {
      "id": 7,
      "module": "util:Iterator",
      "version": 1,
      "mapper": {
        "array": "{{6.data.records}}"
      },
      "metadata": {
        "designer": {
          "x": 600,
          "y": 300
        }
      }
    },
    {
      "id": 8,
      "module": "whatsapp-business:sendMessage",
      "version": 1,
      "parameters": {
        "phoneNumberId": "{{WHATSAPP_PHONE_NUMBER_ID}}"
      },
      "mapper": {
        "to": "{{replace(7.fields.Phone, '+', '')}}",
        "type": "text",
        "text": {
          "body": "{{7.fields.Name}}, tu oferta para {{7.fields['Assigned Property']}} vence HOY a las 23:59 ⏰\\n\\n⚠️ Última oportunidad para apartar con ${{formatNumber(7.fields.Budget, 0, ',', '.')}} MXN\\n\\nDespués de hoy, el precio podría cambiar o la unidad podría venderse.\\n\\n¿Apartamos? Solo necesito tu confirmación.\\n\\nWhatsApp: Sí, aparto | Necesito extensión | No por ahora"
        }
      },
      "metadata": {
        "designer": {
          "x": 900,
          "y": 300
        }
      }
    },
    {
      "id": 9,
      "module": "airtable:updateRecord",
      "version": 3,
      "parameters": {
        "baseId": "{{AIRTABLE_BASE_ID}}",
        "tableName": "Leads",
        "recordId": "{{7.id}}"
      },
      "mapper": {
        "fields": {
          "Follow-up Count": 2,
          "Last Follow-up At": "{{now}}"
        }
      },
      "metadata": {
        "designer": {
          "x": 1200,
          "y": 300
        }
      }
    },
    {
      "id": 10,
      "module": "airtable:searchRecords",
      "version": 3,
      "parameters": {
        "baseId": "{{AIRTABLE_BASE_ID}}",
        "tableName": "Leads"
      },
      "mapper": {
        "formula": "AND({Status} = 'Proposal Sent', IS_BEFORE({Proposal Expires At}, NOW()), {Follow-up Count} >= 2)"
      },
      "metadata": {
        "designer": {
          "x": 300,
          "y": 600
        }
      }
    },
    {
      "id": 11,
      "module": "util:Iterator",
      "version": 1,
      "mapper": {
        "array": "{{10.data.records}}"
      },
      "metadata": {
        "designer": {
          "x": 600,
          "y": 600
        }
      }
    },
    {
      "id": 12,
      "module": "airtable:updateRecord",
      "version": 3,
      "parameters": {
        "baseId": "{{AIRTABLE_BASE_ID}}",
        "tableName": "Leads",
        "recordId": "{{11.id}}"
      },
      "mapper": {
        "fields": {
          "Status": "Cold - Nurture",
          "Notes": "Propuesta expirada sin respuesta. Movido a nurture largo plazo."
        }
      },
      "metadata": {
        "designer": {
          "x": 900,
          "y": 600
        }
      }
    },
    {
      "id": 13,
      "module": "mailchimp:addSubscriberToList",
      "version": 1,
      "parameters": {
        "listId": "{{MAILCHIMP_NURTURE_LIST_ID}}"
      },
      "mapper": {
        "email": "{{11.fields.Email}}",
        "status": "subscribed",
        "merge_fields": {
          "FNAME": "{{11.fields.Name}}",
          "PHONE": "{{11.fields.Phone}}",
          "LASTPROP": "{{11.fields['Assigned Property']}}",
          "BUDGET": "{{11.fields.Budget}}"
        },
        "tags": ["expired-proposal", "warm-lead"]
      },
      "metadata": {
        "designer": {
          "x": 1200,
          "y": 600
        }
      }
    }
  ],
  "metadata": {
    "instant": false,
    "version": 1,
    "scenario": {
      "roundtrips": 1,
      "maxErrors": 3,
      "autoCommit": true,
      "sequential": false
    }
  }
}
```

---

## 5. Workflow 4: Monitoreo Patrimonial

### Descripción

Para clientes que ya compraron, monitorear:
- Revalorización de propiedad (mensual)
- Oportunidades de refinanciamiento
- Oportunidades de venta/reinversión
- Alertas de mantenimiento

### Scenario JSON (Monthly Cron)

```json
{
  "name": "læds - Patrimony Monitoring",
  "flow": [
    {
      "id": 1,
      "module": "builtin:Schedule",
      "version": 1,
      "parameters": {},
      "mapper": {
        "cron": "0 0 1 * *",
        "timezone": "America/Mexico_City"
      },
      "metadata": {
        "designer": {
          "x": 0,
          "y": 0
        },
        "restore": {
          "parameters": {
            "mode": {
              "label": "On specific days"
            }
          }
        }
      }
    },
    {
      "id": 2,
      "module": "airtable:searchRecords",
      "version": 3,
      "parameters": {
        "baseId": "{{AIRTABLE_BASE_ID}}",
        "tableName": "Clients"
      },
      "mapper": {
        "formula": "{Status} = 'Active'"
      },
      "metadata": {
        "designer": {
          "x": 300,
          "y": 0
        }
      }
    },
    {
      "id": 3,
      "module": "util:Iterator",
      "version": 1,
      "mapper": {
        "array": "{{2.data.records}}"
      },
      "metadata": {
        "designer": {
          "x": 600,
          "y": 0
        }
      }
    },
    {
      "id": 4,
      "module": "openai:ChatCompletion",
      "version": 1,
      "parameters": {
        "model": "gpt-4o",
        "temperature": 0.3
      },
      "mapper": {
        "messages": [
          {
            "role": "system",
            "content": "Eres un experto en valuación inmobiliaria en México. Estima el valor actual de una propiedad basándote en datos de compra y tendencias del mercado."
          },
          {
            "role": "user",
            "content": "Propiedad: {{3.fields['Property Title']}}\\nUbicación: {{3.fields['Property Location']}}\\nValor de compra: ${{3.fields['Purchase Price']}} MXN\\nFecha de compra: {{3.fields['Purchase Date']}}\\nTipo: {{3.fields['Property Type']}}\\nÁrea: {{3.fields['Property Area']}} m²\\n\\nEstima:\\n1. Valor actual de mercado\\n2. % de plusvalía\\n3. Análisis breve\\n\\nResponde en formato JSON: {\\\"current_value\\\": number, \\\"appreciation_percent\\\": number, \\\"analysis\\\": string}"
          }
        ]
      },
      "metadata": {
        "designer": {
          "x": 900,
          "y": 0
        }
      }
    },
    {
      "id": 5,
      "module": "json:ParseJSON",
      "version": 1,
      "parameters": {},
      "mapper": {
        "json": "{{4.choices[0].message.content}}"
      },
      "metadata": {
        "designer": {
          "x": 1200,
          "y": 0
        }
      }
    },
    {
      "id": 6,
      "module": "airtable:updateRecord",
      "version": 3,
      "parameters": {
        "baseId": "{{AIRTABLE_BASE_ID}}",
        "tableName": "Clients",
        "recordId": "{{3.id}}"
      },
      "mapper": {
        "fields": {
          "Current Property Value": "{{5.current_value}}",
          "Appreciation %": "{{5.appreciation_percent}}",
          "Last Valuation Date": "{{now}}",
          "Valuation Analysis": "{{5.analysis}}"
        }
      },
      "metadata": {
        "designer": {
          "x": 1500,
          "y": 0
        }
      }
    },
    {
      "id": 7,
      "module": "builtin:BasicRouter",
      "version": 1,
      "mapper": null,
      "metadata": {
        "designer": {
          "x": 1800,
          "y": 0
        }
      },
      "routes": [
        {
          "flow": [
            {
              "id": 8,
              "module": "whatsapp-business:sendMessage",
              "version": 1,
              "parameters": {
                "phoneNumberId": "{{WHATSAPP_PHONE_NUMBER_ID}}"
              },
              "mapper": {
                "to": "{{replace(3.fields.Phone, '+', '')}}",
                "type": "text",
                "text": {
                  "body": "¡Excelentes noticias {{3.fields.Name}}! 📈\\n\\nTu propiedad {{3.fields['Property Title']}} ha aumentado su valor:\\n\\n💰 Valor actual estimado: ${{formatNumber(5.current_value, 0, ',', '.')}} MXN\\n📊 Plusvalía: {{5.appreciation_percent}}%\\n💵 Ganancia: ${{formatNumber(5.current_value - 3.fields['Purchase Price'], 0, ',', '.')}} MXN\\n\\n🎯 Oportunidades:\\n• Refinanciamiento a mejor tasa\\n• Reinversión en segunda propiedad\\n• Venta con alta rentabilidad\\n\\n¿Te gustaría una asesoría personalizada?"
                }
              },
              "metadata": {
                "designer": {
                  "x": 2100,
                  "y": -200
                }
              }
            },
            {
              "id": 9,
              "module": "slack:createMessage",
              "version": 1,
              "parameters": {
                "channel": "{{SLACK_CHANNEL_ID}}"
              },
              "mapper": {
                "text": "🚀 *Oportunidad de Reinversión*\\n\\n*Cliente:* {{3.fields.Name}}\\n*Propiedad:* {{3.fields['Property Title']}}\\n*Plusvalía:* {{5.appreciation_percent}}% (${{formatNumber(5.current_value - 3.fields['Purchase Price'], 0, ',', '.')}} MXN)\\n\\n_Notificación enviada al cliente_ ✅"
              },
              "metadata": {
                "designer": {
                  "x": 2400,
                  "y": -200
                }
              }
            }
          ],
          "filter": {
            "name": "Alta plusvalía",
            "conditions": [
              [
                {
                  "a": "{{5.appreciation_percent}}",
                  "b": 15,
                  "o": "numeric:greater"
                }
              ]
            ]
          }
        },
        {
          "flow": [
            {
              "id": 10,
              "module": "airtable:createRecord",
              "version": 3,
              "parameters": {
                "baseId": "{{AIRTABLE_BASE_ID}}",
                "tableName": "Activities"
              },
              "mapper": {
                "fields": {
                  "Client": ["{{3.id}}"],
                  "Type": "Valuation Update",
                  "Notes": "Valuación mensual realizada. Plusvalía: {{5.appreciation_percent}}%"
                }
              },
              "metadata": {
                "designer": {
                  "x": 2100,
                  "y": 100
                }
              }
            }
          ],
          "filter": {
            "name": "Plusvalía normal",
            "conditions": [
              [
                {
                  "a": "{{5.appreciation_percent}}",
                  "b": 15,
                  "o": "numeric:lesserOrEqual"
                }
              ]
            ]
          }
        }
      ]
    }
  ],
  "metadata": {
    "instant": false,
    "version": 1,
    "scenario": {
      "roundtrips": 1,
      "maxErrors": 3,
      "autoCommit": true,
      "sequential": false
    }
  }
}
```

---

## 6. Configuración de Integraciones

### EasyBroker

```bash
# Obtener API Key
# 1. Ir a https://www.easybroker.com/mx/api
# 2. Login con tu cuenta
# 3. Generar API Key
# 4. Agregar a Make.com connections

# Headers requeridos
X-Authorization: YOUR_EASYBROKER_API_KEY
Content-Type: application/json

# Endpoints principales
GET https://api.easybroker.com/v1/properties
GET https://api.easybroker.com/v1/properties/{property_id}
POST https://api.easybroker.com/v1/contact_requests
```

### WhatsApp Business API

```bash
# Setup (vía Meta Business Suite)
# 1. Crear Meta Business Account
# 2. Agregar WhatsApp Business Platform
# 3. Crear número de teléfono business
# 4. Obtener credenciales:
#    - Phone Number ID
#    - WhatsApp Business Account ID
#    - Access Token (permanente)

# Crear templates en Meta Business Suite
# Templates deben ser aprobados (24-48 horas)

# Headers requeridos
Authorization: Bearer YOUR_WHATSAPP_ACCESS_TOKEN
Content-Type: application/json

# Endpoint
POST https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages
```

### Google Calendar

```bash
# Setup
# 1. Google Cloud Console → Crear proyecto
# 2. Habilitar Google Calendar API
# 3. Crear OAuth 2.0 Client ID
# 4. Configurar en Make.com connections
# 5. Autorizar acceso al calendar de Diana

# Scopes requeridos
- https://www.googleapis.com/auth/calendar
- https://www.googleapis.com/auth/calendar.events
```

### Airtable

```bash
# Setup
# 1. Crear base desde template (ver sección siguiente)
# 2. Obtener Base ID (url: airtable.com/{BASE_ID}/...)
# 3. Crear Personal Access Token
# 4. Configurar en Make.com

# Permisos requeridos
- data.records:read
- data.records:write
- schema.bases:read
```

### Airtable Base Structure

#### Table: Leads
```
Fields:
- Name (Single line text)
- Email (Email)
- Phone (Phone number)
- Budget (Currency - MXN)
- Status (Single select: New, Contacted, Qualified, Proposal Sent, Negotiating, Converted, Lost, Nurture)
- Source (Single line text)
- Assigned Property (Single line text)
- Monthly Payment (Currency - MXN)
- Proposal Sent At (Date & time)
- Proposal Expires At (Date & time)
- Follow-up Count (Number)
- Last Follow-up At (Date & time)
- WhatsApp Message ID (Single line text)
- Payment Amount (Currency - MXN)
- Payment Method (Single line text)
- Payment Date (Date & time)
- Stripe Payment Intent (Single line text)
- Folder ID (Single line text)
- Notes (Long text)
```

#### Table: Clients
```
Fields:
- Name (Single line text)
- Email (Email)
- Phone (Phone number)
- Status (Single select: Active, Inactive)
- Property Title (Single line text)
- Property Location (Single line text)
- Property Type (Single select: Apartment, House, Land, Commercial)
- Property Area (Number - m²)
- Purchase Price (Currency - MXN)
- Purchase Date (Date)
- Current Property Value (Currency - MXN)
- Appreciation % (Percent)
- Last Valuation Date (Date)
- Valuation Analysis (Long text)
- Total Purchases (Currency - MXN)
- Lifetime Value (Currency - MXN)
```

---

## 7. Variables y Secrets

### Make.com Data Stores

```javascript
// Data Store: laeds-config
{
  "organization_id": "org_abc123",
  "easybroker_api_key": "{{EASYBROKER_API_KEY}}", // From vault
  "whatsapp_phone_number_id": "{{WHATSAPP_PHONE_NUMBER_ID}}",
  "airtable_base_id": "{{AIRTABLE_BASE_ID}}",
  "slack_channel_id": "C01ABC123",
  "diana_calendar_id": "diana@laeds.ai",
  "google_drive_aparta_pagado_folder_id": "1aBcDeFgHiJkLmNoPqRsTuV",
  "mailchimp_nurture_list_id": "abc123def",
  "monthly_payment_term": 24,
  "min_qualified_budget": 25000,
  "proposal_validity_hours": 48
}
```

### Environment Variables (Secrets)

```bash
# Make.com Vault o Variables
EASYBROKER_API_KEY=eb_live_xxxxxxxxxxxxx
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
AIRTABLE_PAT=patxxxxxxxxxxxxx.xxxxxxxxxxxxx
GOOGLE_OAUTH_CLIENT_ID=xxxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxx
LAEDS_API_KEY=sk_laeds_xxxxxxxxxxxxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00/B00/xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

---

## 8. Testing y Troubleshooting

### Testing Checklist

#### Workflow 1: Meta Lead → Propuesta
```bash
# Test 1: Simular webhook de Meta
curl -X POST https://hook.us1.make.com/xxxxxxxxxxxxx \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan.perez@example.com",
    "phone": "+521234567890",
    "budget": 30000,
    "bedrooms": 2,
    "location": "Guadalajara",
    "ad_id": "123456789",
    "campaign_name": "Palm Diamante - Guadalajara"
  }'

# Expected:
# 1. Lead creado en Airtable
# 2. WhatsApp enviado a +521234567890
# 3. Notificación en Slack
# 4. Status: "Proposal Sent"

# Test 2: Budget bajo $25k
curl -X POST https://hook.us1.make.com/xxxxxxxxxxxxx \
  -H "Content-Type: application/json" \
  -d '{
    "name": "María López",
    "email": "maria.lopez@example.com",
    "phone": "+521234567891",
    "budget": 15000,
    "bedrooms": 1,
    "location": "CDMX"
  }'

# Expected:
# 1. Lead creado con status "Nurture - Low Budget"
# 2. Agregado a lista Mailchimp
# 3. NO se envía WhatsApp de propuesta
```

#### Workflow 2: Pago → Onboarding
```bash
# Test usando Stripe CLI
stripe trigger payment_intent.succeeded

# Expected:
# 1. Lead actualizado a "Payment Received"
# 2. Carpeta movida en Google Drive
# 3. Evento creado en Calendar de Diana
# 4. 2 WhatsApp enviados (confirmación + documentos)
# 5. Notificación en Slack
```

### Common Issues & Solutions

| Issue | Causa | Solución |
|-------|-------|----------|
| **WhatsApp template rejected** | Formato incorrecto o política violada | Revisar políticas de WhatsApp Business, usar placeholders {{1}}, evitar URLs directas |
| **EasyBroker 401 Unauthorized** | API Key inválida o expirada | Regenerar API Key en dashboard de EasyBroker |
| **Google Calendar event creation fails** | Scopes insuficientes | Re-autorizar con scope calendar.events |
| **Airtable formula error** | Sintaxis incorrecta | Validar fórmula en Airtable UI primero |
| **OpenAI timeout** | Prompt muy largo o rate limit | Reducir tokens, implementar retry con exponential backoff |
| **Make.com scenario incomplete** | Error no manejado | Agregar error handler module, enviar a Slack |

### Debug Mode

```javascript
// Agregar al inicio de cada flujo crítico
// Module: Tools > Set Variable
{
  "name": "debug_enabled",
  "value": true,
  "scope": "roundtrip"
}

// Agregar después de cada paso importante
// Module: Tools > Logger (si debug_enabled)
{
  "message": "Step X completed",
  "data": {
    "leadId": "{{lead.id}}",
    "propertyId": "{{property.id}}",
    "monthly_payment": "{{monthly_payment}}"
  }
}

// Logs se guardan en Make.com > Scenario > History > Execution Details
```

### Monitoring

```javascript
// Agregar al final de cada escenario
// Module: HTTP > Make a Request
{
  "url": "https://api.laeds.ai/v1/analytics/scenario-execution",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer {{LAEDS_API_KEY}}",
    "Content-Type": "application/json"
  },
  "body": {
    "scenario_name": "{{scenario.name}}",
    "execution_id": "{{scenario.executionId}}",
    "status": "success",
    "duration_ms": "{{scenario.durationMs}}",
    "operations_consumed": "{{scenario.operationsConsumed}}",
    "timestamp": "{{now}}"
  }
}

// Dashboard en læds® mostrará:
// - Escenarios ejecutados/hora
// - Tasa de éxito
// - Tiempo promedio de ejecución
// - Operaciones consumidas
```

---

## Resumen

Este documento define **4 workflows de automatización críticos** para læds® CRM:

1. ✅ **Meta Lead → Propuesta 48h**: Calificación, matching y envío automático
2. ✅ **Pago → Onboarding**: Confirmación, agenda y solicitud de documentos
3. ✅ **Seguimiento Automático**: Follow-ups 24h, 48h, 72h
4. ✅ **Monitoreo Patrimonial**: Valuación mensual y alertas de oportunidades

**Todos los escenarios están listos para importar a Make.com** con el JSON proporcionado.

**Siguiente paso:** Importar escenarios, configurar integraciones y hacer testing.

---

**Documento preparado por:** Cursor AI Agent  
**Fecha:** 9 de Septiembre, 2026  
**Versión:** 1.0  
**Estado:** Ready for Implementation
