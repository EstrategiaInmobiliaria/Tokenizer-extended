---
name: reporte-diario
description: "Genera el reporte diario de Palm Diamante para Jimmy: prospectos nuevos, leads fríos, seguimientos vencidos, citas de la semana, inventario por modelo y torre, /sinprecio y borradores pendientes. Usar cada mañana o cuando Jimmy pida 'el reporte de hoy'."
argument-hint: "[fecha AAAA-MM-DD opcional, por defecto hoy]"
allowed-tools: Read, Grep, Glob
model: sonnet
disable-model-invocation: true
---

# /reporte-diario

## Cuándo usarla

Cada mañana antes de las 9:00 (hora de Acapulco), o cuando Jimmy o el equipo pidan "el reporte
de hoy". Si se pasa una fecha como argumento, la sección de prospectos nuevos cubre ese día; el
resto de las secciones siempre reflejan el estado actual.

## Fuentes

1. **Supabase (MCP `supabase`)**, proyecto `palm-lab-practica` (ref `plgfhtvzxhrdfmrlknru`),
   solo lectura. Esquema versionado en `supabase/migrations/`. Vistas (todas devuelven
   columnas `*_local` ya en hora de Acapulco, `America/Mexico_City`):

   | Vista | Qué trae | Filtro que aplica la skill |
   |-------|----------|-----------------------------|
   | `v_prospectos_nuevos` | conteo por `dia_local`, `canal` (origen), `perfil` A/B/C, `temperatura` | `where dia_local = '<fecha>'` |
   | `v_leads_frios` | prospectos activos con > 48 h sin contacto, `horas_sin_contacto`, `cliente_sin_respuesta` | ninguno; ordenar por `horas_sin_contacto desc` |
   | `v_seguimientos_vencidos` | seguimientos pendientes con fecha pasada, `dias_retraso`, `asesor`, `ultimo_contacto_local` | ninguno |
   | `v_apartado_por_tipologia` | por `modelo` y `torre` (I-A … III-B): `disponibles`, `apartadas`, `reservadas`, `vendidas`, rango de precio de disponibles, `lista_vigente` | agrupar por `torre_principal` y por `modelo` |
   | `v_citas_semana` | citas programadas/confirmadas de la semana en curso, `fecha_cita_local`, `lugar` | ninguno |
   | `v_sinprecio_pendientes` | prospectos que recibieron `/sinprecio`; `precio_lista_interno` y `lista_vigente` | ninguno |
   | `v_borradores_pendientes` | borradores en espera de revisión/aprobación, `alerta_lista_negra` | ninguno |
   | `v_alertas_lista_negra` | texto libre que menciona dominios o teléfonos de la lista negra | ninguno |

   Si una vista no existe, correr primero `supabase/migrations/20260928181558_vistas_reporte_diario.sql`
   (o decirlo en el reporte y seguir). No inventar cifras.
2. **Bandeja de revisión manual** del router (`GET /api/v1/revision-manual`) si el servicio
   está corriendo: tickets COYOTE (alerta roja) pendientes. Si no está corriendo, "sin dato".

## Pasos

1. Determinar la fecha del reporte (`<fecha>`), en hora de Acapulco.
2. `v_prospectos_nuevos where dia_local = '<fecha>'`: tabla canal × perfil.
3. `v_leads_frios`: listar, marcando primero los que tienen `cliente_sin_respuesta = true`.
4. `v_seguimientos_vencidos`: ordenados por `dias_retraso desc`.
5. `v_citas_semana`: lista con `fecha_cita_local` y `lugar` (si dice "Por confirmar", va a
   pendientes de Jimmy).
6. `v_apartado_por_tipologia`: dos tablas, por modelo y por `torre_principal`. Incluir
   `lista_vigente` y `fecha_lista`.
7. `v_sinprecio_pendientes` y `v_borradores_pendientes`: cuántos y quiénes.
8. `v_alertas_lista_negra`: si hay filas, sección "Alertas" al principio del reporte.
9. Bandeja del router (si aplica).
10. Redactar con el formato de abajo. Cifras exactas; si un dato no está disponible, escribir
    "sin dato" y el motivo.

## Formato del reporte

```markdown
# Palm Diamante · Reporte diario · <fecha>

Lista de precios: <fecha_lista> · vigente: <sí/no> (mientras sea "no", ningún precio sale a clientes)

## Alertas
- <filas de v_alertas_lista_negra, o "ninguna">

## Prospectos nuevos (<fecha>): <n>
| Canal | Perfil A | Perfil B | Perfil C | Total |
|-------|----------|----------|----------|-------|

## Leads fríos (> 48 h sin contacto): <n>
| Prospecto | Perfil | Horas sin contacto | Cliente sin respuesta | Asesor | Acción |
|-----------|--------|--------------------|-----------------------|--------|--------|

## Seguimientos vencidos: <n>
| Prospecto | Asesor | Tipo | Días de retraso | Último contacto | Acción |
|-----------|--------|------|-----------------|-----------------|--------|

## Citas de la semana: <n>
| Prospecto | Fecha y hora (Acapulco) | Lugar | Estado |
|-----------|-------------------------|-------|--------|

## Inventario (lista <fecha_lista>)
| Modelo | Disponibles | Apartadas | Reservadas | Vendidas | m² | Precio disponibles (interno) |
|--------|-------------|-----------|------------|----------|----|------------------------------|

| Torre | Disponibles | Apartadas | Reservadas | Vendidas |
|-------|-------------|-----------|------------|----------|

## /sinprecio pendientes: <n>
| Prospecto | Unidad de interés | Asesor |
|-----------|-------------------|--------|

## Borradores pendientes de revisión: <n>
## Revisión manual del router (alerta roja): <n> tickets

## Pendientes de Jimmy
- Confirmar lista vigente (afecta /sinprecio pendientes y precios en borradores)
- Lugar de citas ("Por confirmar" en <n> citas)
- <otros de CLAUDE.md que sigan abiertos>
```

## Reglas

- El reporte es interno: puede incluir precios y datos de inventario, pero **no se reenvía a
  clientes**. Marcar los precios como "interno" mientras `lista_vigente = false`.
- No calcular "velocidad de venta" ni proyecciones si no hay al menos 30 días de datos.
- Respetar `CLAUDE.md`: nunca incluir dominios ni teléfonos de la lista negra; si aparecen en
  `v_alertas_lista_negra`, citar solo tabla, registro y campo, no el valor.
- Los registros cuyo nombre empieza con "EJEMPLO" son datos ficticios de prueba: si aparecen,
  indicarlo en el encabezado del reporte.
