# Mapa 11 — Métricas que monetizan

| Campo | Valor |
| --- | --- |
| Identificador | MAPA-11 |
| Estado | Parcial |
| Corte | 2026-10-05 |
| Objetos ancla | `fuentes_lead`, `campanas`, `leads`, `interacciones`, `matches`, `citas`, `comisiones`, vistas `v_*` |

## 1. Propósito operativo

La métrica que manda el presupuesto es la comisión por fuente: suma de `comisiones.monto` atribuida al `fuentes_lead` del lead, puesta al lado del `campanas.presupuesto` de esa fuente. El resto de indicadores explica por qué esa razón sube o baja. En el corte la métrica reina no se puede calcular: el numerador y el costo de campaña están en cero. Sí se pueden calcular indicadores de laboratorio sobre los 15 leads y el inventario.

## 2. Conexión sistémica

### Entrada

| Fuente de la métrica | Filas útiles hoy | Qué falta para monetizar |
| --- | ---: | --- |
| `fuentes_lead` | 10 catálogos | Asignación efectiva en los leads de pauta. |
| `campanas` | 0 | Presupuesto y fechas. |
| `leads` | 15, con estado y temperatura | `campana_id` aprovechable. |
| `interacciones` | 0 | Tiempos de respuesta. |
| `matches` | 0 | Tasa de propuesta y de aceptación. |
| `citas` | 2, colgadas de prospecto | Cruce con lead y con fuente. |
| `comisiones` | 0 | Monto, estado y match. |
| `scoring` | 15, modelo de migración | Modelo vivo para confiar en la clase. |

### Tránsito

Definiciones que ya se pueden implementar como consulta, usando solo columnas existentes.

| Indicador | Definición auditable | ¿Calculable hoy? |
| --- | --- | --- |
| Comisión por fuente | `sum(comisiones.monto)` agrupado por `fuentes_lead.slug`, uniendo comisión → match → lead → fuente. Estados incluidos deben declararse (`pagada` para caja, `devengada`+`pagada` para devengo). | No. Cero comisiones. |
| Costo por fuente | `sum(campanas.presupuesto)` por fuente, campañas `activa` o `cerrada`. | No. Cero campañas. |
| Comisión / costo | Razón de las dos anteriores, misma ventana de fechas. | No. |
| Mix de temperatura | Conteo de `leads.temperatura`. | Sí. Caliente 6, tibio 6, frío 3. |
| Mix de etapa | Conteo de `leads.estado`. | Sí. Ver mapa 02. |
| Clase | Conteo de `scoring` con `vigente`. | Sí. A 7, B 5, C 3. Dato de migración. |
| Prospectos por día, canal, perfil y temperatura | `v_prospectos_nuevos`. | Sí, sobre los 15. |
| Fríos sin contacto | `v_leads_frios`: estado fuera de apartado/cerrado/descartado y último contacto (o alta) anterior a 48 horas. | Sí, como vista. El nombre dice leads y la vista lee `prospectos`. |
| Seguimientos vencidos | `v_seguimientos_vencidos`: `pendiente` con fecha pasada, o estado `vencido`. | La vista existe. En el corte hay 2 pendientes; el vencimiento depende de `fecha_seguimiento` frente a `now()`. |
| Citas de la semana | `v_citas_semana`, semana lunes a lunes en `America/Mexico_City`, estados `programada` y `confirmada`. | Sí. 2 citas programadas en tabla; entran en la vista si caen en la semana del corte. |
| Tiempo de primera respuesta | `ultimo_msg_asesor_at - ultimo_msg_cliente_at` por lead, o diferencia entre la primera interacción entrante y la primera saliente. | Columnas listas. Interacciones en cero: la medición fina no tiene hechos. |
| Oferta disponible | `v_apartado_por_tipologia` y `v_unidades_ofertables`. | Sí. 204 disponibles, precio publicable nulo. |
| Cola de aprobación | `v_borradores_pendientes`. | Sí. 1 pendiente. |
| Precios retenidos | `v_sinprecio_pendientes`. | Vista lista. Depende de `sinprecio_pendiente`. |

No hay vista materializada ni job que congele un tablero. El tablero ejecutivo es una lectura de estas definiciones. Quien lo publique usa `service_role` o un rol futuro con RLS; `v_leads_temperatura` hoy solo está otorgada a `service_role`.

### Salida

Decisiones de presupuesto por fuente, cuando existan campañas y comisiones. Mientras tanto, el tablero honesto del laboratorio muestra inventario, temperatura de la semilla, cola de borradores y citas, y declara en cero la comisión por fuente.

## 3. Análisis por capas

### Inputs

- Marcas de tiempo: `created_at`, `ultimo_msg_*`, `ocurrido_at`, `aprobado_at`, `enviado_at`, `pagada_at`, `fecha_cita`, `fecha_seguimiento`.
- Estados de lead, match, cita, seguimiento, borrador y comisión.
- Montos: `comisiones.monto` (generado), `campanas.presupuesto`, `unidades.precio_lista` solo si `lista_vigente`.
- Canal de origen: `fuentes_lead.slug`, `leads.origen_detalle`, `prospectos.origen`.

### Outputs

- Conteos y sumas con la definición de la tabla anterior.
- Reportes de seguimientos vencidos y de borradores pendientes.
- Ingresos por canal: vacíos hasta la primera comisión.

### Control de temperatura

El mix frío/tibio/caliente mide si la nutrición mueve leads. La nutrición automática no existe todavía, así que el mix del corte es una foto de la semilla (6 / 6 / 3), no un resultado de campaña. `v_leads_frios` añade el criterio operativo de 48 horas. Cuando haya interacciones, el mismo mix se parte por `fuente_id`.

### Consumos y recursos

- Consultas agregadas sobre tablas pequeñas en el corte (decenas de leads, 605 unidades).
- Sin procesador de reportes periódicos dentro de la base (`pg_cron` ausente).
- Zona horaria de negocio fija en las vistas diarias: `America/Mexico_City`.

## 4. Contrato de datos

Fórmula de la métrica reina, para cuando haya filas:

```text
comision_por_fuente(slug, desde, hasta) =
  sum(c.monto)
  donde c.estado in (conjunto declarado)
    y c.created_at en [desde, hasta)
    y c.match_id → matches.lead_id → leads.fuente_id → fuentes_lead.slug
```

El conjunto de estados se documenta en el tablero. Mezclar `potencial` con `pagada` infla la cifra. La definición de caja usa solo `pagada`.

`comisiones.monto` ya es `round(base_monto * porcentaje, 2)`. El reporte no recalcula el porcentaje por su cuenta.

## 5. Evidencia

- Vistas creadas en la migración `vistas_reporte_diario` y extendidas por el ERD (`v_leads_temperatura`, `v_unidades_ofertables`).
- Conteos del corte en el índice.
- `campanas` y `comisiones` en cero.

## 6. Criterio de producción

El tablero de producción publica comisión por fuente solo con filas de `comisiones` unidas a `fuentes_lead`, excluye `leads_prueba_formulario` y `lab_meta_demo`, y muestra la ventana y el conjunto de estados en el encabezado. Hasta que exista la primera comisión, el indicador se presenta vacío y el presupuesto de pauta no se optimiza contra una razón imaginaria.
