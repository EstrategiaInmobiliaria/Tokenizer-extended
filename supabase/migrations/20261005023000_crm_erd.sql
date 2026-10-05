-- Fuente de verdad comercial: desarrollo → torre → unidad, y lead → perfil → score → match → comisión.
-- No reemplaza public.inventario ni public.prospectos. Los copia, los enlaza y se mantiene en sincronía.
-- Las reglas de negocio (unidad no disponible, lista sin vigencia, precio en mensajes) corren por trigger
-- para cualquier rol, incluido service_role. El permiso de cada agente corre en el mismo camino de escritura.

create type public.unidad_estatus as enum ('disponible', 'apartado', 'reservado', 'vendido');
create type public.desarrollo_estatus as enum ('planeacion', 'preventa', 'obra', 'entrega', 'cerrado');
create type public.lead_estado as enum ('nuevo', 'contactado', 'calificado', 'cita', 'apartado', 'cerrado', 'descartado');
create type public.lead_temperatura as enum ('caliente', 'tibio', 'frio');
create type public.lead_tipo as enum ('persona', 'empresa');
create type public.clase_lead as enum ('A', 'B', 'C');
create type public.objetivo_inversion as enum ('uso_propio', 'vacacional', 'inversion', 'plusvalia', 'renta', 'balanceado');
create type public.match_estado as enum ('propuesto', 'ofrecido', 'aceptado', 'rechazado', 'vencido', 'cancelado');
create type public.interaccion_canal as enum ('whatsapp', 'email', 'llamada', 'visita', 'linkedin', 'meta', 'sistema', 'otro');
create type public.interaccion_direccion as enum ('entrante', 'saliente');
create type public.interaccion_estado as enum ('borrador', 'aprobado', 'enviado', 'recibido', 'fallido', 'cancelado');
create type public.comision_estado as enum ('potencial', 'devengada', 'pagada', 'cancelada');
create type public.fuente_familia as enum ('linkedin', 'meta', 'web', 'referido', 'directo', 'otro');
create type public.crm_agente as enum ('inventario', 'matching', 'prospecting', 'followup', 'comercial');

create table public.desarrollos (
  id uuid primary key default gen_random_uuid(),
  nombre text not null check (char_length(btrim(nombre)) between 2 and 160),
  slug text not null unique check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  ciudad text not null,
  municipio text,
  estado text,
  pais text not null default 'MX',
  estatus public.desarrollo_estatus not null default 'preventa',
  moneda char(3) not null default 'MXN',
  actor text not null default 'sistema',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.torres (
  id uuid primary key default gen_random_uuid(),
  desarrollo_id uuid not null references public.desarrollos (id) on delete restrict,
  clave text not null check (char_length(btrim(clave)) between 1 and 40),
  nombre text,
  niveles integer check (niveles is null or niveles > 0),
  actor text not null default 'sistema',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (desarrollo_id, clave)
);

create table public.unidades (
  id uuid primary key default gen_random_uuid(),
  torre_id uuid not null references public.torres (id) on delete restrict,
  inventario_id bigint unique references public.inventario (id) on delete restrict,
  clave text not null unique,
  numero text not null,
  modelo text,
  tipologia text,
  piso integer,
  m2 numeric(12, 2) check (m2 is null or m2 > 0),
  recamaras numeric(4, 1) check (recamaras is null or recamaras >= 0),
  banos numeric(4, 1) check (banos is null or banos >= 0),
  estacionamientos integer check (estacionamientos is null or estacionamientos >= 0),
  precio_lista numeric(14, 2) check (precio_lista is null or precio_lista >= 0),
  precio_m2 numeric(14, 2) generated always as (
    case
      when m2 is null or m2 = 0 or precio_lista is null then null
      else round(precio_lista / m2, 2)
    end
  ) stored,
  moneda char(3) not null default 'MXN',
  estatus public.unidad_estatus not null default 'disponible',
  lista_vigente boolean not null default false,
  fecha_lista date,
  codigo_vendedor text,
  caracteristicas jsonb not null default '{}'::jsonb,
  id_externo text,
  clave_idempotencia text,
  actor text not null default 'sistema',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (torre_id, numero)
);

create unique index unidades_idempotencia_uidx
  on public.unidades (clave_idempotencia)
  where clave_idempotencia is not null;

create index unidades_torre_estatus_idx on public.unidades (torre_id, estatus);
create index unidades_estatus_idx on public.unidades (estatus);

create table public.unidad_historial (
  id uuid primary key default gen_random_uuid(),
  unidad_id uuid not null references public.unidades (id) on delete restrict,
  campo text not null,
  valor_anterior text,
  valor_nuevo text,
  motivo text,
  actor text not null,
  created_at timestamptz not null default now()
);

create index unidad_historial_unidad_idx
  on public.unidad_historial (unidad_id, created_at desc);

create table public.fuentes_lead (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  nombre text not null,
  familia public.fuente_familia not null,
  activa boolean not null default true,
  actor text not null default 'sistema',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.campanas (
  id uuid primary key default gen_random_uuid(),
  fuente_id uuid not null references public.fuentes_lead (id) on delete restrict,
  nombre text not null,
  id_externo text,
  estado text not null default 'activa' check (estado in ('borrador', 'activa', 'pausada', 'cerrada')),
  presupuesto numeric(14, 2) check (presupuesto is null or presupuesto >= 0),
  moneda char(3) not null default 'MXN',
  inicia_en date,
  termina_en date,
  actor text not null default 'sistema',
  clave_idempotencia text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (termina_en is null or inicia_en is null or termina_en >= inicia_en)
);

create unique index campanas_fuente_externo_uidx
  on public.campanas (fuente_id, id_externo)
  where id_externo is not null;

create unique index campanas_idempotencia_uidx
  on public.campanas (clave_idempotencia)
  where clave_idempotencia is not null;

create index campanas_fuente_idx on public.campanas (fuente_id);

create table public.leads (
  id uuid primary key default gen_random_uuid(),
  prospecto_id uuid unique references public.prospectos (id) on delete set null,
  tipo public.lead_tipo not null default 'persona',
  nombre text not null check (char_length(btrim(nombre)) between 2 and 160),
  empresa text,
  telefono text not null,
  telefono_normalizado text not null,
  email text check (email is null or email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
  estado public.lead_estado not null default 'nuevo',
  temperatura public.lead_temperatura,
  fuente_id uuid references public.fuentes_lead (id) on delete restrict,
  campana_id uuid references public.campanas (id) on delete set null,
  origen_detalle text,
  id_externo text,
  horario_contacto text,
  unidad_interes_clave text,
  sinprecio_pendiente boolean not null default false,
  consentimiento_privacidad boolean,
  asignado_a text,
  notas text,
  ultimo_msg_cliente_at timestamptz,
  ultimo_msg_asesor_at timestamptz,
  proximo_seguimiento_at timestamptz,
  actor text not null default 'sistema',
  clave_idempotencia text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (tipo = 'persona' or empresa is not null)
);

create unique index leads_telefono_uidx on public.leads (telefono_normalizado);
create unique index leads_idempotencia_uidx
  on public.leads (clave_idempotencia)
  where clave_idempotencia is not null;
create unique index leads_fuente_externo_uidx
  on public.leads (fuente_id, id_externo)
  where id_externo is not null;
create index leads_estado_idx on public.leads (estado);
create index leads_seguimiento_idx on public.leads (proximo_seguimiento_at)
  where proximo_seguimiento_at is not null;
create index leads_fuente_idx on public.leads (fuente_id);
create index leads_campana_idx on public.leads (campana_id);

create table public.perfiles_inversion (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid not null unique references public.leads (id) on delete cascade,
  presupuesto_objetivo numeric(14, 2) check (presupuesto_objetivo is null or presupuesto_objetivo >= 0),
  presupuesto_min numeric(14, 2) check (presupuesto_min is null or presupuesto_min >= 0),
  presupuesto_max numeric(14, 2) check (presupuesto_max is null or presupuesto_max >= 0),
  moneda char(3) not null default 'MXN',
  forma_pago text,
  horizonte_anios integer check (horizonte_anios is null or horizonte_anios > 0),
  yield_minimo numeric(6, 4) check (yield_minimo is null or (yield_minimo >= 0 and yield_minimo <= 1)),
  objetivo public.objetivo_inversion,
  tipologia text,
  proposito_detalle text,
  plazo text,
  actor text not null default 'sistema',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (
    presupuesto_min is null or presupuesto_max is null or presupuesto_max >= presupuesto_min
  )
);

create table public.scoring (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid not null references public.leads (id) on delete cascade,
  clase public.clase_lead not null,
  vigente boolean not null default true,
  variables jsonb not null default '{}'::jsonb,
  modelo text not null,
  actor text not null default 'sistema',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index scoring_vigente_uidx on public.scoring (lead_id) where vigente;
create index scoring_lead_idx on public.scoring (lead_id, created_at desc);

create table public.matches (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid not null references public.leads (id) on delete restrict,
  unidad_id uuid not null references public.unidades (id) on delete restrict,
  estado public.match_estado not null default 'propuesto',
  score numeric(5, 2) check (score is null or (score >= 0 and score <= 100)),
  explicacion text,
  variables jsonb not null default '{}'::jsonb,
  precio_ofrecido numeric(14, 2) check (precio_ofrecido is null or precio_ofrecido >= 0),
  motivo text,
  actor text not null default 'sistema',
  clave_idempotencia text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (
    estado not in ('ofrecido', 'aceptado')
    or char_length(btrim(coalesce(explicacion, ''))) >= 10
  )
);

create unique index matches_abiertos_uidx
  on public.matches (lead_id, unidad_id)
  where estado in ('propuesto', 'ofrecido', 'aceptado');
create unique index matches_aceptado_unidad_uidx
  on public.matches (unidad_id)
  where estado = 'aceptado';
create unique index matches_idempotencia_uidx
  on public.matches (clave_idempotencia)
  where clave_idempotencia is not null;
create index matches_lead_idx on public.matches (lead_id);
create index matches_unidad_idx on public.matches (unidad_id, estado);

create table public.interacciones (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid not null references public.leads (id) on delete restrict,
  unidad_id uuid references public.unidades (id) on delete set null,
  campana_id uuid references public.campanas (id) on delete set null,
  canal public.interaccion_canal not null,
  direccion public.interaccion_direccion not null,
  estado public.interaccion_estado not null default 'borrador',
  contenido text not null check (char_length(contenido) <= 8000),
  id_externo text,
  ocurrido_at timestamptz not null default now(),
  actor text not null default 'sistema',
  clave_idempotencia text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index interacciones_idempotencia_uidx
  on public.interacciones (clave_idempotencia)
  where clave_idempotencia is not null;
create index interacciones_lead_idx on public.interacciones (lead_id, ocurrido_at desc);
create index interacciones_unidad_idx on public.interacciones (unidad_id);
create index interacciones_campana_idx on public.interacciones (campana_id);

create table public.comisiones (
  id uuid primary key default gen_random_uuid(),
  match_id uuid not null references public.matches (id) on delete restrict,
  beneficiario text not null,
  estado public.comision_estado not null default 'potencial',
  porcentaje numeric(7, 4) not null check (porcentaje > 0 and porcentaje <= 1),
  base_monto numeric(14, 2) not null check (base_monto >= 0),
  monto numeric(14, 2) generated always as (round(base_monto * porcentaje, 2)) stored,
  moneda char(3) not null default 'MXN',
  pagada_at timestamptz,
  actor text not null default 'sistema',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index comisiones_abiertas_uidx
  on public.comisiones (match_id, beneficiario)
  where estado <> 'cancelada';
create index comisiones_match_idx on public.comisiones (match_id);

create table public.agente_permisos (
  agente public.crm_agente not null,
  tabla text not null,
  puede_leer boolean not null default false,
  puede_crear boolean not null default false,
  puede_modificar boolean not null default false,
  puede_borrar boolean not null default false,
  primary key (agente, tabla)
);

comment on table public.desarrollos is 'Proyecto inmobiliario. Padre de torres.';
comment on table public.torres is 'Torre o edificio dentro de un desarrollo.';
comment on table public.unidades is 'Inventario real de unidades. lista_vigente = false impide cotizar precio.';
comment on table public.unidad_historial is 'Bitácora append-only de precio, estatus y vigencia. No se edita.';
comment on table public.leads is 'Prospecto persona o empresa. El teléfono normalizado deduplica.';
comment on table public.perfiles_inversion is 'Capacidad y tesis de inversión vigentes del lead.';
comment on table public.scoring is 'Clase A/B/C. Una sola fila vigente por lead. variables explica la clase.';
comment on table public.matches is 'Unidad propuesta a un lead. Una vendida o no disponible no puede ofrecerse.';
comment on table public.interacciones is 'WhatsApp, email, llamada y demás. El envío con precio pasa por la lista vigente.';
comment on table public.comisiones is 'Comisión potencial, devengada o pagada de un match.';
comment on table public.fuentes_lead is 'Origen del lead: LinkedIn, Meta, web, referido.';
comment on table public.campanas is 'Campaña de prospección. Sin acento en el nombre de tabla para no citar el identificador.';
comment on table public.agente_permisos is 'Matriz de lo que cada agente puede leer o escribir. Cambiarla es una migración.';

create or replace function private.crm_actor()
returns text
language sql
stable
set search_path = ''
as $$
  select nullif(current_setting('crm.agente', true), '');
$$;

create or replace function private.asumir_agente(p_agente text)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if p_agente not in ('inventario', 'matching', 'prospecting', 'followup', 'comercial') then
    raise exception 'agente desconocido: %', p_agente using errcode = 'check_violation';
  end if;
  perform set_config('crm.agente', p_agente, true);
end;
$$;

create or replace function public.asumir_agente(p_agente text)
returns void
language sql
security invoker
set search_path = ''
as $$
  select private.asumir_agente(p_agente);
$$;

create or replace function private.crm_permiso(p_tabla text, p_accion text)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1
    from public.agente_permisos
    where agente::text = private.crm_actor()
      and tabla = p_tabla
      and case p_accion
        when 'leer' then puede_leer
        when 'crear' then puede_crear
        when 'modificar' then puede_modificar
        when 'borrar' then puede_borrar
        else false
      end
  );
$$;

create or replace function private.normalizar_telefono(p_telefono text)
returns text
language sql
immutable
set search_path = ''
as $$
  select regexp_replace(coalesce(p_telefono, ''), '\D', '', 'g');
$$;

create or replace function private.crm_guard_write()
returns trigger
language plpgsql
set search_path = ''
as $$
declare
  v_actor text := private.crm_actor();
  v_accion text;
begin
  if tg_op = 'INSERT' then
    v_accion := 'crear';
  elsif tg_op = 'UPDATE' then
    v_accion := 'modificar';
  else
    v_accion := 'borrar';
  end if;

  -- crm.reglas lo encienden los triggers de negocio (apartar, cancelar matches,
  -- historial, sync). Esa escritura es de la base, no del agente.
  if current_setting('crm.reglas', true) = 'on' then
    if tg_op = 'DELETE' then
      return old;
    end if;
    return new;
  end if;

  if v_actor is null and current_user in ('postgres', 'supabase_admin') then
    if tg_op = 'DELETE' then
      return old;
    end if;
    return new;
  end if;

  if not private.crm_permiso(tg_table_name, v_accion) then
    raise exception 'el agente % no puede % en %',
      coalesce(v_actor, current_user), v_accion, tg_table_name
      using errcode = '42501';
  end if;

  if tg_op = 'DELETE' then
    return old;
  end if;

  if tg_table_name <> 'agente_permisos'
     and (new.actor is null or new.actor = 'sistema')
  then
    new.actor := coalesce(v_actor, current_user);
  end if;

  if tg_op = 'UPDATE' and tg_table_name = 'unidades' and v_actor = 'comercial' then
    if new.precio_lista is distinct from old.precio_lista
       or new.lista_vigente is distinct from old.lista_vigente
       or new.m2 is distinct from old.m2
       or new.clave is distinct from old.clave
       or new.torre_id is distinct from old.torre_id
       or new.numero is distinct from old.numero
       or new.modelo is distinct from old.modelo
       or new.tipologia is distinct from old.tipologia
       or new.piso is distinct from old.piso
       or new.inventario_id is distinct from old.inventario_id
    then
      raise exception 'el agente comercial solo puede cambiar estatus y codigo_vendedor'
        using errcode = '42501';
    end if;
  end if;

  if tg_op = 'UPDATE' and tg_table_name = 'leads' and v_actor = 'followup' then
    if new.nombre is distinct from old.nombre
       or new.telefono is distinct from old.telefono
       or new.email is distinct from old.email
       or new.fuente_id is distinct from old.fuente_id
       or new.campana_id is distinct from old.campana_id
       or new.tipo is distinct from old.tipo
       or new.empresa is distinct from old.empresa
       or new.prospecto_id is distinct from old.prospecto_id
       or new.asignado_a is distinct from old.asignado_a
    then
      raise exception 'el agente followup no cambia identidad, fuente ni asignación del lead'
        using errcode = '42501';
    end if;
  end if;

  if tg_op = 'UPDATE' and tg_table_name = 'leads' and v_actor = 'prospecting' then
    if new.asignado_a is distinct from old.asignado_a then
      raise exception 'la asignación del lead la cambia el agente comercial'
        using errcode = '42501';
    end if;
  end if;

  if tg_op = 'UPDATE' and tg_table_name = 'leads' and v_actor = 'comercial' then
    if new.nombre is distinct from old.nombre
       or new.telefono is distinct from old.telefono
       or new.email is distinct from old.email
       or new.fuente_id is distinct from old.fuente_id
       or new.campana_id is distinct from old.campana_id
    then
      raise exception 'el agente comercial no reescribe la identidad ni la fuente del lead'
        using errcode = '42501';
    end if;
  end if;

  if tg_op = 'INSERT' and tg_table_name = 'interacciones' and v_actor = 'prospecting' then
    if new.direccion <> 'entrante' and new.canal <> 'sistema' then
      raise exception 'prospecting solo registra entrada o notas de sistema'
        using errcode = '42501';
    end if;
  end if;

  return new;
end;
$$;

create or replace function private.crm_normaliza_lead()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.telefono_normalizado := private.normalizar_telefono(new.telefono);
  if char_length(new.telefono_normalizado) < 10 or char_length(new.telefono_normalizado) > 15 then
    raise exception 'telefono inválido' using errcode = 'check_violation';
  end if;
  return new;
end;
$$;

create or replace function private.unidad_historial_escribir()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_prev text := current_setting('crm.reglas', true);
begin
  perform set_config('crm.reglas', 'on', true);
  if tg_op = 'INSERT' then
    insert into public.unidad_historial (unidad_id, campo, valor_nuevo, actor)
    values (new.id, 'alta', new.estatus::text, new.actor);
  else
    if new.precio_lista is distinct from old.precio_lista then
      insert into public.unidad_historial (unidad_id, campo, valor_anterior, valor_nuevo, actor)
      values (new.id, 'precio_lista', old.precio_lista::text, new.precio_lista::text, new.actor);
    end if;
    if new.estatus is distinct from old.estatus then
      insert into public.unidad_historial (unidad_id, campo, valor_anterior, valor_nuevo, actor)
      values (new.id, 'estatus', old.estatus::text, new.estatus::text, new.actor);
    end if;
    if new.lista_vigente is distinct from old.lista_vigente then
      insert into public.unidad_historial (unidad_id, campo, valor_anterior, valor_nuevo, actor)
      values (new.id, 'lista_vigente', old.lista_vigente::text, new.lista_vigente::text, new.actor);
    end if;
  end if;
  perform set_config('crm.reglas', case when v_prev = 'on' then 'on' else 'off' end, true);
  return new;
end;
$$;

create or replace function private.unidad_reglas()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_prev text;
begin
  if tg_op = 'UPDATE'
     and old.estatus = 'vendido'
     and new.estatus is distinct from 'vendido'
     and nullif(current_setting('crm.reapertura_motivo', true), '') is null
  then
    raise exception 'una unidad vendida no se reabre sin motivo de reapertura'
      using errcode = 'check_violation';
  end if;

  if tg_op = 'UPDATE'
     and new.estatus = 'disponible'
     and old.estatus is distinct from 'disponible'
     and exists (
       select 1 from public.matches
       where unidad_id = new.id and estado = 'aceptado'
     )
  then
    raise exception 'hay un match aceptado; cancélalo antes de liberar la unidad'
      using errcode = 'check_violation';
  end if;

  if tg_op = 'UPDATE' and new.estatus is distinct from 'disponible' then
    v_prev := current_setting('crm.reglas', true);
    perform set_config('crm.reglas', 'on', true);
    update public.matches
    set estado = 'cancelado',
        motivo = 'unidad_no_disponible',
        actor = coalesce(new.actor, 'sistema')
    where unidad_id = new.id
      and estado in ('propuesto', 'ofrecido')
      and id::text is distinct from nullif(current_setting('crm.match_excluir', true), '');
    perform set_config('crm.reglas', case when v_prev = 'on' then 'on' else 'off' end, true);
  end if;

  return new;
end;
$$;

create or replace function private.match_reglas()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_estatus public.unidad_estatus;
  v_vigente boolean;
  v_clave text;
begin
  if new.estado in ('propuesto', 'ofrecido', 'aceptado') then
    select estatus, lista_vigente, clave
      into v_estatus, v_vigente, v_clave
    from public.unidades
    where id = new.unidad_id;

    if v_estatus is distinct from 'disponible' then
      raise exception 'la unidad % no se puede ofrecer: estatus %', v_clave, v_estatus
        using errcode = 'check_violation';
    end if;

    if new.precio_ofrecido is not null and v_vigente is not true then
      raise exception 'lista no vigente: no se puede fijar precio ofrecido en %', v_clave
        using errcode = 'check_violation';
    end if;
  end if;

  if new.estado = 'aceptado'
     and (tg_op = 'INSERT' or old.estado is distinct from 'aceptado')
  then
    perform set_config('crm.match_excluir', new.id::text, true);
    perform set_config('crm.reglas', 'on', true);
    update public.unidades
    set estatus = 'apartado',
        actor = coalesce(new.actor, 'sistema')
    where id = new.unidad_id
      and estatus = 'disponible';
    perform set_config('crm.reglas', 'off', true);
    perform set_config('crm.match_excluir', '', true);
  end if;

  return new;
end;
$$;

create or replace function private.comision_reglas()
returns trigger
language plpgsql
set search_path = ''
as $$
declare
  v_estatus public.unidad_estatus;
begin
  select u.estatus into v_estatus
  from public.matches m
  join public.unidades u on u.id = m.unidad_id
  where m.id = new.match_id;

  if tg_op = 'UPDATE' and old.estado in ('pagada', 'cancelada') and new.estado is distinct from old.estado then
    raise exception 'una comisión % no cambia de estado', old.estado
      using errcode = 'check_violation';
  end if;

  if new.estado = 'devengada' and v_estatus not in ('reservado', 'vendido') then
    raise exception 'la comisión se devenga solo con la unidad reservada o vendida'
      using errcode = 'check_violation';
  end if;

  if new.estado = 'pagada' then
    if v_estatus is distinct from 'vendido' then
      raise exception 'la comisión se paga cuando la unidad está vendida'
        using errcode = 'check_violation';
    end if;
    if new.pagada_at is null then
      new.pagada_at := now();
    end if;
  end if;

  return new;
end;
$$;

create or replace function private.interaccion_reglas()
returns trigger
language plpgsql
set search_path = ''
as $$
declare
  prohibido text;
  patron_precio constant text :=
    '(\$[[:space:]]*[[:digit:]])|([[:digit:]][[:space:]]*(millones|mdp|mxn|pesos))|([[:digit:]]{1,3}(,[[:digit:]]{3}){2,})';
begin
  prohibido := public.contiene_lista_negra(new.contenido);
  if prohibido is not null then
    raise exception 'interacción rechazada: contiene un canal de la lista negra (%)', prohibido
      using errcode = 'check_violation';
  end if;

  if new.estado in ('aprobado', 'enviado')
     and new.contenido ~* patron_precio
     and not public.lista_precios_vigente()
  then
    raise exception 'mensaje con precio bloqueado: la lista no está vigente'
      using errcode = 'check_violation';
  end if;

  if new.estado in ('aprobado', 'enviado')
     and new.contenido ~* patron_precio
     and private.crm_actor() is distinct from 'comercial'
     and current_user not in ('postgres', 'supabase_admin')
  then
    raise exception 'un mensaje con precio lo aprueba el agente comercial'
      using errcode = '42501';
  end if;

  return new;
end;
$$;

create or replace function private.scoring_retirar_vigente()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_prev text;
begin
  if new.vigente then
    v_prev := current_setting('crm.reglas', true);
    perform set_config('crm.reglas', 'on', true);
    update public.scoring
    set vigente = false
    where lead_id = new.lead_id
      and vigente
      and id is distinct from new.id;
    perform set_config('crm.reglas', case when v_prev = 'on' then 'on' else 'off' end, true);
  end if;
  return new;
end;
$$;

create or replace function private.sync_unidad_hacia_inventario()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  if current_setting('crm.syncing', true) = 'on' or new.inventario_id is null then
    return new;
  end if;
  perform set_config('crm.syncing', 'on', true);
  update public.inventario
  set estatus = new.estatus::text,
      precio_lista = new.precio_lista,
      precio_m2 = new.precio_m2,
      m2 = new.m2,
      lista_vigente = new.lista_vigente,
      fecha_lista = coalesce(new.fecha_lista, fecha_lista),
      modelo = new.modelo,
      tipologia = new.tipologia,
      piso = new.piso,
      codigo_vendedor = new.codigo_vendedor
  where id = new.inventario_id;
  perform set_config('crm.syncing', 'off', true);
  return new;
end;
$$;

create or replace function private.sync_inventario_hacia_unidad()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_torre uuid;
  v_desarrollo uuid;
begin
  if current_setting('crm.syncing', true) = 'on' then
    return new;
  end if;

  select d.id into v_desarrollo
  from public.desarrollos d
  where d.slug = 'palm-diamante';

  select t.id into v_torre
  from public.torres t
  where t.desarrollo_id = v_desarrollo
    and t.clave = new.torre;

  if v_torre is null then
    raise exception 'no existe la torre % en el desarrollo Palm Diamante', new.torre
      using errcode = 'foreign_key_violation';
  end if;

  perform set_config('crm.syncing', 'on', true);
  perform set_config('crm.reglas', 'on', true);
  insert into public.unidades (
    torre_id, inventario_id, clave, numero, modelo, tipologia, piso, m2,
    precio_lista, estatus, lista_vigente, fecha_lista, codigo_vendedor, actor
  ) values (
    v_torre, new.id, new.clave, new.unidad, new.modelo, new.tipologia, new.piso, new.m2,
    new.precio_lista, new.estatus::public.unidad_estatus, new.lista_vigente,
    new.fecha_lista, new.codigo_vendedor, 'sync-inventario'
  )
  on conflict (inventario_id) do update
  set torre_id = excluded.torre_id,
      clave = excluded.clave,
      numero = excluded.numero,
      modelo = excluded.modelo,
      tipologia = excluded.tipologia,
      piso = excluded.piso,
      m2 = excluded.m2,
      precio_lista = excluded.precio_lista,
      estatus = excluded.estatus,
      lista_vigente = excluded.lista_vigente,
      fecha_lista = excluded.fecha_lista,
      codigo_vendedor = excluded.codigo_vendedor,
      actor = excluded.actor;
  perform set_config('crm.reglas', 'off', true);
  perform set_config('crm.syncing', 'off', true);
  return new;
end;
$$;

create or replace function private.buscar_lead_por_telefono(p_telefono text)
returns table (id uuid, estado public.lead_estado)
language sql
stable
security definer
set search_path = ''
as $$
  select l.id, l.estado
  from public.leads l
  where l.telefono_normalizado = private.normalizar_telefono(p_telefono);
$$;

create or replace function public.buscar_lead_por_telefono(p_telefono text)
returns table (id uuid, estado public.lead_estado)
language plpgsql
stable
security invoker
set search_path = ''
as $$
begin
  if private.crm_actor() not in ('prospecting', 'comercial', 'followup', 'matching')
     and current_user not in ('postgres', 'supabase_admin')
  then
    raise exception 'sin permiso para buscar leads' using errcode = '42501';
  end if;
  return query
  select hallado.id, hallado.estado
  from private.buscar_lead_por_telefono(p_telefono) as hallado;
end;
$$;

create or replace function public.clasificar_lead(
  p_presupuesto numeric,
  p_temperatura public.lead_temperatura,
  p_forma_pago text
)
returns public.clase_lead
language sql
immutable
set search_path = ''
as $$
  select case
    when p_presupuesto >= 6000000
         and p_temperatura = 'caliente'
         and nullif(btrim(coalesce(p_forma_pago, '')), '') is not null
      then 'A'::public.clase_lead
    when p_presupuesto >= 4000000 or p_temperatura = 'tibio'
      then 'B'::public.clase_lead
    else 'C'::public.clase_lead
  end;
$$;

revoke all on function private.crm_actor() from public;
revoke all on function private.asumir_agente(text) from public;
revoke all on function private.crm_permiso(text, text) from public;
revoke all on function private.normalizar_telefono(text) from public;
revoke all on function private.crm_guard_write() from public;
revoke all on function private.crm_normaliza_lead() from public;
revoke all on function private.unidad_historial_escribir() from public;
revoke all on function private.unidad_reglas() from public;
revoke all on function private.match_reglas() from public;
revoke all on function private.comision_reglas() from public;
revoke all on function private.interaccion_reglas() from public;
revoke all on function private.scoring_retirar_vigente() from public;
revoke all on function private.sync_unidad_hacia_inventario() from public;
revoke all on function private.sync_inventario_hacia_unidad() from public;
revoke all on function private.buscar_lead_por_telefono(text) from public;
revoke all on function public.asumir_agente(text) from public, anon, authenticated;
revoke all on function public.buscar_lead_por_telefono(text) from public, anon, authenticated;
revoke all on function public.clasificar_lead(numeric, public.lead_temperatura, text) from public, anon, authenticated;

grant usage on schema private to service_role;
grant execute on function private.crm_actor() to service_role;
grant execute on function private.normalizar_telefono(text) to service_role;
grant execute on function private.crm_guard_write() to service_role;
grant execute on function private.crm_normaliza_lead() to service_role;
grant execute on function private.unidad_historial_escribir() to service_role;
grant execute on function private.unidad_reglas() to service_role;
grant execute on function private.match_reglas() to service_role;
grant execute on function private.comision_reglas() to service_role;
grant execute on function private.interaccion_reglas() to service_role;
grant execute on function private.scoring_retirar_vigente() to service_role;
grant execute on function private.sync_unidad_hacia_inventario() to service_role;
grant execute on function private.sync_inventario_hacia_unidad() to service_role;
grant execute on function private.buscar_lead_por_telefono(text) to service_role;
grant execute on function private.crm_permiso(text, text) to service_role;
grant execute on function private.asumir_agente(text) to service_role;
grant execute on function public.asumir_agente(text) to service_role;
grant execute on function public.buscar_lead_por_telefono(text) to service_role;
grant execute on function public.clasificar_lead(numeric, public.lead_temperatura, text) to service_role;

do $$
declare
  t text;
begin
  foreach t in array array[
    'desarrollos', 'torres', 'unidades', 'unidad_historial', 'fuentes_lead', 'campanas',
    'leads', 'perfiles_inversion', 'scoring', 'matches', 'interacciones', 'comisiones',
    'agente_permisos'
  ]
  loop
    execute format('drop trigger if exists trg_%I_permiso on public.%I', t, t);
    execute format(
      'create trigger trg_%I_permiso before insert or update or delete on public.%I for each row execute function private.crm_guard_write()',
      t, t
    );
    if t <> 'unidad_historial' then
      execute format('drop trigger if exists trg_%I_touch on public.%I', t, t);
      execute format(
        'create trigger trg_%I_touch before update on public.%I for each row execute function public.touch_updated_at()',
        t, t
      );
    end if;
  end loop;
end;
$$;

create trigger trg_leads_normaliza
  before insert or update of telefono on public.leads
  for each row execute function private.crm_normaliza_lead();

create trigger trg_unidades_historial
  after insert or update of precio_lista, estatus, lista_vigente on public.unidades
  for each row execute function private.unidad_historial_escribir();

create trigger trg_unidades_reglas
  before update of estatus on public.unidades
  for each row execute function private.unidad_reglas();

create trigger trg_matches_reglas
  before insert or update of estado, precio_ofrecido, unidad_id on public.matches
  for each row execute function private.match_reglas();

create trigger trg_comisiones_reglas
  before insert or update on public.comisiones
  for each row execute function private.comision_reglas();

create trigger trg_interacciones_reglas
  before insert or update of contenido, estado on public.interacciones
  for each row execute function private.interaccion_reglas();

create trigger trg_scoring_retirar_vigente
  before insert or update of vigente on public.scoring
  for each row execute function private.scoring_retirar_vigente();

insert into public.agente_permisos (agente, tabla, puede_leer, puede_crear, puede_modificar, puede_borrar)
values
  ('inventario', 'desarrollos', true, true, true, false),
  ('inventario', 'torres', true, true, true, false),
  ('inventario', 'unidades', true, true, true, false),
  ('inventario', 'unidad_historial', true, false, false, false),
  ('inventario', 'agente_permisos', true, false, false, false),
  ('matching', 'desarrollos', true, false, false, false),
  ('matching', 'torres', true, false, false, false),
  ('matching', 'unidades', true, false, false, false),
  ('matching', 'unidad_historial', true, false, false, false),
  ('matching', 'fuentes_lead', true, false, false, false),
  ('matching', 'campanas', true, false, false, false),
  ('matching', 'leads', true, false, false, false),
  ('matching', 'perfiles_inversion', true, false, false, false),
  ('matching', 'scoring', true, false, false, false),
  ('matching', 'matches', true, true, true, false),
  ('matching', 'interacciones', true, false, false, false),
  ('matching', 'comisiones', true, false, false, false),
  ('matching', 'agente_permisos', true, false, false, false),
  ('prospecting', 'desarrollos', true, false, false, false),
  ('prospecting', 'torres', true, false, false, false),
  ('prospecting', 'unidades', true, false, false, false),
  ('prospecting', 'fuentes_lead', true, true, false, false),
  ('prospecting', 'campanas', true, true, true, false),
  ('prospecting', 'leads', true, true, true, false),
  ('prospecting', 'perfiles_inversion', true, true, true, false),
  ('prospecting', 'scoring', true, true, true, false),
  ('prospecting', 'interacciones', true, true, false, false),
  ('prospecting', 'agente_permisos', true, false, false, false),
  ('followup', 'desarrollos', true, false, false, false),
  ('followup', 'torres', true, false, false, false),
  ('followup', 'unidades', true, false, false, false),
  ('followup', 'fuentes_lead', true, false, false, false),
  ('followup', 'campanas', true, false, false, false),
  ('followup', 'leads', true, false, true, false),
  ('followup', 'perfiles_inversion', true, false, false, false),
  ('followup', 'scoring', true, false, false, false),
  ('followup', 'matches', true, false, false, false),
  ('followup', 'interacciones', true, true, true, false),
  ('followup', 'agente_permisos', true, false, false, false),
  ('comercial', 'desarrollos', true, false, false, false),
  ('comercial', 'torres', true, false, false, false),
  ('comercial', 'unidades', true, false, true, false),
  ('comercial', 'unidad_historial', true, false, false, false),
  ('comercial', 'fuentes_lead', true, true, false, false),
  ('comercial', 'campanas', true, false, false, false),
  ('comercial', 'leads', true, false, true, false),
  ('comercial', 'perfiles_inversion', true, false, true, false),
  ('comercial', 'scoring', true, true, true, false),
  ('comercial', 'matches', true, false, true, false),
  ('comercial', 'interacciones', true, true, true, false),
  ('comercial', 'comisiones', true, true, true, false),
  ('comercial', 'agente_permisos', true, false, false, false);

insert into public.desarrollos (nombre, slug, ciudad, municipio, estado, pais, estatus, actor)
values (
  'Palm Diamante', 'palm-diamante', 'Acapulco', 'Acapulco de Juárez', 'Guerrero', 'MX', 'preventa', 'migracion'
);

insert into public.torres (desarrollo_id, clave, nombre, actor)
select d.id, torre.clave, torre.clave, 'migracion'
from public.desarrollos d
cross join (values ('I-A'), ('I-B'), ('II-A'), ('II-B'), ('III-A'), ('III-B')) as torre (clave)
where d.slug = 'palm-diamante';

insert into public.unidades (
  torre_id, inventario_id, clave, numero, modelo, tipologia, piso, m2,
  precio_lista, estatus, lista_vigente, fecha_lista, codigo_vendedor, actor
)
select
  t.id,
  i.id,
  i.clave,
  i.unidad,
  i.modelo,
  i.tipologia,
  i.piso,
  i.m2,
  i.precio_lista,
  i.estatus::public.unidad_estatus,
  i.lista_vigente,
  i.fecha_lista,
  i.codigo_vendedor,
  'migracion'
from public.inventario i
join public.torres t on t.clave = i.torre
join public.desarrollos d on d.id = t.desarrollo_id and d.slug = 'palm-diamante';

insert into public.fuentes_lead (slug, nombre, familia, actor)
values
  ('facebook', 'Facebook', 'meta', 'migracion'),
  ('instagram', 'Instagram', 'meta', 'migracion'),
  ('linkedin', 'LinkedIn', 'linkedin', 'migracion'),
  ('google', 'Google', 'web', 'migracion'),
  ('portal', 'Portal', 'web', 'migracion'),
  ('referido', 'Referido', 'referido', 'migracion'),
  ('whatsapp', 'WhatsApp', 'directo', 'migracion'),
  ('formulario', 'Formulario', 'web', 'migracion'),
  ('easybroker', 'EasyBroker', 'otro', 'migracion'),
  ('otro', 'Otro', 'otro', 'migracion');

insert into public.leads (
  prospecto_id, nombre, telefono, estado, temperatura, fuente_id, origen_detalle,
  horario_contacto, unidad_interes_clave, sinprecio_pendiente, asignado_a, notas, actor,
  ultimo_msg_cliente_at, ultimo_msg_asesor_at, proximo_seguimiento_at
)
select
  p.id,
  p.nombre,
  p.telefono,
  p.estado::public.lead_estado,
  p.temperatura::public.lead_temperatura,
  f.id,
  p.origen,
  p.horario_contacto,
  p.unidad_interes,
  p.sinprecio_pendiente,
  p.asignado_a,
  p.notas,
  'migracion',
  p.ultimo_msg_cliente_at,
  p.ultimo_msg_asesor_at,
  p.proximo_seguimiento_at
from public.prospectos p
left join public.fuentes_lead f on f.slug = lower(p.origen);

insert into public.perfiles_inversion (
  lead_id, presupuesto_objetivo, forma_pago, objetivo, tipologia, proposito_detalle, plazo, actor
)
select
  l.id,
  p.presupuesto,
  p.forma_pago,
  case p.proposito
    when 'vivir' then 'uso_propio'
    when 'vacacional' then 'vacacional'
    when 'inversion' then 'inversion'
    else null
  end::public.objetivo_inversion,
  p.tipologia,
  p.proposito,
  p.plazo,
  'migracion'
from public.prospectos p
join public.leads l on l.prospecto_id = p.id;

insert into public.scoring (lead_id, clase, vigente, variables, modelo, actor)
select
  l.id,
  p.perfil::public.clase_lead,
  true,
  jsonb_build_object(
    'origen', 'prospectos.perfil',
    'nota', 'clase previa migrada; no fue recalculada por clasificar_lead'
  ),
  'migracion-prospectos',
  'migracion'
from public.prospectos p
join public.leads l on l.prospecto_id = p.id;

create trigger trg_unidades_sync_inventario
  after insert or update of precio_lista, estatus, lista_vigente, m2, modelo, tipologia, piso, codigo_vendedor, fecha_lista
  on public.unidades
  for each row execute function private.sync_unidad_hacia_inventario();

create trigger trg_inventario_sync_unidad
  after insert or update on public.inventario
  for each row execute function private.sync_inventario_hacia_unidad();

create view public.v_unidades_ofertables
with (security_invoker = true) as
select
  u.id,
  d.nombre as desarrollo,
  t.clave as torre,
  u.clave,
  u.numero,
  u.modelo,
  u.tipologia,
  u.piso,
  u.m2,
  u.estatus,
  u.lista_vigente,
  case when u.lista_vigente then u.precio_lista else null end as precio_publicable,
  case when u.lista_vigente then u.precio_m2 else null end as precio_m2_publicable
from public.unidades u
join public.torres t on t.id = u.torre_id
join public.desarrollos d on d.id = t.desarrollo_id
where u.estatus = 'disponible';

comment on view public.v_unidades_ofertables is
  'Solo unidades disponibles. El precio sale nulo mientras lista_vigente sea false.';

do $$
declare
  t text;
begin
  foreach t in array array[
    'desarrollos', 'torres', 'unidades', 'unidad_historial', 'fuentes_lead', 'campanas',
    'leads', 'perfiles_inversion', 'scoring', 'matches', 'interacciones', 'comisiones',
    'agente_permisos'
  ]
  loop
    execute format('alter table public.%I enable row level security', t);
    execute format('revoke all on table public.%I from anon, authenticated', t);
  end loop;
end;
$$;

grant select, insert, update, delete on
  public.desarrollos, public.torres, public.unidades, public.fuentes_lead, public.campanas,
  public.leads, public.perfiles_inversion, public.scoring, public.matches,
  public.interacciones, public.comisiones, public.agente_permisos
to service_role;

revoke all on table public.unidad_historial from service_role;
grant select on table public.unidad_historial to service_role;

revoke all on public.v_unidades_ofertables from anon, authenticated;
grant select on public.v_unidades_ofertables to service_role;

do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'crm_agent') then
    create role crm_agent nologin;
  end if;
end;
$$;

grant usage on schema public to crm_agent;
grant select, insert, update on
  public.desarrollos, public.torres, public.unidades, public.fuentes_lead, public.campanas,
  public.leads, public.perfiles_inversion, public.scoring, public.matches,
  public.interacciones, public.comisiones, public.agente_permisos
to crm_agent;
grant select on public.unidad_historial, public.v_unidades_ofertables to crm_agent;
grant usage on schema private to crm_agent;
grant execute on function public.asumir_agente(text) to crm_agent;
grant execute on function private.asumir_agente(text) to crm_agent;
grant execute on function private.crm_permiso(text, text) to crm_agent;
grant execute on function private.crm_actor() to crm_agent;
grant execute on function private.normalizar_telefono(text) to crm_agent;
grant execute on function private.crm_guard_write() to crm_agent;
grant execute on function private.crm_normaliza_lead() to crm_agent;
grant execute on function private.unidad_historial_escribir() to crm_agent;
grant execute on function private.unidad_reglas() to crm_agent;
grant execute on function private.match_reglas() to crm_agent;
grant execute on function private.comision_reglas() to crm_agent;
grant execute on function private.interaccion_reglas() to crm_agent;
grant execute on function private.scoring_retirar_vigente() to crm_agent;
grant execute on function private.sync_unidad_hacia_inventario() to crm_agent;
grant execute on function private.sync_inventario_hacia_unidad() to crm_agent;
grant execute on function private.buscar_lead_por_telefono(text) to crm_agent;
grant execute on function public.buscar_lead_por_telefono(text) to crm_agent;
grant execute on function public.clasificar_lead(numeric, public.lead_temperatura, text) to crm_agent;

do $$
declare
  t text;
begin
  foreach t in array array[
    'desarrollos', 'torres', 'unidades', 'unidad_historial', 'fuentes_lead', 'campanas',
    'leads', 'perfiles_inversion', 'scoring', 'matches', 'interacciones', 'comisiones',
    'agente_permisos'
  ]
  loop
    execute format(
      'create policy %I on public.%I for select to crm_agent using (private.crm_permiso(%L, %L))',
      t || '_leer', t, t, 'leer'
    );
    execute format(
      'create policy %I on public.%I for insert to crm_agent with check (private.crm_permiso(%L, %L))',
      t || '_crear', t, t, 'crear'
    );
    execute format(
      'create policy %I on public.%I for update to crm_agent using (private.crm_permiso(%L, %L)) with check (private.crm_permiso(%L, %L))',
      t || '_modificar', t, t, 'modificar', t, 'modificar'
    );
  end loop;
end;
$$;
