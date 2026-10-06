# Clave del instructor — dataset de 30 días

**No compartir con alumnos.** El CSV es didáctico (`SRC-D01`), no datos de planta ni del paper.

## Patrón oculto (firma del operador)

| Operador | Limpia el sensor tras cambio de rollo | Paros no planificados |
|---|---|---|
| Ana | ~85% de las veces | baseline |
| Bruno | ~22% de las veces | **claramente más paros** que Ana/Carla, concentrados cuando `sensor_cleaned=0` |
| Carla | ~85% de las veces | baseline |

Semilla: `seed=20261006` en `generar_dataset_clase.py`.

## Otros patrones más débiles (ruido estructurado)

- Los días con **secuencia que cruza familia** (API distinta) tienen setup más largo (4.5 h vs 1.5 h), coherente con SRC-001.
- Turno 3 del viernes acumula un poco más de espera residual (fatiga), pero el efecto es menor que el de Bruno.

## Cómo deberían encontrarlo los alumnos

1. Agrupar paros por operador.  
2. Cruzar con `sensor_cleaned` y `hours_since_roll_change`.  
3. Ver que Bruno no limpia y que sus paros se agrupan post-cambio.  
4. Calcular costo de no actuar con `lfi.py` (didáctico).  
5. Proponer la acción LPS: hacer ready “limpiar sensor en cada cambio de rollo” y medir PPC.

## Lo que no deben concluir

- Que el paper reporta estos dólares o a Bruno.  
- Que 13.6% y 19.3% salen de este CSV.
