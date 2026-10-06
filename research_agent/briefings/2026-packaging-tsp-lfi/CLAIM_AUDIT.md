# Auditoría de claims

Estados: `supported` · `partial` · `conflict` · `didactic` · `not found`

| Claim | Origen | Fuentes | Estado | Uso |
|---|---|---|---|---|
| Familias por sustancia activa, blíster y formato; 4 líneas | paper 2024 | SRC-001 | **supported** | citar |
| Setup de 4.5 h a 1.5 h | paper 2024 abstract | SRC-001 | **supported** (abstract; falta tabla del PDF) | citar con “según abstract” |
| Secuenciación manual por personal experimentado | papers | SRC-001, SRC-003 | **supported** | citar |
| Clustering + TSP; Gurobi + Ant System; 4 líneas | preprint 2026 | SRC-002, SRC-003 | **supported** | citar |
| TSP con restricciones MTZ | un resumen del preprint | SRC-002; SRC-006 (definición MTZ) | **partial** | citar como “una versión del abstract”; confirmar en PDF |
| 9 meses de datos históricos | un resumen | SRC-002 | **partial** | no está en el abstract IBERO |
| Reducción de setup **hasta 13.6%** vs. manual | un resumen | SRC-002 vs SRC-003 | **conflict** | no usar como cifra única |
| Reducción de setup **hasta 19.3%** vs. manual | abstract IBERO/SSRN | SRC-003 vs SRC-002 | **conflict** | ídem |
| Ant System comparable o mejor al exacto cuando crece la complejidad | preprint | SRC-002, SRC-003 | **supported** (abstract) | citar |
| “100 cambios mayores menos al año” | conversación previa | — | **not found** | no usar |
| El paper define o usa “LFI / Loss Function Index” | conversación previa | búsquedas 2026-10-06 | **not found** | no atribuir al paper |
| LPS = Should-Can-Will-Did + PPC | literatura LPS | SRC-004, SRC-005 | **supported** | citar; es marco, no resultado del paper |
| El paper se integra “dentro” del LPS | interpretación de este briefing | — | **partial** (traducción de marco) | decir “propuesta de encaje”, no hallazgo empírico |
| $4,200/paro, $1.89 M/mes, ROI 193× | aula | SRC-D01 | **didactic** | solo clase; mostrar supuestos |
| Ahorro diario = 4 × $4,200 = $16,800 | conversación previa | SRC-D01 | **partial / aritmética inconsistente** | 6→2 paros *por turno* son 12 evitados/día, no 4. El lab usa 12 |
| Secuencia A-C-B-D = 27 h vs A-B-C-D = 17 h | aula | SRC-D01 | **didactic** | ilustra el método, no es dato de planta |
| FlexSim, Tecnomatix y AnyLogic son el “primer nivel” de la revisión de 9 softwares | conversación previa | SRC-008 | **conflict / false as stated** | AnyLogic **no está** en esos 9; FlexSim sí lidera esa revisión |
| AnyLogic es fuerte en híbrido DES+agentes | review CPPS | SRC-009 | **supported** | citar SRC-009, no SRC-008 |
| SimPy modela máquinas con `Resource` | docs | SRC-013 | **supported** | citar |
| workflowio importa Mermaid y adjunta mediciones | PyPI | SRC-014 | **supported** | citar; paquete v0.1.0 |
| Arena / AutoMod están siendo discontinuados | conversación previa | SRC-008, SRC-015 | **not found** en estas fuentes | no afirmar |
| Dataset 30 días con firma de operador | este lab | SRC-D01 | **didactic** | clave en `CLAVE_INSTRUCTOR.md` |
