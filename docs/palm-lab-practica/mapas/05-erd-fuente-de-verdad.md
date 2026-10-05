# Mapa 05 — ERD fuente de verdad

| Campo | Valor |
| --- | --- |
| Identificador | MAPA-05 |
| Estado | Operativo |
| Corte | 2026-10-05 |
| Objetos ancla | migraciones `crm_erd_fuente_verdad_*`, tabla pivote `leads` |

## 1. Propósito operativo

El ERD ordena cuatro dominios alrededor de `leads`: catálogo inmobiliario, atribución de marketing, inteligencia comercial y operación. La migración que lo instaló es la serie `crm_erd_fuente_verdad_tablas`, `_funciones_a`, `_reglas`, `_sync_y_busqueda`, `_semilla` y `_rls` (2026-10-05), más `crm_erd_permiso_service_role`, `crm_erd_buscar_lead_columnas` y el endurecimiento `crm_hardening_upsert_webhook_vista_comision`.

## 2. Conexión sistémica

### Entrada

| Dominio | Camino | Cardinalidad observada |
| --- | --- | --- |
| Inventario canónico | `desarrollos` → `torres` → `unidades` | 1 desarrollo, 6 torres, 605 unidades |
| Inventario legado | `inventario` sincronizado con `unidades` por `inventario_id` | 605 y 605, claves únicas en ambos |
| Catálogo externo | `easybroker_propiedades` | 365, sin llave foránea hacia `unidades` |
| Atribución | `fuentes_lead` → `campanas` → `leads` | 10 fuentes, 0 campañas |
| Conversación | `prospectos` → `leads.prospecto_id` | 15 y 15 |

`desarrollos` del corte: slug `palm-diamante`, estatus `preventa`, ciudad Acapulco, moneda `MXN`.

Torres de `inventario` admiten solo `I-A`, `I-B`, `II-A`, `II-B`, `III-A`, `III-B`. La clave de unidad es generada `torre || '-' || unidad`.

### Tránsito

`leads` es la pivote. De ella salen:

| Rama | Tabla | Relación |
| --- | --- | --- |
| Inteligencia | `perfiles_inversion` | 1:1 por `lead_id` |
| Inteligencia | `scoring` | 1:N, una fila `vigente` |
| Inteligencia | `matches` | N:M lógico lead–unidad, con unicidad de abiertos |
| Operación de canal | `interacciones` | 1:N, `lead_id` obligatorio |
| Atribución | `fuente_id`, `campana_id` | opcionales |

La operación diaria anterior al ERD sigue colgada de `prospectos`, no de `leads`:

| Tabla | Llave | Nota de diseño |
| --- | --- | --- |
| `seguimientos` | `prospecto_id` | Tipos `llamada`, `whatsapp`, `email`, `visita`, `otro`. |
| `citas` | `prospecto_id` | Estados `programada`, `confirmada`, `cancelada`, `completada`. |
| `borradores` | `prospecto_id` | Aprobación humana. |

Esa doble ancla es deliberada en el laboratorio y es la deuda que el mapa 06 administra: el objeto de negocio es el lead; la cola de trabajo del asesor sigue leyendo al prospecto.

### Salida

- `unidad_historial`: bitácora append-only de precio, estatus y vigencia. Los agentes no tienen `INSERT` directo. La escribe `private.unidad_historial_escribir` después de cada alta o cambio de `unidades`.
- `comisiones`: liquidación. `match_id` obligatorio, `unidad_id` opcional de apoyo.

## 3. Análisis por capas

### Inputs

- DDL de las migraciones citadas.
- Semilla `crm_erd_fuente_verdad_semilla`, que explica el scoring `migracion-prospectos` y el puente de los 15 prospectos.
- Sync bidireccional `inventario` ↔ `unidades` por triggers `sync_inventario_hacia_unidad` y `sync_unidad_hacia_inventario`.

### Outputs

- Restricciones de llave foránea en el grafo descrito.
- Enums de estatus de desarrollo, unidad, lead, match, comisión, canal e interacción.
- Catálogos normalizados: fuentes por `slug`, desarrollo por `slug`, unidad por `clave`.

### Control de temperatura

La temperatura no tiene tabla propia. Vive en `leads.temperatura` (`lead_temperatura`) y en `prospectos.temperatura` (check de texto con los mismos tres valores). `v_leads_temperatura` es la lectura transversal: lead, prospecto, fuente, campaña y marcas de seguimiento. Grant de esa vista: `service_role`. El perfil de inversión no guarda temperatura; guarda presupuesto y objetivo, que `clasificar_lead` combina con la temperatura para emitir la clase.

### Consumos y recursos

- Almacenamiento Postgres del proyecto, hoy dominado por 605 unidades, su historial y 365 documentos EasyBroker (JSON `raw`, `images`, `features`, `operations`).
- Índices únicos por UUID de negocio y por claves naturales (`telefono_normalizado`, `clave`, `public_id`).
- Integridad referencial evaluada en cada escritura. No hay borrado en cascada documentado como política de negocio: los permisos de `puede_borrar` están en falso para todos los agentes en la matriz observada.

## 4. Contrato de datos

Enums instalados y usados por el ERD:

| Enum | Valores |
| --- | --- |
| `desarrollo_estatus` | `planeacion`, `preventa`, `obra`, `entrega`, `cerrado` |
| `unidad_estatus` | `disponible`, `apartado`, `reservado`, `vendido` |
| `lead_tipo` | `persona`, `empresa` |
| `lead_estado` | `nuevo`, `contactado`, `calificado`, `cita`, `apartado`, `cerrado`, `descartado` |
| `lead_temperatura` | `caliente`, `tibio`, `frio` |
| `clase_lead` | `A`, `B`, `C` |
| `objetivo_inversion` | `uso_propio`, `vacacional`, `inversion`, `plusvalia`, `renta`, `balanceado` |
| `match_estado` | `propuesto`, `ofrecido`, `aceptado`, `rechazado`, `vencido`, `cancelado` |
| `comision_estado` | `potencial`, `devengada`, `pagada`, `cancelada` |
| `crm_agente` | `inventario`, `matching`, `prospecting`, `followup`, `comercial` |

`precio_m2` en `unidades` es generado: `round(precio_lista / m2, 2)` cuando ambos datos permiten la división.

## 5. Evidencia

- 22 tablas en `public`, todas con `relrowsecurity = true`.
- Vistas de lectura: `v_leads_temperatura`, `v_leads_frios`, `v_unidades_ofertables`, `v_apartado_por_tipologia`, `v_borradores_pendientes`, `v_citas_semana`, `v_seguimientos_vencidos`, `v_sinprecio_pendientes`, `v_prospectos_nuevos`, `v_alertas_lista_negra`. Todas con `security_invoker = true`.
- Divergencia lead/prospecto en temperatura y estado: 0 sobre 15 pares.

## 6. Criterio de producción

El ERD se mantiene como fuente de verdad si toda escritura nueva de negocio entra por estas tablas y si las colas de asesor (`citas`, `seguimientos`, `borradores`) ganan una llave hacia `leads` o una vista única que impida operar un prospecto cuyo lead divergió. El esquema relacional ya está en condiciones de recibir ese tráfico.
