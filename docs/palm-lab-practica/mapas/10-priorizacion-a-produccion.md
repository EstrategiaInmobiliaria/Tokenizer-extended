# Mapa 10 — Priorización a producción

| Campo | Valor |
| --- | --- |
| Identificador | MAPA-10 |
| Estado | Especificado |
| Corte | 2026-10-05 |
| Objetos ancla | laboratorio `palm-lab-practica`, registro de brechas B-01 a B-15 |

## 1. Propósito operativo

La salida a preventa comercial es una secuencia. Cada paso deja evidencia en el proyecto antes de abrir el siguiente. La pauta pagada es el último paso de captura, nunca el primero. Este mapa no añade objetos: ordena los que los otros mapas ya midieron.

## 2. Conexión sistémica

### Entrada

Estado de laboratorio en el corte:

- Esquema CRM migrado y con RLS.
- 15 leads de semilla, scoring de migración, lista de precios apagada.
- Canal WhatsApp sin receptor y sin emisor.
- Inventario canónico cargado (605) y catálogo EasyBroker cargado (365), sin cruce por `id_externo`.
- Formulario de práctica y esquema `lab_meta_demo` con datos sintéticos.

### Tránsito

Orden de despliegue. Un paso no se declara cerrado con una tarea pendiente: se declara cerrado con la prueba de la columna “Hecho observable”.

| Paso | Nombre | Hecho observable en este proyecto | Situación en el corte |
| --- | --- | --- | --- |
| 1 | Cuenta y número de Meta | El número 55 4018 0018 queda registrado como configuración del receptor, no solo en la especificación. | Número declarado. Sin fila de configuración. |
| 2 | Plantillas | Cada plantilla que el outbound puede usar existe en `borradores.plantilla` con nombre aprobado por Meta. | Columna lista. Catálogo de plantillas vacío. |
| 3 | Webhook | Un evento de prueba produce una fila idempotente en `webhook_eventos` y una interacción entrante. | 0 y 0. Brecha B-01, B-04. |
| 4 | Borde de funciones | `verify_jwt = false` solo con secreto. `easybroker-load` retirada. Sync con calendario. | Secretos activos. Load en 410. Sin cron. |
| 5 | Inventario homologado | `id_externo` o una tabla puente une la unidad canónica con EasyBroker cuando aplique. `lista_vigente` refleja la confirmación humana. | 605 externos nulos. Vigencia falsa en todas. |
| 6 | Calificación | Un mensaje de prueba cambia `scoring` con un `modelo` distinto de `migracion-prospectos` y actualiza temperatura en lead y prospecto en la misma transacción. | 15 filas del modelo de migración. |
| 7 | Matching | De 1 a 3 matches `propuesto` sobre `v_unidades_ofertables` para un lead tibio o caliente. | 0 matches. |
| 8 | Outbound gobernado | Borrador aprobado, ventana de 24 h evaluada, interacción saliente con id de Meta. | Reglas de precio y lista negra activas. Ventana y envío ausentes. |
| 9 | Comisión | Una comisión de prueba en estado `potencial` cuelga de un match real y no avanza a `pagada` si la unidad no está `vendido`. | Regla activa. 0 filas. |
| 10 | Pauta | La primera fila de `campanas` con presupuesto nace después de los pasos 3, 6 y 8. | 0 campañas. |

### Salida

Un CRM en el que un lead originado por una campaña tiene interacciones, temperatura, matches y, si cierra, una comisión cuya unidad y cuyo match se pueden recorrer con llaves foráneas. Ese estado no es el del corte.

## 3. Análisis por capas

### Inputs

- Migraciones aplicadas hasta `20261005104549`.
- Aprobaciones de Meta Business (fuera de la base; este mapa las exige como prerequisito del paso 2).
- Confirmación humana de `lista_vigente`.
- Secretos ya separados: `SYNC_SECRET`, secreto de Vault de la alerta, `EASYBROKER_API_KEY`, `RESEND_API_KEY`, llave de servicio inyectada.

### Outputs

Componentes activados en el orden de la tabla, cada uno con una fila o una respuesta HTTP de prueba conservada.

### Control de temperatura

Desde el primer mensaje posterior a la pauta, el lead recibe temperatura `frio`, `tibio` o `caliente` en la misma transacción que crea la interacción entrante. Un lead de pauta sin temperatura no se considera capturado. El corte todavía no tiene ese camino: las temperaturas existentes pertenecen a la semilla.

### Consumos y recursos

- Trabajo de ingeniería sobre el receptor, el emisor, el motor de matches y el cron de sync.
- Validación de la ventana de 24 horas y de las plantillas antes de cualquier envío masivo.
- Prueba de extremo a extremo sobre un teléfono de control, con purga posterior para que no entre en las métricas (mapa 12).

## 4. Contrato de datos

No introduce tablas. Usa el registro de brechas como lista de cierre. Una brecha bloqueante (B-01, B-02, B-05, B-07, B-08, B-11, B-12) mantiene el paso correspondiente abierto.

## 5. Evidencia

El corte completo está resumido en el índice de `docs/palm-lab-practica/README.md`. Este mapa es la lectura de ese corte en orden de dependencia.

## 6. Criterio de producción

La preventa con pauta empieza el día en que los pasos 1 a 8 tienen un hecho observable en producción y el paso 10 inserta la primera campaña. Abrir presupuesto de `campanas` con `webhook_eventos` vacío deja leads fuera de la fuente de verdad. Esa combinación permanece prohibida.
