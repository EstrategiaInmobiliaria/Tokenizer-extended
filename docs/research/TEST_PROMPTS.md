# Prompts de prueba para el agente de investigación

Usa estos mensajes en el panel de test run para validar el agente `web-researcher`.

## Prompt básico

```
Investiga el estado actual de las herramientas de simulación de eventos discretos
para líneas de empaque farmacéutico. Compara AnyLogic, Plant Simulation, SimPy y
workflowio. Incluye citas de fuentes primarias y una tabla comparativa.
```

## Prompt de integración (paper + LPS + MUDA)

```
Analiza cómo se integran estos tres marcos para optimización de líneas de empaque:
1. El paper de Soria-Argüello et al. (2026) sobre secuenciación TSP+MTZ
2. Last Planner System (LPS) con PPC
3. Los 7 MUDA de lean manufacturing

¿Qué ataca cada marco? ¿Qué gaps quedan? Cita fuentes académicas.
```

## Prompt de verificación (LFI)

```
¿Existe un concepto académico llamado "Loss Function Index" (LFI) en lean
manufacturing o optimización de producción? Busca en papers, estándares y
documentación de consultoras. Si no existe, propón un nombre alternativo
estandarizado.
```

## Prompt de novedades

```
¿Qué herramientas nuevas (2025-2026) permiten simular flujos de manufactura
partiendo de diagramas Mermaid? Verifica en PyPI y GitHub. Incluye versiones
y estado de madurez.
```

## Criterios de evaluación

Una respuesta exitosa del agente debe:

- [ ] Seguir el workflow de 5 fases (scope → search → synthesis → citations → deliverables)
- [ ] Citar al menos 3 fuentes primarias con URLs
- [ ] Incluir al menos 1 tabla comparativa
- [ ] Distinguir conceptos académicos de marcos heurísticos
- [ ] Reportar discrepancias entre fuentes (ej. 13.6% vs 19.3%)
- [ ] Listar gaps y preguntas abiertas
- [ ] Producir bibliografía completa al final
