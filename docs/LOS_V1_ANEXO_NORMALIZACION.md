# Anexo de normalización (borrador para LOS v1)

Este anexo no se envía. La normalización es el paso 8 del orden del Camino C, no el Sprint 0. Quien diseñe sobre `listings` y `listing_unit_matches` está trabajando una arquitectura ya reemplazada.

## Arquitectura vigente

| Antes | Camino C |
|---|---|
| `listings` | `source_listings` |
| `listing_unit_matches` | `entity_matches` |
| — | `source_documents` |
| — | `parse_attempts` |

`entity_matches` usa `MATCHED`, `POSSIBLE_MATCH` y `REJECTED`, con merge y unmerge. Las capas de datos anteriores a ese corte no se usan para diseñar.

## Correcciones que este borrador todavía no cumple

No implementar las curvas de este anexo tal como estaban redactadas. Cinco fallas:

1. **Price gap.** Un gap grande es señal de comparables contaminados, no un premio. Arriba de +12% el gap enciende una bandera de anomalía, penaliza el LCS y obliga a revisión o a `INSUFFICIENT_DATA`. Extender la escala para que +15% valga 93 y +20% valga 100 contradice esa lectura.
2. **Appreciation.** Hay que elegir una sola definición. O los subcomponentes producen el porcentaje anual esperado y ese porcentaje se normaliza después, o se promedian componentes que ya están normalizados. Las dos cosas a la vez no se pueden implementar. La fórmula citada en el borrador era A = 0.45·H + 0.35·I + 0.20·Supply, en paralelo con una tabla del porcentaje anual.
3. **Umbrales nominales.** Un 4% nominal en pesos, con inflación cercana, es casi cero real y no debe puntuar como si fuera plusvalía. El cap rate se lee como diferencial contra una tasa libre de riesgo en MXN (CETES), o se declara en el anexo si el tramo es nominal o real y en qué moneda.
4. **UnitIdentityCertainty.** No pesa como un 5%. Si la identidad de la unidad no está resuelta, el LCS tiene un techo (30) o pasa a `INSUFFICIENT_DATA`. Una confirmación humana revisada vale más que un fuzzy de 80 o más. En el borrador el match manual valía 60 y el fuzzy ≥80 valía 75; esa precedencia se invierte.
5. **Liquidity en preventa.** El DOM de una unidad en preventa mide la estrategia de lanzamiento del desarrollador. La absorción se mide en el desarrollo, no en la unidad. Para Palm v1, LBW usa la variante de preventa o se publica con confianza baja. No se trata como liquidez de reventa.

Cuando el paso 8 se abra, las tablas numéricas se reescriben con estas cinco reglas. Hasta entonces este archivo es solo el registro del borrador.
