# Mapa 03 — Flujo WhatsApp inbound

| Campo | Valor |
| --- | --- |
| Identificador | MAPA-03 |
| Estado | Parcial |
| Corte | 2026-10-05 |
| Objetos ancla | `webhook_eventos`, `leads.telefono_normalizado`, `private.normalizar_telefono`, `interacciones`, `public.buscar_lead_por_telefono` |

## 1. Propósito operativo

Todo mensaje que llegue al número 55 4018 0018 debe quedar íntegro antes de que cualquier agente responda. La integridad exigida es de tres capas: autenticidad del webhook, identidad única del teléfono y bitácora inalterable del mensaje. El número está declarado en la especificación operativa y no está persistido como configuración en la base.

## 2. Conexión sistémica

### Entrada

`webhook_eventos` es el buzón.

| Columna | Contrato |
| --- | --- |
| `proveedor` | Default `meta_whatsapp`. |
| `event_id` | Identificador externo, nullable. |
| `payload` | JSON del webhook, obligatorio. |
| `headers` | JSON de cabeceras, para conservar la firma. |
| `estado` | `recibido` (default), `procesado`, `error`, `descartado`. |
| `clave_idempotencia` | Única. Reintentos de Meta no duplican la fila. |
| `procesado_at`, `error_mensaje` | Cierre del procesamiento. |

RLS activo, sin políticas. Grants solo de `service_role`. Comentario de tabla: almacén crudo, sin políticas públicas.

No hay función que verifique HMAC, que responda el reto de verificación de Meta ni que inserte en esta tabla. Brecha B-01.

### Tránsito

Cuando el receptor exista, el tránsito ya tiene primitivas:

1. `private.normalizar_telefono` reduce el teléfono a dígitos.
2. `private.crm_normaliza_lead`, trigger `BEFORE INSERT OR UPDATE` sobre `leads`, exige entre 10 y 15 dígitos y escribe `telefono_normalizado`.
3. Índice único `leads_telefono_uidx` sobre `telefono_normalizado`. Un teléfono es un lead.
4. `public.buscar_lead_por_telefono` devuelve `id` y `estado` solo si el actor es `prospecting`, `comercial`, `followup` o `matching`, o si la sesión es `postgres` / `supabase_admin`.
5. `prospectos.telefono` es único. El puente `leads.prospecto_id` también es único.

El alta prevista: si el teléfono no existe, insertar `prospectos` y el `leads` enlazado; si existe, actualizar `ultimo_msg_cliente_at`. Ambas columnas existen en las dos tablas. En el corte no hay trigger que haga ese upsert a partir de `webhook_eventos`.

El agente `prospecting` puede crear leads, perfiles y scoring, y puede crear interacciones solo si `direccion = entrante` o `canal = sistema` (`private.crm_guard_write`).

### Salida

La salida especificada es invocar calificación y abrir borrador, seguimiento o cita.

| Salida | Preparación | Tráfico |
| --- | --- | --- |
| `interacciones` dirección `entrante`, estado `recibido` | Tabla, enums, índice único `(canal, id_externo)`, tope de 8 000 caracteres | 0 filas |
| Recalculo de temperatura | Columnas y `clasificar_lead` | Scoring estático de migración |
| `borradores` | Tabla con estado `pendiente` | 2 filas de laboratorio, no atribuidas a un webhook |
| `seguimientos` / `citas` | Tablas hijas de `prospectos` | 4 y 2 filas |

## 3. Análisis por capas

### Inputs

- Payload de Meta Cloud API: metadatos, id de mensaje, texto o referencia a multimedia.
- El esquema guarda el JSON completo. No hay columnas separadas para tipo de media ni para el id de WhatsApp Business. Esos datos viajan dentro de `payload` hasta que un receptor los proyecte a `interacciones`.

### Outputs

- Fila de `webhook_eventos` con idempotencia.
- Alta o actualización de `prospectos` y `leads`.
- Fila de `interacciones` (`canal = whatsapp`, `direccion = entrante`, `estado = recibido`, `id_externo` del mensaje).
- Efectos condicionales en `borradores`, `seguimientos` o `citas`.

### Control de temperatura

El recálculo por intención de compra está especificado como trabajo de un agente de lenguaje. En la base, la temperatura es un dato que alguien escribe. La función disponible clasifica la clase A/B/C a partir de una temperatura ya decidida, un presupuesto y una forma de pago. No lee el texto del mensaje. Las 15 temperaturas actuales son datos de laboratorio (caliente 6, tibio 6, frío 3), coherentes con su prospecto, producidas por la migración y no por un webhook.

### Consumos y recursos

| Recurso | Situación |
| --- | --- |
| Validación HMAC | Especificada. No hay función ni verificación de firma. |
| Lookup por `telefono_normalizado` | Índice único btree listo. |
| Escritura transaccional | Triggers de normalización y permiso listos en `leads`. |
| Llamadas a modelo de lenguaje | Sin proveedor, sin tabla de corridas y sin filas de `interacciones` que analizar. |

## 4. Contrato de datos

Enums de la bitácora:

- `interaccion_canal`: `whatsapp`, `email`, `llamada`, `visita`, `linkedin`, `meta`, `sistema`, `otro`.
- `interaccion_direccion`: `entrante`, `saliente`.
- `interaccion_estado`: `borrador`, `aprobado`, `enviado`, `recibido`, `fallido`, `cancelado`.

`interacciones.lead_id` es obligatorio. Un mensaje no puede existir sin lead. `unidad_id` y `campana_id` son opcionales.

## 5. Evidencia

- `webhook_eventos`: 0 filas.
- `interacciones`: 0 filas.
- 15 leads con teléfono normalizado único y puente a prospecto.
- Migración `20261005104549 crm_hardening_upsert_webhook_vista_comision` endurece el upsert de webhook; el receptor que lo llene sigue fuera.

## 6. Criterio de producción

Una prueba con un mensaje real al 55 4018 0018 deja exactamente una fila en `webhook_eventos` (`estado = procesado`), exactamente una interacción entrante con el id de Meta, y un lead cuyo `ultimo_msg_cliente_at` avanza. Un segundo envío del mismo evento no crea otra fila. Un payload con firma inválida queda en `descartado` o ni siquiera se inserta, y no dispara calificación.
