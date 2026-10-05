# Mapa 07 — Inventario y matching

| Campo | Valor |
| --- | --- |
| Identificador | MAPA-07 |
| Estado | Bloqueado |
| Corte | 2026-10-05 |
| Objetos ancla | `unidades`, `inventario`, `easybroker_propiedades`, `matches`, `private.match_reglas`, `v_unidades_ofertables` |

## 1. Propósito operativo

El matching cruza la oferta de Palm Diamante con un lead que ya tiene perfil. El resultado permitido es un conjunto corto de unidades realmente disponibles, escrito en `matches`, listo para que un humano lo convierta en borrador. En este corte el cruce automático no ha corrido: `matches` tiene 0 filas. La oferta de precio está cerrada porque la lista no está vigente.

## 2. Conexión sistémica

### Entrada

Dos inventarios conviven.

| Inventario | Papel | Filas | Precio publicable |
| --- | --- | ---: | --- |
| `unidades` + `torres` + `desarrollos` | Canónico. El match apunta aquí. | 605 | No. `lista_vigente = false` en todas. |
| `inventario` | Lista oficial legado, sincronizada por trigger con `unidades`. | 605 | No. Misma bandera. Comentario: si es falso, ningún precio se da al cliente. |
| `easybroker_propiedades` | Copia de lectura del catálogo externo. | 365 | No se ofrece al lead. No hay FK hacia `unidades`. |

Estatus EasyBroker: `published` 107, `suspended` 222, `not_published` 31, `rented` 2, `sold` 1, nulo 2. Una búsqueda por texto `palm` o ciudad Acapulco devuelve 16 filas. `unidades.id_externo` es nulo en las 605. El catálogo externo y el canónico todavía no están homologados. Brecha B-08.

Estatus canónico: `disponible` 204, `apartado` 7, `reservado` 6, `vendido` 388.

### Tránsito

El tránsito algorítmico —elegir de 1 a 3 unidades— no está implementado como función. Lo que sí está implementado es la compuerta de cada fila que alguien inserte en `matches`:

`private.match_reglas`, trigger antes de insertar o actualizar:

- En estado `propuesto`, `ofrecido` o `aceptado`, la unidad tiene que estar `disponible`.
- Si `precio_ofrecido` viene informado, `lista_vigente` de esa unidad tiene que ser verdadero. Hoy esa rama rechaza cualquier precio.
- Al pasar a `aceptado`, la unidad se actualiza a `apartado` dentro de la misma regla.
- Índice único: un solo match `aceptado` por unidad, y un solo match abierto (`propuesto`, `ofrecido`, `aceptado`) por par lead–unidad.

`private.unidad_reglas` cierra el círculo. Una unidad `vendido` no se reabre sin `crm.reapertura_motivo`. Volver a `disponible` exige que no haya match `aceptado`. Si la unidad deja de estar disponible, los matches `propuesto` y `ofrecido` pasan a `cancelado` con motivo `unidad_no_disponible`.

`v_unidades_ofertables` es el conjunto legal de entrada del motor futuro: estatus `disponible`, y `precio_publicable` nulo mientras `lista_vigente` sea falso. En el corte esa vista devuelve 204 unidades sin precio publicable.

Insumos de demanda ya poblados para cuando el motor exista:

- `perfiles_inversion`: presupuesto objetivo, mínimo y máximo, moneda, forma de pago, horizonte, yield, objetivo, tipología, plazo. 15 filas.
- `scoring` vigente. El agente `matching` puede leer scoring, perfiles, unidades y leads, y puede crear y modificar `matches`. No puede crear leads ni cambiar inventario.

### Salida

| Salida especificada | Estado |
| --- | --- |
| Filas en `matches` | 0. Estados previstos: `propuesto`, `ofrecido`, `aceptado`, `rechazado`, `vencido`, `cancelado`. `score` de 0 a 100. `explicacion` y `variables` jsonb. |
| Borrador comercial derivado del match | No hay columna `match_id` en `borradores` ni trigger que copie un match a un borrador. La traducción a propuesta es un paso de aplicación todavía por escribir. |

## 3. Análisis por capas

### Inputs

- Presupuesto, plazo, forma de pago y tipología del perfil.
- Disponibilidad en tiempo de lectura de `unidades.estatus`.
- Catálogo EasyBroker como referencia externa, no como inventario ofertable.

### Outputs

- Match `propuesto` sin precio mientras la lista siga caída, o match con `precio_ofrecido` el día en que `lista_vigente` sea verdadero.
- Apartado automático de la unidad al aceptar.
- Cancelación automática de propuestas si la unidad se aparta, reserva o vende por otro camino.

### Control de temperatura

Umbral de negocio de este mapa: un match se ofrece a temperatura `tibio` o `caliente`. El frío entra a nutrición (mapa 02) y no a `matches`.

Esa compuerta no está en `match_reglas`. La función no lee `leads.temperatura` ni `scoring`. Un agente `matching` podría insertar un match para un lead frío y la base lo aceptaría si la unidad está disponible. El umbral queda como control de la aplicación que inserte, hasta que se promueva a trigger.

### Consumos y recursos

| Recurso | Situación |
| --- | --- |
| Reglas de integridad de match | Activas en cada escritura. |
| Consulta paramétrica de ofertables | Vista lista. No hay tipo geoespacial ni índice espacial en `unidades`. EasyBroker sí guarda `lat`/`lng` como `float8`, sin índice espacial. |
| API EasyBroker | `easybroker-sync` lee con pausa, backoff y tope de detalles. No borra filas locales. |
| Ranking 1 a 3 | Especificado. Sin función de score de adecuación. `matches.score` espera el resultado. |

## 4. Contrato de datos

`inventario.estatus`: `disponible`, `apartado`, `reservado`, `vendido`. El canónico usa el enum `unidad_estatus` con los mismos literales.

`lista_vigente` default `false` en ambas tablas. Comentario de `inventario`: solo se confirma de forma explícita cuando la lista puede usarse con clientes.

`matches.explicacion` es el lugar de la justificación auditable (presupuesto, tipología, estatus). Sin esa explicación, una propuesta no debería llegar a borrador.

## 5. Evidencia

- `matches`: 0 filas.
- `lista_vigente`: falso en 605 unidades y 605 filas de inventario.
- `id_externo`: nulo en 605 unidades.
- Comentario de `matches`: una unidad vendida o no disponible no puede ofrecerse. La regla lo hace cumplir.

## 6. Criterio de producción

El mapa se desbloquea en dos pasos, en este orden. Primero, `lista_vigente` pasa a verdadero solo sobre las unidades cuya lista fue confirmada, y `v_unidades_ofertables` muestra precio únicamente en esas filas. Segundo, para un lead tibio o caliente con perfil, el agente `matching` inserta entre 1 y 3 matches `propuesto` sobre unidades `disponible`, con `score`, `explicacion` y sin `precio_ofrecido` si la unidad sigue no vigente. La base rechaza cualquier intento de ofrecer una unidad apartada, reservada o vendida.
