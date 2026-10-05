# Paquete operativo v1 — palm-lab-practica

Versión cerrada contra el catálogo real del proyecto `palm-lab-practica` (`plgfhtvzxhrdfmrlknru`). Cada marca `-- VERIFICAR` del borrador quedó resuelta en este archivo. La primera pasada del bloque 1 se ejecutó el 2026-10-05 con un rol que salta RLS. No se aplicó ninguna policy, ningún `comment on`, ninguna purga ni ningún cron.

| Convención | Decisión verificada |
| --- | --- |
| Tiempo | Las columnas de negocio son `timestamptz` (instante UTC). Las vistas diarias convierten a `America/Mexico_City` solo para lectura. |
| Severidad | P0 bloquea producción. P1 exige acción en menos de 24 h. P2 es revisión semanal. |
| Ejecución | Estas consultas se corren con `service_role` o con un rol de lectura de auditoría. `anon` no tiene `SELECT` sobre el CRM. |
| Teléfono | `prospectos.telefono` está en E.164 (`+52` y 10 dígitos) en las 15 filas. `leads.telefono_normalizado` lo calcula `private.normalizar_telefono`: solo dígitos. Las 15 filas miden 12 caracteres y cumplen `^52[0-9]{10}$`. El trigger pisa cualquier valor que se intente escribir en la columna normalizada. |
| Panel de asesores | No existe. Las policies de `authenticated` quedan redactadas y sin ejecutar. |

## Primera pasada del bloque 1

Cero filas significa que la regla se cumple hoy. Un cero vacío (no hay filas que la regla pueda evaluar) no cierra un P0.

| Regla | Severidad | Filas | Lectura |
| --- | --- | ---: | --- |
| 1.1 Prospectos sin lead | P0 | 0 | Cumple. |
| 1.2 Leads sin prospecto o con puente roto | P0 | 0 | Cumple. `prospecto_id` es nullable en el esquema; hoy ningún lead lo deja vacío. |
| 1.3 Sin `fuente_id` | P1 | 0 | Cumple. Las 15 filas tienen fuente. |
| 1.3 Con fuente y sin `campana_id` | P2 | 15 | Esperado. `campanas` tiene 0 filas. No es fallo de atribución primaria. |
| 1.4 Tibios o calientes sin match | P0 | 12 | Incumple. 6 tibios y 6 calientes. `matches` está vacío y `lista_vigente` es falso: el motor todavía no puede cumplir la regla. |
| 1.5 `proximo_seguimiento_at` vencido | P1 | 8 | Incumple en la agenda del prospecto (1 calificado, 3 contactados, 4 nuevos). |
| 1.5 Filas de `seguimientos` vencidas | P1 | 2 | Dos seguimientos `pendiente` con fecha pasada, o estado `vencido`. |
| 1.6 Primera respuesta mayor a 5 min | P1 | 12 | De 12 prospectos con mensaje de cliente: 1 sin respuesta de asesor y 11 con respuesta posterior a 5 minutos. 0 dentro del umbral. 3 prospectos no tienen `ultimo_msg_cliente_at`. |
| 1.7 Ventana de 24 h | P0 | 0 vacías | `interacciones` tiene 0 filas. El cero no demuestra cumplimiento: no existe columna `es_plantilla` ni valor `direccion = 'out'`. |
| 1.8 Borrador `enviado` sin `aprobado_por` | P0 | 0 | Cumple sobre las filas actuales. Hay 0 borradores `enviado` (1 pendiente y 1 aprobado). |
| 1.9 Comisión sin match, sin lead o sin fuente | P0 | 0 | Cumple de forma vacía: `comisiones` tiene 0 filas. La traza real es `match_id`, no `lead_id`. |
| 1.10 Inventario contra unidades | P1 | 0 huérfanas | 605 y 605 coinciden por `clave` y por `unidades.inventario_id`. |
| 1.11 Número verificado en Meta | P0 | Checklist | Sigue fuera de la base. |
| 1.12 Lead sin scoring vigente | P1 | 0 | Cumple. El modelo vigente de las 15 filas es `migracion-prospectos`. |

Fuentes de esos 15 leads: facebook 4, google 3, referido 3, instagram 3, portal 2.

Formato telefónico de purga sobre `prospectos.telefono ~ '^\+52[0-9]{10}$'`: 15 de 15 cumplen. Ese resultado no convierte la semilla en clientes de producción.

---

## Bloque 1. SQL de auditoría

Cada consulta devuelve filas problemáticas. Programarla exige instalar `pg_cron` o dispararla desde n8n: la extensión no está en el proyecto.

### 1.1 Prospectos sin lead (Mapa 06, P0)

`created_at` existe en `prospectos`. `leads.prospecto_id` referencia `prospectos.id`.

```sql
select p.id, p.telefono, p.nombre, p.created_at
from public.prospectos p
left join public.leads l on l.prospecto_id = p.id
where l.id is null;
```

### 1.2 Leads sin prospecto (Mapa 06, P0)

`prospecto_id` es nullable y único. La regla de producción lo trata como obligatorio aunque el tipo lo permita.

```sql
select l.id, l.telefono_normalizado, l.prospecto_id
from public.leads l
left join public.prospectos p on p.id = l.prospecto_id
where l.prospecto_id is null
   or p.id is null;
```

### 1.3 Atribución (Mapa 02, P1 y P2)

`fuente_id` y `campana_id` existen y son nullable. `created_at` existe. Exigir campaña cuando la fuente ya está puesta marcaría hoy a los 15 leads, porque no hay filas en `campanas`. La campaña queda en P2 hasta la primera campaña real.

```sql
-- P1: sin fuente
select id, telefono_normalizado, fuente_id, campana_id, estado, created_at
from public.leads
where fuente_id is null;

-- P2: fuente presente y campaña ausente
select id, telefono_normalizado, fuente_id, estado, created_at
from public.leads
where fuente_id is not null
  and campana_id is null;
```

### 1.4 Leads tibios o calientes sin match (Mapa 07, P0)

La llave es `matches.lead_id`. `temperatura` es el enum `lead_temperatura` (`caliente`, `tibio`, `frio`). Un match cancelado o rechazado no cuenta como cobertura.

```sql
select l.id, l.temperatura, l.estado
from public.leads l
where l.temperatura in ('tibio', 'caliente')
  and not exists (
    select 1
    from public.matches m
    where m.lead_id = l.id
      and m.estado in ('propuesto', 'ofrecido', 'aceptado')
  );
```

### 1.5 Seguimientos vencidos (Mapas 04 y 11, P1)

No existe el estado `perdido`. El check de `prospectos.estado` y el enum `lead_estado` usan `descartado`. `apartado` y `cerrado` salen de la cola. La agenda del prospecto y la tabla `seguimientos` se auditan por separado: la vista `v_seguimientos_vencidos` lee la tabla, no `proximo_seguimiento_at`.

```sql
select p.id, p.telefono, p.proximo_seguimiento_at, p.temperatura, p.estado
from public.prospectos p
where p.proximo_seguimiento_at is not null
  and p.proximo_seguimiento_at < now()
  and p.estado not in ('cerrado', 'descartado', 'apartado');

select s.id, s.prospecto_id, s.estado, s.fecha_seguimiento, s.tipo
from public.seguimientos s
where (s.estado = 'pendiente' and s.fecha_seguimiento < now())
   or s.estado = 'vencido';
```

### 1.6 Primera respuesta mayor a 5 minutos (Mapa 11, P1)

Las dos marcas existen en `prospectos` y en `leads`. Esta pasada mide la última pareja de mensajes, no cada turno de `interacciones` (esa tabla sigue vacía).

```sql
select p.id,
       p.telefono,
       p.ultimo_msg_cliente_at,
       p.ultimo_msg_asesor_at,
       extract(epoch from (p.ultimo_msg_asesor_at - p.ultimo_msg_cliente_at)) / 60
         as min_respuesta
from public.prospectos p
where p.ultimo_msg_cliente_at is not null
  and (
    p.ultimo_msg_asesor_at is null
    or p.ultimo_msg_asesor_at > p.ultimo_msg_cliente_at + interval '5 minutes'
  );
```

### 1.7 Ventana de 24 horas (Mapa 04, P0)

Columnas reales de `interacciones`: `direccion` (`entrante`, `saliente`), `canal`, `estado`, `contenido`, `ocurrido_at`, `created_at`, `lead_id`. No existen `tipo`, `es_plantilla` ni el literal `out`. La plantilla vive en `borradores.plantilla`. Mientras `interacciones` esté vacía, un resultado de 0 filas es vacío.

```sql
select i.id,
       i.lead_id,
       i.ocurrido_at,
       i.canal,
       i.estado,
       p.ultimo_msg_cliente_at
from public.interacciones i
join public.leads l on l.id = i.lead_id
left join public.prospectos p on p.id = l.prospecto_id
where i.direccion = 'saliente'
  and i.estado = 'enviado'
  and i.ocurrido_at >
      coalesce(p.ultimo_msg_cliente_at, l.ultimo_msg_cliente_at, '-infinity'::timestamptz)
      + interval '24 hours'
  and not exists (
    select 1
    from public.borradores b
    where b.prospecto_id = p.id
      and b.plantilla is not null
      and b.estado = 'enviado'
      and b.enviado_at is not null
  );
```

Cerrar el P0 de verdad requiere guardar en la interacción el nombre de la plantilla, o una llave al borrador. Hoy esa columna no existe.

### 1.8 Borrador enviado sin aprobador (Mapa 04, P0)

`borradores` no tiene `lead_id`. Tiene `prospecto_id`. Estados reales: `pendiente`, `aprobado`, `rechazado`, `enviado`. `aprobado_por` existe.

```sql
select b.id, b.prospecto_id, b.estado, b.created_at, b.aprobado_por, b.aprobado_at
from public.borradores b
where b.estado = 'enviado'
  and b.aprobado_por is null;
```

### 1.9 Comisión sin origen trazable (Mapa 02, P0)

`comisiones` no tiene `lead_id` ni `monto` escribible. La traza es `comisiones.match_id` → `matches.lead_id` → `leads.fuente_id`. `monto` es `round(base_monto * porcentaje, 2)`. `unidad_id` es opcional.

```sql
select c.id, c.match_id, c.unidad_id, c.estado, c.monto, l.id as lead_id, l.fuente_id
from public.comisiones c
left join public.matches m on m.id = c.match_id
left join public.leads l on l.id = m.lead_id
where m.id is null
   or l.id is null
   or l.fuente_id is null;
```

### 1.10 Conciliación inventario y unidades (Mapa 07, P1)

Las dos tablas tienen `clave`. `unidades.inventario_id` referencia `inventario.id` y es único. Un `full outer join` agrupado con `having count(*) > 1` no detecta huérfanos: la clave ya es única, así que cada par cuenta 1. La consulta que sí detecta el desfase es esta.

```sql
select
  (select count(*) from public.inventario) as inventario,
  (select count(*) from public.unidades) as unidades,
  (select count(*)
     from public.inventario i
     join public.unidades u on u.clave = i.clave) as match_por_clave,
  (select count(*)
     from public.inventario i
     left join public.unidades u on u.clave = i.clave
    where u.id is null) as inventario_sin_unidad,
  (select count(*)
     from public.unidades u
     left join public.inventario i on i.clave = u.clave
    where i.id is null) as unidad_sin_inventario,
  (select count(*)
     from public.unidades u
     join public.inventario i
       on i.id = u.inventario_id
      and u.clave is not distinct from i.clave) as puente_id_y_clave;
```

En el corte: 605, 605, 605, 0, 0, 605.

### 1.11 Número de WhatsApp (Mapa 01, P0)

No es SQL. En Meta Business el número 55 4018 0018 debe constar como verificado y las plantillas del bloque 4 como `approved`. Evidencia: captura, fecha y responsable. El número no está guardado en el esquema.

### 1.12 Cobertura de scoring (Mapas 07 y 11, P1)

`scoring.lead_id` referencia `leads.id`. La fila que cuenta es la vigente (`scoring_vigente_uidx`).

```sql
select count(*) filter (where s.id is null) as leads_sin_scoring_vigente,
       count(*) as total_leads
from public.leads l
left join public.scoring s
  on s.lead_id = l.id
 and s.vigente;
```

---

## Bloque 2. Policies RLS

Estado verificado: RLS activo en las 22 tablas de `public`. La consulta de tablas con RLS apagado devolvió 0 filas. `anon` conserva un solo privilegio de tabla, `INSERT` en `leads_prueba_formulario`. `service_role` tiene `BYPASSRLS`. `crm_agent` ya tiene policies ligadas a `agente_permisos`.

Estas policies de `authenticated` no se ejecutaron. `asignado_a` es texto libre (nombre del asesor), no el UUID de `auth.uid()`. Crearlas ahora no asignaría leads a personas reales y, el día que `authenticated` reciba `GRANT SELECT`, abriría filas por una igualdad que nadie cumple o, peor, por un texto que alguien copie dentro de `auth.uid()::text`.

Tampoco se ejecutó el `comment on table public.leads`: reemplazaría el comentario operativo que ya describe al lead.

### 2.1 Confirmar RLS

```sql
select schemaname, tablename
from pg_tables
where schemaname = 'public'
  and rowsecurity = false;
```

Resultado del corte: 0 filas.

### 2.2 anon

Se mantiene sin policies de lectura ni de escritura sobre el CRM. La única excepción sigue siendo el insert del formulario de práctica, con `consentimiento_privacidad = true`.

### 2.3 authenticated, cuando exista el panel

Prerrequisito de esquema, antes de cualquier `create policy`:

1. `asignado_a uuid` referenciando `auth.users`, o una tabla `asesores(user_id, nombre)`.
2. `GRANT SELECT, UPDATE` explícito sobre las tablas que el panel lee.
3. Revocar antes los `GRANT` amplios que `authenticated` ya tiene sobre vistas con teléfono (`v_borradores_pendientes`, `v_citas_semana`, `v_leads_frios` y las demás de reporte). Esas vistas son `security_invoker = true`; hoy devuelven vacío porque la tabla base no tiene policy. El grant ya está concedido.

Borrador correcto para ese día, todavía sin ejecutar:

```sql
create policy asesor_lee_sus_leads
on public.leads
for select
to authenticated
using (asignado_a = (select auth.uid()));

create policy asesor_actualiza_sus_leads
on public.leads
for update
to authenticated
using (asignado_a = (select auth.uid()))
with check (asignado_a = (select auth.uid()));

create policy asesor_lee_sus_prospectos
on public.prospectos
for select
to authenticated
using (
  exists (
    select 1
    from public.leads l
    where l.prospecto_id = prospectos.id
      and l.asignado_a = (select auth.uid())
  )
);
```

`interacciones`, `scoring` y `matches` sí tienen `lead_id`. `borradores`, `citas` y `seguimientos` tienen `prospecto_id` y no tienen `lead_id`. El patrón de esas tres pasa por el prospecto:

```sql
create policy asesor_lee_borradores_de_sus_prospectos
on public.borradores
for select
to authenticated
using (
  exists (
    select 1
    from public.leads l
    where l.prospecto_id = borradores.prospecto_id
      and l.asignado_a = (select auth.uid())
  )
);
```

La misma existencia aplica a `citas` y `seguimientos`.

### 2.4 agente_permisos

La tabla real no tiene `agente_id` ni `permiso`. Su llave es `(agente, tabla)` con `agente` en el enum `crm_agente` (`inventario`, `matching`, `prospecting`, `followup`, `comercial`) y booleanos `puede_leer`, `puede_crear`, `puede_modificar`, `puede_borrar`. El filtro ya está en `private.crm_permiso` y en las policies del rol `crm_agent`. Añadir una policy de `authenticated` contra columnas que no existen fallaría al ejecutarla.

Aprobar un borrador sigue siendo una escritura `service_role` o un futuro permiso del agente `comercial` sobre la tabla que corresponda. `borradores` hoy no entra en `agente_permisos`: RLS activo y cero policies, así que solo `service_role` la escribe.

### 2.5 comisiones

No hay `comisiones.lead_id`. La lectura del asesor, el día del panel, recorre el match:

```sql
create policy asesor_lee_sus_comisiones
on public.comisiones
for select
to authenticated
using (
  exists (
    select 1
    from public.matches m
    join public.leads l on l.id = m.lead_id
    where m.id = comisiones.match_id
      and l.asignado_a = (select auth.uid())
  )
);
```

Sin `INSERT` ni `UPDATE` para `authenticated`. Crear y mover una comisión queda en el agente `comercial` vía `crm_agent`, que ya puede crear y modificar `comisiones`, sujeto a `private.comision_reglas`.

### 2.6 service_role

Sin policies nuevas. Webhook, n8n y Edge Functions usan esa llave solo desde secretos.

---

## Bloque 3. Contratos de datos

El borrador proponía tipos y checks distintos a los que ya están migrados. El contrato vigente es el de la base. Cambiar `estado` a un `text` con valor `perdido`, o `comisiones.lead_id`, sería otra migración, no una aclaración.

### 3.1 leads

| Columna | Tipo real | Nulo | Restricción real |
| --- | --- | --- | --- |
| `id` | uuid | no | PK, `gen_random_uuid()` |
| `prospecto_id` | uuid | sí | Único. FK → `prospectos.id`. La regla de negocio lo exige; el tipo todavía lo permite. |
| `telefono` | text | no | Texto de entrada. El trigger lo normaliza aparte. |
| `telefono_normalizado` | text | no | Único. Solo dígitos, longitud 10–15. No es E.164. |
| `fuente_id` | uuid | sí | FK → `fuentes_lead.id` |
| `campana_id` | uuid | sí | FK → `campanas.id` |
| `estado` | `lead_estado` | no | `nuevo`, `contactado`, `calificado`, `cita`, `apartado`, `cerrado`, `descartado`. No existe `perdido`. |
| `temperatura` | `lead_temperatura` | sí | `caliente`, `tibio`, `frio` |
| `asignado_a` | text | sí | Texto libre. No es `auth.uid()`. |
| `created_at`, `updated_at` | timestamptz | no | `now()` |

También existen, y el contrato de escritura no debe ignorarlas: `tipo` (`persona`/`empresa`), `nombre`, `empresa`, `email`, `origen_detalle`, `id_externo`, `horario_contacto`, `unidad_interes_clave`, `sinprecio_pendiente`, `consentimiento_privacidad`, `notas`, marcas de mensaje, `proximo_seguimiento_at`, `actor`, `clave_idempotencia`.

Regla de deduplicación: quien inserta manda el teléfono en `telefono`. `private.crm_normaliza_lead` escribe `telefono_normalizado`. Un segundo lead con los mismos dígitos choca con `leads_telefono_uidx`.

### 3.2 prospectos

| Columna | Tipo real | Nulo | Restricción real |
| --- | --- | --- | --- |
| `id` | uuid | no | PK |
| `nombre` | text | sí | |
| `telefono` | text | no | Único. En el corte, E.164 mexicano. |
| `origen` | text | sí | No es `NOT NULL`. |
| `presupuesto` | numeric | sí | No es text. |
| `forma_pago`, `plazo`, `tipologia` | text | sí | |
| `temperatura` | text | sí | Check `caliente`, `tibio`, `frio` |
| `estado` | text | no | Default `nuevo`. Mismos literales que el enum del lead, incluido `apartado`. No existe `perdido`. |
| `unidad_interes` | text | sí | FK → `inventario.clave` |
| `ultimo_msg_cliente_at`, `ultimo_msg_asesor_at`, `proximo_seguimiento_at`, `cita_at` | timestamptz | sí | |
| `created_at`, `updated_at` | timestamptz | no | `now()` |

También: `perfil` (`A`/`B`/`C`, default `A`), `notas`, `sinprecio_pendiente`, `asignado_a`, `horario_contacto`, `proposito`.

Regla de espejo: 1 prospecto activo de canal = 1 lead, verificada por las consultas 1.1 y 1.2. La temperatura de negocio se escribe en `leads` y se copia a `prospectos` en la misma transacción. No hay trigger que lo haga solo.

### 3.3 matches

| Columna | Tipo real | Nulo | Restricción real |
| --- | --- | --- | --- |
| `id` | uuid | no | PK |
| `lead_id` | uuid | no | FK → `leads.id` |
| `unidad_id` | uuid | no | FK → `unidades.id` |
| `score` | numeric | sí | 0–100 |
| `explicacion` | text | sí | El borrador la llamaba `razon`. El nombre real es `explicacion`. |
| `estado` | `match_estado` | no | `propuesto`, `ofrecido`, `aceptado`, `rechazado`, `vencido`, `cancelado`. No existen `enviado`, `descartado` ni `apartado`. |
| `precio_ofrecido` | numeric | sí | Rechazado por `private.match_reglas` si `lista_vigente` es falso. |
| `variables` | jsonb | no | Default `{}` |
| `created_at`, `updated_at` | timestamptz | no | |

Reglas ya forzadas por trigger, no por un tope de tres filas:

- Estado `propuesto`, `ofrecido` o `aceptado` exige unidad `disponible`.
- `aceptado` aparta la unidad.
- Un solo match abierto por par lead–unidad.
- Un solo `aceptado` por unidad.

El máximo de 3 matches activos por lead es regla de aplicación. La base todavía no lo restringe.

### 3.4 comisiones

| Columna | Tipo real | Nulo | Restricción real |
| --- | --- | --- | --- |
| `id` | uuid | no | PK |
| `match_id` | uuid | no | FK → `matches.id`. No existe `lead_id`. |
| `unidad_id` | uuid | sí | FK → `unidades.id` |
| `beneficiario` | text | no | |
| `porcentaje` | numeric | no | Mayor que 0 y menor o igual a 1 |
| `base_monto` | numeric | no | ≥ 0 |
| `monto` | numeric | generado | `round(base_monto * porcentaje, 2)` |
| `moneda` | char | no | Default `MXN` |
| `estado` | `comision_estado` | no | `potencial`, `devengada`, `pagada`, `cancelada`. No existen `estimada` ni `confirmada`. |
| `pagada_at` | timestamptz | sí | Se sella al pasar a `pagada`. No hay `fecha_pago date`. |
| `created_at`, `updated_at` | timestamptz | no | |

`devengada` exige unidad `reservado` o `vendido`. `pagada` exige unidad `vendido`. `pagada` y `cancelada` no cambian de estado. La fuente auditable se lee por el match y el lead, que es lo que cubre la consulta 1.9.

---

## Bloque 4. Plantillas WhatsApp

Listas para cargar en Meta Business. Ninguna se envía hasta que Meta la marque `approved`. Fuera de la ventana de 24 horas el outbound solo usa estas plantillas. Dentro de la ventana el texto libre sigue pasando por `borradores` y por `borradores_cumplimiento` (lista negra y precio).

El nombre de la plantilla aprobada se guarda en `borradores.plantilla`.

### 4.1 `palm_diamante_bienvenida` (Utility)

Idioma `es_MX`. Variable `{{1}}` nombre.

```text
Hola {{1}}, gracias por tu interés en Palm Diamante, la preventa de lujo frente al mar en Acapulco.

Soy asesor de Estrategia Inmobiliaria. Para enviarte las opciones que mejor se ajusten a tu perfil, ¿me confirmas estos 4 datos?

1. Presupuesto aproximado
2. Forma de pago (contado, crédito, mixto)
3. Plazo de compra
4. Tipología deseada (2 o 3 recámaras, penthouse)

Con esto te preparo una propuesta personalizada.
```

### 4.2 `palm_diamante_seguimiento` (Marketing)

Variables `{{1}}` nombre, `{{2}}` unidad o avance.

```text
Hola {{1}}, te comparto una actualización de Palm Diamante: {{2}}.

¿Te agendo una llamada de 15 minutos para resolver dudas y revisar disponibilidad?
```

### 4.3 `palm_diamante_cita_confirmacion` (Utility)

Variables `{{1}}` nombre, `{{2}}` fecha, `{{3}}` hora.

```text
{{1}}, confirmo tu cita para el {{2}} a las {{3}}.

Te contactará un asesor de Estrategia Inmobiliaria. Si necesitas reprogramar, responde a este mensaje.
```

Estas plantillas no incluyen precio. Con `lista_vigente = false` en las 605 unidades, un cuerpo con precio sería rechazado al aprobar el borrador.

---

## Bloque 5. Flujo n8n — webhook inbound

El workflow canónico, inactivo y sin secretos, es [n8n/PD-WF-001_meta-inbound.json](n8n/PD-WF-001_meta-inbound.json) (PD-WF-001, versión del manual 1.1). Valida HMAC, responde 401 si la firma falla y normaliza el teléfono. El nodo de búsqueda de lead queda deshabilitado hasta cerrar PD-P10 §6.1. [n8n/webhook-inbound.json](n8n/webhook-inbound.json) es el esqueleto anterior, con la misma ruta `meta-inbound`.

### 5.1 Nodos

```text
[Webhook Meta]
  → [Validar firma HMAC]
  → ¿válida?
       no → [Registrar descarte si ya hubo cuerpo fiable] → [401]
       sí → [Guardar webhook_eventos con clave_idempotencia = message_id]
  → ¿clave duplicada?
       sí → [200 ya procesado]
       no → [Normalizar a dígitos y conservar E.164]
  → [Buscar leads.telefono_normalizado]
       no existe → [Insert prospectos] → [Insert leads] → [Insert interacciones entrante]
       existe    → [Update ultimo_msg_cliente_at en prospectos y en leads]
                 → [Insert interacciones entrante]
  → [Agente calificador]
  → [Insert scoring vigente + update leads.temperatura]
  → [Update prospectos.temperatura en la misma transacción]
  → [Router]
       caliente → [Alerta de lead caliente del núcleo] + [Insert borrador pendiente]
       tibio    → [Insert borrador pendiente con preguntas]
       frio     → [Insert seguimiento + proximo_seguimiento_at]
       listo    → [Insert cita programada]
  → [Marcar webhook_eventos.estado = procesado]
```

La función desplegada `lead-alert-email` responde 202 si el cuerpo no es un `INSERT` de `leads_prueba_formulario`. El router de un lead caliente del núcleo no debe llamarla. Hace falta una alerta distinta, o esa función tiene que aprender un segundo contrato. Hasta entonces el nodo de alerta queda desconectado a propósito en el JSON.

### 5.2 Validación HMAC

Meta manda el cuerpo crudo y la cabecera `x-hub-signature-256`. En n8n el cuerpo JSON ya parseado no sirve para recomputar el HMAC: hay que conservar los bytes originales. `timingSafeEqual` lanza si las longitudes difieren; por eso se comparan longitudes antes.

```js
const crypto = require('crypto');

const appSecret = $env.META_APP_SECRET;
const rawBody = $input.first().json.rawBody;
const signature = String($input.first().json.headers['x-hub-signature-256'] || '');
const expected = 'sha256=' + crypto.createHmac('sha256', appSecret).update(rawBody).digest('hex');

const a = Buffer.from(expected);
const b = Buffer.from(signature);
const firmaValida = a.length === b.length && crypto.timingSafeEqual(a, b);

if (!appSecret || !rawBody || !firmaValida) {
  return [{ json: { valid: false } }];
}
return [{ json: { valid: true, rawBody } }];
```

Un nodo que hace `throw` deja el webhook en error 500 y Meta reintenta. El flujo responde 401 y no inserta prospecto ni lead.

### 5.3 Contrato de escritura

1. Firma inválida: HTTP 401. No se crea lead.
2. `webhook_eventos.clave_idempotencia` = id del mensaje de Meta. El índice único absorbe el reintento.
3. `prospectos.telefono` se guarda en E.164 (`+52` y 10 dígitos). `leads.telefono` puede llevar el mismo valor. `telefono_normalizado` lo escribe el trigger, solo dígitos.
4. Alta: `prospectos`, luego `leads` con `prospecto_id`, luego `interacciones` con `direccion = 'entrante'`, `canal = 'whatsapp'`, `estado = 'recibido'`, `id_externo` = id del mensaje.
5. Lead existente: actualizar `ultimo_msg_cliente_at` en las dos tablas e insertar la interacción. El agente `prospecting` solo puede crear interacciones entrantes o de canal `sistema`.
6. El calificador inserta `scoring` (`vigente = true`). El trigger `scoring_retirar_vigente` apaga la fila anterior.
7. Copiar `leads.temperatura` a `prospectos.temperatura` en la misma transacción.
8. El borrador nace en `pendiente`, con `prospecto_id`, nunca marcado `enviado` por el workflow.
9. Idempotencia de la interacción: índice único `(canal, id_externo)`.

---

## Bloque 6. Purga antes de producción

No se ejecutó `truncate`, `drop` ni rotación de secretos. La tabla es la orden de trabajo. La verificación es una consulta de conteo, sin listar teléfonos en el repositorio.

| # | Elemento | Acción | Verificación en el corte |
| --- | --- | --- | --- |
| 1 | `leads_prueba_formulario` (3) | Exportar y después vaciar | Sigue en 3. Sigue en `public`. |
| 2 | `lab_meta_demo` (4 / 8 / 16 / 224) | Exportar y después vaciar o retirar el esquema | Sigue poblado y aislado (sin `USAGE` para `anon` ni `authenticated`). |
| 3 | Semilla de 15 prospectos y 15 leads | Revisión fila por fila. Purgar los de prueba junto con `scoring` y `perfiles_inversion`. | Siguen los 15. El formato E.164 no prueba que sean clientes. |
| 4 | `campanas` | Confirmar vacío y después dar de alta campañas reales | 0 filas. |
| 5 | `inventario` / `unidades` (605) | Conciliar contra la lista oficial. No purgar el inventario junto con la semilla de leads. | 605 = 605 por clave y por `inventario_id`. `lista_vigente` falso en todas. |
| 6 | `easybroker_propiedades` (365) | Tratarla como referencia. `id_externo` de unidades sigue nulo en las 605. | 365 filas. |
| 7 | `seguimientos` (4) | Revisar si son de prueba | 4 filas. |
| 8 | `citas` (2) | Revisar si son de prueba | 2 programadas. |
| 9 | `comisiones` | Nada que purgar | 0 filas. |
| 10 | Secretos | Rotar llave de servicio, secreto de Meta, llave de EasyBroker, secreto de sync y secreto de la alerta | No rotados en este corte. |

Consulta de formato, para correr en el proyecto y leer solo el conteo:

```sql
select count(*) as prospectos_fuera_de_e164_mx
from public.prospectos
where telefono !~ '^\+52[0-9]{10}$';

select count(*) as leads_fuera_de_digitos_mx
from public.leads
where telefono_normalizado !~ '^52[0-9]{10}$';
```

En el corte ambos conteos son 0. El gate de producción añade el conteo de semilla que todavía no haya sido aceptada como cliente real. Ese criterio no es un regex.

Orden de borrado de una semilla aceptada como prueba: `scoring`, `perfiles_inversion`, `borradores`, `citas`, `seguimientos`, `interacciones`, `matches`, `comisiones`, después `leads`, después `prospectos`. `unidades` y `unidad_historial` se quedan.

---

## Bloque 7. Matriz RACI

| Mapa | Responsable (R) | Aprobador (A) | Consultado (C) | Informado (I) |
| --- | --- | --- | --- | --- |
| 01 Arquitectura | Backend Lead | CTO | Asesores | Dirección |
| 02 Funnel | Comercial Lead | Dirección | Backend | Asesores |
| 03 Inbound | Backend Lead | CTO | Comercial | Asesores |
| 04 Outbound | Comercial Lead | Dirección | Backend | Asesores |
| 05 ERD | Backend Lead | CTO | Comercial | Dirección |
| 06 Prospectos / leads | Backend Lead | CTO | Comercial | Asesores |
| 07 Matching | Backend Lead y Comercial | CTO | Asesores | Dirección |
| 08 Edge Functions | Backend Lead | CTO | — | Dirección |
| 09 Seguridad | Backend Lead | CTO | Legal | Dirección |
| 10 Producción | CTO | Dirección | Comercial | Todos |
| 11 Métricas | Comercial Lead | Dirección | Backend | Asesores |
| 12 Lab vs producción | Backend Lead | CTO | Comercial | Dirección |

## Qué queda prohibido hasta el siguiente cambio de esquema

- Ejecutar el SQL de policies del borrador original (`asignado_a = auth.uid()::text`, `comisiones.lead_id`, `borradores.lead_id`, `agente_permisos.agente_id`).
- Sustituir el comentario de `public.leads`.
- Llamar a `lead-alert-email` para un lead caliente del núcleo.
- Declarar cumplidas las reglas 1.4, 1.5, 1.6 y 1.7 por un cero vacío o por la semilla de laboratorio.
