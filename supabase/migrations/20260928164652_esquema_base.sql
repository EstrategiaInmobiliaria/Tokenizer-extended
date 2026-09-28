-- ============================================================
-- PALM DIAMANTE · Esquema base (Supabase / Postgres 15+)
--
-- Consolida, en un solo archivo idempotente, el esquema que ya está aplicado en el
-- proyecto Supabase `palm-lab-practica` (migraciones 20260928164652 … 20260928180122).
-- Sirve para reproducir la base en local o en un proyecto nuevo. En `palm-lab-practica`
-- NO hace falta volverlo a correr; si se corre, no cambia nada (todo lleva IF NOT EXISTS).
--
-- Reglas de negocio que este esquema hace cumplir (ver CLAUDE.md):
--   · inventario.lista_vigente = false  →  ningún precio puede darse a clientes (/sinprecio).
--   · borradores: nada pasa a 'enviado' sin aprobado_por (Jimmy).
--   · RLS activo en todas las tablas; solo `authenticated` (y service_role, que la omite).
-- ============================================================

create extension if not exists pgcrypto;

-- ------------------------------------------------------------
-- Función común: updated_at automático
-- ------------------------------------------------------------
create or replace function public.touch_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end
$$;

-- ------------------------------------------------------------
-- 1. INVENTARIO (lista oficial por unidad)
-- ------------------------------------------------------------
create table if not exists public.inventario (
  id               bigint generated always as identity primary key,
  torre            text not null
                   check (torre in ('I-A', 'I-B', 'II-A', 'II-B', 'III-A', 'III-B')),
  unidad           text not null,                 -- '302', 'PH1', 'SRG-01', 'GH02'
  clave            text unique,                   -- torre || '-' || unidad, p. ej. 'III-B-302'
  modelo           text,                          -- 'A1','B1','C1','GH','PH','Suite Roof Garden','Fusión 175 m² (sin tipo)'
  tipologia        text,                          -- 'A1','B1','C1','GH01'…'GH04','PH 3R','Suite Roof Garden'
  piso             integer,
  m2               numeric(8,2),
  precio_lista     numeric(14,2),                 -- null en unidades vendidas / apartadas
  precio_m2        numeric(12,2),
  estatus          text not null default 'disponible'
                   check (estatus in ('disponible', 'apartado', 'reservado', 'vendido')),
  codigo_vendedor  text,
  fecha_lista      date not null,                 -- 2026-09-15 para la lista actual
  lista_vigente    boolean not null default false,
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now(),
  unique (torre, unidad)
);

comment on table  public.inventario is
  'Inventario por unidad según la lista oficial. Si lista_vigente = false, NINGÚN precio puede darse a clientes (usar /sinprecio).';
comment on column public.inventario.piso is '0 = PB (planta baja)';
comment on column public.inventario.lista_vigente is
  'Solo Jimmy la cambia a true cuando confirme que la lista está vigente. Mientras sea false, los precios no se usan con clientes.';

create index if not exists inventario_estatus_torre_idx on public.inventario (estatus, torre);
create index if not exists inventario_modelo_idx        on public.inventario (modelo);

drop trigger if exists trg_inventario_touch on public.inventario;
create trigger trg_inventario_touch
  before update on public.inventario
  for each row execute function public.touch_updated_at();

-- ------------------------------------------------------------
-- 2. PROSPECTOS
-- ------------------------------------------------------------
create table if not exists public.prospectos (
  id                      uuid primary key default gen_random_uuid(),
  nombre                  text not null,
  telefono                text not null unique,   -- formato E.164: '+525512345678'
  origen                  text,                   -- 'WhatsApp','Facebook','Instagram','Google','Portal','Referido'…
  proposito               text,                   -- vivir / vacacionar / invertir
  presupuesto             numeric(12,2),
  forma_pago              text,                   -- contado / plan de pagos / crédito
  plazo                   text,
  tipologia               text,
  horario_contacto        text,
  temperatura             text check (temperatura in ('caliente', 'tibio', 'frio')),
  notas                   text,
  perfil                  text not null default 'A' check (perfil in ('A', 'B', 'C')),
  unidad_interes          text references public.inventario (clave)
                          on update cascade on delete set null,
  estado                  text not null default 'nuevo'
                          check (estado in ('nuevo', 'contactado', 'calificado', 'cita',
                                            'apartado', 'cerrado', 'descartado')),
  ultimo_msg_cliente_at   timestamptz,
  ultimo_msg_asesor_at    timestamptz,
  proximo_seguimiento_at  timestamptz,
  cita_at                 timestamptz,
  sinprecio_pendiente     boolean not null default false,
  asignado_a              text,
  created_at              timestamptz not null default now(),
  updated_at              timestamptz not null default now()
);

comment on column public.prospectos.sinprecio_pendiente is
  'true = el prospecto pidió precios y se le respondió con /sinprecio; queda pendiente enviarle la lista cuando Jimmy la confirme';
comment on column public.prospectos.asignado_a is 'Asesor responsable del prospecto (texto libre por ahora)';

create index if not exists prospectos_created_at_perfil_idx      on public.prospectos (created_at, perfil);
create index if not exists prospectos_perfil_estado_idx          on public.prospectos (perfil, estado);
create index if not exists prospectos_proximo_seguimiento_at_idx on public.prospectos (proximo_seguimiento_at);
create index if not exists prospectos_ultimo_msg_cliente_at_idx  on public.prospectos (ultimo_msg_cliente_at);
create index if not exists prospectos_unidad_interes_idx         on public.prospectos (unidad_interes);
create index if not exists prospectos_sinprecio_pendiente_idx    on public.prospectos (sinprecio_pendiente)
  where sinprecio_pendiente;

drop trigger if exists trg_prospectos_touch on public.prospectos;
create trigger trg_prospectos_touch
  before update on public.prospectos
  for each row execute function public.touch_updated_at();

-- ------------------------------------------------------------
-- 3. SEGUIMIENTOS
-- ------------------------------------------------------------
create table if not exists public.seguimientos (
  id                 uuid primary key default gen_random_uuid(),
  prospecto_id       uuid not null references public.prospectos (id) on delete cascade,
  fecha_seguimiento  timestamptz not null,
  tipo               text not null default 'whatsapp'
                     check (tipo in ('llamada', 'whatsapp', 'email', 'visita', 'otro')),
  estado             text not null default 'pendiente'
                     check (estado in ('pendiente', 'completado', 'vencido', 'cancelado')),
  notas              text,
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now()
);

comment on table public.seguimientos is
  'Seguimientos por prospecto. Vencido = fecha pasada y estado pendiente (o marcado vencido).';

create index if not exists seguimientos_prospecto_idx    on public.seguimientos (prospecto_id);
create index if not exists seguimientos_estado_fecha_idx on public.seguimientos (estado, fecha_seguimiento);

drop trigger if exists trg_seguimientos_touch on public.seguimientos;
create trigger trg_seguimientos_touch
  before update on public.seguimientos
  for each row execute function public.touch_updated_at();

-- ------------------------------------------------------------
-- 4. CITAS
-- ------------------------------------------------------------
create table if not exists public.citas (
  id            uuid primary key default gen_random_uuid(),
  prospecto_id  uuid not null references public.prospectos (id) on delete cascade,
  fecha_cita    timestamptz not null,
  lugar         text not null default 'Por confirmar',   -- lugar de citas: pendiente de Jimmy
  estado        text not null default 'programada'
                check (estado in ('programada', 'confirmada', 'cancelada', 'completada')),
  notas         text,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

comment on table public.citas is
  'Citas con prospectos. El reporte diario lee la semana en curso (America/Mexico_City).';

create index if not exists citas_prospecto_idx on public.citas (prospecto_id);
create index if not exists citas_fecha_idx     on public.citas (fecha_cita);

drop trigger if exists trg_citas_touch on public.citas;
create trigger trg_citas_touch
  before update on public.citas
  for each row execute function public.touch_updated_at();

-- ------------------------------------------------------------
-- 5. BORRADORES (todo mensaje a cliente nace aquí)
-- ------------------------------------------------------------
create table if not exists public.borradores (
  id            uuid primary key default gen_random_uuid(),
  prospecto_id  uuid not null references public.prospectos (id) on delete cascade,
  canal         text not null default 'whatsapp',
  contenido     text not null,
  plantilla     text,                          -- '/hola', '/sinprecio', '/cita', …
  estado        text not null default 'pendiente'
                check (estado in ('pendiente', 'aprobado', 'rechazado', 'enviado')),
  creado_por    text,
  aprobado_por  text,
  aprobado_at   timestamptz,
  enviado_at    timestamptz,
  notas         text,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  constraint borradores_enviado_requiere_aprobacion
    check (estado <> 'enviado' or aprobado_por is not null)
);

comment on table public.borradores is
  'Borradores de mensajes a clientes. Deben pasar por el subagente auditor-inventario y ser aprobados antes de enviarse.';

create index if not exists borradores_prospecto_idx      on public.borradores (prospecto_id);
create index if not exists borradores_estado_created_idx on public.borradores (estado, created_at);

drop trigger if exists trg_borradores_touch on public.borradores;
create trigger trg_borradores_touch
  before update on public.borradores
  for each row execute function public.touch_updated_at();

-- ------------------------------------------------------------
-- SEGURIDAD (RLS)
-- Solo usuarios autenticados. service_role (n8n / Make / backend) omite RLS.
-- anon no tiene política → no ve nada.
-- ------------------------------------------------------------
alter table public.inventario   enable row level security;
alter table public.prospectos   enable row level security;
alter table public.seguimientos enable row level security;
alter table public.citas        enable row level security;
alter table public.borradores   enable row level security;

do $$
declare
  t text;
begin
  foreach t in array array['inventario', 'prospectos', 'seguimientos', 'citas', 'borradores'] loop
    if not exists (
      select 1 from pg_policies
      where schemaname = 'public' and tablename = t and policyname = t || '_authenticated_all'
    ) then
      execute format(
        'create policy %I on public.%I for all to authenticated using (true) with check (true)',
        t || '_authenticated_all', t
      );
    end if;
  end loop;
end
$$;
