# PD-EV-CHECK-2026-W41 Auditoría de arranque

Plantilla vigente: PD-SGC-PDCA-001. Esta copia es la primera pasada de PD-CTRL-001 a PD-CTRL-012, ejecutada el 2026-10-05 con rol de lectura sobre `palm-lab-practica`. No sustituye la firma del CTO.

## 1. Identificación

| Campo | Valor |
| --- | --- |
| Código | PD-SGC-PDCA-001 |
| Periodo | 2026-09-28 a 2026-10-05 |
| Semana ISO | 2026-W41 |
| Auditor | Backend Lead |
| Aprobó CTO | Pendiente |

## 2. Alcance

Procesos PD-P01 a PD-P12. Controles PD-CTRL-001 a PD-CTRL-012. El SQL reproducible está en PD-SGC-MAN-001 versión 1.1.

## 3. Resultados

| Proceso | Control | Esperado en producción | Obtenido | Cumple hoy | Hallazgo |
| --- | --- | --- | --- | --- | --- |
| PD-P01 | PD-CTRL-001 | Interacciones con tráfico | prospectos 15, leads 15, interacciones 0 | No | Cero vacío en el canal |
| PD-P02 | PD-CTRL-002 | Conversión con historial de etapa | 15 leads; etapa actual exclusiva | Parcial | El estado no acumula etapas |
| PD-P03 | PD-CTRL-003 | 0 mensajes sin firma | webhook_eventos 0 | No | Control de firma sin filas y sin columna `metadata` |
| PD-P04 | PD-CTRL-004 | 0 envíos sin aprobación | 0 enviados sin aprobador | Vacío | No existe `draft_id` ni `es_plantilla` |
| PD-P05 | PD-CTRL-005 | FK del ERD 1.1 | Citas, seguimientos y borradores → prospectos; comisiones → matches | Sí | El ERD que cuelga esas tablas de leads no coincide |
| PD-P06 | PD-CTRL-006 | 0 huérfanos y 0 divergencias | 0, 0 y 0 | Sí | El espejo no tiene trigger |
| PD-P07 | PD-CTRL-007 | 0 tibios o calientes sin match | 12 | No | matches = 0 |
| PD-P08 | PD-CTRL-008 | Secreto ausente rechaza sin escribir | sync 503 `SYNC_SECRET missing`; alerta 401 | Parcial | Sync apagado por falta de secreto |
| PD-P09 | PD-CTRL-009 | 0 tablas sin RLS y 0 grants anon al núcleo | 0 y 0 | Sí | Policies de asesor siguen sin crear |
| PD-P10 | §6.1 a §6.6 | Seis requisitos cerrados | Abiertos | No | Ver sección 6 del manual |
| PD-P11 | PD-CTRL-011 | Comisión por fuente | 0 comisiones; 12 respuestas > 5 min | No | Métrica reina sin numerador |
| PD-P12 | PD-CTRL-012 | 0 demo antes de pauta | E.164 0 excepciones; formulario 3; lab 4/8/16/224; campañas 0 | No | Purga pendiente |

## 4. Hallazgos y acciones

| # | Hallazgo | Proceso | Severidad | Acción | Responsable | Compromiso | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Webhook sin host y sin eventos | PD-P03 | P0 | Publicar PD-ING-012 y pasar PD-CTRL-008 del sync a secreto configurado | Backend Lead | 2026-11-05 | Abierto |
| 2 | 12 leads tibios o calientes sin match | PD-P07 | P0 | No abrir pauta. Cerrar lista vigente y el motor | Backend y Comercial | 2026-11-05 | Abierto |
| 3 | Ventana 24 h y `draft_id` sin columna | PD-P04 | P0 | Migración de trazabilidad antes del primer envío | Backend Lead | 2026-11-05 | Abierto |
| 4 | `SYNC_SECRET` ausente: la función responde 503 | PD-P08 | P1 | Configurar secreto y repetir PD-CTRL-008 | Backend Lead | 24 h tras decisión | Abierto |
| 5 | Laboratorio poblado y semilla de 15 leads | PD-P12 | P1 | PD-EV-012 antes de producción | Backend Lead | 2026-11-05 | Abierto |

## 5. Acciones preventivas

El control SQL de la versión 1.1 usa solo columnas que existen. Una consulta con `interacciones.message_id`, `direccion = 'out'` o `comisiones.lead_id` no se programa: fallaría al ejecutarla.

## 6. Actualizaciones al manual

| Campo | Valor |
| --- | --- |
| Versión anterior | 1.0 |
| Versión nueva | 1.1 |
| Cambios | Controles PD-CTRL, requisitos de salida PD-P10 y workflow PD-WF-001 |

## 7. Firma

| Rol | Nombre | Fecha |
| --- | --- | --- |
| Auditor | Backend Lead | 2026-10-05 |
| CTO | Pendiente | |

## Plantilla del siguiente trimestre

Copiar este archivo como `PD-EV-CHECK-Q_AAAA-QQ_auditoria-trimestral.md` y vaciar la columna «Obtenido».
