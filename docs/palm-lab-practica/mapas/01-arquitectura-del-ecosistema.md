# Mapa 01 — Arquitectura del ecosistema

| Campo | Valor |
| --- | --- |
| Identificador | MAPA-01 |
| Estado | Parcial |
| Corte | 2026-10-05 |
| Objetos ancla | esquema `public`, rol `service_role`, rol `crm_agent`, Edge Functions desplegadas |

## 1. Propósito operativo

Este mapa fija el perímetro del laboratorio. Toda pieza de negocio —prospecto, lead, inventario, match, cita, borrador, comisión— se escribe en Postgres sobre el proyecto `palm-lab-practica`. Un microservicio o un agente que necesite el estado de otro lo lee en una tabla. La conversación entre agentes ocurre en filas, con actor y con la matriz `agente_permisos`.

El perímetro separa tres planos:

| Plano | Qué contiene | Dónde vive en este corte |
| --- | --- | --- |
| Fuente de verdad | Catálogos, CRM, reglas, historial | Postgres `public`, funciones `private` |
| Borde serverless | Sincronización EasyBroker y alerta de formulario | `easybroker-sync`, `lead-alert-email`, `easybroker-load` |
| Borde externo | WhatsApp, pauta, orquestación, inferencia | Declarado para producción; sin objeto interno |

## 2. Conexión sistémica

### Entrada

Dos entradas están materializadas y una está declarada.

| Entrada | Contrato actual | Evidencia |
| --- | --- | --- |
| Catálogo EasyBroker | `POST` a `easybroker-sync` con cabecera `x-webhook-secret`. Upsert en `easybroker_propiedades` por `public_id`. | 365 filas. Función versión 1, `verify_jwt = false`. |
| Formulario de práctica | `INSERT` anónimo en `leads_prueba_formulario`. | 3 filas. Trigger `trg_lead_alert_email`. |
| Cloud API de Meta | Webhook hacia `webhook_eventos` (`proveedor` default `meta_whatsapp`). | Tabla lista, 0 filas. Sin función receptora. |

El número operativo declarado para el canal es 55 4018 0018. Ese número no está almacenado en el esquema auditado.

### Tránsito

El tránsito obligatorio es una escritura en Supabase.

- Las tablas conversacionales (`prospectos`, `borradores`, `citas`, `seguimientos`, `inventario`, `easybroker_propiedades`, `webhook_eventos`) tienen RLS activo y cero políticas. `anon` y `authenticated` no las leen ni las escriben. El camino de escritura es `service_role`, que tiene `BYPASSRLS`.
- Las tablas del ERD de negocio (`leads`, `matches`, `scoring`, `interacciones`, `comisiones`, inventario canónico) aceptan además al rol `crm_agent`, siempre que `private.crm_permiso` autorice la acción y el trigger `private.crm_guard_write` deje pasar al agente asumido.
- `private` no está expuesto al API. Ahí viven la normalización de teléfono, las reglas de match, interacción y comisión, y la verificación del secreto de alerta.

### Salida y orquestación

| Salida | Estado en el corte |
| --- | --- |
| Filas de CRM | Operativas en laboratorio: 15 leads enlazados, 605 unidades, bitácora de historial. |
| Correo `lead-alert-email` | Operativo solo para altas del formulario de prueba, vía Resend y `pg_net`. |
| HTTP saliente a WhatsApp | Especificado. No hay cliente de la Cloud API en las funciones desplegadas. |
| n8n leyendo estados y devolviendo borradores | Especificado. Cero referencias en el catálogo de la base. |

Los cinco agentes de base (`inventario`, `matching`, `prospecting`, `followup`, `comercial`) son el mecanismo interno de orquestación. Se asumen con `public.asumir_agente` y quedan limitados por `agente_permisos` (52 filas).

## 3. Análisis por capas

### Inputs

- Payload JSON de propiedades EasyBroker (lista paginada y detalle).
- Payload JSON de webhook, con columnas `payload`, `headers`, `event_id` y `clave_idempotencia` única. Aún sin tráfico.
- Aprobaciones humanas sobre `borradores` (`aprobado_por`, `aprobado_at`).
- Acciones de asesores cuando operan como `crm_agent` / agente `comercial`.

### Outputs

- Registros en `prospectos`, `leads`, `perfiles_inversion`, `scoring`, `borradores`, `citas`, `seguimientos`.
- Catálogo externo en `easybroker_propiedades` y catálogo canónico en `desarrollos` → `torres` → `unidades`.
- Correo transaccional del formulario de prueba.
- Petición HTTP a WhatsApp: salida requerida en producción, ausente en el corte.

### Control de temperatura

Este mapa no calcula temperatura. Habilita las columnas `leads.temperatura` y `prospectos.temperatura`, restringidas a `caliente`, `tibio` y `frio`, y la vista `v_leads_temperatura` que las junta. El cálculo vive en los mapas 02, 03 y 11.

### Consumos y recursos

| Recurso | Uso observado |
| --- | --- |
| Postgres 17 en `us-east-1` | Esquema, RLS, triggers, 605 unidades y 365 propiedades externas. |
| Edge Functions (Deno) | Tres funciones. `easybroker-load` responde 410. |
| `pg_net` + Vault | Encolan y autentican la alerta de formulario. |
| Inferencia de agentes de IA | Sin llamada registrada en la base. El scoring vigente proviene de la migración (`modelo = migracion-prospectos`). |
| Ejecuciones de n8n | Sin objeto que las contabilice. |
| Ancho de banda de webhooks Meta | `webhook_eventos` preparado, sin filas. |

## 4. Contrato de datos

Roles de Postgres relevantes:

| Rol | `BYPASSRLS` | Superusuario | Papel |
| --- | --- | --- | --- |
| `anon` | no | no | Inserta solo en el formulario de práctica. |
| `authenticated` | no | no | Grants sobre vistas de reporte; las tablas base no le abren política. |
| `crm_agent` | no | no | Agentes de negocio bajo `agente_permisos`. |
| `service_role` | sí | no | Backend. Único rol de servicio con escritura total. |
| `postgres` | sí | no | Migraciones y operación de plataforma. |

Extensiones instaladas: `plpgsql`, `pgcrypto`, `uuid-ossp`, `pg_stat_statements`, `supabase_vault`, `pg_net`. `pg_cron` no está instalado.

## 5. Evidencia

- Proyecto `ACTIVE_HEALTHY`, creado 2026-09-28.
- Migración inicial `20260928164652 esquema_inicial` hasta `20261005104549 crm_hardening_upsert_webhook_vista_comision`.
- Comentario de `webhook_eventos`: almacén crudo de webhooks Meta WhatsApp, solo `service_role`, sin políticas públicas.
- Comentario de `easybroker_propiedades`: copia de solo lectura lógica respecto de EasyBroker; la escritura local es upsert del sync.

## 6. Criterio de producción

El mapa queda cerrado cuando un mensaje de prueba del número operativo produce, en una sola traza, una fila en `webhook_eventos`, un lead resuelto por `telefono_normalizado` y una interacción entrante, y cuando la respuesta aprobada sale por la Cloud API y regresa como interacción saliente. Hasta entonces el ecosistema es la columna vertebral de datos, con el canal de WhatsApp todavía fuera del tránsito.
