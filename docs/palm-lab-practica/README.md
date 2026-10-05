# Documentación operativa de palm-lab-practica

Documentación de procesos del CRM de preventa Palm Diamante. Cada mapa describe el propósito, la conexión en el ecosistema, las entradas, las salidas, el control de temperatura y los consumos, y queda anclado a objetos que existen en el proyecto Supabase `palm-lab-practica`.

| Campo | Valor |
| --- | --- |
| Proyecto | `palm-lab-practica` |
| Ref | `plgfhtvzxhrdfmrlknru` |
| Región | `us-east-1` |
| Postgres | 17.6.1.166 |
| Estado del proyecto | `ACTIVE_HEALTHY` |
| Corte de auditoría | 2026-10-05 |
| Última migración aplicada | `20261005104549` `crm_hardening_upsert_webhook_vista_comision` |
| Desarrollo canónico | `desarrollos.slug = palm-diamante`, estatus `preventa`, ciudad Acapulco |

Esta documentación describe el laboratorio. El laboratorio todavía no es la operación comercial de preventa.

## Cómo leer un mapa

Cada mapa usa el mismo contrato:

1. **Propósito operativo.** Qué decisión o invariante protege el proceso.
2. **Conexión sistémica.** Quién entrega la entrada, qué objeto de Supabase es el tránsito obligatorio y cuál es la salida observable.
3. **Capas.** Inputs, outputs, control de temperatura y consumos.
4. **Contrato de datos.** Tablas, columnas, restricciones, funciones y vistas que sostienen el proceso.
5. **Evidencia.** Conteos y objetos observados en el corte.
6. **Criterio de producción.** Condición medible para considerar el mapa cerrado.

### Estados

| Estado | Significado |
| --- | --- |
| Operativo | El objeto existe y tiene datos o ejecución vigente dentro del laboratorio. |
| Parcial | El contrato de datos o la regla existe; el camino de ejecución de punta a punta está incompleto. |
| Especificado | El proceso está definido para producción y no tiene objeto correspondiente en este proyecto. |
| Bloqueado | El objeto existe y una regla impide usarlo con clientes. |

## Principio arquitectónico

Supabase es la fuente de verdad. Un dato de negocio se considera ocurrido cuando queda escrito en una tabla de `public` con su restricción, su actor y su marca de tiempo. Los agentes de base de datos (`inventario`, `matching`, `prospecting`, `followup`, `comercial`) se comunican a través de esas tablas. La matriz `agente_permisos` y los triggers `private.crm_guard_write` impiden que un agente escriba fuera de su incumbencia.

El orquestador externo (n8n), la Cloud API de Meta y el modelo de lenguaje de calificación son sistemas periféricos. En este corte no hay workflow, función ni job dentro del proyecto que los invoque.

## Semáforo de los 12 mapas

| Mapa | Proceso | Estado | Hecho que fija el estado |
| --- | --- | --- | --- |
| 01 | Arquitectura del ecosistema | Parcial | Fuente de verdad relacional activa. Receptor de WhatsApp y orquestador ausentes. |
| 02 | Funnel de monetización | Parcial | Estados de `leads` poblados (15). `campanas`, `matches` y `comisiones` en cero. |
| 03 | WhatsApp inbound | Parcial | Normalización de teléfono y `webhook_eventos` existen. Cero eventos y cero interacciones. |
| 04 | Flujo outbound | Parcial | Borradores con aprobación y bloqueo de precio. Ventana de 24 h sin regla. |
| 05 | ERD fuente de verdad | Operativo | Migraciones `crm_erd_fuente_verdad_*` aplicadas. Integridad referencial activa. |
| 06 | Dualidad prospectos / leads | Parcial | 15 puentes 1:1 coherentes. Sin trigger que mantenga el espejo. |
| 07 | Inventario y matching | Bloqueado | 204 unidades disponibles. `lista_vigente = false` en las 605. `matches = 0`. |
| 08 | Edge Functions | Parcial | Tres funciones desplegadas. Cron no instalado. Alerta atada al formulario de prueba. |
| 09 | Seguridad y RLS | Operativo | `anon` sin lectura de CRM. `service_role` con `BYPASSRLS`. Matriz de agentes activa. |
| 10 | Priorización a producción | Especificado | Secuencia de salida definida. Gates de captura, plantillas y pauta abiertos. |
| 11 | Métricas que monetizan | Parcial | Vistas operativas de laboratorio. Comisión por fuente sin filas que la calculen. |
| 12 | Lab vs producción | Parcial | `lab_meta_demo` aislado. `leads_prueba_formulario` vive en `public`. |

## Inventario de filas en el corte

| Objeto | Filas |
| --- | ---: |
| `prospectos` | 15 |
| `leads` | 15 |
| `perfiles_inversion` | 15 |
| `scoring` | 15 |
| `desarrollos` | 1 |
| `torres` | 6 |
| `inventario` / `unidades` / `unidad_historial` | 605 / 605 / 605 |
| `easybroker_propiedades` | 365 |
| `fuentes_lead` | 10 |
| `campanas` | 0 |
| `matches` | 0 |
| `interacciones` | 0 |
| `comisiones` | 0 |
| `webhook_eventos` | 0 |
| `borradores` | 2 |
| `citas` | 2 |
| `seguimientos` | 4 |
| `leads_prueba_formulario` | 3 |
| `lab_meta_demo.campaigns` / `adsets` / `ads` / `insights_daily` | 4 / 8 / 16 / 224 |

Temperatura de los 15 leads, idéntica a la de los 15 prospectos enlazados: caliente 6, tibio 6, frío 3. Divergencia de temperatura, estado, `ultimo_msg_cliente_at` y `proximo_seguimiento_at` entre cada par lead–prospecto: 0.

Unidades por estatus: disponible 204, apartado 7, reservado 6, vendido 388. `lista_vigente = false` en las 605 unidades y en las 605 filas de `inventario`.

## Índice

- [Paquete operativo v1 (SQL, RLS, contratos, plantillas, n8n, purga, RACI)](paquete-operativo-v1.md)
- [Registro de brechas](registro-brechas.md)
- [Mapa 01 — Arquitectura del ecosistema](mapas/01-arquitectura-del-ecosistema.md)
- [Mapa 02 — Funnel de monetización](mapas/02-funnel-de-monetizacion.md)
- [Mapa 03 — WhatsApp inbound](mapas/03-flujo-whatsapp-inbound.md)
- [Mapa 04 — Flujo outbound](mapas/04-flujo-outbound.md)
- [Mapa 05 — ERD fuente de verdad](mapas/05-erd-fuente-de-verdad.md)
- [Mapa 06 — Dualidad prospectos y leads](mapas/06-dualidad-prospectos-leads.md)
- [Mapa 07 — Inventario y matching](mapas/07-inventario-y-matching.md)
- [Mapa 08 — Edge Functions](mapas/08-edge-functions.md)
- [Mapa 09 — Seguridad y acceso](mapas/09-seguridad-y-acceso.md)
- [Mapa 10 — Priorización a producción](mapas/10-priorizacion-a-produccion.md)
- [Mapa 11 — Métricas que monetizan](mapas/11-metricas-que-monetizan.md)
- [Mapa 12 — Lab vs producción](mapas/12-lab-vs-produccion.md)

## Gate de pauta

La pauta pagada permanece cerrada mientras exista cualquiera de estas condiciones, medidas en el mismo proyecto:

1. `webhook_eventos` no recibe el payload de Meta con idempotencia, o `interacciones` de dirección `entrante` sigue en cero tras una prueba controlada.
2. Un borrador puede salir a WhatsApp sin pasar por `estado = aprobado` y por la ventana de 24 horas.
3. `lista_precios_vigente()` devuelve falso y aun así existe un camino que publique `precio_lista`.
4. `matches` no propone unidades disponibles a un lead tibio o caliente con perfil de inversión.
5. `leads_prueba_formulario` o `lab_meta_demo` pueden mezclarse en el cálculo de comisión por fuente.
6. `anon` obtiene un privilegio distinto de `INSERT` sobre `leads_prueba_formulario`.
