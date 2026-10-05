# ERD comercial — fuente de verdad

Versión aplicada en el proyecto Supabase `palm-lab-practica`. El SQL está en `supabase/migrations/20261005023000_crm_erd.sql`.

`public.inventario` (605 unidades) y `public.prospectos` (15 personas) siguen en su sitio. Este modelo los copia, los enlaza y se mantiene sincronizado. EasyBroker y el laboratorio de Meta no entran aquí: son otras fuentes, todavía no el inventario de torres.

## Mapa

```text
desarrollos
   └── torres
         └── unidades ──── unidad_historial
                │
                └── matches ──── comisiones
                      ▲
leads ────────────────┘
   ├── perfiles_inversion
   ├── scoring            (una clase A/B/C vigente)
   └── interacciones
fuentes_lead ── campanas ── leads
```

La tabla de campañas se llama `campanas`, sin acento, para no tener que citar el identificador en cada consulta.

## Reglas que viven en la base

Estas corren por trigger. Un agente no puede saltárselas, tampoco `service_role`.

1. Una unidad que no está `disponible` no admite un match `propuesto`, `ofrecido` ni `aceptado`. Eso incluye `vendido`, `apartado` y `reservado`.
2. Aceptar un match aparta la unidad. Solo puede haber un match `aceptado` por unidad.
3. Si la unidad deja de estar disponible, los matches `propuesto` y `ofrecido` se cancelan solos. El aceptado se conserva como el trato.
4. No se libera una unidad a `disponible` mientras tenga un match aceptado.
5. Una unidad `vendida` no cambia de estatus si la transacción no trae `crm.reapertura_motivo`.
6. Con `lista_vigente = false` no se guarda `precio_ofrecido`. Hoy las 605 unidades están así: ningún precio se cotiza.
7. Un mensaje `aprobado` o `enviado` que contiene un precio se bloquea si la lista no está vigente, y solo lo puede aprobar el agente comercial. La lista negra de canales de `borradores` también aplica a `interacciones`.
8. La comisión `devengada` exige unidad `reservada` o `vendida`. La `pagada` exige `vendida`. Una pagada o cancelada no se reabre.
9. El teléfono se normaliza a dígitos y es único. Un alta repetida falla; no se fusiona en silencio.
10. `unidad_historial` es append-only. `service_role` no tiene `INSERT`, `UPDATE` ni `DELETE`. Lo escribe el trigger.

Cuando un trigger aparta la unidad, cancela matches abiertos o escribe el historial, esa escritura la hace la base. No depende de que el agente tenga permiso sobre la tabla afectada.

`public.clasificar_lead(presupuesto, temperatura, forma_pago)` es la regla A/B/C para leads nuevos:

- A: presupuesto ≥ 6 M, temperatura caliente y forma de pago informada.
- B: presupuesto ≥ 4 M, o temperatura tibia.
- C: el resto.

Los 15 prospectos actuales conservan su clase previa con modelo `migracion-prospectos`. No se recalcularon. La clase del formulario de prueba (`A_Inversionista`, `B_Tecnologia_IA`, `C_Patrimonial`) es otra taxonomía y no entra en este scoring.

## Campos

Los identificadores son `uuid`. El dinero es `numeric`. Las fechas de auditoría son `timestamptz`.

Cada tabla operativa lleva `actor`, `created_at` y `updated_at`. Donde un agente puede reintentar un alta hay `clave_idempotencia`. Donde el registro nace en otro sistema hay `id_externo`.

### desarrollos

`nombre`, `slug`, `ciudad`, `municipio`, `estado`, `pais`, `estatus` (`planeacion`, `preventa`, `obra`, `entrega`, `cerrado`), `moneda`.

### torres

`desarrollo_id`, `clave`, `nombre`, `niveles`. Único `(desarrollo_id, clave)`. Palm Diamante queda con `I-A`, `I-B`, `II-A`, `II-B`, `III-A`, `III-B`.

### unidades

`torre_id`, `inventario_id` (enlace a la lista oficial), `clave`, `numero`, `modelo`, `tipologia`, `piso`, `m2`, `recamaras`, `banos`, `estacionamientos`, `precio_lista`, `precio_m2` (generado), `moneda`, `estatus` (`disponible`, `apartado`, `reservado`, `vendido`), `lista_vigente`, `fecha_lista`, `codigo_vendedor`, `caracteristicas`.

Único: `clave`, `(torre_id, numero)`, `inventario_id`.

La vista `v_unidades_ofertables` solo muestra disponibles. Si la lista no está vigente, `precio_publicable` sale nulo.

### unidad_historial

`unidad_id`, `campo`, `valor_anterior`, `valor_nuevo`, `motivo`, `actor`, `created_at`. Se llena al alta y cuando cambian precio, estatus o vigencia.

### fuentes_lead y campanas

Fuentes sembradas: facebook e instagram (`meta`), linkedin, google y portal (`web`), referido, whatsapp, formulario, easybroker, otro.

`campanas`: `fuente_id`, `nombre`, `id_externo`, `estado` (`borrador`, `activa`, `pausada`, `cerrada`), `presupuesto`, `inicia_en`, `termina_en`.

### leads

`prospecto_id`, `tipo` (`persona`, `empresa`), `nombre`, `empresa`, `telefono`, `telefono_normalizado`, `email`, `estado` (el mismo pipeline que `prospectos`), `temperatura` (`caliente`, `tibio`, `frio`), `fuente_id`, `campana_id`, `origen_detalle`, `id_externo`, `horario_contacto`, `unidad_interes_clave`, `sinprecio_pendiente`, `consentimiento_privacidad`, `asignado_a`, `notas`, `ultimo_msg_cliente_at`, `ultimo_msg_asesor_at`, `proximo_seguimiento_at`.

Único: teléfono normalizado, y `(fuente_id, id_externo)` cuando hay id externo.

`buscar_lead_por_telefono` devuelve id y estado. Inventario no puede llamarla.

### perfiles_inversion

Uno por lead. `presupuesto_objetivo`, `presupuesto_min`, `presupuesto_max`, `forma_pago`, `horizonte_anios`, `yield_minimo`, `objetivo` (`uso_propio`, `vacacional`, `inversion`, `plusvalia`, `renta`, `balanceado`), `tipologia`, `plazo`.

### scoring

`lead_id`, `clase` (`A`, `B`, `C`), `vigente`, `variables` (json con lo que justifica la clase), `modelo`. Solo una fila vigente por lead. Al insertar otra vigente, la anterior deja de serlo.

### matches

`lead_id`, `unidad_id`, `estado` (`propuesto`, `ofrecido`, `aceptado`, `rechazado`, `vencido`, `cancelado`), `score` 0–100, `explicacion`, `variables`, `precio_ofrecido`, `motivo`.

`ofrecido` y `aceptado` exigen una explicación de al menos 10 caracteres. No puede haber dos matches abiertos del mismo lead y la misma unidad.

### interacciones

`lead_id`, `unidad_id`, `campana_id`, `canal` (`whatsapp`, `email`, `llamada`, `visita`, `linkedin`, `meta`, `sistema`, `otro`), `direccion` (`entrante`, `saliente`), `estado` (`borrador`, `aprobado`, `enviado`, `recibido`, `fallido`, `cancelado`), `contenido`, `id_externo`, `ocurrido_at`.

### comisiones

`match_id`, `beneficiario`, `estado` (`potencial`, `devengada`, `pagada`, `cancelada`), `porcentaje`, `base_monto`, `monto` (generado), `pagada_at`.

## Cómo entra un agente

Al empezar la transacción:

```sql
select public.asumir_agente('matching');
```

Los nombres son `inventario`, `matching`, `prospecting`, `followup`, `comercial`. Sin esa llamada, `service_role` puede leer (en Supabase se salta RLS) pero cualquier escritura falla.

La matriz está en `agente_permisos`. Cambiarla es una migración: ningún agente puede editarla.

| Tabla | Inventario | Matching | Prospecting | Follow-up | Comercial |
|---|---|---|---|---|---|
| desarrollos, torres | leer, crear, modificar | leer | leer | leer | leer |
| unidades | leer, crear, modificar | leer | leer | leer | leer, modificar estatus y vendedor |
| unidad_historial | leer | leer | — | — | leer |
| fuentes_lead | — | leer | leer, crear | leer | leer, crear |
| campanas | — | leer | leer, crear, modificar | leer | leer |
| leads | — | leer | leer, crear, modificar | leer, modificar seguimiento | leer, modificar asignación y estado |
| perfiles_inversion | — | leer | leer, crear, modificar | leer | leer, modificar |
| scoring | — | leer | leer, crear, modificar | leer | leer, crear, modificar |
| matches | — | leer, crear, modificar | — | leer | leer, modificar |
| interacciones | — | leer | crear entrada o nota de sistema | leer, crear, modificar | leer, crear, modificar |
| comisiones | — | leer | — | — | leer, crear, modificar |

Límites de columnas, además de la matriz:

- Comercial no toca precio, metros ni clave de la unidad.
- Follow-up no cambia nombre, teléfono, correo, fuente ni asignación.
- Prospecting no asigna al asesor.
- Comercial no reescribe identidad ni fuente.
- Un mensaje con precio lo aprueba comercial.

El rol `crm_agent` ya tiene RLS para cuando la conexión deje de usar `service_role`. Hoy `service_role` sigue pudiendo leer todo. Las escrituras no.

## Qué no se conecta todavía

LinkedIn, Meta y WhatsApp no tienen conector. Sus leads, cuando existan, entran por `fuentes_lead` → `leads` → `scoring` → `matches` → `interacciones`. WhatsApp es un `canal`, no una tabla.

`public.citas`, `public.seguimientos` y `public.borradores` siguen operando como hasta ahora. El modelo nuevo no los borra.
