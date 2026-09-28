# Palm Diamante · Estrategia Inmobiliaria

Instrucciones de proyecto para Claude Code y cualquier asistente o bot que trabaje en este
repositorio. Leer completo antes de redactar, auditar o programar nada relacionado con
Palm Diamante.

## Contexto

- **Proyecto:** Palm Diamante, Costera de las Palmas, Granjas del Marqués, C.P. 39890,
  Acapulco Diamante, Guerrero. Desarrolladora: Agartha Bienes Raices.
- **Quién vende:** Estrategia Inmobiliaria. Aprobador único de todo mensaje a cliente: **Jimmy**.
- **Sitio nuestro:** https://palm-diamante.com/es/ (versión en inglés en `/en/`).
- **Código relacionado:** `palm_diamante_router/` (rama `cursor/palm-diamante-router-1e3c`):
  router FastAPI de primer contacto, inventario maestro JSON, política de comunicación y guía
  de respuestas de WhatsApp. La política vive en `palm_diamante_router/router/policy.py` y la
  guía en `palm_diamante_router/prompts/guia_respuestas_whatsapp.md`.

## Reglas de comunicación (no negociables)

1. **Todo es borrador.** Nada se envía a un cliente sin aprobación de Jimmy.
2. **Siempre la verdad.** No inventar precios, disponibilidad, fechas, plazos ni condiciones.
   Todo dato sale del inventario maestro o de la lista vigente; si no está ahí, no se afirma.
3. **Sin precios hasta que Jimmy confirme que la lista del 15-sep-2026 sigue vigente.**
   Mientras, se usa la respuesta `/sinprecio`.
4. **Sin promesas de entrega ni avance de obra.** "Un asesor te lo confirma".
5. **Sin urgencia no respaldada** ("últimas unidades", "el precio sube", etc.).
6. **Lo que está entre [corchetes] se confirma o se borra** antes de enviar.
7. **Cerrar con `/calificar`** (uso, presupuesto, forma de pago) cuando el borrador no termina
   en una pregunta.

## Canales

**Nuestros canales (los únicos que se comunican al cliente):**

| Tipo | Valor |
|------|-------|
| WhatsApp principal | 55 4437 8776 (`wa.me/525544378776`) |
| Teléfono / WhatsApp | 55 6100 0600 |
| Teléfono / WhatsApp | 55 2855 7467 |
| Sitio | palm-diamante.com/es |

**Lista negra (uso interno, nunca se mencionan ni se enlazan):**

| Tipo | Valor |
|------|-------|
| Dominio | palmdiamante.mx (incluido su recorrido `/showroom`) |
| Dominio | palmdiamanteacapulco.mx |
| Dominio | palmdiamanteacapulco.com |
| Dominio | ventadeptosacapulco.com |
| Teléfono | 55 4021 2638 |
| Teléfono | 744 271 3055 |

Si un cliente trae información de esos canales, solo se le confirma la información correcta,
sin hablar de terceros. Cualquier borrador, página o documento que contenga uno de estos
valores es una violación de severidad **Alta**.

## Discrepancias conocidas web vs. lista (pendientes de Jimmy)

Hasta que Jimmy resuelva cada punto, **prevalece la lista del 15-sep-2026** y el dato de la web
se marca como hallazgo, no se corrige por cuenta propia:

| Dato | Web dice | Lista dice |
|------|----------|------------|
| Precio de entrada | $4.3 M | $5.04 M (B1 76.04 m², solo Torre III) |
| Número de torres | 5 | 3 |
| Tamaño máximo | 152 m² | 178.84 m² (Penthouse) |
| Recámaras por modelo | varios | solo indicadas en Penthouse (3) |

Otros pendientes: terrazas y amenidades, plazos de financiamiento por escrito, lugar y horario
de citas, dossier PDF con fechas de entrega y avance de obra.

## Herramientas de Claude Code en este repo

| Herramienta | Ubicación | Uso |
|-------------|-----------|-----|
| `/reporte-diario` | `.claude/skills/reporte-diario/` | Resumen diario de prospectos, seguimientos vencidos y apartados |
| `/auditar-sitio` | `.claude/skills/auditar-sitio/` | Auditoría visual, de enlaces, de datos, de canales y de velocidad de palm-diamante.com |
| `auditor-inventario` | `.claude/agents/auditor-inventario.md` | Subagente que revisa un borrador antes de enviarlo: precios, canales, lista negra, promesas |
| MCP | `.mcp.json` | Supabase (OAuth), Chrome DevTools, Context7 |

Uso manual del subagente mientras no exista el envío real de WhatsApp:
"Usa auditor-inventario para revisar este borrador antes de enviarlo."

**Hooks:** pendientes. Se activan cuando exista la herramienta de envío de WhatsApp
(WhatsApp Business API / MCP). Hasta entonces la validación automática equivalente ya corre en
código en `PoliticaComunicacion.validar_borrador` y en los tests del router.

## Modelos aprobados

Catálogo vigente de Anthropic (verificado el 28-sep-2026 en
https://docs.anthropic.com/en/docs/about-claude/models/overview): Claude Fable 5.1, Claude
Opus 5, Claude Sonnet 5 y Claude Haiku 4.5. Las familias Claude 3 / 3.5 (Haiku 3, Sonnet 3.5)
ya no aparecen en el catálogo vigente y **no se usan**.

### Por componente

| Componente | Modelo aprobado | ID de API | Alternativa | Por qué |
|------------|-----------------|-----------|-------------|---------|
| Bot de WhatsApp: clasificación Comprador / Lead frío / Coyote y respuestas cortas con plantilla | **Claude Haiku 4.5** | `claude-haiku-4-5` | Claude Sonnet 5 si la precisión del clasificador baja del umbral acordado | Muchas respuestas cortas; el más rápido y barato ($1 / $5 por MTok). El router actual es determinista; el LLM entra solo como clasificador o redactor de borradores |
| Borradores que incluyen precios o datos de inventario | **Claude Sonnet 5** | `claude-sonnet-5` | Claude Opus 5 | Los números deben salir exactos del inventario; Sonnet equilibra velocidad y precisión |
| Subagente `auditor-inventario` (revisión de borradores) | **Claude Sonnet 5** | `claude-sonnet-5` | Claude Opus 5 | Revisión rápida y sistemática contra la lista y la lista negra |
| `/auditar-sitio`, `/reporte-diario` | **Claude Sonnet 5** | `claude-sonnet-5` | Claude Opus 5 | Trabajo con navegador/Supabase de varios pasos, pero acotado |
| Análisis de ventas, reportes ejecutivos, reescritura de prompts y guías | **Claude Opus 5** | `claude-opus-5` | Claude Fable 5.1 para análisis largos o de varias fuentes | Mayor razonamiento y contexto (1M tokens) |
| Sesiones de desarrollo en Claude Code / Cursor sobre este repo | **Claude Opus 5** o **Claude Fable 5.1** | `claude-opus-5` / `claude-fable-5-1` | Claude Sonnet 5 para cambios pequeños | Refactors y trabajo agéntico largo |

Equivalentes de otros proveedores (solo si Anthropic no está disponible en la integración):
para el bot, el modelo "mini"/"flash" vigente del proveedor; para análisis, su modelo grande
vigente. Documentar aquí cuál se usó y por qué antes de ponerlo en producción.

### Reglas

1. Un modelo que no esté en esta tabla **no se usa** sin autorización de Jimmy. La lista se
   aplica también en `.claude/settings.json` (`availableModels`), que restringe `/model`,
   `--model` y el campo `model` de skills y subagentes.
2. El modelo nunca sustituye la fuente de verdad: los precios y la disponibilidad salen del
   inventario maestro, no de la memoria del modelo, sin importar cuál sea.
3. Revisar esta sección cada trimestre o cuando Anthropic anuncie un retiro (las fechas de
   retiro están en la página de cada modelo). Usar los alias sin fecha (`claude-sonnet-5`,
   `claude-haiku-4-5`) para que las actualizaciones menores entren solas.
4. Cualquier cambio de modelo en producción se prueba primero contra los tests del router
   (`pytest -q` en `palm_diamante_router/`) y contra 20 mensajes reales de WhatsApp
   anonimizados.
