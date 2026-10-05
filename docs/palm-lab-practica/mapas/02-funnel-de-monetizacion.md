# Mapa 02 — Funnel de monetización

| Campo | Valor |
| --- | --- |
| Identificador | MAPA-02 |
| Estado | Parcial |
| Corte | 2026-10-05 |
| Objetos ancla | `fuentes_lead`, `campanas`, `leads.estado`, `perfiles_inversion`, `matches`, `citas`, `comisiones` |

## 1. Propósito operativo

El funnel obliga a que cada avance comercial deje evidencia. Un lead de Palm Diamante recorre un estado cerrado y termina, si hay contraprestación, en `comisiones`. La comisión nace de un `match_id`. El match nace de un lead y de una unidad. El lead nace de una fuente. Esa cadena es la que vuelve rastreable cada peso.

## 2. Conexión sistémica

### Entrada

La etapa de awareness está modelada, no alimentada.

- `fuentes_lead` tiene 10 slugs activos en catálogo: `facebook`, `instagram`, `linkedin`, `google`, `portal`, `referido`, `whatsapp`, `formulario`, `easybroker`, `otro`. Familia enum: `linkedin`, `meta`, `web`, `referido`, `directo`, `otro`.
- `campanas` cuelga de `fuentes_lead` y guarda `presupuesto`, `moneda` (default `MXN`), `estado` (`borrador`, `activa`, `pausada`, `cerrada`) e `id_externo`. Tiene 0 filas. No hay costo de adquisición persistido.
- Los 15 leads tienen `prospecto_id`. La atribución de campaña (`campana_id`) no tiene campañas a las cuales apuntar.

### Tránsito

El estado del lead es el riel del funnel. Enum `lead_estado`:

`nuevo` → `contactado` → `calificado` → `cita` → `apartado` → `cerrado`, con salida lateral `descartado`.

Conteo en el corte: nuevo 5, contactado 3, calificado 1, cita 3, apartado 1, cerrado 1, descartado 1.

Entre calificación y apartado el tránsito previsto es:

1. `perfiles_inversion` (15 filas, una por lead): presupuesto, forma de pago, horizonte, yield, objetivo (`uso_propio` 3, `vacacional` 5, `inversion` 7).
2. `scoring` vigente, clase `A`/`B`/`C`.
3. `matches` sobre unidades `disponible`.
4. `citas` (hoy colgadas de `prospectos`, 2 programadas) y `seguimientos`.
5. Cambio de `unidades.estatus` a `apartado` cuando un match pasa a `aceptado` (`private.match_reglas`).

`prospectos.estado` repite el mismo vocabulario en un `CHECK` de texto. En el corte los 15 pares coinciden. El estado con autoridad de negocio para el ERD nuevo es `leads.estado`.

### Salida

`comisiones` es la salida financiera. Estados: `potencial`, `devengada`, `pagada`, `cancelada`. El monto es columna generada `round(base_monto * porcentaje, 2)`. El porcentaje está entre 0 y 1, extremo superior incluido. Índice único parcial: un beneficiario no tiene dos comisiones abiertas sobre el mismo match.

Reglas de `private.comision_reglas`:

- `devengada` solo si la unidad del match está `reservado` o `vendido`.
- `pagada` solo si la unidad está `vendido`; se sella `pagada_at` si venía nulo.
- `pagada` y `cancelada` son terminales.

En el corte hay 0 comisiones. El funnel llega, en datos de laboratorio, hasta un lead `cerrado` y un lead `apartado`, sin liquidación.

## 3. Análisis por capas

### Inputs

- Impacto de fuente (`fuentes_lead`) y, cuando exista, presupuesto de `campanas`.
- Declaraciones de presupuesto, plazo, forma de pago y tipología en `perfiles_inversion` y, en el almacén conversacional, en `prospectos`.
- Disponibilidad real: `unidades.estatus = disponible` (204 filas).

### Outputs

| Salida | Tabla | Filas en el corte |
| --- | --- | ---: |
| Cambio de etapa | `leads.estado` | 15 |
| Cita | `citas` | 2 |
| Historial de unidad | `unidad_historial` | 605 |
| Asignación de inventario comercial | `matches` | 0 |
| Registro financiero | `comisiones` | 0 |

`unidad_historial` hoy registra la carga del inventario (una fila por unidad en el corte), no todavía una cadena de apartados originada por matches.

### Control de temperatura

La temperatura no sustituye al estado. Convive con él.

| Temperatura | Filas | Encaminamiento que el esquema ya permite | Encaminamiento aún sin motor |
| --- | ---: | --- | --- |
| Frío | 3 | Consulta de inactividad en `v_leads_frios` (más de 48 h sin contacto y estado distinto de apartado, cerrado o descartado). Campo `proximo_seguimiento_at` en lead y prospecto. | Workflow que inserte seguimientos de nutrición. |
| Tibio | 6 | Elegible, por regla de negocio de este mapa, a match cuando el perfil está completo. | Inserción automática en `matches`. |
| Caliente | 6 | Misma elegibilidad, con prioridad de aviso al asesor. | La alerta de correo actual no lee esta columna. |

`public.clasificar_lead(presupuesto, temperatura, forma_pago)` traduce temperatura a clase, no al revés:

- Clase `A` si presupuesto ≥ 6 000 000, temperatura `caliente` y forma de pago presente.
- Clase `B` si presupuesto ≥ 4 000 000 o temperatura `tibio`.
- Clase `C` en el resto.

Scoring vigente del corte: A 7, B 5, C 3. Todas las filas declaran `modelo = migracion-prospectos` y `vigente = true` (el índice `scoring_vigente_uidx` permite una sola vigente por lead).

### Consumos y recursos

- Almacenamiento transaccional de estados, perfiles y scoring: operando.
- Motor de reglas de match y comisión: instalado, sin filas que lo ejerciten en `matches` y `comisiones`.
- Tiempo de asesores: la asignación es texto libre en `asignado_a` (lead y prospecto). No hay catálogo de asesores ni cola medible.

## 4. Contrato de datos

Cadena referencial de la monetización:

```text
fuentes_lead 1—* campanas
fuentes_lead 1—* leads *—1 campanas
leads 1—1 perfiles_inversion
leads 1—* scoring (una vigente)
leads 1—* matches *—1 unidades
matches 1—* comisiones *—1 unidades
```

`comisiones.unidad_id` es nullable a propósito, para backfill desde `matches.unidad_id`.

## 5. Evidencia

- Enums `lead_estado`, `lead_temperatura`, `clase_lead`, `match_estado`, `comision_estado`, `objetivo_inversion`, `fuente_familia`.
- Comentario de `comisiones`: comisión potencial, devengada o pagada de un match.
- Comentario de `campanas`: campaña de prospección. Tabla vacía.

## 6. Criterio de producción

Un peso de comisión es auditable cuando existe una fila `comisiones` cuyo `match_id` apunta a un match de un lead con `fuente_id`, y ese lead tiene interacciones que explican el paso de `nuevo` a `cerrado`. Con `campanas`, `matches` y `comisiones` en cero, el ciclo de conversión está dibujado y todavía no recorre la última milla.
