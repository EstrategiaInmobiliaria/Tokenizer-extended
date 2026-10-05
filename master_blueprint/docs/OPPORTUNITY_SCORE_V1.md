# Læds Opportunity Score v1

Versión: `laeds-opportunity-score-v1`

El score ordena **oportunidades de compra** dentro de un inventario que ya se puede ver. No dice que una propiedad sea buena en abstracto. Dice si, frente a sus comparables, hay una anomalía que conviene investigar, y si esa anomalía también renta, está en un mercado que se mueve y se puede salir.

El primer libro de prueba es un export normalizado. Palm Diamante entra con ese formato. EasyBroker entra después, por el mismo formato, cuando el acceso sea de Integration Partner. La API de cuenta solo ve los inmuebles de esa cuenta.

## Qué entra y qué no

Entran señales que salen del inventario o de una serie de precios que se entrega aparte:

- precio pedido, precio original, fecha de publicación
- metros, recámaras, baños, estacionamientos, antigüedad, renovación, características
- renta del mismo aviso o de avisos de renta comparables
- colonia, microzona, corredor, municipio, ciudad
- conteo y antigüedad de los anuncios activos de la misma microzona y tipo
- serie opcional de precio/m² de la microzona

No entran, y v1 no las inventa: infraestructura, movilidad, desarrollos nuevos, usos de suelo, seguridad, servicios ni actividad comercial. Sin fuente, imputarlas produciría un 91/100 que no se puede auditar.

El cap rate se muestra y no vota. Con vacancia y opex iguales para todo el libro es solo el yield bruto por una constante.

```text
NOI = renta anual × (1 − vacancia) × (1 − opex)
cap rate = NOI / precio pedido
```

Supuestos de partida, editables por libro: vacancia 8%, opex 25%. El factor resultante es 0.69.

## Las 12 variables

Cada variable pasa de un dato crudo a un puntaje 0–100 con una curva de tramos lineales. Fuera del primer y del último nudo, el puntaje se queda en el extremo. Si el dato no existe, la variable se omite y los pesos de su bloque se renormalizan. No se rellena con 50.

| # | Variable | Crudo | Curva (x → puntaje) | Bloque |
|---|---|---|---|---|
| 1 | `basis_discount` | (valor estimado − precio) / valor estimado | −20%→0, 0%→35, +10%→85, +20%→100 | anomalía, inversión |
| 2 | `price_cut` | (precio original − precio) / precio original | 0%→25, 8%→80, 15%→100 | anomalía |
| 3 | `dom_window` | días desde la publicación | 0–21d→35, 60d→75, 150d→100, 270d→55, 450d→20 | anomalía |
| 4 | `gross_yield` | renta anual / precio | 0%→0, 3%→15, 5%→68, 8%→100 | inversión |
| 5 | `age_condition` | años; +12 si está renovada, tope 100 | 0→100, 30→40, 50→15 | propiedad |
| 6 | `spec_fit` | recámaras, baños y estacionamientos vs. el tipo | 100 en el benchmark; −18/−15/−12 por unidad faltante | propiedad |
| 7 | `differentiators` | aciertos del catálogo del tipo | 20 + 13 × aciertos, tope 100 | propiedad |
| 8 | `zone_momentum` | variación anualizada del precio/m² de oferta | −5%→15, 0%→48, +8%→100 | plusvalía |
| 9 | `absorption` | mediana de días publicado de los pares | 30d→100, 90d→62, 210d→20 | plusvalía, liquidez |
| 10 | `supply_scarcity` | anuncios de venta activos | 5→100, 25→40, 40→15. Con menos de 5 no se interpreta | plusvalía |
| 11 | `market_depth` | el mismo conteo, otra curva | 1→15, 3→30, 8→70, 20→100 | liquidez |
| 12 | `price_band` | percentil del precio en la microzona y tipo | 100 entre p25 y p75; cae a 25 a 25 puntos de distancia | liquidez |

`supply_scarcity` y `market_depth` leen el mismo conteo. No se cancelan dentro del Opportunity Score: escasez pesa 0.05 del total y profundidad 0.036. Un mercado ni desierto ni inundado queda arriba de los dos extremos.

Benchmarks de `spec_fit`: departamento 2 / 2 / 1; casa 3 / 3 / 2. Un estacionamiento o una recámara de más no se penaliza; dos de más sí, −5 por unidad extra.

Catálogo de departamento: elevador, seguridad, gimnasio, balcón, terraza, vista, amueblado, bodega. Catálogo de casa: alberca, jardín, terraza, vista, seguridad, amueblado, bodega, balcón.

`dom_window` no es “mientras más viejo, mejor”. El pico está entre dos y cinco meses: ya hubo tiempo de negociar y el aviso no huele a inventario muerto. `absorption` mide lo contrario a nivel mercado: pares que rotan rápido suben plusvalía y liquidez.

## Valor estimado

Comparables de venta: misma ciudad, microzona, tipo, moneda, y metros entre ±30% del sujeto. Se excluye el sujeto. Con menos de 3 comparables no hay descuento; la variable se omite.

```text
valor = mediana(precio / m² de los comps) × m² del sujeto × (1 + ajuste)
ajuste = edad + recámaras + estacionamiento, acotado a ±12%
edad = −0.4% por año contra la mediana de los comps, acotado a ±8%
recámaras = +1.5% por recámara contra la mediana, acotado a ±4.5%
estacionamiento = +2% por lugar contra la mediana, acotado a ±4%
```

## Renta

1. Si el aviso trae renta, se usa esa.
2. Si no, mediana de renta/m² de avisos de renta de la misma microzona y tipo, con metros ±40%, por los metros del sujeto.
3. Si no hay ninguna, el yield no se calcula. No se inventa un porcentaje del precio: eso haría que todos los inmuebles rentaran igual y el ranking sería circular.

## Plusvalía

Solo entra una serie entregada de precio/m² de la microzona, con al menos 90 días entre el primer y el último punto:

```text
g = (ppm2_final / ppm2_inicial) ^ (365.25 / días) − 1
```

Esa `g` es una lectura de precios de oferta. El campo `illustrative_annual_appreciation` la repite. No es un pronóstico.

Si la serie no trae `property_type`, se aplica a todos los tipos de esa microzona. Una serie de departamentos no debería usarse para casas: en ese caso hay que etiquetar el tipo.

Si no hay serie y hay al menos 8 avisos con fecha, se calcula un proxy partiendo el libro en mitad vieja y mitad nueva. Ese proxy se guarda en el detalle y **no vota**: mezcla cambio de composición con cambio de precio.

## Los cinco puntajes

```text
Property      = 0.45·edad + 0.35·spec + 0.20·diferenciales
Appreciation  = 0.45·momentum + 0.30·absorción + 0.25·escasez
Investment    = 0.70·yield + 0.30·descuento
Liquidity     = 0.40·absorción + 0.30·profundidad + 0.30·banda de precio
Anomaly       = 0.60·descuento + 0.25·recorte + 0.15·ventana de días

Opportunity   = 0.35·Anomaly
              + 0.25·Investment
              + 0.20·Appreciation
              + 0.12·Liquidity
              + 0.08·Property
```

Un departamento caro y bien amenado puede ganar Property y perder Opportunity. Eso es el producto: la propiedad y la oportunidad no son la misma pregunta.

## Confianza

Va de 0 a 1, separada del puntaje. Un 94 con confianza 0.40 no se lee como un 94 con confianza 0.90.

| Pieza | Peso | 1.0 cuando |
|---|---|---|
| CMA | 0.25 | 5 o más comparables (0.6 si hay 3 o 4) |
| Renta | 0.20 | renta del aviso, o 3+ comps de renta (0.5 si hay 1 o 2) |
| Momentum | 0.15 | hay serie de precios (0.45 si solo existe el proxy de cohorte) |
| Publicación | 0.10 | hay fecha |
| Historial de precio | 0.10 | hay precio original |
| Antigüedad | 0.08 | hay años |
| Características | 0.07 | el campo vino en el registro, aunque esté vacío |
| Precio y metros | 0.05 | ambos presentes |

## Tesis

El score no cambia con la tesis. La tesis filtra y reordena.

Filtros duros: ciudad, presupuesto, tipo, microzona, yield mínimo, cap rate mínimo. Si se pide un yield mínimo y la renta no se observó, el inmueble no pasa.

Orden, después de filtrar:

| Objetivo | Orden |
|---|---|
| `appreciation` | 0.50 plusvalía + 0.25 oportunidad + 0.15 inversión + 0.10 liquidez |
| `income` | 0.45 inversión + 0.25 oportunidad + 0.15 liquidez + 0.15 plusvalía |
| `opportunity` | el Opportunity Score |
| `balanced` | 0.40 oportunidad + 0.25 plusvalía + 0.25 inversión + 0.10 liquidez |

“Máxima plusvalía a 5 años” elige `appreciation` y `horizon_years = 5`. El horizonte solo convierte la serie observada en un cambio ilustrativo `(1+g)^n − 1`. No corre un DCF. El motor DCF del blueprint sigue siendo el lugar para valorar un proyecto con flujos propios.

## Cómo probarlo con Palm Diamante

El archivo `data/palm_diamante_sample.json` es un libro sintético con la forma del export. No es el inventario de la agencia. Para el inventario real, sustituir `listings` por el export normalizado y, si existe, `price_index`.

```bash
cd master_blueprint
python example_opportunity_score.py
python example_opportunity_score.py data/palm_diamante_sample.json
```

Cada inmueble de venta necesita, como mínimo, `id`, `ask_price` y `construction_m2`. El resto mejora la confianza. La geografía que usa el comparable es `city` + `microzone` (si no hay microzona, se usa la colonia).

```text
POST /api/v1/opportunity/score
{
  "as_of": "2026-10-05",
  "assumptions": {"vacancy_rate": 0.08, "opex_ratio": 0.25},
  "thesis": {
    "city": "Acapulco",
    "budget_min": 4000000,
    "budget_max": 8000000,
    "min_gross_yield": 0.05,
    "objective": "appreciation",
    "horizon_years": 5
  },
  "price_index": [
    {"city": "Acapulco", "microzone": "Costa", "median_ppm2": 52000, "as_of": "2025-10-05"},
    {"city": "Acapulco", "microzone": "Costa", "median_ppm2": 56200, "as_of": "2026-10-05"}
  ],
  "listings": []
}
```

## EasyBroker, cuando haya acceso de partner

`from_easybroker_property` traduce el objeto de propiedad. No hace HTTP.

| EasyBroker | Campo normalizado |
|---|---|
| `public_id` | `id` |
| `operations[].type = sale` | `sale_price` |
| `operations[].type = rental` | `rent_monthly` |
| `construction_size` | `construction_m2` |
| `location.neighborhood` o el primer tramo de `location.name` | `neighborhood` y, si no hay microzona, `microzone` |
| `published_at` | `published_at` |
| `features` | catálogo canónico |

EasyBroker no trae precio original ni microzona. Sin precio original, `price_cut` se omite. Sin una microzona propia, los comparables se arman por colonia, que es más gruesa.

La sincronización de 15–30 minutos es el trabajo del conector de Integration Partners (`listing_statuses` y después el detalle de cada `public_id`). Este módulo puntúa el libro que ese conector deje. No publica anuncios ni participa en la transacción.
