---
name: auditar-sitio
description: Audita palm-diamante.com (visual, enlaces, consistencia de datos con la lista vigente, canales de terceros y velocidad) y entrega un reporte priorizado en tabla Hallazgo / Severidad / Corrección sugerida. Usar antes de una campaña, después de un cambio en el sitio o cuando Jimmy pida revisar la página.
argument-hint: "[url opcional, por defecto https://palm-diamante.com/es/]"
allowed-tools: Read, Grep, Glob, WebFetch, Bash(curl *), Bash(node *), Bash(npx *)
model: sonnet
disable-model-invocation: true
---

# /auditar-sitio

## Cuándo usarla

- Antes de lanzar una campaña o anuncio que mande tráfico al sitio.
- Después de que la agencia publique un cambio.
- Cuando Jimmy pida "revisar la página" o un cliente reporte algo raro.
- Si el usuario pasa una URL como argumento, auditar esa URL; si no, auditar
  `https://palm-diamante.com/es/` y `https://palm-diamante.com/en/`.

## Fuentes de verdad

- Reglas, canales y lista negra: `CLAUDE.md` de este repo (secciones "Canales" y
  "Discrepancias conocidas").
- Lista vigente y referencia interna: `palm_diamante_router/prompts/guia_respuestas_whatsapp.md`
  (rama `cursor/palm-diamante-router-1e3c`), sección "Referencia interna".
- Inventario: `palm_diamante_router/data/inventario_maestro.json`.

Si un dato del sitio contradice la lista, **la lista gana**; el sitio se reporta como hallazgo.

## Pasos

### 1. Revisión visual

Cargar cada página objetivo con Chrome DevTools (MCP) en escritorio (1440×900) y móvil
(390×844). Tomar captura de cada vista y revisar:

- Hero, galería, planos y sección de contacto se renderizan sin recortes ni imágenes rotas.
- Textos legibles, sin placeholders ("Lorem ipsum", "[…]", "TBD").
- Botones de WhatsApp visibles y funcionales en ambas vistas.
- Errores en consola (JS) y recursos 404 en la pestaña de red.

### 2. Enlaces

Extraer todos los `<a href>` y los `wa.me` / `tel:` / `mailto:` del HTML de cada página.
Verificar con `curl -sIL` que cada enlace externo responde 2xx/3xx y que los internos existen.
Reportar enlaces rotos, redirecciones a dominios inesperados y anclas vacías (`href="#"`).

### 3. Consistencia de datos con la lista vigente

Comparar cada cifra publicada con la referencia interna de la guía (lista del 15-sep-2026):

| Dato | Referencia interna |
|------|--------------------|
| Precio de entrada | $5.04 M (B1 76.04 m², solo Torre III) |
| Número de torres | 3 |
| Superficies | 76.04 a 178.84 m² |
| Recámaras | Penthouse 3 rec.; otros modelos sin confirmar |
| Financiamiento | no publicar plazos hasta confirmación por escrito |

Los casos conocidos de discrepancia (web $4.3 M vs. $5.04 M; 5 torres vs. 3; 152 m² vs.
178.84 m²) se reportan siempre mientras sigan en la web, con la nota "pendiente de Jimmy".
Cualquier fecha de entrega, porcentaje de avance o frase de urgencia publicada también es hallazgo.

### 4. Enlaces y canales de terceros (lista negra)

Además de verificar que los enlaces funcionen, confirmar que el sitio **no mencione ni enlace**
a ninguno de los dominios ni teléfonos de la lista negra de `CLAUDE.md`:

- Dominios: `palmdiamante.mx` (y su `/showroom`), `palmdiamanteacapulco.mx`,
  `palmdiamanteacapulco.com`, `ventadeptosacapulco.com`.
- Teléfonos: `55 4021 2638`, `744 271 3055`.

Cómo revisarlo:

1. Descargar el HTML de cada página (`curl -sL`) y también los JS/CSS propios enlazados,
   `robots.txt`, `sitemap.xml` y el `<head>` (canónicas, `og:url`, `hreflang`, JSON-LD).
2. Buscar los dominios sin distinguir mayúsculas y con y sin `www.` / `https://`.
3. Buscar los teléfonos **solo por dígitos** (quitar espacios, guiones, paréntesis y prefijo
   `+52`): `5540212638`, `7442713055`. Revisar también `href="tel:..."` y `wa.me/...`.
4. Verificar que los únicos canales publicados sean los nuestros: 55 4437 8776, 55 6100 0600,
   55 2855 7467 y palm-diamante.com. Un número que no esté en esa lista es hallazgo aunque no
   esté en la lista negra (severidad Media hasta que Jimmy lo confirme).

Cualquier coincidencia con la lista negra es severidad **Alta** y se reporta con la URL exacta,
el fragmento de HTML y la línea.

### 5. Velocidad

Correr Lighthouse (`npx lighthouse <url> --only-categories=performance --preset=desktop` y
sin `--preset` para móvil) o el trace de rendimiento de Chrome DevTools. Registrar LCP, CLS,
INP/TBT y peso total. Umbrales: LCP > 2.5 s o CLS > 0.1 en móvil es severidad Media; LCP > 4 s
es Alta. Listar las 3 imágenes/scripts más pesados con su corrección (formato, tamaño, lazy).

## Formato del reporte

Entregar siempre este formato, para que Jimmy o el equipo puedan priorizar:

```markdown
# Auditoría palm-diamante.com · <fecha> · <URLs auditadas>

Resumen: <n> hallazgos (Alta: x · Media: y · Baja: z). Lista de referencia: 15-sep-2026.

| # | Hallazgo | Severidad | Corrección sugerida |
|---|----------|-----------|---------------------|
| 1 | <qué, dónde (URL + elemento), evidencia (cifra/fragmento)> | Alta | <acción concreta y quién: agencia / Jimmy / equipo> |
| 2 | ... | Media | ... |
| 3 | ... | Baja | ... |

Pendientes de Jimmy detectados: <lista de discrepancias que requieren su decisión>
Capturas: <rutas de las capturas tomadas>
```

Criterios de severidad:

- **Alta:** mención o enlace a la lista negra; teléfono o dominio que no sea nuestro; precio,
  plazo, fecha de entrega o avance publicado que contradiga la lista o que no esté confirmado;
  formulario o botón de WhatsApp roto; LCP > 4 s.
- **Media:** enlace externo roto; discrepancia de dato secundario (torres, m², recámaras) ya
  conocida y pendiente de Jimmy; LCP 2.5–4 s o CLS > 0.1; imagen rota visible.
- **Baja:** detalles visuales, textos mejorables, imágenes sin optimizar sin impacto en LCP,
  anclas vacías, faltas de ortografía.

Ordenar la tabla por severidad (Alta primero). No proponer cambios de precio ni de datos
comerciales: para esos, la corrección sugerida es siempre "Confirmar con Jimmy y alinear web a
la lista vigente".
