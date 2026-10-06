# Revisión humana: el paper de secuenciación en líneas de empaque farmacéutico

Aplicación del [protocolo de revisión](../AGENTE_INVESTIGACION.md#4-protocolo-de-revisión-y-documentación-de-hallazgos)
al informe que generó el agente en
[`HALLAZGOS_SECUENCIACION_EMPAQUE.md`](HALLAZGOS_SECUENCIACION_EMPAQUE.md).

El objetivo no es resumir el paper otra vez, sino **separar lo que está verificado
de lo que se venía dando por cierto sin comprobar**, y dejar documentado cómo se
hizo esa separación.

---

## 1. Ficha verificada

| Campo | Valor |
| :--- | :--- |
| Título | A prescriptive analytics framework for product sequencing in pharmaceutical packaging lines |
| Autoría | Esbeydi Villicaña-García, Edwin Montes-Orozco, Luis Eduardo Urbán-Rivero, Isidro Soria-Arguello |
| Publicación | *Healthcare Analytics*, vol. 10, art. 100496 (diciembre 2026), Elsevier |
| DOI | [10.1016/j.health.2026.100496](https://doi.org/10.1016/j.health.2026.100496) |
| Acceso | Abierto (oro) |
| Preprint | SSRN, [10.2139/ssrn.6416055](https://doi.org/10.2139/ssrn.6416055), con los mismos cuatro autores en otro orden |

Confirmado de forma independiente en OpenAlex y en Crossref: ambos registros
coinciden en título, DOI, revista, volumen y lista de autores.

**Alcance de esta verificación.** ScienceDirect y SSRN devuelven HTTP 403 a
peticiones automatizadas, así que todo lo que sigue está contrastado contra el
**resumen**, no contra el texto completo. Las afirmaciones sobre el interior del
artículo quedan marcadas como no verificadas. Conviene abrir el PDF a mano antes
de citar cualquiera de ellas.

---

## 2. Qué dice el resumen, literalmente

Lo verificable, con la cita al lado:

- **Problema.** «Operational efficiency in pharmaceutical packaging is often
  hindered by costly setup times and manual scheduling limitations.»
- **Hipótesis.** «a two-stage integration of product clustering and mathematical
  optimization can systematically minimize transition costs and improve
  production capacity.»
- **Método, dos etapas.** Primero un modelo descriptivo que «groups products into
  homogeneous families based on attribute similarity»; después uno prescriptivo
  que «sequences products within these families to minimize setup times».
- **Formulación.** «a Traveling Salesman Problem (TSP) formulation with
  Miller–Tucker–Zemlin (MTZ) constraints to ensure sequence feasibility».
- **Dos implementaciones.** «through both the Gurobi exact solver and an Ant
  System metaheuristic algorithm».
- **Validación.** «nine months of historical data from four real-world production
  lines».
- **Resultado comparativo.** «the Ant System achieves solutions comparable to or
  better than exact methods as complexity increases».
- **Resultado principal.** «the proposed framework reduces setup times by up to
  13.6%».

---

## 3. Correcciones que obligó la verificación

Este es el valor concreto del ejercicio. Cuatro cosas que circulaban como ciertas
y no resisten el contraste con la fuente.

### 3.1 La atribución estaba invertida

El trabajo se venía citando como «Soria-Arguello et al.». En la versión publicada
Soria-Arguello firma **en cuarto lugar**; la primera autora es Esbeydi
Villicaña-García. El orden invertido viene del preprint en SSRN, donde
Soria-Arguello aparece primero.

La forma correcta de citarlo es **Villicaña-García et al. (2026)**, y conviene
decir cuál de las dos versiones se está usando.

### 3.2 Es «hasta un 13.6%», no «un 13.6%»

El resumen dice «up to 13.6%»: es el mejor caso observado, no la mejora media ni
la esperable. Presentarlo como cifra plana convierte una cota superior en una
promesa, que es justo el error que hunde la credibilidad de un caso de negocio
cuando el resultado real llega al 6%.

### 3.3 Faltaban dos piezas centrales del método

Ni el solucionador exacto (Gurobi) ni la metaheurística (Ant System) aparecían en
las descripciones previas del paper, y la comparación entre ambos **es** uno de
sus resultados: la metaheurística iguala o supera al método exacto a medida que
crece la complejidad.

Esto importa en la práctica. Una licencia de Gurobi es cara; que un Ant System
rinda igual o mejor en los casos grandes es precisamente el hallazgo que decide
si el enfoque es implementable con presupuesto limitado.

### 3.4 Dos afirmaciones que no se pudieron verificar

| Afirmación en circulación | Estado |
| :--- | :--- |
| «100 cambios mayores menos al año» | **No verificable** desde el resumen. Puede estar en el texto completo; hay que comprobarlo antes de usarla |
| «LFI (Loss Function Index)» como marco asociado | **Sin respaldo.** Una búsqueda dirigida sobre el término devolvió 18 fuentes, todas de literatura genérica de *lean manufacturing*; ninguna define un «Loss Function Index» |

Sobre la segunda: si el concepto se usa internamente, conviene renombrarlo a algo
como «cuantificación monetaria del desperdicio». «Loss function» ya significa otra
cosa muy distinta en estadística y aprendizaje automático, y usar la sigla ante
una audiencia técnica invita al malentendido.

---

## 4. Contexto y novedades que aportó la búsqueda

El agente recuperó 26 fuentes pertinentes en 40 consultas. Lo relevante para
situar el paper:

**Nadie lo cita todavía.** OpenAlex registra cero citas, consistente con una
publicación de diciembre de 2026. No hay aún validación externa ni réplicas.

**El problema está activo en varias industrias a la vez.** Aparecen trabajos
recientes sobre secuenciación con tiempos de setup dependientes de la secuencia en
máquinas paralelas no idénticas, sobre programación de lotes con algoritmos
evolutivos en plantas de formulación industrial, y sobre secuenciación en talleres
de pintura resolviendo el cambio de color con computación cuántica. Es un campo
con varios enfoques compitiendo, no uno con una solución asentada.

**La alternativa dominante en planta sigue siendo SMED.** Buena parte de la
literatura aplicada sobre reducción de cambios de formato no optimiza la secuencia:
reorganiza la operación del cambio en sí. Son estrategias complementarias y se
atacan cosas distintas —SMED abarata cada cambio, la secuenciación reduce cuántos
cambios caros ocurren—, pero hay que decidir cuál se hace primero.

**Hay una línea específica sobre limpieza entre cambios en farmacéutica.** Un
trabajo de 2026 aborda la optimización de la limpieza de cambio de formato en la
industria farmacéutica, que es exactamente el coste que hace caros los cambios
mayores. Es la lectura complementaria más directa al paper revisado.

---

## 5. Lo que el paper no cubre

Delimitarlo es tan útil como resumirlo, porque marca dónde no se puede apoyar una
decisión en él:

- **No modela inventario intermedio.** Una secuencia óptima en setup puede
  acumular producto entre etapas.
- **No optimiza el layout ni el transporte.** El recorrido físico del material
  queda fuera.
- **Asume calidad perfecta en el cambio.** No hay reproceso ni mermas de arranque,
  que en empaque farmacéutico existen y pesan.
- **No reporta el coste de implantación.** Licencias, integración con el ERP y
  formación no entran en el 13.6%.

Ninguna de estas es una crítica al paper: son los límites declarados de un caso de
estudio. Son, eso sí, exactamente las preguntas que hay que responder por separado
antes de llevar el enfoque a una planta.

---

## 6. Cómo se documentó

Aplicación literal del protocolo, para que el procedimiento sea repetible:

1. **Ejecución congelada.** El informe y su auditoría JSON están en este mismo
   directorio, en el commit que los generó. Las 40 consultas lanzadas se pueden
   reproducir una por una.
2. **Matriz repartida.** Se verificó cada afirmación contra su fuente: que el DOI
   resolviera y que la frase citada apareciera literalmente.
3. **Reclasificación.** Las ocho citas de la sección 2 quedan **confirmadas**. La
   del «13.6%» pasa a **matizada** (es una cota superior). Las dos de la sección
   3.4 quedan como **no verificables** y se retiran de cualquier conclusión.
4. **Brechas declaradas.** El informe automático avisa de que 30 de sus 32
   afirmaciones dependen de una sola fuente. No se borró ese aviso: describe con
   precisión el estado del campo, que tiene mucha actividad y poca réplica.
5. **Ambos documentos publicados.** Este análisis no sustituye al informe
   generado; va al lado. La diferencia entre los dos es, literalmente, lo que
   aportó la revisión humana.

### Lo que este caso enseña sobre el agente

Los dos errores que se encontraron no fueron de búsqueda —encontró el paper a la
primera—, sino **de evaluación de la evidencia**: contó el preprint y la versión
publicada como dos confirmaciones independientes, y dio por revisados por pares
unos registros de Crossref que eran preprints. Ambos están corregidos en el código
y cubiertos con tests de regresión.

La lección general es que un agente de investigación falla raras veces por no
encontrar las fuentes y muy a menudo por **sobrevalorar las que encuentra**. Por
eso el diseño gasta más esfuerzo en degradar la confianza que en subirla.
