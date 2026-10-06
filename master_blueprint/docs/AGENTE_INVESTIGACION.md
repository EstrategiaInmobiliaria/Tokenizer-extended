# Agente de investigación: diseño y protocolo de revisión

Este documento explica cómo está construido el agente de investigación
(`master_blueprint/research_agent/`), por qué toma las decisiones que toma, y
—sobre todo— **cómo revisar y documentar los hallazgos que produce** para que
sirvan como base de una decisión y no sólo como lectura interesante.

---

## 1. El problema que resuelve

Una búsqueda normal responde «¿qué dice internet sobre X?». Eso basta para
orientarse y no basta para decidir. Para decidir hacen falta tres cosas que una
búsqueda suelta no da:

1. **Saber qué se buscó y qué no.** Una conclusión apoyada en una sola consulta
   afortunada es frágil, pero por fuera se lee igual que una bien fundada.
2. **Saber cuántas fuentes independientes lo sostienen.** No es lo mismo un
   resultado replicado por tres equipos que uno publicado por uno solo.
3. **Poder volver al original.** Si una afirmación no se puede rastrear hasta una
   frase concreta de un documento identificable, no es verificable.

El agente está diseñado alrededor de estas tres necesidades. Todo lo demás es
consecuencia.

---

## 2. El bucle

```
    pregunta
       │
       ▼
  ┌─────────────┐
  │ PLANIFICAR  │  descompone en 5 sub-preguntas: definición, evidencia,
  │             │  método, contraste, novedad
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │   BUSCAR    │  cada sub-pregunta × cada proveedor; todo queda en auditoría
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │  FILTRAR    │  descarta lo que no es del tema; deduplica por DOI,
  │ DEDUPLICAR  │  por título exacto y por título casi idéntico
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │   MEDIR     │  ¿qué sub-pregunta quedó floja, por pocas fuentes
  │  COBERTURA  │  o porque casi todas son del mismo equipo?
  └──────┬──────┘
         │  si hay brechas y quedan rondas
         ├──────────────► reformula con el vocabulario aprendido ──┐
         │                                                          │
         │ ◄────────────────────────────────────────────────────────┘
         ▼
  ┌─────────────┐
  │ SINTETIZAR  │  extrae la frase que respalda cada punto, agrupa las que
  │             │  dicen lo mismo, detecta contradicciones, asigna confianza
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │  INFORMAR   │  citas en línea, matriz de evidencia, brechas declaradas,
  │             │  bibliografía y registro de auditoría
  └─────────────┘
```

Lo que hace al bucle multi-paso no es repetir la búsqueda, sino que **la ronda
N+1 depende del resultado de la ronda N**: sólo se reabren las sub-preguntas mal
cubiertas, y las consultas nuevas se construyen con términos extraídos de los
documentos ya recuperados. El agente aprende la terminología del campo en lugar
de repetir las palabras de quien preguntó.

### Por qué cinco tipos de sub-pregunta

La lista es fija y no se puede acortar por descuido. Dos de los cinco tipos
existen contra el sesgo natural de quien investiga:

- **CONTRASTE** busca limitaciones, críticas y enfoques alternativos. Sin él, un
  informe sólo encuentra lo que confirma la hipótesis de partida.
- **NOVEDAD** restringe la búsqueda a los últimos años. Sin él, el informe queda
  anclado en la literatura más citada, que por definición es la más antigua.

---

## 3. Las cuatro decisiones que sostienen la credibilidad

Cada una de estas vino de ver fallar al agente contra literatura real.

### 3.1 La independencia se mide por equipo autoral, no por dominio

Lo intuitivo es contar dominios distintos. Para literatura académica no funciona:
casi todos los artículos resuelven por `doi.org`, así que veinte papers de veinte
equipos distintos cuentan como una sola fuente.

Pero mirar sólo al primer autor tampoco basta. El caso que lo reveló: el preprint
en SSRN y la versión publicada del mismo trabajo listan a los mismos cuatro
investigadores **en distinto orden**, así que el agente los tomaba por dos
confirmaciones independientes y declaraba confianza alta sobre un único trabajo
contado dos veces.

La regla actual: dos fuentes son dependientes si comparten **cualquier** autor, y
la relación es transitiva. Un investigador que firma dos trabajos los encadena.

### 3.2 El agrupamiento de afirmaciones es estricto a propósito

Para triangular hay que saber que dos fuentes dicen lo mismo. Midiendo sobre
resúmenes reales, los pares más «parecidos» léxicamente sólo compartían
vocabulario de redacción académica: `study`, `paper`, `research`, `planning`. Un
umbral permisivo no produce triangulación, produce **triangulación falsa**, que es
peor que ninguna: le pone un sello de confianza alta a dos trabajos que nunca
hablaron del mismo resultado.

Por eso se exige solapamiento ponderado por rareza del término más un mínimo de
términos compartidos poco frecuentes. La consecuencia es que la mayoría de
afirmaciones quedan con una sola fuente, y el informe lo declara.

### 3.3 Un título no es evidencia

Cuando una fuente no trae resumen, el agente cita el título y lo marca como tal.
Una afirmación sostenida únicamente por títulos nunca sube de confianza baja,
aunque la firmen tres equipos distintos: tres títulos que comparten palabras son
una coincidencia léxica, no un consenso.

### 3.4 El nivel de la fuente se deduce del registro, no del proveedor

Crossref asigna DOI a preprints, tesis e informes además de a artículos
revisados. Etiquetarlos todos como literatura revisada por pares inflaba la
confianza de todo el informe. Ahora el tipo del registro se traduce
explícitamente a nivel de autoridad.

### Cómo se combina todo en el nivel de confianza

| Nivel | Condición |
| :--- | :--- |
| ⚠️ **Disputada** | Hay contradicciones sin resolver entre las fuentes |
| 🟢 **Alta** | Dos o más grupos autorales independientes, con al menos uno revisado por pares |
| 🟡 **Media** | Dos grupos sin respaldo académico, o una sola fuente revisada por pares |
| 🔴 **Baja** | Todo lo demás, incluida cualquier afirmación que sólo se apoye en títulos |

---

## 4. Protocolo de revisión y documentación de hallazgos

El informe automático es **material de entrada para una revisión**, no un
resultado publicable. Este es el proceso para convertirlo en lo segundo.

### Paso 1 — Congelar la ejecución

Guarda el Markdown y el JSON de auditoría en el repositorio, en el mismo commit.
Sin el JSON no hay forma de saber después qué se buscó, y una conclusión cuya
procedencia no se puede reconstruir no es revisable.

```bash
python -m research_agent "<pregunta>" \
  --terms <términos> --rounds 3 \
  --out docs/investigacion/HALLAZGOS_<tema>.md \
  --json docs/investigacion/hallazgos_<tema>.json

git add docs/investigacion/ && git commit -m "Investigación: <tema> (ejecución inicial)"
```

### Paso 2 — Repartir la matriz de evidencia

La sección 3 del informe es una tabla con una fila por afirmación y una columna
«Verificado por» vacía. Esa columna es el reparto del trabajo: **una fila, un
revisor**. Para cada fila hay que comprobar dos cosas, en este orden:

1. **Que la fuente existe.** El DOI resuelve y el documento es el que dice la
   bibliografía.
2. **Que la cita es literal.** La frase entrecomillada aparece tal cual en el
   documento, en el lugar que indica el localizador.

Si falla cualquiera de las dos, la fila se marca como no verificable y se elimina
del informe revisado. No se «arregla» reescribiéndola.

### Paso 3 — Reclasificar cada afirmación

Con la fuente delante, el revisor humano hace lo que el agente no puede: leer.
Cada fila termina en una de cuatro categorías:

| Categoría | Significado | Qué se hace con ella |
| :--- | :--- | :--- |
| **Confirmada** | La fuente dice eso, en ese contexto | Pasa al informe revisado |
| **Matizada** | Lo dice, pero con condiciones que la cita no recoge | Pasa con las condiciones añadidas |
| **Refutada** | La fuente no sostiene la afirmación | Se elimina y se anota por qué |
| **No verificable** | No se pudo acceder o la cita no aparece | Se elimina y se anota |

El motivo de las eliminaciones se documenta. Es la parte más valiosa del
ejercicio: enseña qué tipo de error comete el agente en ese dominio concreto.

### Paso 4 — Atacar las brechas, no esconderlas

La sección 4 del informe lista sub-preguntas mal cubiertas y afirmaciones
disputadas. Para cada una hay que decidir explícitamente entre tres opciones:
buscar más con otros términos, aceptar que es un límite del alcance, o declararlo
desconocido. La peor salida es la cuarta: borrar la sección porque afea el
informe. Una brecha silenciada se lee como ausencia de evidencia, y no es lo
mismo que evidencia de ausencia.

### Paso 5 — Publicar el revisado junto al original

El informe revisado se añade **sin borrar** el generado. El diff entre ambos es el
registro de qué aportó la revisión humana, y permite responder más adelante a la
pregunta que siempre aparece: «¿esto lo dijo la IA o lo comprobó alguien?».

### Reglas de redacción del informe revisado

- Una afirmación de confianza baja no se presenta nunca como conclusión. Si no
  hay nada mejor, la conclusión es «no hay evidencia suficiente».
- Toda cifra lleva su cita. Una cifra sin fuente es una estimación, y debe decir
  que lo es.
- Las contradicciones se muestran, no se resuelven promediando. Dos estudios que
  reportan 13% y 40% probablemente midieron cosas distintas, y eso es el
  hallazgo.

---

## 5. Limitaciones conocidas

**Sólo lee títulos y resúmenes.** Un resultado enterrado en la sección de
resultados de un artículo es invisible para el agente. Para los trabajos que de
verdad importan, hay que abrir el PDF.

**El agrupamiento es léxico, no semántico.** Dos fuentes que dicen lo mismo con
palabras distintas no se fusionan, así que el recuento de triangulaciones es una
cota inferior. Se prefirió ese error al contrario.

**La cobertura depende de los términos de búsqueda.** El agente los extrae de la
pregunta, y una pregunta mal planteada produce una investigación mal planteada.
`--terms` existe para corregirlo a mano.

**Los proveedores abiertos están sesgados hacia el inglés y hacia lo indexado.**
Literatura gris, normativa sectorial y documentación interna quedan fuera salvo
que se añada un proveedor web con clave.

---

## 6. Ejemplo aplicado

Ver [`docs/investigacion/`](investigacion/):

- `HALLAZGOS_SECUENCIACION_EMPAQUE.md` — informe generado por el agente sobre
  reducción de tiempos de setup en líneas de empaque farmacéutico.
- `hallazgos_secuenciacion_empaque.json` — auditoría completa de esa ejecución.
- `ANALISIS_PAPER_SECUENCIACION.md` — revisión humana aplicando el protocolo de
  la sección 4 a un paper concreto, incluidas las correcciones que la
  verificación obligó a hacer.
