# Cómo revisar y documentar hallazgos (trabajo de equipo)

El aprendizaje personal deja notas. Un hallazgo de equipo deja **una cadena de evidencia** que otra persona puede auditar sin haber estado en la conversación.

## 1. Separar tres capas

| Capa | Pregunta | Ejemplo en este briefing |
|---|---|---|
| **Paper** | ¿Qué afirma el texto citado, con localizador? | Familias por sustancia activa; TSP; 4.5 h → 1.5 h (COMPSE 2024) |
| **Marco** | ¿Qué constructo estándar se está usando para interpretar? | 7 MUDA (Ohno); LPS Should-Can-Will-Did (Ballard) |
| **Didáctico** | ¿Qué inventamos para enseñar? | $4,200/paro, dataset de 30 días, secuencia A-C-B-D |

Mezclar las tres capas es el error que convierte un ejemplo de aula en “resultado del paper”.

## 2. Una ficha por fuente, un renglón por claim

1. Registrar la fuente (`templates/ficha-fuente.md`).
2. Extraer claims atómicos (“reduce setup hasta 19.3%”, no “el paper es bueno”).
3. Auditar cada claim (`templates/claim-audit.md`).
4. Solo entonces escribir el briefing.

Si un número aparece en una conversación previa y **no** en el abstract/PDF, el estado es `not found` o `didactic`. No se “recuerda” como dato.

## 3. Conflictos: no promediar

Cuando dos abstracts del mismo preprint dan 13.6% y 19.3%, el hallazgo documentable es:

> Hay conflicto entre versiones del resumen; no hay cifra única citables hasta consultar el PDF.

Eso es más útil para un equipo que elegir 13.6% porque “ya lo usamos en clase”.

## 4. Revisión en cuatro preguntas (checklist de pares)

1. **¿Se abrió la fuente o solo el snippet?** Si no se abrió, no se cita.
2. **¿El localizador existe?** Abstract, sección, página, tabla.
3. **¿El término es el de la fuente?** LPS ≠ LFI. Taguchi QLF ≠ “Loss Function Index”.
4. **¿El artefacto está etiquetado?** Diagrama, CSV y gráfico deben decir `paper` o `didactic`.

## 5. Dónde vive el archivo (propuesta de carpeta)

```
briefings/AAAA-tema-corto/
  HALLAZGOS.md        # síntesis
  FUENTES.md          # registro
  sources.json        # mismo registro, máquina-legible
  CLAIM_AUDIT.md      # claims
  simulations/        # código reproducible
  output/             # PNG/CSV generados
```

El briefing se revisa como un PR: el revisor no discute opiniones, discute **estados de claim**.

## 6. Qué promover internamente

| Evitar | Preferir |
|---|---|
| “El LFI del paper” | “Capa didáctica de pérdida monetaria, no es un índice académico” |
| “El paper reduce 13.6%” | “Abstracts del preprint 2026 reportan 13.6% o 19.3%; COMPSE 2024 reporta 4.5 h → 1.5 h” |
| “100 cambios mayores menos al año” | `not found` en abstracts; no usar hasta PDF |
| Promedio de dos cifras en conflicto | Tabla de conflicto |

## 7. Cierre de un ciclo de revisión

Un hallazgo está listo para clase o cliente cuando:

- cada cifra usada tiene estado `supported` o está explícitamente `didactic`;
- los `conflict` y `not found` están visibles en el briefing;
- otra persona puede repetir las queries y llegar a los mismos DOI.
