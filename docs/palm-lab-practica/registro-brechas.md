# Registro de brechas

Cada brecha es una diferencia entre el proceso descrito para producción y el estado del proyecto `palm-lab-practica` en el corte 2026-10-05. El identificador es estable para auditoría.

| ID | Mapa | Severidad | Evidencia | Cierre |
| --- | --- | --- | --- | --- |
| B-01 | 01, 03 | Bloquea pauta | No existe Edge Function receptora de Meta. `webhook_eventos` tiene 0 filas. | Función que valide la firma del webhook, persista el payload y avance `estado` a `procesado` o `error`. |
| B-02 | 01, 04 | Bloquea pauta | Ningún objeto del proyecto llama a la Cloud API de WhatsApp. | Envío único, posterior a borrador `aprobado`, con registro en `interacciones`. |
| B-03 | 01, 10 | Alcance | n8n no aparece en tablas, funciones, triggers ni extensiones. | Declarar el workflow como sistema externo y hacer que lea y escriba solo vía `service_role`. |
| B-04 | 03 | Integridad | `interacciones` tiene 0 filas. El índice único `(canal, id_externo)` está listo y sin uso. | Cada mensaje entrante inserta una interacción `entrante` / `recibido` con `id_externo` de Meta. |
| B-05 | 04 | Política Meta | No hay función que compare `ultimo_msg_cliente_at` con un intervalo de 24 horas. | Regla de salida: texto libre solo con ventana abierta; plantilla aprobada si está cerrada. |
| B-06 | 06 | Integridad | 15 pares lead–prospecto coinciden hoy. No hay trigger de sincronización. | Una transacción que escriba primero `prospectos` y después `leads`, o un trigger que rechace la divergencia. |
| B-07 | 07 | Bloquea oferta | `matches = 0`. `private.match_reglas` valida una fila; no rankea unidades. | Motor que inserte de 1 a 3 `matches` `propuesto` sobre `v_unidades_ofertables`. |
| B-08 | 07 | Bloquea precio | `lista_vigente = false` en 605/605. `unidades.id_externo` es nulo en 605/605. | Confirmación de lista y cruce explícito EasyBroker → unidad canónica. |
| B-09 | 08 | Operación | `pg_cron` no está instalado. `cron.job` no existe. `easybroker-sync` queda en invocación manual. | Programación horaria con el secreto de cabecera, o registro de que el scheduler vive fuera. |
| B-10 | 08 | Temperatura | `lead-alert-email` escucha `INSERT` en `leads_prueba_formulario`, no la temperatura `caliente` de `leads`. | Disparador separado para leads calientes del núcleo, sin reutilizar la tabla de prueba. |
| B-11 | 02, 11 | Monetización | `campanas = 0`, `comisiones = 0`. La comisión por fuente no tiene numerador ni costo de campaña. | Primera campaña con presupuesto y primera comisión solo después de un match y una unidad vendida. |
| B-12 | 12 | Aislamiento | `leads_prueba_formulario` está en `public` y `anon` puede insertar. El trigger llama a la alerta de correo. | Mantenerla fuera de las vistas de comisión. Purgar sus 3 filas antes del corte de producción. |
| B-13 | 05, 09 | Superficie | Las vistas de reporte tienen `security_invoker = true` y `GRANT` amplio a `authenticated`. Las tablas base no tienen política para ese rol, así que hoy la lectura regresa vacía. | Revocar esos grants antes de abrir políticas de asesores, para que el privilegio nazca junto con la política. |
| B-14 | 03, 05 | Calificación | Las 15 filas de `scoring` usan `modelo = migracion-prospectos`. `clasificar_lead` es SQL determinista. | Registrar el modelo vivo que recalcule temperatura y clase, y retirar la vigencia anterior. |
| B-15 | 08 | Higiene | `easybroker-load` responde HTTP 410. Sigue desplegada con `verify_jwt = true`. | Retirar la función del proyecto cuando el tablero lo permita. |

## Lo que el corte sí sostiene

- RLS activo en las 22 tablas de `public` y en las 4 de `lab_meta_demo`.
- `anon` tiene un solo privilegio de tabla: `INSERT` en `leads_prueba_formulario`, con `CHECK (consentimiento_privacidad = true)`.
- `service_role` tiene `rolbypassrls = true` y es el único rol con privilegios completos sobre el núcleo conversacional.
- `crm_agent` no salta RLS. Su acceso pasa por `private.crm_permiso` y por `public.asumir_agente`.
- `unidad_historial` es de solo lectura para los agentes: `crm_agent` y `service_role` tienen `SELECT`. El historial lo escribe `private.unidad_historial_escribir`.
- Precio en borrador o interacción aprobado/enviado queda rechazado mientras `lista_precios_vigente()` sea falso.
- Una comisión `pagada` exige unidad `vendido`. Una comisión `devengada` exige unidad `reservado` o `vendido`. Una comisión `pagada` o `cancelada` no cambia de estado.
- Un match `aceptado` aparta la unidad. Una unidad que deja de estar `disponible` cancela matches `propuesto` y `ofrecido`.
