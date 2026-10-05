# Mapa 09 — Seguridad y acceso

| Campo | Valor |
| --- | --- |
| Identificador | MAPA-09 |
| Estado | Operativo |
| Corte | 2026-10-05 |
| Objetos ancla | RLS de `public`, `agente_permisos`, `private.crm_permiso`, `private.crm_guard_write` |

## 1. Propósito operativo

El teléfono, el presupuesto y el perfil de inversión se leen solo por un rol que el proyecto haya autorizado. `anon` no consulta el CRM. El asesor autenticado todavía no tiene políticas de fila. `service_role` existe para el backend y salta RLS, así que permanece fuera de clientes, repositorios públicos y variables `NEXT_PUBLIC_*`.

## 2. Conexión sistémica

### Entrada

Tres contextos de llamada:

| Contexto | Rol | Cómo entra |
| --- | --- | --- |
| Formulario público de práctica | `anon` | Data API. Un privilegio: `INSERT` en `leads_prueba_formulario`. |
| Panel de asesor, cuando exista | `authenticated` | Hoy no hay políticas sobre tablas CRM para este rol. |
| Agente de negocio | `crm_agent` | `public.asumir_agente` fija el agente. RLS usa `private.crm_permiso`. |
| Backend, sync, alerta, migraciones operativas | `service_role` | Llave de servicio. `rolbypassrls = true`. |

`lab_meta_demo` no otorga `USAGE` a `anon` ni a `authenticated`.

### Tránsito

RLS está activo en las 22 tablas de `public`. El efecto depende de si hay política:

| Grupo | Políticas | Efecto para roles sin bypass |
| --- | --- | --- |
| `prospectos`, `borradores`, `citas`, `seguimientos`, `inventario`, `easybroker_propiedades`, `webhook_eventos` | Ninguna | Denegación. El advisor `rls_enabled_no_policy` los marca como INFO. Es el cierre deseado: solo `service_role` entra. |
| `leads`, `campanas`, `comisiones`, `desarrollos`, `fuentes_lead`, `interacciones`, `matches`, `perfiles_inversion`, `scoring`, `torres`, `unidad_historial`, `unidades`, `agente_permisos` | `SELECT` / `INSERT` / `UPDATE` para `crm_agent`, predicado `private.crm_permiso(tabla, accion)` | El rol pasa y la matriz decide la celda. |
| `leads_prueba_formulario` | `INSERT` para `anon` con `consentimiento_privacidad = true` | Alta pública. Sin política de `SELECT`: el anónimo no lee lo que insertó. |

`private.crm_guard_write` repite el permiso en trigger, cubre `DELETE` y añade límites por agente:

- `comercial` en `unidades` solo cambia estatus y `codigo_vendedor`.
- `followup` en `leads` no cambia identidad, fuente, campaña, tipo, empresa, `prospecto_id` ni asignación.
- `prospecting` no cambia `asignado_a`.
- `comercial` no reescribe nombre, teléfono, email, fuente ni campaña.
- `prospecting` solo inserta interacciones `entrante` o canal `sistema`.
- El actor de la fila se rellena con el agente asumido cuando venía vacío o como `sistema`.

`unidad_historial` no tiene privilegio de escritura para `crm_agent` ni para `service_role` más allá de `SELECT` en el caso del agente. La bitácora la escribe la función dueña del trigger.

Las diez vistas de reporte usan `security_invoker = true`. Heredan el RLS de quien consulta. `authenticated` tiene grants amplios sobre la mayoría de esas vistas; como no puede leer `prospectos`, la vista regresa vacía. Ese grant amplio es la brecha latente B-13: el día que se agregue una política de asesor, el privilegio de la vista ya estaría concedido, incluyendo columnas de teléfono.

`public.contiene_lista_negra`, `lista_precios_vigente` y `borradores_cumplimiento` son ejecutables por `anon` y `authenticated`. La primera revela si un texto contiene un canal prohibido. La segunda revela si existe alguna fila con lista vigente, sin devolver precios. Conviene revocar `EXECUTE` a `anon` cuando el formulario público no las necesite.

`lead_alert_verify_secret` solo la ejecuta `service_role`.

### Salida

Autorización o rechazo. Los rechazos de negocio usan `errcode` `42501` (privilegio) o `check_violation` (precio, lista negra, comisión, unidad vendida).

## 3. Análisis por capas

### Inputs

- JWT de `anon` o `authenticated`.
- Sesión `crm_agent` más el valor fijado por `asumir_agente`.
- Llave `service_role` en backend y en Edge Functions.

### Outputs

- Filas filtradas por la matriz, o cero filas por RLS.
- Excepciones de trigger cuando el agente se sale de su columna.

### Control de temperatura

La temperatura no tiene política propia por valor. Un lead caliente y un lead frío pasan por la misma matriz. El agente `matching` y el agente `comercial` pueden leer leads; `followup` también. No hay columna `asesor_id` ni política `asignado_a = auth.uid()`. `asignado_a` es texto libre. La visibilidad “solo el asesor asignado” está especificada para el panel y todavía no es una política RLS. Hoy el aislamiento del lead caliente es más grueso: el rol anónimo no lo ve, y el backend con `service_role` lo ve completo.

### Consumos y recursos

- Evaluación de políticas RLS y de `private.crm_permiso` en cada sentencia del rol `crm_agent`.
- `crm_permiso` es `SECURITY DEFINER` con `search_path` vacío y lee `agente_permisos`. Cambiar la matriz es una decisión de migración: el comentario de la tabla lo dice así.

## 4. Contrato de datos

Matriz vigente (leer / crear / modificar / borrar). Borrar es falso en todas las celdas observadas.

| Tabla | inventario | matching | prospecting | followup | comercial |
| --- | --- | --- | --- | --- | --- |
| `desarrollos`, `torres` | L/C/M | L | L | L | L |
| `unidades` | L/C/M | L | L | L | L/M (estatus y código) |
| `unidad_historial` | L | L | — | — | L |
| `leads` | — | L | L/C/M | L/M | L/M |
| `perfiles_inversion` | — | L | L/C/M | L | L/M |
| `scoring` | — | L | L/C/M | L | L/C/M |
| `matches` | — | L/C/M | — | L | L/M |
| `interacciones` | — | L | L/C (entrada) | L/C/M | L/C/M |
| `comisiones` | — | L | — | — | L/C/M |
| `fuentes_lead` | — | L | L/C | L | L/C |
| `campanas` | — | L | L/C/M | L | L |
| `agente_permisos` | L | L | L | L | L |

`—` indica que esa combinación agente/tabla no tiene fila que conceda permiso. Sin fila, `crm_permiso` devuelve falso.

## 5. Evidencia

- `rolbypassrls`: verdadero solo en `service_role` y `postgres`, entre los roles de aplicación revisados.
- Advisor de seguridad del corte: 11 hallazgos INFO `rls_enabled_no_policy` (4 de `lab_meta_demo` y 7 de `public`). Cero hallazgos de RLS desactivado en el resultado.
- Migración `20261004133314 restrict_core_tables_to_service_role`.
- Política `leads_prueba_anon_insert`.

## 6. Criterio de producción

Se considera vigente mientras `anon` conserve un único privilegio de tabla, `service_role` no aparezca en código de cliente, y cada pantalla de asesor nazca con una política RLS explícita (por asignación o por rol de negocio) en lugar de reutilizar la llave de servicio. Antes de esa política se revocan los grants de `authenticated` sobre vistas que exponen teléfono. La matriz de agentes se modifica solo por migración.
