# Mapa 08 — Edge Functions

| Campo | Valor |
| --- | --- |
| Identificador | MAPA-08 |
| Estado | Parcial |
| Corte | 2026-10-05 |
| Objetos ancla | `easybroker-load`, `easybroker-sync`, `lead-alert-email` |

## 1. Propósito operativo

Las funciones de borde concentran el HTTP que el laboratorio sí expone. La política de exposición es binaria: o la plataforma exige el JWT de Supabase, o la función nace con `verify_jwt = false` y exige un secreto propio antes de tocar datos. Las tres funciones cumplen esa política. Su alcance real es más estrecho que el nombre del mapa de temperatura.

## 2. Conexión sistémica

### Entrada

| Función | Versión | `verify_jwt` | Quién la llama hoy | Autorización propia |
| --- | --- | --- | --- | --- |
| `easybroker-load` | 2 | verdadero | Nadie. Responde 410. | El JWT no alcanza a ejecutar lógica: el handler no lee el cuerpo. |
| `easybroker-sync` | 1 | falso | Invocación externa. `pg_cron` no existe. | Cabecera `x-webhook-secret` comparada en tiempo constante (SHA-256) con `SYNC_SECRET`. Secreto ausente o corto: HTTP 503. Cabecera incorrecta: HTTP 401. Sin `EASYBROKER_API_KEY`: HTTP 503. |
| `lead-alert-email` | 2 | falso | Trigger `AFTER INSERT` en `leads_prueba_formulario`, vía `pg_net.http_post`. | Cabecera `x-webhook-secret` de 32 a 256 caracteres, verificada con `public.lead_alert_verify_secret` contra Vault (`lead_alert_webhook_secret`). El secreto no se imprime. Fallo de verificación: 401. Base inaccesible: 503. |

### Tránsito

`easybroker-sync` lee EasyBroker (`https://api.easybroker.com/v1`) por estatus `published`, `not_published`, `reserved`, `sold`, `rented`, `suspended`, pagina de 50 en 50, pide detalle solo de lo nuevo o cambiado, respeta pausa y `Retry-After`, y hace upsert en `easybroker_propiedades` por `public_id`. No borra ausentes: los reporta como `missing_in_easybroker`. Acepta `dry_run`, `full` y `max_details` en el JSON. Presupuesto de tiempo interno: 110 segundos.

`lead-alert-email` ignora cualquier cuerpo que no sea `INSERT` sobre `leads_prueba_formulario` (responde 202). Con `RESEND_API_KEY` arma un correo por destinatario. Destinatarios: variable `ALERT_TO`, o el destinatario primario de la cuenta de envío, más uno secundario solo si `ALERT_INCLUDE_ME_COM=true`. Remitente: `ALERT_FROM`. El lead ya está guardado aunque el correo falle.

`private.notify_lead_alert_email` es `SECURITY DEFINER`. Si el secreto de Vault no está, deja un warning y no envía. Un error de red no revierte el `INSERT`.

### Salida

| Función | Salida |
| --- | --- |
| `easybroker-load` | HTTP 410, cuerpo `gone`. Comentario en código: carga única del 2026-10-04, candidata a borrarse. |
| `easybroker-sync` | JSON con `listed`, `upserted`, `deferred_to_next_run`, `detail_failures`. Efecto: filas en `easybroker_propiedades` (365 en el corte). |
| `lead-alert-email` | Correo transaccional y JSON `{ sent, results }`. No escribe temperatura ni toca `leads`. |

## 3. Análisis por capas

### Inputs

- Secretos de entorno y de Vault. Ningún secreto está en el código de las funciones.
- `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY`, inyectados por la plataforma.
- Evento de inserción del formulario de prueba.
- Catálogo remoto de EasyBroker, solo lectura.

### Outputs

- Respuestas JSON de estado.
- Upsert del catálogo externo.
- Correo de alerta del formulario.

### Control de temperatura

La especificación de este mapa pide alerta inmediata al detectar un lead `caliente`. El código desplegado no lee `leads.temperatura`. Dispara en cada alta de `leads_prueba_formulario`, sea cual sea el perfil del formulario (`A_Inversionista`, `B_Tecnologia_IA`, `C_Patrimonial`). Un lead caliente del núcleo CRM no genera este correo. Brecha B-10.

### Consumos y recursos

| Recurso | Control observado |
| --- | --- |
| Invocaciones Deno | Tres funciones `ACTIVE`. Una está apagada por respuesta 410. |
| Cuota de correo | Un envío por destinatario, con llave de idempotencia `lead-{id}-{destinatario}`. Sin `RESEND_API_KEY` no se intenta. |
| Cron | Extensión `pg_cron` ausente. El comentario de `easybroker-sync` describe una corrida horaria que este proyecto no tiene instalada. Brecha B-09. |
| Rate limit EasyBroker | Pausa default 350 ms, reintentos con backoff, tope default de 60 detalles por corrida. |

## 4. Contrato de datos

Tablas que estas funciones pueden modificar:

- `easybroker_propiedades`, solo `easybroker-sync`, con `service_role`.
- Ninguna función modifica `unidades` ni `leads`.
- `lead-alert-email` lee la fila que el trigger ya insertó; no hace `UPDATE`.

`lead_alert_verify_secret(text)` es `SECURITY DEFINER` y solo `service_role` puede ejecutarla.

## 5. Evidencia

- Listado de Edge Functions del proyecto en el corte: exactamente las tres slugs anteriores.
- Extensiones: `pg_net` y `supabase_vault` presentes; `pg_cron` ausente.
- Trigger `trg_lead_alert_email` sobre `public.leads_prueba_formulario`.
- 365 propiedades sincronizadas, 3 filas de formulario capaces de haber disparado la alerta.

## 6. Criterio de producción

Cada función expuesta con `verify_jwt = false` sigue rechazando la llamada si falta el secreto. `easybroker-load` se retira. La sincronización queda en un calendario verificable, dentro o fuera de la base, con una corrida cuyo JSON de resumen se conserva. La alerta de lead caliente, cuando se construya, escucha `leads` del núcleo y no la tabla de práctica. El formulario de práctica puede conservar su aviso durante el laboratorio, identificado como tal en el asunto y en el cuerpo, que ya dice que la fila viene de esa tabla.
