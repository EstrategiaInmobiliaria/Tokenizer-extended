# PD-SGC-PDCA-001 Auditoría trimestral

| Campo | Valor |
| --- | --- |
| Código | PD-SGC-PDCA-001 |
| Versión | 1.0 |
| Fecha de plantilla | 2026-10-05 |
| Periodo a auditar | ____-__-__ a ____-__-__ |
| Auditor | |
| Aprobador | CTO |
| Manual de referencia | PD-SGC-MAN-001 |

Completar una fila por proceso. «Check» usa la consulta de la sección 4 del manual. Un cero vacío se anota como abierto.

| Proceso | Plan: liga y KPI | Do: evidencia del periodo | Check: filas | Act: versión y acción | Dueño | Cierre |
| --- | --- | --- | --- | --- | --- | --- |
| PD-P01 | PD-ING-010 / PD-KPI-001 | PD-EV-001 | | | Backend Lead | |
| PD-P02 | Vistas de etapa / PD-KPI-002 | PD-EV-002 | | | Comercial Lead | |
| PD-P03 | PD-ING-012 / PD-KPI-003 | PD-EV-003 | | | Backend Lead | |
| PD-P04 | Cloud API / PD-KPI-004 | PD-EV-004 | | | Comercial Lead | |
| PD-P05 | Esquema / PD-KPI-005 | PD-EV-005 | | | Backend Lead | |
| PD-P06 | Huérfanos / PD-KPI-006 | PD-EV-006 | | | Backend Lead | |
| PD-P07 | PD-ING-031 / PD-KPI-007 | PD-EV-007 | | | Backend y Comercial | |
| PD-P08 | Tres funciones / PD-KPI-008 | PD-EV-008 | | | Backend Lead | |
| PD-P09 | Policies / PD-KPI-009 | PD-EV-009 | | | Backend Lead | |
| PD-P10 | PD-EV-010 / PD-KPI-010 | PD-EV-010 | | | CTO | |
| PD-P11 | Tablero / PD-KPI-011 | PD-EV-011 | | | Comercial Lead | |
| PD-P12 | Aislamiento / PD-KPI-012 | PD-EV-012 | | | Backend Lead | |

## Lectura de línea base — 2026-10-05

Esta fila no sustituye la auditoría del trimestre. Fija el punto de partida de la versión 1.0.

| Proceso | Check | Lectura | Riesgo |
| --- | --- | --- | --- |
| PD-P01 | RLS apagado en `public` | 0 | PD-RIE-001 abierto en webhook y n8n |
| PD-P02 | Leads sin fuente | 0 | 15 sin campaña, P2 |
| PD-P03 | Eventos e interacciones | 0 y 0, vacío | PD-RIE-003 abierto |
| PD-P04 | Enviados sin aprobador | 0 | Ventana de 24 h sin evaluador |
| PD-P05 | Llaves del diagrama | Presentes | PD-RIE-005 controlado en esta versión |
| PD-P06 | Huérfanos | 0 | El espejo no tiene trigger |
| PD-P07 | Tibios y calientes sin match | 12 | PD-KPI-007 = 0 % |
| PD-P08 | Funciones con secreto en código | 2 de 2 activas con JWT falso | Cron ausente |
| PD-P09 | Tablas sin RLS | 0 | Policies de asesor sin aplicar |
| PD-P10 | Hitos | Abiertos desde P1 de Meta | PD-RIE-010 |
| PD-P11 | Comisión sin traza | 0 vacío | PD-KPI-011 sin numerador |
| PD-P12 | Teléfonos fuera de E.164 | 0 | Semilla de 15 sin acta |

## Cierre del auditor

| Pregunta | Respuesta |
| --- | --- |
| ¿Algún P0 quedó sin acción fechada? | |
| ¿La bitácora de PD-SGC-MAN-001 subió de versión? | |
| ¿El CTO aprobó el acta? | |
| Fecha del siguiente Plan | |
