# Mapa 04 — Flujo outbound

| Campo | Valor |
| --- | --- |
| Identificador | MAPA-04 |
| Estado | Parcial |
| Corte | 2026-10-05 |
| Objetos ancla | `borradores`, `public.borradores_cumplimiento`, `private.interaccion_reglas`, `ultimo_msg_asesor_at`, `proximo_seguimiento_at` |

## 1. Propósito operativo

Ningún texto sale al cliente sin dejar un borrador y sin pasar el control de cumplimiento. El control protege la reputación del número de WhatsApp y la lista de precios. La política de Meta de ventana de 24 horas está especificada; la base todavía no la evalúa.

## 2. Conexión sistémica

### Entrada

Disparadores previstos: respuesta de agente, vencimiento de seguimiento, confirmación de cita.

Objetos que ya pueden originar un texto:

- `borradores` (2 filas: 1 `pendiente`, 1 `aprobado`).
- `seguimientos` (2 `pendiente`, 1 `completado`, 1 `cancelado`).
- `citas` (2 `programada`).

El borrador pertenece a `prospectos` (`prospecto_id` obligatorio), no a `leads`. Canal default `whatsapp`. Estados: `pendiente`, `aprobado`, `rechazado`, `enviado`.

### Tránsito

Trigger `trg_borradores_cumplimiento` llama a `public.borradores_cumplimiento` en cada insert y update.

1. Si `contiene_lista_negra(contenido)` devuelve un valor, el borrador se rechaza con `check_violation`. La función compacta el texto y busca dominios y teléfonos de canales ajenos al número operativo.
2. Si el estado pasa a `aprobado` o `enviado` y el contenido parece un precio, y `lista_precios_vigente()` es falso, el borrador se rechaza. El mensaje de la regla remite a responder con `/sinprecio` mientras la lista del inventario no esté confirmada.
3. Al aprobar, si `aprobado_at` es nulo, se sella con `now()`. Al marcar `enviado`, se sella `enviado_at`.

`lista_precios_vigente()` es verdadero solo si existe al menos una fila de `inventario` con `lista_vigente`. En el corte todas son falsas, así que la función es falsa: un borrador aprobado con precio no puede guardarse.

La misma barrera está en `private.interaccion_reglas` para `interacciones` en estado `aprobado` o `enviado`. Además, un contenido con precio en esos estados solo lo aprueba el agente `comercial` (o la sesión `postgres` / `supabase_admin`).

La ventana de 24 horas usa, en la especificación, `ultimo_msg_cliente_at`. La columna existe en `prospectos` y en `leads`. No existe función, check ni trigger que reste esa marca a `now()` y exija plantilla cuando la diferencia supere 24 horas. `borradores.plantilla` está preparada para guardar el nombre de la plantilla HSM.

### Salida

| Salida especificada | Soporte en datos | Ejecución |
| --- | --- | --- |
| HTTP a Meta Cloud API, texto libre con ventana abierta | `borradores.contenido`, `borradores.estado` | Sin cliente HTTP |
| HTTP con plantilla si la ventana está cerrada | `borradores.plantilla` | Sin registro de plantillas aprobadas por Meta |
| Interacción saliente | `interacciones.direccion = saliente`, estado `enviado` | 0 filas |
| Sello de asesor | `ultimo_msg_asesor_at` | Columna presente en lead y prospecto |
| Próximo contacto | `proximo_seguimiento_at` y filas de `seguimientos` | Columna y tabla presentes |

El agente `followup` puede crear y modificar interacciones y puede modificar el lead sin cambiar identidad, fuente ni asignación. El agente `comercial` es quien puede aprobar precio.

## 3. Análisis por capas

### Inputs

- Texto propuesto por un agente o por un asesor (`creado_por`).
- Decisión humana (`estado`, `aprobado_por`).
- Marcas `ultimo_msg_cliente_at` para la ventana, todavía sin evaluador.
- Vigencia de lista de precios.

### Outputs

- Borrador que sobrevive al trigger, o excepción que impide la escritura.
- Cuando el envío exista: interacción saliente, `ultimo_msg_asesor_at` y `proximo_seguimiento_at`.

### Control de temperatura

La velocidad y el tono según temperatura son una política de redacción. La base no elige plantilla ni cadencia a partir de `temperatura`. Lo que sí hace el esquema es exponer la temperatura al redactor (`v_leads_temperatura`) y separar a los fríos inactivos (`v_leads_frios`, umbral de 48 horas sobre `prospectos`).

### Consumos y recursos

| Recurso | Situación |
| --- | --- |
| Tarifas de la Cloud API y plantillas Utility/Marketing | Sin envíos que las consuman. |
| Supervisión humana | Modelada: un borrador `pendiente` espera `aprobado_por`. Vista `v_borradores_pendientes` lista la cola con el teléfono del prospecto. |
| Bloqueo de precio y de canales ajenos | Activo en cada escritura de borrador. |

## 4. Contrato de datos

Vista de cola, `security_invoker = true`:

`v_borradores_pendientes` une borradores `pendiente` con el prospecto y marca `alerta_lista_negra` si el contenido dispara `contiene_lista_negra`.

`v_alertas_lista_negra` revisa notas y origen de prospectos, notas de seguimientos, lugar y notas de citas, y notas de borradores.

## 5. Evidencia

- 1 borrador `pendiente` y 1 `aprobado`.
- `lista_precios_vigente()` falso por 605 filas con `lista_vigente = false`.
- Cero interacciones salientes.
- Comentario de `borradores`: deben pasar por el subagente auditor de inventario y aprobarse antes de enviarse. El trigger implementa la lista negra y el precio; el subagente como proceso externo no está en el catálogo.

## 6. Criterio de producción

Un mensaje de salida de producción cumple las cuatro condiciones en orden: borrador creado en `pendiente`, transición a `aprobado` con `aprobado_por` humano, evaluación explícita de la ventana de 24 horas contra `ultimo_msg_cliente_at`, y una interacción `saliente` / `enviado` cuyo `id_externo` sea el id devuelto por Meta. Si la ventana está cerrada, `plantilla` es obligatoria y el contenido libre no se envía. Un contenido con precio sigue bloqueado mientras `lista_precios_vigente()` sea falso.
