# Briefing: secuenciación de empaque farmacéutico, MUDA, LPS y “LFI”

**Fecha de acceso:** 2026-10-06  
**Pregunta:** ¿Qué dice realmente el paper de Soria-Arguello et al., qué se puede documentar como hallazgo de equipo, y cómo se conecta (sin forzar equivalencias) con los 7 MUDA, el Last Planner System y un índice de pérdida monetaria para enseñanza?  
**Alcance:** abstracts institucionales y revisiones de simulación de acceso público. **No se consultó el PDF completo** del preprint SSRN ni del capítulo Springer (paywall). Las cifras de planta en dólares son didácticas.

## Conclusión

Hay **dos papers distintos**, no uno. El capítulo COMPSE 2024 forma familias por sustancia activa, tamaño de blíster y formato, y reporta setup de **4.5 h a 1.5 h** en cuatro líneas [SRC-001]. El preprint de 2026 añade clustering + TSP (en una versión del resumen, con restricciones MTZ), resuelto con Gurobi y un Ant System, sobre cuatro líneas reales; los **resúmenes públicos no coinciden** en el ahorro: **hasta 13.6%** [SRC-002] vs **hasta 19.3%** [SRC-003]. El paper ataca sobre todo el MUDA de **espera (setup)** y, vía clustering, el de **sobreproceso** (cambios mayores innecesarios). **No modela inventario, transporte, movimiento ni defectos.** El Last Planner System sí es un marco académico (Should-Can-Will-Did, PPC) [SRC-004][SRC-005]; el “LFI / Loss Function Index” **no aparece** como constructo de manufactura. Úsalo solo como capa didáctica de priorización monetaria, o sustituye el nombre por matriz pérdidas-costos / Taguchi QLF. Para simular en clase: Mermaid + SimPy (o el lab de este repo). Para fábrica: FlexSim o Tecnomatix según Ivanov et al. [SRC-008]; AnyLogic si se necesita híbrido DES+agentes [SRC-009].

## 1. Los dos papers (no mezclar)

### SRC-001 — COMPSE 2023 / Springer 2024 (familias + secuenciación)

Soria-Arguello, Ruiz-Morales y Ochoa-Zezzatti, *Mathematical Model for Product Family Design and Product Sequencing for a Pharmaceutical Company*, en *7th EAI COMPSE 2023*, Springer, pp. 251–269, 2024. DOI: [10.1007/978-3-031-67440-2_20](https://doi.org/10.1007/978-3-031-67440-2_20).

El abstract institucional [SRC-001] afirma:

- la secuenciación habitual es empírica, a criterio del planner;
- el modelo agrupa productos en familias para **cuatro líneas de empaque**;
- criterios: **sustancia activa, tamaño de blíster y tipos de formato**;
- hay un algoritmo de secuenciación intra-familia;
- resultado comparado con el plan de producción: setup **de 4.5 horas a 1.5 horas**.

Eso es una reducción de **66.7% en la duración del cambio mayor→menor** en el caso reportado, **no** un 13.6% de setup total anual. Son métricas distintas.

### SRC-002 / SRC-003 — preprint 2026 (analytics prescriptivo + TSP)

Soria-Arguello, Villicaña-García, Montes-Orozco y Urbán-Rivero, *A Prescriptive Analytics Framework for Modeling Product Sequencing in Pharmaceutical Packaging Lines*. Preprint SSRN, DOI: [10.2139/ssrn.6416055](https://doi.org/10.2139/ssrn.6416055). Registro IBERO: publicado 17 mar 2026, 30 páginas [SRC-003].

Puntos que **sí coinciden** entre resúmenes:

- problema de analytics **prescriptivo** (no solo describir);
- dos etapas: clustering por similitud → secuenciación tipo TSP para minimizar setup;
- Gurobi (exacto) y metaheurística **Ant System**;
- evaluación en **cuatro líneas reales**;
- al crecer la complejidad, el Ant System empata o mejora al solver exacto en el set completo;
- el clustering en familias homogéneas da reducciones adicionales;
- hay patrones de transición estables intra-familia;
- comparación contra **scheduling manual** de la empresa.

Puntos que **no coinciden**:

| Versión del resumen | Ahorro de setup vs. manual | Extra |
|---|---|---|
| Resumen indexado tipo library [SRC-002] | **hasta 13.6%** | 9 meses de historia; TSP **con MTZ**; menciona “medical device manufacturing systems” en el lead (posible copy-edit) |
| Perfil IBERO / DOI SSRN [SRC-003] | **hasta 19.3%** | no menciona MTZ ni los 9 meses en el abstract visible |

**Hallazgo de equipo:** no citar “el paper reduce 13.6%” ni “19.3%” como cifra única. Citar el conflicto hasta leer tablas del PDF.

La formulación MTZ (Miller–Tucker–Zemlin, 1960) [SRC-006] es el mecanismo clásico para eliminar subtours en TSP entero. Es plausible en el preprint; el abstract IBERO no la nombra.

## 2. Novedad respecto al paper 2024

| 2024 (familias) | 2026 (prescriptivo) |
|---|---|
| Familias por atributos explícitos (API, blíster, formato) | Clustering de similitud + TSP |
| Un algoritmo de secuencia intra-familia | Gurobi vs Ant System, escalado con complejidad |
| 4.5 h → 1.5 h (duración de setup) | % vs. práctica manual (13.6 o 19.3, en conflicto) |
| COMPSE / Springer, peer-reviewed | Preprint SSRN |

La novedad documentable del 2026 es el **pipeline descriptivo→prescriptivo** y la comparación exacto vs. metaheurística, no un “LFI” ni un bucle LPS.

## 3. Centralizar el problema: 7 MUDA en el flujo

Traducción operativa (Ohno / TPS) [SRC-007] → señal en el diagrama → qué cubre el paper. Detalle y diagrama en [`MUDA_FLUJO.md`](MUDA_FLUJO.md).

| MUDA | ¿El paper lo ataca? | Evidencia |
|---|---|---|
| Espera (setup) | **Sí** | Función objetivo = minimizar setup [SRC-001][SRC-003] |
| Sobreproceso | **Parcial** | Clustering reduce cambios de sustancia/formato innecesarios [SRC-001] |
| Inventario | No | No aparece en abstracts |
| Transporte / layout | No | No optimiza movimiento entre áreas |
| Movimiento del operario | No | No hay ergonomía |
| Defectos | No | Se asume setup de calidad |
| Sobreproducción | No | No hay demanda/takt en el modelo citado |

Para documentar en el equipo: el paper **no es un programa lean completo**. Es una pieza (secuencia) del MUDA espera. El resto hay que mapearlo en el flujo con datos propios.

## 4. LPS sí; LFI no (como término académico)

### Last Planner System — sí se puede citar

Ballard (2000) [SRC-004] y el benchmark LCI/P2SL [SRC-005] definen:

- **Should** — master/phase: qué debería hacerse;
- **Can** — lookahead: quitar restricciones para que el trabajo esté listo;
- **Will** — weekly work plan: compromiso;
- **Did** — comparar lo hecho vs. lo prometido;
- **PPC** = asignaciones completadas / asignaciones planificadas (confiabilidad de flujo, no productividad).

El paper resuelve el **Should** de secuencia (qué orden minimiza setup). No organiza compromisos ni mide PPC. Encajar LPS es una **traducción de marco**, no un resultado del paper. Ver [`integracion-paper-lps-lfi.md`](integracion-paper-lps-lfi.md).

### “LFI / Loss Function Index” — no encontrado

Búsqueda de “Loss Function Index” + manufactura/lean/packaging: **sin constructo aplicable**. Lo que sí existe:

- **Quality Loss Function de Taguchi**, \(L(y)=k(y-m)^2\) — pérdida por desviación de calidad, no por paro de línea [SRC-010];
- **Production Waste Index** (acumula 7 desperdicios) [SRC-011];
- **Matriz pérdidas vs. costos (TPM / LCM)** para priorizar [SRC-012].

Conclusión de documentación: en clase se puede usar “índice de pérdida monetaria” o “costo de no actuar”. No se debe enseñar como si el paper definiera un LFI. Los $4,200/paro y $1.89 M/mes son **escenario didáctico** de este repo, no del paper.

Integración correcta (marco, no fórmula):

```
LFI didáctico  → prioriza restricciones caras
LPS lookahead  → “¿se puede hacer?” + dueño
Paper TSP      → “¿en qué orden?”
PPC            → “¿se cumplió?”
```

Insertar el LFI **dentro** del TSP cambiaría la función objetivo (tiempo → dinero). Eso ya es otro modelo; no está en los abstracts.

## 5. Simulación visual: qué usar según el objetivo

Fuentes, no ranking inventado:

| Objetivo | Herramienta | Fuente | Nota |
|---|---|---|---|
| Aula, prototipo, cero licencia | **Mermaid** (flujo) + **SimPy** (colas) o el lab de este repo | SimPy docs [SRC-013]; workflowio importa Mermaid y le pone mediciones [SRC-014] | Sin 3D |
| Fábrica / gemelo, 3D, experimentos | **FlexSim** o **Tecnomatix Plant Simulation** | Revisión de 9 paquetes: FlexSim lidera como herramienta universal [SRC-008] | Ivanov et al. **no incluyen AnyLogic** en esos nueve |
| Híbrido DES + agentes + SD, demo en navegador | **AnyLogic** | Review CPPS: AnyLogic es el más prometedor para híbrido DES+ABS [SRC-009] | Distinta revisión que SRC-008 |
| Sin código, bloques | **Arena** | Comparado en DES manufactura [SRC-015] | Mayor costo de aprendizaje; no asumimos “discontinuación” (no hallada en estas fuentes) |
| Código + objetos de planta | FactorySimPy sobre SimPy [SRC-016] | Opcional, no usado en el lab |

**Corrección respecto a conversaciones previas:** la revisión de nueve softwares (FlexSim, Tecnomatix, Visual Components, ProModel, iGrafx, Arena, Delmia, simul8, Simio) [SRC-008] **no** coloca AnyLogic “en el primer nivel de esos nueve”, porque AnyLogic no está en esa lista. AnyLogic entra por la revisión de simulación híbrida [SRC-009].

Este agente **sí genera PNG** (matplotlib). El lab en `simulations/` produce: paros vs. ahorro (didáctico), secuencia TSP ilustrativa, bucle de mejora, y un CSV de 30 días con firma de operador oculta.

## 6. Qué no está cubierto (oportunidad de análisis)

1. PDF completo: tablas por línea, trade-off cambios mayores vs. menores, “100 cambios/año”.
2. Inventario WIP, layout, OEE, calidad post-setup.
3. Integración con LPS o con un índice de pérdida en el modelo matemático.
4. Validación estadística del 13.6% vs 19.3%.
5. Datos reales de planta (el dataset de clase es sintético).

## Cómo re-ejecutar

Queries usadas el 2026-10-06:

- `Soria-Arguello pharmaceutical packaging sequencing TSP MTZ`
- `"A Prescriptive Analytics Framework for Modeling Product Sequencing"`
- `Soria-Arguello "Mathematical Model for Product Family Design"`
- `Last Planner System Should Can Will Did PPC Ballard`
- `"Loss Function Index" LFI manufacturing lean`
- `Simulation software for smart manufacturing: a review FlexSim Tecnomatix`
- `SimPy Resource production line`; `workflowio mermaid pypi`

DOI ancla: `10.1007/978-3-031-67440-2_20`, `10.2139/ssrn.6416055`, `10.1007/s42452-025-08012-y`.
