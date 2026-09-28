-- ============================================================
-- PALM DIAMANTE · Datos de prueba (todos marcados EJEMPLO)
--
-- Para entornos locales o proyectos nuevos. `palm-lab-practica` ya tiene la lista real
-- (605 unidades, 15-sep-2026) y prospectos EJEMPLO cargados: ahí NO hace falta correrlo.
-- Idempotente: usa ON CONFLICT DO NOTHING sobre claves naturales (clave, telefono).
--
-- Reglas respetadas (CLAUDE.md): tipologías y rangos de la lista del 15-sep-2026,
-- lista_vigente = false, citas con lugar "Por confirmar", ningún canal de la lista negra.
-- ============================================================

-- Inventario EJEMPLO: unidades ficticias (unidad 'EJ-*') dentro de los rangos reales de la lista.
insert into public.inventario
  (torre, unidad, clave, modelo, tipologia, piso, m2, precio_lista, precio_m2, estatus, fecha_lista, lista_vigente)
values
  ('III-B', 'EJ-302', 'III-B-EJ-302', 'B1', 'B1',                 3,  76.04,  5163482.40, 67904.82, 'disponible', '2026-09-15', false),
  ('III-A', 'EJ-102', 'III-A-EJ-102', 'B1', 'B1',                 1,  76.04,  5043733.20, 66330.00, 'disponible', '2026-09-15', false),
  ('III-A', 'EJ-SRG-01', 'III-A-EJ-SRG-01', 'Suite Roof Garden', 'Suite Roof Garden', 18, 81.97, 5711666.20, 69679.96, 'disponible', '2026-09-15', false),
  ('II-A',  'EJ-104', 'II-A-EJ-104',  'A1', 'A1',                 1,  94.07,  7039363.30, 74830.98, 'disponible', '2026-09-15', false),
  ('I-A',   'EJ-GH01', 'I-A-EJ-GH01', 'GH', 'GH01',               19, 145.52, 10388889.24, 71391.35, 'disponible', '2026-09-15', false),
  ('III-B', 'EJ-PH1', 'III-B-EJ-PH1', 'PH', 'PH 3R',              20, 158.45, 12129842.00, 76552.49, 'disponible', '2026-09-15', false),
  ('III-B', 'EJ-201', 'III-B-EJ-201', 'A1', 'A1',                 2,  94.07,  null,        null,     'apartado',   '2026-09-15', false),
  ('I-B',   'EJ-1001', 'I-B-EJ-1001', 'A1', 'A1',                 10, 94.07,  null,        null,     'vendido',    '2026-09-15', false)
on conflict (clave) do nothing;

-- Prospectos EJEMPLO (mismos nombres y teléfonos que en palm-lab-practica).
insert into public.prospectos
  (nombre, telefono, origen, perfil, temperatura, estado, unidad_interes, sinprecio_pendiente,
   ultimo_msg_cliente_at, ultimo_msg_asesor_at, proximo_seguimiento_at, created_at)
values
  ('EJEMPLO Ana Ruiz',       '+525500000001', 'Facebook',  'A', 'caliente', 'nuevo',      'III-B-EJ-302', false,
     now() - interval '2 hours',  null,                        now() + interval '1 day',   now() - interval '3 hours'),
  ('EJEMPLO Bruno Soto',     '+525500000002', 'Instagram', 'A', 'tibio',    'contactado', 'III-B-EJ-201', false,
     now() - interval '3 days',   now() - interval '3 days',   now() - interval '1 day',   now() - interval '10 days'),
  ('EJEMPLO Carla Mena',     '+525500000003', 'Referido',  'B', 'tibio',    'nuevo',      'III-B-EJ-PH1', true,
     null,                        null,                        now() + interval '2 hours', now() - interval '7 hours'),
  ('EJEMPLO Diego Lara',     '+525500000004', 'Portal',    'B', 'caliente', 'cita',       'III-A-EJ-102', false,
     now() - interval '20 hours', now() - interval '19 hours', null,                       now() - interval '8 days'),
  ('EJEMPLO Elena Paz',      '+525500000005', 'Facebook',  'C', 'frio',     'contactado', null,           false,
     now() - interval '5 days',   now() - interval '6 days',   now() - interval '3 days',  now() - interval '20 days'),
  ('EJEMPLO Hugo Vera',      '+525500000008', 'Referido',  'B', 'caliente', 'nuevo',      'III-B-EJ-PH1', true,
     null,                        null,                        now() - interval '3 hours', now() - interval '22 hours'),
  ('EJEMPLO Karla Ortiz',    '+525500000011', 'Referido',  'B', 'caliente', 'apartado',   'III-B-EJ-201', false,
     now() - interval '1 day',    now() - interval '1 day',    now() + interval '3 days',  now() - interval '30 days'),
  ('EJEMPLO Mariana Solis',  '+525500000013', 'Facebook',  'C', 'frio',     'descartado', null,           false,
     null,                        null,                        null,                       now() - interval '25 days')
on conflict (telefono) do nothing;

-- Seguimientos EJEMPLO: uno vencido, uno futuro, uno completado, uno cancelado.
insert into public.seguimientos (prospecto_id, fecha_seguimiento, tipo, estado, notas)
select p.id, now() - interval '1 day', 'whatsapp', 'pendiente', 'EJEMPLO seguimiento vencido - DATO FICTICIO'
from public.prospectos p where p.telefono = '+525500000002'
  and not exists (select 1 from public.seguimientos s where s.prospecto_id = p.id and s.notas like 'EJEMPLO seguimiento vencido%');

insert into public.seguimientos (prospecto_id, fecha_seguimiento, tipo, estado, notas)
select p.id, now() + interval '1 day', 'llamada', 'pendiente', 'EJEMPLO seguimiento futuro - DATO FICTICIO'
from public.prospectos p where p.telefono = '+525500000001'
  and not exists (select 1 from public.seguimientos s where s.prospecto_id = p.id and s.notas like 'EJEMPLO seguimiento futuro%');

insert into public.seguimientos (prospecto_id, fecha_seguimiento, tipo, estado, notas)
select p.id, now() - interval '2 days', 'whatsapp', 'completado', 'EJEMPLO seguimiento completado - DATO FICTICIO'
from public.prospectos p where p.telefono = '+525500000004'
  and not exists (select 1 from public.seguimientos s where s.prospecto_id = p.id and s.notas like 'EJEMPLO seguimiento completado%');

insert into public.seguimientos (prospecto_id, fecha_seguimiento, tipo, estado, notas)
select p.id, now() - interval '3 days', 'email', 'cancelado', 'EJEMPLO seguimiento cancelado - DATO FICTICIO'
from public.prospectos p where p.telefono = '+525500000005'
  and not exists (select 1 from public.seguimientos s where s.prospecto_id = p.id and s.notas like 'EJEMPLO seguimiento cancelado%');

-- Citas EJEMPLO: lugar "Por confirmar" (pendiente de Jimmy).
insert into public.citas (prospecto_id, fecha_cita, lugar, estado, notas)
select p.id, now() + interval '1 day', 'Por confirmar', 'programada', 'EJEMPLO cita - DATO FICTICIO'
from public.prospectos p where p.telefono = '+525500000004'
  and not exists (select 1 from public.citas c where c.prospecto_id = p.id and c.notas like 'EJEMPLO cita%');

insert into public.citas (prospecto_id, fecha_cita, lugar, estado, notas)
select p.id, now() + interval '2 days', 'Por confirmar', 'programada', 'EJEMPLO cita - DATO FICTICIO'
from public.prospectos p where p.telefono = '+525500000011'
  and not exists (select 1 from public.citas c where c.prospecto_id = p.id and c.notas like 'EJEMPLO cita%');

-- Borradores EJEMPLO: uno pendiente (/hola) y uno aprobado por Jimmy (sin precios).
insert into public.borradores (prospecto_id, canal, plantilla, contenido, estado, creado_por)
select p.id, 'whatsapp', '/hola',
       'EJEMPLO: Hola Ana, gracias por tu interés en Palm Diamante. Te atiende Estrategia Inmobiliaria. Puedes escribirnos o llamarnos al 55 4437 8776, 55 6100 0600 o 55 2855 7467, y conocer el proyecto en palm-diamante.com/es. ¿Qué tipo de departamento te interesa?',
       'pendiente', 'bot'
from public.prospectos p where p.telefono = '+525500000001'
  and not exists (select 1 from public.borradores b where b.prospecto_id = p.id and b.plantilla = '/hola');

insert into public.borradores (prospecto_id, canal, plantilla, contenido, estado, creado_por, aprobado_por, aprobado_at)
select p.id, 'whatsapp', '/cita',
       'EJEMPLO: Hola Diego, te confirmo que tu cita queda programada; el lugar te lo confirmamos en cuanto esté listo. Cualquier duda, estamos a tus órdenes.',
       'aprobado', 'bot', 'EJEMPLO Jimmy', now()
from public.prospectos p where p.telefono = '+525500000004'
  and not exists (select 1 from public.borradores b where b.prospecto_id = p.id and b.plantilla = '/cita');
