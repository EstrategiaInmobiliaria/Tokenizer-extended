---
name: reporte-diario
description: "Genera el reporte diario de Palm Diamante para Jimmy: prospectos nuevos, seguimientos vencidos, apartados por tipología y pendientes. Usar cada mañana o cuando Jimmy pida 'el reporte de hoy'."
argument-hint: "[fecha AAAA-MM-DD opcional, por defecto hoy]"
allowed-tools: Read, Grep, Glob
model: sonnet
disable-model-invocation: true
---

# /reporte-diario

## Cuándo usarla

Cada mañana antes de las 9:00, o cuando Jimmy o el equipo pidan "el reporte de hoy". Si se pasa
una fecha como argumento, el reporte cubre ese día.

## Fuentes

1. **Supabase (MCP `supabase`)**, proyecto de Palm Diamante, solo lectura. Vistas esperadas:
   - `v_leads_frios`: prospectos sin respuesta o con más de N días sin contacto.
   - `v_seguimientos_vencidos`: seguimientos con fecha comprometida ya pasada.
   - `v_apartado_por_tipologia`: unidades apartadas / disponibles por prototipo y torre.
   - Tablas base: `prospectos`, `inventario`.
   Si las vistas o tablas aún no existen, decirlo en el reporte y continuar con lo demás; no
   inventar cifras.
2. **Inventario maestro** `palm_diamante_router/data/inventario_maestro.json` (rama
   `cursor/palm-diamante-router-1e3c`) para el conteo de disponibles cuando Supabase no
   tenga inventario cargado.
3. **Bandeja de revisión manual** del router (`GET /api/v1/revision-manual`) si el servicio
   está corriendo: tickets COYOTE (alerta roja) pendientes.

## Pasos

1. Determinar la fecha del reporte y el rango (00:00–23:59 hora de Acapulco, UTC-6).
2. Consultar prospectos nuevos del día por canal (WhatsApp, formulario web, llamada) y
   categoría (Comprador real / Lead frío / Coyote).
3. Consultar seguimientos vencidos y ordenarlos por días de retraso.
4. Consultar apartados y disponibles por tipología (B1, Suite Roof Garden, A1, Green House,
   Penthouse) y por torre (I, II, III).
5. Listar tickets de revisión manual pendientes.
6. Redactar el reporte con el formato de abajo. Cifras exactas; si un dato no está disponible,
   escribir "sin dato" y el motivo.

## Formato del reporte

```markdown
# Palm Diamante · Reporte diario · <fecha>

## Prospectos nuevos: <n>
| Canal | Comprador real | Lead frío | Coyote |
|-------|----------------|-----------|--------|

## Seguimientos vencidos: <n>
| Prospecto | Asesor | Días de retraso | Último contacto | Acción |
|-----------|--------|-----------------|-----------------|--------|

## Inventario
| Tipología | Disponibles | Apartadas | Torre I / II / III |
|-----------|-------------|-----------|--------------------|

## Revisión manual (alerta roja): <n> tickets pendientes

## Pendientes de Jimmy
- <los de CLAUDE.md que siguen abiertos y afecten el reporte, p. ej. lista vigente>
```

## Reglas

- El reporte es interno: puede incluir precios y datos de inventario, pero **no se reenvía a
  clientes**.
- No calcular "velocidad de venta" ni proyecciones si no hay al menos 30 días de datos.
- Respetar `CLAUDE.md`: nunca incluir dominios ni teléfonos de la lista negra, ni siquiera como
  "fuente del lead" sin marcarlo como interno.
