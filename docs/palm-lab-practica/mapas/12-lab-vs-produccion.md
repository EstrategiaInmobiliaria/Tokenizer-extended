# Mapa 12 — Lab vs producción

| Campo | Valor |
| --- | --- |
| Identificador | MAPA-12 |
| Estado | Parcial |
| Corte | 2026-10-05 |
| Objetos ancla | esquema `lab_meta_demo`, tabla `public.leads_prueba_formulario` |

## 1. Propósito operativo

Los datos de demostración no entran en la comisión por fuente, no disparan la operación de un asesor sobre un cliente real y no se mezclan con `prospectos`, `leads`, `unidades` ni `comisiones`. El laboratorio necesita esos datos para probar formularios y anuncios. El aislamiento es el proceso que los mantiene a un lado.

## 2. Conexión sistémica

### Entrada

| Origen de prueba | Dónde cae | Filas |
| --- | --- | ---: |
| Simulación de campañas, conjuntos, anuncios e insights diarios | `lab_meta_demo.campaigns`, `adsets`, `ads`, `insights_daily` | 4, 8, 16, 224 |
| Formulario público de práctica | `public.leads_prueba_formulario` | 3 |
| Semilla del CRM (15 prospectos, scoring `migracion-prospectos`) | Tablas núcleo de `public` | 15 |

La semilla del núcleo es el punto delicado: vive en las mismas tablas que usará la preventa. No está marcada por una columna `es_laboratorio`. Se reconoce por el `scoring.modelo` y por el historial de la migración `crm_erd_fuente_verdad_semilla`.

### Tránsito

`lab_meta_demo` está separado de verdad en este corte:

- Esquema propio, creado por `20261004190247 lab_meta_demo_schema` y sembrado por `20261004190304 lab_meta_demo_seed`.
- RLS activo y sin políticas en las cuatro tablas.
- `anon` y `authenticated` no tienen `USAGE` del esquema.
- No hay grants de tabla para `anon`, `authenticated`, `service_role` ni `public` en el catálogo consultado.
- No hay llave foránea desde `lab_meta_demo` hacia `leads`, `fuentes_lead` ni `comisiones`.

Un reporte que no nombre el esquema `lab_meta_demo` no puede mezclar sus 224 insights con la comisión.

`leads_prueba_formulario` está aislada por privilegio y no por esquema:

- Sigue en `public`.
- `anon` inserta si `consentimiento_privacidad` es verdadero.
- No hay `SELECT` para `anon`. La lectura es de `service_role` o SQL de plataforma.
- Checks de longitud, teléfono, email, perfil y consentimiento.
- No tiene FK hacia `leads` ni hacia `prospectos`. Un insert aquí no crea un lead de negocio.
- Sí dispara `lead-alert-email`. El correo avisa a las personas del laboratorio y el cuerpo identifica la tabla de prueba.
- Comentario de tabla: práctica, solo insert anónimo, lectura por service role.

Eso impide el cruce analítico accidental por join, y no impide que un humano sume “leads” contando esta tabla junto con `leads`. La métrica del mapa 11 tiene que nombrar `public.leads` y excluir esta tabla por escrito.

### Salida

Antes del corte de producción se purgan o se archivan:

- Las 3 filas de `leads_prueba_formulario`.
- El contenido de `lab_meta_demo`, o se deja el esquema sin grants, como está, y fuera de todo reporte.
- La semilla de 15 leads del núcleo, si esos registros no son clientes reales de preventa. El corte no trae una bandera que lo certifique; la decisión de purga es operativa y queda registrada con el conteo antes y después.

La purga de la semilla respeta las llaves: primero hijas (`scoring`, `perfiles_inversion`, `borradores`, `citas`, `seguimientos`, interacciones y matches si los hubiera) y después `leads` y `prospectos`. `unidad_historial` y `unidades` no forman parte de esa purga.

## 3. Análisis por capas

### Inputs

- Formularios de prueba con UTM, perfil y rango de presupuesto.
- Campañas sintéticas de Meta en `lab_meta_demo`.
- Semilla de demostración del ERD.

### Outputs

- Esquema de anuncios ilegible para `anon` y `authenticated`.
- Formulario que acumula filas sin convertirse en `leads`.
- Núcleo todavía compartido con la semilla.

### Control de temperatura

Las temperaturas de prueba no deben abrir la alerta de asesor del núcleo ni mover `v_leads_frios`.

- `lab_meta_demo` no tiene columna de temperatura ni conexión con leads. Cumple.
- `leads_prueba_formulario` no tiene temperatura. Su perfil (`A_Inversionista`, `B_Tecnologia_IA`, `C_Patrimonial`) no escribe `scoring`. Cumple.
- Su trigger de correo sí notifica. Esa notificación es de laboratorio y debe seguir diciéndolo en el cuerpo, como ya lo hace.
- La semilla de 15 sí tiene temperatura dentro de `prospectos` y `leads`. Esas 6 calientes aparecen en `v_leads_temperatura`. Si un asesor usa esa vista como cola real, verá la semilla. Aislarlas exige purgarlas o marcarlas antes de operar.

### Consumos y recursos

- Almacenamiento secundario: 224 insights diarios y 3 formularios. Tamaño menor frente a 605 unidades.
- Rutina de purga: todavía no hay función `purge_lab`. El procedimiento es el orden de borrado descrito arriba, ejecutado con rol de plataforma, con conteo previo.
- El formulario público sigue aceptando inserts mientras la política anónima exista. En producción comercial, esa política se elimina o el formulario apunta a otro proyecto.

## 4. Contrato de datos

`leads_prueba_formulario` exige:

- `nombre` de 2 a 120 caracteres.
- `telefono` contra `^\+?[0-9]{10,15}$`.
- `email` opcional con formato y tope de 254.
- `perfil` en `A_Inversionista`, `B_Tecnologia_IA`, `C_Patrimonial`.
- `consentimiento_privacidad = true`.
- `origen` default `formulario_prueba`, tope 60.
- `mensaje` tope 2 000. `user_agent` tope 500.

`lab_meta_demo.insights_daily` tiene llave primaria `(date, ad_id)`.

## 5. Evidencia

- Migraciones `create_leads_prueba_formulario`, `leads_prueba_presupuesto_por_perfil_y_grants`, `lab_meta_demo_schema`, `lab_meta_demo_seed`.
- `has_schema_privilege` de `anon` y `authenticated` sobre `lab_meta_demo`: falso.
- Grants de `lab_meta_demo` hacia esos roles: ninguno.
- Cero llaves foráneas entre el formulario de prueba y `leads`.

## 6. Criterio de producción

El día del arranque, una consulta de comisión por fuente sobre `public.leads` y `public.comisiones` no puede leer `lab_meta_demo` ni `leads_prueba_formulario` ni siquiera por error de búsqueda de nombres. La semilla de demostración que comparta tablas con la preventa está purgada o identificada con una marca que todas las vistas de métricas filtran. El formulario anónimo deja de escribir en el proyecto de producción, o sigue escribiendo en una tabla que ninguna métrica y ningún agente comercial consultan.
