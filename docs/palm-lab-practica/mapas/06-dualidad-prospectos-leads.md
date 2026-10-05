# Mapa 06 — Dualidad prospectos y leads

| Campo | Valor |
| --- | --- |
| Identificador | MAPA-06 |
| Estado | Parcial |
| Corte | 2026-10-05 |
| Objetos ancla | `prospectos`, `leads`, `leads.prospecto_id`, `leads_telefono_uidx` |

## 1. Propósito operativo

`prospectos` guarda lo que el cliente dijo y lo que el canal necesita para operar hoy. `leads` es el objeto de negocio dentro del funnel: estado enum, temperatura enum, fuente, campaña, teléfono normalizado e idempotencia. Separarlos evita que un ajuste de CRM reescriba el relato, y evita que una frase suelta del chat sea, por sí misma, una etapa de venta.

En el laboratorio la separación es real en el modelo y todavía incompleta en las columnas: `prospectos` también tiene `estado`, `temperatura`, `presupuesto`, `forma_pago`, `plazo`, `tipologia`, `perfil` y `asignado_a`. Esos campos nacieron antes del ERD y siguen alimentando las vistas diarias.

## 2. Conexión sistémica

### Entrada

Mensajes y eventos de canal. El receptor de WhatsApp aún no escribe aquí (mapa 03). Los 15 prospectos y sus 15 leads son semilla de laboratorio, enlazados uno a uno.

### Tránsito

Orden de escritura que este mapa exige, y que el esquema permite sin imponerlo en un solo trigger:

1. Resolver el teléfono. En `prospectos`, unicidad sobre `telefono` tal como se guardó. En `leads`, unicidad sobre dígitos (`telefono_normalizado`).
2. Insertar o actualizar `prospectos` con el texto y las marcas de conversación (`ultimo_msg_cliente_at`, `notas`, `sinprecio_pendiente`).
3. Insertar o actualizar `leads` con `prospecto_id`, estado, temperatura, fuente y `clave_idempotencia`.
4. Alimentar hijas: perfil, scoring e interacciones desde el lead; borradores, citas y seguimientos desde el prospecto.

`leads.prospecto_id` es único y nullable. En el corte los 15 leads tienen puente (`con_puente = 15`). No hay lead huérfano ni prospecto sin lead.

No hay trigger `prospectos → leads` ni `leads → prospectos`. La coherencia observada es de datos, no de motor.

### Salida

La salida es un par consistente: el texto y los atributos declarativos quedan en `prospectos`; la etapa comercial queda en `leads`. Las vistas de reporte diario leen `prospectos`. La vista de temperatura de negocio, `v_leads_temperatura`, lee las dos y publica ambos lados (`lead_*` y `prospecto_*`).

## 3. Análisis por capas

### Inputs

- Atributos extraídos de la conversación: nombre, teléfono, propósito, presupuesto, forma de pago, plazo, tipología, horario, unidad de interés.
- Cambios de estado hechos por el agente `comercial` o `followup` sobre `leads`. Esos agentes no tienen política RLS sobre `prospectos`. Un cambio de estado en `leads` no se replica solo.

### Outputs

| Autoridad | Tabla | Qué manda |
| --- | --- | --- |
| Negocio | `leads` | `estado` enum, `temperatura` enum, fuente, campaña, teléfono normalizado, asignación protegida por agente. |
| Declaración y cola diaria | `prospectos` | Texto, perfil A/B/C de laboratorio, unidad de interés hacia `inventario.clave`, marcas de mensaje, `sinprecio_pendiente`. |

`prospectos.unidad_interes` referencia `inventario.clave`. `leads.unidad_interes_clave` es texto sin llave foránea. Otro punto que el espejo debe cuidar.

`prospectos.perfil` acepta `A`, `B`, `C` (default `A`). La clase de negocio equivalente es `scoring.clase`, no la columna del prospecto.

### Control de temperatura

Regla de este mapa: la temperatura se decide en el lead y se refleja en el prospecto para que `v_leads_frios` y el reporte diario no muestren otra cosa.

Observación del corte: 0 divergencias de `temperatura`, `estado`, `ultimo_msg_cliente_at` y `proximo_seguimiento_at` en los 15 pares. Distribución: caliente 6, tibio 6, frío 3.

Ausencia: no hay constraint ni trigger que impida la próxima divergencia. Brecha B-06.

### Consumos y recursos

- Dos escrituras por evento de identidad. Deben ir en la misma transacción para no dejar un prospecto sin lead.
- Índice único de teléfono en cada tabla. Un formato distinto (`+52…` frente a dígitos) puede colisionar en una y pasar en la otra: por eso el lead normaliza y el prospecto debe guardar el mismo valor canónico que se acuerde en el receptor.
- `buscar_lead_por_telefono` es el lookup de negocio. El lookup de prospecto es por `telefono` exacto.

## 4. Contrato de datos

Checks de `prospectos.estado`: `nuevo`, `contactado`, `calificado`, `cita`, `apartado`, `cerrado`, `descartado`. Mismos literales que `lead_estado`, con tipos distintos (`text` contra enum).

Checks de `prospectos.temperatura`: `caliente`, `tibio`, `frio`, nullable, igual que el enum del lead.

Columnas de canal compartidas por nombre: `ultimo_msg_cliente_at`, `ultimo_msg_asesor_at`, `proximo_seguimiento_at`, `sinprecio_pendiente`, `asignado_a`, `notas`.

## 5. Evidencia

- `leads_prospecto_id_key` único.
- `prospectos_telefono_key` único.
- `leads_telefono_uidx` único.
- Comentario de `leads`: el teléfono normalizado deduplica.
- Conteos y divergencia consultados en el corte, sin leer nombres ni teléfonos.

## 6. Criterio de producción

Cada alta de canal crea exactamente un prospecto y un lead en la misma transacción, con `prospecto_id` poblado y teléfonos equivalentes tras normalizar. Un update de `leads.estado` o `leads.temperatura` actualiza el reflejo en `prospectos` dentro de esa transacción, o una revisión programada con la consulta de divergencia devuelve cero. Las vistas diarias pueden seguir leyendo `prospectos` mientras ese reflejo sea una regla y no una coincidencia de la semilla.
