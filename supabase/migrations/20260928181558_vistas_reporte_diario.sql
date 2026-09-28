-- ============================================================
-- PALM DIAMANTE · Vistas del reporte diario + cumplimiento (CLAUDE.md)
--
-- Requiere 20260928164652_esquema_base.sql (o el esquema ya aplicado en palm-lab-practica).
-- Idempotente: se puede volver a correr.
--
-- Zona horaria: Acapulco (Guerrero) usa America/Mexico_City (UTC-6, sin horario de verano).
-- Todas las vistas exponen columnas *_local ya convertidas para que el reporte no haga
-- aritmética de zonas horarias.
-- ============================================================

-- ------------------------------------------------------------
-- Lista negra (CLAUDE.md → "Canales"): dominios y teléfonos de terceros.
-- Devuelve el primer valor prohibido que aparece en el texto, o null si está limpio.
-- Los teléfonos se buscan solo por dígitos para atrapar '55 4021 2638', '+52 55-4021-2638', etc.
-- ------------------------------------------------------------
create or replace function public.contiene_lista_negra(texto text)
returns text
language plpgsql
immutable
set search_path = ''
as $$
declare
  compacto  text := regexp_replace(lower(coalesce(texto, '')), '\s', '', 'g');
  digitos   text := regexp_replace(coalesce(texto, ''), '\D', '', 'g');
  dominio   text;
  telefono  text;
begin
  foreach dominio in array array[
    'palmdiamante.mx', 'palmdiamanteacapulco.mx', 'palmdiamanteacapulco.com', 'ventadeptosacapulco.com'
  ] loop
    if position(dominio in compacto) > 0 then
      return dominio;
    end if;
  end loop;

  foreach telefono in array array['5540212638', '7442713055'] loop
    if position(telefono in digitos) > 0 then
      return telefono;
    end if;
  end loop;

  return null;
end
$$;

comment on function public.contiene_lista_negra(text) is
  'Devuelve el dominio o teléfono de la lista negra (CLAUDE.md) que aparece en el texto, o null.';

-- ------------------------------------------------------------
-- ¿Hay lista de precios confirmada como vigente por Jimmy?
-- ------------------------------------------------------------
create or replace function public.lista_precios_vigente()
returns boolean
language sql
stable
set search_path = ''
as $$
  select exists (select 1 from public.inventario where lista_vigente);
$$;

-- ------------------------------------------------------------
-- Cumplimiento en borradores:
--   · Nunca contenido con dominios/teléfonos de la lista negra.
--   · No se aprueba ni se envía un borrador con precios mientras la lista no esté vigente.
--     (Sí se puede guardar como 'pendiente' para que auditor-inventario lo revise.)
-- ------------------------------------------------------------
create or replace function public.borradores_cumplimiento()
returns trigger
language plpgsql
set search_path = ''
as $$
declare
  prohibido text := public.contiene_lista_negra(new.contenido);
  patron_precio constant text :=
    '(\$\s*\d)|(\d\s*(millones|mdp|mxn|pesos))|(\d{1,3}(,\d{3}){2,})';
begin
  if prohibido is not null then
    raise exception 'Borrador rechazado: contiene un canal de la lista negra (%). Ver CLAUDE.md → Canales.', prohibido
      using errcode = 'check_violation';
  end if;

  if new.estado in ('aprobado', 'enviado')
     and new.contenido ~* patron_precio
     and not public.lista_precios_vigente() then
    raise exception 'Borrador con precios bloqueado: la lista del 15-sep-2026 no está confirmada como vigente (inventario.lista_vigente). Usar /sinprecio.'
      using errcode = 'check_violation';
  end if;

  if new.estado = 'aprobado' and new.aprobado_at is null then
    new.aprobado_at := now();
  end if;
  if new.estado = 'enviado' and new.enviado_at is null then
    new.enviado_at := now();
  end if;

  return new;
end
$$;

drop trigger if exists trg_borradores_cumplimiento on public.borradores;
create trigger trg_borradores_cumplimiento
  before insert or update on public.borradores
  for each row execute function public.borradores_cumplimiento();

-- ------------------------------------------------------------
-- VISTAS DEL REPORTE DIARIO (security_invoker: respetan RLS del usuario que consulta)
-- ------------------------------------------------------------

-- Prospectos nuevos por día local, canal de origen y perfil.
-- El reporte filtra: where dia_local = <fecha del reporte>
create or replace view public.v_prospectos_nuevos
with (security_invoker = true) as
select
  (p.created_at at time zone 'America/Mexico_City')::date as dia_local,
  coalesce(p.origen, 'Sin origen')                        as canal,
  p.perfil,
  p.temperatura,
  count(*)                                                as total
from public.prospectos p
group by 1, 2, 3, 4;

comment on view public.v_prospectos_nuevos is
  'Prospectos nuevos por día (America/Mexico_City), canal de origen, perfil A/B/C y temperatura.';

-- Leads fríos: más de 48 h sin contacto (del cliente o del asesor) y todavía en juego.
create or replace view public.v_leads_frios
with (security_invoker = true) as
select
  p.id,
  p.nombre,
  p.telefono,
  p.perfil,
  p.temperatura,
  p.estado,
  p.origen                                                        as canal,
  p.asignado_a                                                    as asesor,
  p.unidad_interes,
  greatest(p.ultimo_msg_cliente_at, p.ultimo_msg_asesor_at)        as ultimo_contacto_at,
  greatest(p.ultimo_msg_cliente_at, p.ultimo_msg_asesor_at)
    at time zone 'America/Mexico_City'                            as ultimo_contacto_local,
  floor(extract(epoch from now() - coalesce(
          greatest(p.ultimo_msg_cliente_at, p.ultimo_msg_asesor_at), p.created_at)) / 3600)::int
                                                                  as horas_sin_contacto,
  (p.ultimo_msg_cliente_at is not null
   and p.ultimo_msg_cliente_at > coalesce(p.ultimo_msg_asesor_at, '-infinity'::timestamptz))
                                                                  as cliente_sin_respuesta,
  p.sinprecio_pendiente
from public.prospectos p
where p.estado not in ('apartado', 'cerrado', 'descartado')
  and coalesce(greatest(p.ultimo_msg_cliente_at, p.ultimo_msg_asesor_at), p.created_at)
      < now() - interval '48 hours'
order by horas_sin_contacto desc;

comment on view public.v_leads_frios is
  'Prospectos activos con más de 48 h sin contacto. cliente_sin_respuesta = el último mensaje es del cliente y nadie le contestó.';

-- Seguimientos vencidos: pendientes con fecha pasada, o ya marcados como vencidos.
create or replace view public.v_seguimientos_vencidos
with (security_invoker = true) as
select
  s.id                                                            as seguimiento_id,
  p.id                                                            as prospecto_id,
  p.nombre                                                        as prospecto,
  p.telefono,
  p.perfil,
  p.asignado_a                                                    as asesor,
  s.tipo,
  s.estado,
  s.fecha_seguimiento,
  s.fecha_seguimiento at time zone 'America/Mexico_City'          as fecha_seguimiento_local,
  floor(extract(epoch from now() - s.fecha_seguimiento) / 86400)::int as dias_retraso,
  greatest(p.ultimo_msg_cliente_at, p.ultimo_msg_asesor_at)
    at time zone 'America/Mexico_City'                            as ultimo_contacto_local,
  s.notas
from public.seguimientos s
join public.prospectos p on p.id = s.prospecto_id
where (s.estado = 'pendiente' and s.fecha_seguimiento < now())
   or s.estado = 'vencido'
order by s.fecha_seguimiento asc;

comment on view public.v_seguimientos_vencidos is
  'Seguimientos pendientes con fecha pasada (o marcados vencidos), con días de retraso y asesor.';

-- Inventario por modelo y torre: disponibles / apartadas / reservadas / vendidas y rango de precio.
-- torre_principal agrupa I-A e I-B como "I", etc. Los precios son de uso interno.
create or replace view public.v_apartado_por_tipologia
with (security_invoker = true) as
select
  coalesce(i.modelo, 'Sin modelo')                                as modelo,
  i.torre,
  split_part(i.torre, '-', 1)                                     as torre_principal,
  count(*) filter (where i.estatus = 'disponible')                as disponibles,
  count(*) filter (where i.estatus = 'apartado')                  as apartadas,
  count(*) filter (where i.estatus = 'reservado')                 as reservadas,
  count(*) filter (where i.estatus = 'vendido')                   as vendidas,
  count(*)                                                        as total,
  min(i.m2)                                                       as m2_min,
  max(i.m2)                                                       as m2_max,
  min(i.precio_lista) filter (where i.estatus = 'disponible')     as precio_min_disponible,
  max(i.precio_lista) filter (where i.estatus = 'disponible')     as precio_max_disponible,
  max(i.fecha_lista)                                              as fecha_lista,
  bool_or(i.lista_vigente)                                        as lista_vigente
from public.inventario i
group by 1, 2, 3
order by 3, 2, 1;

comment on view public.v_apartado_por_tipologia is
  'Conteo de unidades por modelo y torre según estatus, con rango de precio de las disponibles (uso interno).';

-- Citas de la semana en curso (lunes 00:00 a domingo 23:59, America/Mexico_City).
create or replace view public.v_citas_semana
with (security_invoker = true) as
with semana as (
  select
    date_trunc('week', now() at time zone 'America/Mexico_City') as inicio_local
)
select
  c.id                                                            as cita_id,
  p.id                                                            as prospecto_id,
  p.nombre                                                        as prospecto,
  p.telefono,
  p.asignado_a                                                    as asesor,
  c.fecha_cita,
  c.fecha_cita at time zone 'America/Mexico_City'                 as fecha_cita_local,
  c.lugar,
  c.estado,
  c.notas
from public.citas c
join public.prospectos p on p.id = c.prospecto_id
cross join semana s
where c.fecha_cita >= (s.inicio_local at time zone 'America/Mexico_City')
  and c.fecha_cita <  ((s.inicio_local + interval '7 days') at time zone 'America/Mexico_City')
  and c.estado in ('programada', 'confirmada')
order by c.fecha_cita asc;

comment on view public.v_citas_semana is
  'Citas programadas/confirmadas de la semana en curso, límites calculados en America/Mexico_City.';

-- Prospectos que pidieron precio y recibieron /sinprecio: se les avisa cuando Jimmy confirme la lista.
create or replace view public.v_sinprecio_pendientes
with (security_invoker = true) as
select
  p.id,
  p.nombre,
  p.telefono,
  p.perfil,
  p.asignado_a                                                    as asesor,
  p.unidad_interes,
  i.modelo,
  i.m2,
  i.precio_lista                                                  as precio_lista_interno,
  i.lista_vigente,
  p.created_at at time zone 'America/Mexico_City'                 as creado_local
from public.prospectos p
left join public.inventario i on i.clave = p.unidad_interes
where p.sinprecio_pendiente
order by p.created_at desc;

comment on view public.v_sinprecio_pendientes is
  'Prospectos con /sinprecio pendiente. precio_lista_interno NO se comunica mientras lista_vigente = false.';

-- Borradores que esperan revisión (auditor-inventario) y aprobación (Jimmy).
create or replace view public.v_borradores_pendientes
with (security_invoker = true) as
select
  b.id                                                            as borrador_id,
  p.nombre                                                        as prospecto,
  p.telefono,
  b.canal,
  b.plantilla,
  b.contenido,
  b.creado_por,
  b.created_at at time zone 'America/Mexico_City'                 as creado_local,
  public.contiene_lista_negra(b.contenido) is not null            as alerta_lista_negra
from public.borradores b
join public.prospectos p on p.id = b.prospecto_id
where b.estado = 'pendiente'
order by b.created_at asc;

comment on view public.v_borradores_pendientes is
  'Borradores en estado pendiente, en orden de llegada, para revisión del auditor y aprobación de Jimmy.';

-- Texto libre que menciona canales de la lista negra (notas, origen, lugar, contenido).
-- No se bloquea en notas internas (a veces hay que registrar de dónde viene el cliente),
-- pero el reporte diario lo lista para que se revise.
create or replace view public.v_alertas_lista_negra
with (security_invoker = true) as
select 'prospectos' as tabla, p.id::text as registro_id, 'notas' as campo,
       public.contiene_lista_negra(p.notas) as valor_prohibido, p.updated_at
from public.prospectos p where public.contiene_lista_negra(p.notas) is not null
union all
select 'prospectos', p.id::text, 'origen', public.contiene_lista_negra(p.origen), p.updated_at
from public.prospectos p where public.contiene_lista_negra(p.origen) is not null
union all
select 'seguimientos', s.id::text, 'notas', public.contiene_lista_negra(s.notas), s.updated_at
from public.seguimientos s where public.contiene_lista_negra(s.notas) is not null
union all
select 'citas', c.id::text, 'lugar', public.contiene_lista_negra(c.lugar), c.updated_at
from public.citas c where public.contiene_lista_negra(c.lugar) is not null
union all
select 'citas', c.id::text, 'notas', public.contiene_lista_negra(c.notas), c.updated_at
from public.citas c where public.contiene_lista_negra(c.notas) is not null
union all
select 'borradores', b.id::text, 'notas', public.contiene_lista_negra(b.notas), b.updated_at
from public.borradores b where public.contiene_lista_negra(b.notas) is not null;

comment on view public.v_alertas_lista_negra is
  'Registros cuyo texto libre menciona dominios o teléfonos de la lista negra (CLAUDE.md).';
