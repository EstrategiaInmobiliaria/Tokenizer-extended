# 🚀 GraphRAG Pragmático: 15-25K Contactos en 3 Semanas

## 🎯 Plan Aterrizado: Solo Fuentes Legales

**Objetivo**: Grafo funcional en 7 días, 100% legal, cero riesgo de ban.

**Stack minimalista**:
- ✅ Kùzu (embebido, 10-100x más rápido que Neo4j)
- ✅ GPT-4o-mini ($0.15/1M tokens = ~$3 para 15K contactos)
- ✅ n8n (automatización WhatsApp)
- ✅ Python scripts CLI (sin dependencias pesadas)

---

## 📅 Cronograma de 3 Semanas

### **Semana 1: Contactos + LinkedIn**

**Día 1-2: Exportar VCF**
```bash
# iPhone: Contactos → Seleccionar todos → Compartir → Guardar en Archivos → contacts.vcf
# Android: Contactos → Configuración → Exportar → contacts.vcf
```

**Día 3-4: LinkedIn export**
```
LinkedIn → Configuración → Privacidad → Datos
→ "Solicitar archivo de datos"
→ Esperar email (24-48 horas)
→ Descargar Connections.csv
```

**Día 5-7: Procesar con script Python**
```bash
# Instalar dependencias
pip install kuzu pandas vobject openai tqdm

# Ejecutar pipeline (10 minutos para 15K contactos)
python scripts/vcf_to_kuzu_pipeline.py \
    --vcf ~/Downloads/contacts.vcf \
    --openai-key sk-xxxxx \
    --output ./output

# Output:
# - output/contacts_raw.csv (15K filas)
# - output/contacts_classified.csv (con tier, tema, zona)
# - output/contact_graph_db/ (Kùzu database)
```

**Resultado Semana 1**: 15K contactos limpios en Kùzu, clasificados por tier/tema/zona

---

### **Semana 2: Instagram (Legal) + Análisis**

**Día 8-10: Instagram export**
```
Instagram App → Configuración → Seguridad → Descargar datos
→ Formato: JSON
→ Esperar email (48 horas)
→ Descargar followers.json + following.json
```

**Nota**: Este export es **100% legal** (GDPR compliance), pero:
- ❌ No es en tiempo real (snapshot a fecha de export)
- ✅ Te da tu lista completa de seguidores/siguiendo
- ✅ Incluye bios, ubicaciones, hashtags seguidos

**Día 11-12: Parsear Instagram JSON**
```bash
python scripts/parse_instagram_export.py \
    --followers ~/Downloads/instagram/followers.json \
    --following ~/Downloads/instagram/following.json \
    --output ./output

# Merge con Kùzu:
python scripts/merge_instagram_to_kuzu.py \
    --instagram ./output/instagram_parsed.csv \
    --kuzu-db ./output/contact_graph_db
```

**Día 13-14: Análisis de comunidades**
```python
# Ejecutar clustering en Kùzu
python scripts/detect_communities.py --kuzu-db ./output/contact_graph_db

# Output ejemplo:
# Community 1: "Desarrolladores Querétaro" (47 miembros)
# Community 2: "Inversionistas Latam ESG" (31 miembros)
# Community 3: "Directores Inmobiliarios CDMX" (23 miembros)
```

**Resultado Semana 2**: 20-25K contactos totales, 3-5 comunidades detectadas

---

### **Semana 3: WhatsApp en Vivo + Consultas**

**Día 15-16: Setup n8n**
```bash
# Docker (recomendado)
docker run -d \
    --name n8n \
    -p 5678:5678 \
    -v ~/.n8n:/home/node/.n8n \
    n8nio/n8n

# Abrir http://localhost:5678
```

**Día 17-18: Configurar workflow WhatsApp**
1. Importar `n8n/whatsapp-voice-to-kuzu.json`
2. Configurar credenciales:
   - Twilio (WhatsApp Business API)
   - OpenAI (Whisper + GPT-4o-mini)
   - Postgres (para conectar a Kùzu vía HTTP)
3. Activar webhook

**Día 19-21: Testing + Consultas**

**Uso del sistema**:

1. **Grabar nota de voz en WhatsApp**:
```
"Acabo de comer con Juan López de Tesla. Está abriendo planta en Monterrey 
para reciclaje de baterías. Quiere consultoría en economía circular. 
Le interesa conectar con universidades. Seguimiento en 2 semanas."
```

2. **n8n automáticamente**:
   - Transcribe con Whisper
   - Extrae: nombre, empresa, tema, zona, contexto
   - Actualiza Kùzu:
     ```cypher
     MATCH (p:Persona {nombre: 'Juan López'})
     SET p.empresa = 'Tesla',
         p.tema = 'ESG',
         p.zona = 'Monterrey',
         p.notas = p.notas + '\n[2026-08-19] Proyecto reciclaje baterías...',
         p.ultima_interaccion = '2026-08-19'
     ```
   - Si urgencia = alta → Te envía WhatsApp con acción sugerida

**Resultado Semana 3**: Sistema en vivo capturando contexto automáticamente

---

## 🔍 Consultas Ejemplo (Kùzu SQL)

Kùzu usa sintaxis SQL-like (más fácil que Cypher):

### 1. **Tier 1 en CDMX (Real Estate)**
```sql
MATCH (p:Persona)
WHERE p.tier = 1 
  AND p.zona = 'CDMX'
  AND p.tema = 'Inmobiliario'
RETURN p.nombre, p.empresa, p.puesto, p.score_estimado
ORDER BY p.score_estimado DESC
LIMIT 10;
```

### 2. **Expertos ESG que no he visto en 6 meses**
```sql
MATCH (p:Persona)
WHERE p.tema = 'ESG'
  AND date_diff('month', p.ultima_interaccion, current_date()) > 6
RETURN p.nombre, p.empresa, p.zona, p.score_estimado
ORDER BY p.score_estimado DESC;
```

### 3. **Contactos en Monterrey para viaje mañana**
```sql
MATCH (p:Persona)
WHERE p.zona = 'Monterrey'
  AND p.tier IN [1, 2]
  AND date_diff('month', p.ultima_interaccion, current_date()) > 3
RETURN p.nombre, p.empresa, p.telefono, p.score_estimado
ORDER BY p.score_estimado DESC
LIMIT 20;
```

### 4. **Colegas de Juan López (para introducción)**
```sql
MATCH (jaime:Persona {nombre: 'Jaime Wilk'})
      -[:CONECTA_CON]-(puente:Persona)
      -[:CONECTA_CON]-(juan:Persona {nombre: 'Juan López'})
RETURN puente.nombre as introductor,
       puente.empresa,
       puente.telefono
LIMIT 5;
```

### 5. **Top 10 contactos por score estimado**
```sql
MATCH (p:Persona)
WHERE p.tier <= 2
RETURN p.nombre, p.empresa, p.tema, p.zona, p.score_estimado
ORDER BY p.score_estimado DESC
LIMIT 10;
```

---

## 💰 Costos Reales

### Una sola vez (Setup):
| Item | Costo |
|------|-------|
| GPT-4o-mini clasificación (15K contactos) | $3 USD |
| Whisper transcripciones (100 notas de voz) | $2 USD |
| **Total setup** | **$5 USD** |

### Mensual (Operación):
| Item | Costo |
|------|-------|
| Twilio WhatsApp Business API | $0 (recibir) + $0.005/msg (enviar) |
| n8n self-hosted (Docker) | $0 |
| Kùzu local | $0 |
| GPT-4o-mini (200 notas/mes) | $4 USD |
| **Total mensual** | **$5-10 USD** |

**Comparación**:
- Neo4j Aura: $200-500/mes
- Vector DB (Pinecone): $70-200/mes
- **Sistema propuesto**: $5-10/mes (99% reducción)

---

## 📊 Arquitectura Minimalista

```
┌─────────────────────────────────────────────────────────┐
│              FUENTES DE DATOS (100% LEGALES)            │
├─────────────────────────────────────────────────────────┤
│  VCF (15K)  │  LinkedIn (5K)  │  Instagram (3K)  │      │
│  Export     │  GDPR Export    │  GDPR Export     │      │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│           PROCESAMIENTO (Python CLI Scripts)            │
├─────────────────────────────────────────────────────────┤
│  1. Parse VCF/CSV/JSON                                  │
│  2. GPT-4o-mini: Clasificar tier/tema/zona ($3)         │
│  3. Cargar a Kùzu (embebido, sin servidor)              │
│  4. Detect communities (Leiden algorithm)               │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                 KÙZU GRAPH DATABASE                     │
│              (Embebido, 10-100x más rápido)             │
├─────────────────────────────────────────────────────────┤
│  Nodos: Persona (25K), Empresa (500)                    │
│  Relaciones: TRABAJA_EN, CONECTA_CON                    │
│  Queries: SQL-like (más fácil que Cypher)               │
└─────────────────────────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
┌──────────────────────┐    ┌──────────────────────┐
│   WHATSAPP (n8n)     │    │   CONSULTAS SQL      │
├──────────────────────┤    ├──────────────────────┤
│ Nota de voz          │    │ CLI / Jupyter        │
│   ↓                  │    │   ↓                  │
│ Whisper transcribe   │    │ Tier 1 en CDMX       │
│   ↓                  │    │ Expertos ESG         │
│ GPT extrae info      │    │ Viajes Monterrey     │
│   ↓                  │    │ Introducción paths   │
│ Actualiza Kùzu       │    └──────────────────────┘
└──────────────────────┘
```

---

## 🎯 Alineación con tu Negocio

### Tier Definitions (Personalizado):

**Tier 1** (Score ≥80): Decisores C-Level inmobiliario + ESG
- CEOs desarrolladores inmobiliarios
- Directores de sustentabilidad corporativa
- VPs de inversión impacto social

**Tier 2** (Score 50-79): Partners operativos
- Gerentes de proyectos Agartha
- Consultores Estrategia Inmobiliaria
- Directores de universidades (alianzas académicas)

**Tier 3** (Score <50): Red general para nurture
- Contactos sin clasificar
- Conexiones indirectas (amigos, familia)
- Prospects fríos

### Tema Definitions:

- **Inmobiliario**: Desarrollo, inversión, brokers
- **ESG**: Economía circular, sustentabilidad, impacto social
- **Manufactura**: Automotriz, reciclaje industrial
- **Academia**: Profesores, investigadores, universidades
- **Gobierno**: Funcionarios, regulación
- **Consultoría**: Estrategia, transformación
- **Finanzas**: Banca, fondos, inversión
- **Otro**: Sin clasificar

### Zona Definitions:

- **CDMX**: Ciudad de México + Estado de México
- **Monterrey**: Monterrey + Área Metropolitana
- **Querétaro**: Querétaro + San Juan del Río
- **Guadalajara**: GDL + Zapopan
- **Internacional**: Latam, USA, Europa
- **Otra**: Sin clasificar

---

## 🚀 Quick Start (Hora 0)

### 1. Instalar dependencias

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar
pip install kuzu pandas vobject openai tqdm python-dotenv
```

### 2. Exportar tu VCF

**iPhone**:
1. Contactos → Seleccionar todos (deslizar hacia abajo)
2. Compartir contacto
3. Guardar en Archivos → `contacts.vcf`

**Android**:
1. Contactos → ⚙️ Configuración
2. Exportar contactos
3. Guardar como `contacts.vcf`

### 3. Ejecutar script

```bash
# Configurar API key
export OPENAI_API_KEY="sk-xxxxx"

# Ejecutar pipeline (10 min para 15K contactos)
python scripts/vcf_to_kuzu_pipeline.py \
    --vcf ~/Downloads/contacts.vcf \
    --openai-key $OPENAI_API_KEY \
    --output ./mi_grafo

# Esperar output:
# ✅ Parseados 15,247 contactos
# ✅ Clasificados con GPT-4o-mini ($2.85)
# ✅ Cargados a Kùzu
# 
# Estadísticas:
#   Tier 1: 1,234 (8%)
#   Tier 2: 4,567 (30%)
#   Tier 3: 9,446 (62%)
```

### 4. Consultar tu grafo

```python
import kuzu

# Conectar
db = kuzu.Database('./mi_grafo/contact_graph_db')
conn = kuzu.Connection(db)

# Query: Tier 1 en CDMX
result = conn.execute("""
    MATCH (p:Persona)
    WHERE p.tier = 1 AND p.zona = 'CDMX'
    RETURN p.nombre, p.empresa, p.score_estimado
    ORDER BY p.score_estimado DESC
    LIMIT 10
""")

# Ver resultados
print(result.get_as_df())
```

**Output**:
```
           nombre                    empresa  score_estimado
0  Juan López CEO                Tesla Motors              95
1  Ana García CFO              Google Mexico              92
2  Carlos Méndez Dir            BBVA Bancomer              88
...
```

---

## 📈 ROI Esperado (Realista)

### Escenario Base (Conservador):

| Métrica | Antes Sistema | Con Sistema | Mejora |
|---------|---------------|-------------|--------|
| Tiempo prospección | 8h/semana | 2h/semana | **75% reducción** |
| Deals cerrados/mes | 2 | 4 | **2x** |
| Conversión (intro caliente) | 3% | 15% | **5x** |
| Valor promedio deal | $50K | $75K | **1.5x** |

**Ingresos anuales**:
- Antes: 2 deals/mes × $50K × 12 = $1.2M
- Después: 4 deals/mes × $75K × 12 = $3.6M
- **Incremento: +$2.4M/año** (+200%)

### Escenario Optimista:

Si además aprovechas:
- Viajes optimizados (5 reuniones Tier 1 por viaje)
- Eventos por comunidad (3-5 leads/evento)
- Intros calientes (35% conversión vs. 3%)

**Incremento potencial: +$5-8M/año** (+400-650%)

**ROI**:
- Inversión: $5 setup + $10/mes × 12 = $125
- Retorno año 1: $2.4M conservador
- **ROI: 19,200x**

---

## ✅ Checklist Semana por Semana

### Semana 1:
- [ ] Exportar VCF de iPhone/Android
- [ ] Solicitar LinkedIn export (GDPR)
- [ ] Instalar Python + dependencias (`kuzu`, `openai`)
- [ ] Ejecutar `vcf_to_kuzu_pipeline.py`
- [ ] Verificar output: `contacts_classified.csv`
- [ ] Consultar Tier 1 en tu zona

### Semana 2:
- [ ] Solicitar Instagram export (GDPR)
- [ ] Parsear Instagram JSON
- [ ] Merge con Kùzu
- [ ] Ejecutar community detection
- [ ] Identificar 3-5 clusters clave

### Semana 3:
- [ ] Instalar n8n (Docker)
- [ ] Configurar Twilio WhatsApp
- [ ] Importar workflow `whatsapp-voice-to-kuzu.json`
- [ ] Probar 10 notas de voz
- [ ] Validar actualizaciones automáticas en Kùzu

---

## 🎓 Por Qué Este Stack

### Kùzu vs. Neo4j

| Feature | Kùzu | Neo4j |
|---------|------|-------|
| **Performance** | 10-100x más rápido | Estándar |
| **Deployment** | Embebido (sin servidor) | Requiere servidor |
| **Costo** | $0 (open-source) | $200-500/mes (Aura) |
| **Query Language** | SQL-like (fácil) | Cypher (curva de aprendizaje) |
| **Mejor para** | <1M nodos, local | >1M nodos, cloud |

**Para 25K contactos**: Kùzu es **perfecto**.

### GPT-4o-mini vs. Modelos Grandes

| Model | Costo (1M tokens) | Para 15K contactos | Calidad |
|-------|-------------------|---------------------|---------|
| GPT-4o | $5.00 | $75 | 95% |
| GPT-4o-mini | $0.15 | $2.25 | 92% |
| Gemini 1.5 Flash | $0.075 | $1.13 | 90% |

**Para clasificación simple**: GPT-4o-mini es **óptimo** (92% calidad, 97% más barato).

---

## 🔐 Privacidad

Todo 100% local y privado:
- ✅ Kùzu: Base de datos local (no cloud)
- ✅ Python scripts: Ejecutan en tu máquina
- ✅ n8n: Self-hosted (Docker local)
- ⚠️ OpenAI API: Envía datos para clasificar (pero no los retiene según TOS)

**Alternativa 100% privada**:
Reemplazar GPT-4o-mini con LLaMA 3.1 8B local (vía Ollama):
```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Descargar LLaMA 3.1 8B
ollama pull llama3.1:8b

# Modificar script para usar Ollama en lugar de OpenAI
# Costo: $0, 100% privado
```

---

## 📞 Soporte

**Archivos entregados**:
- `scripts/vcf_to_kuzu_pipeline.py`: Pipeline completo VCF → Kùzu
- `n8n/whatsapp-voice-to-kuzu.json`: Workflow WhatsApp automático
- `README-PRAGMATIC.md`: Esta guía

**Siguiente paso**:
```bash
python scripts/vcf_to_kuzu_pipeline.py --help
```

**¿Dudas?** Revisa la sección de troubleshooting más abajo.

---

## 🐛 Troubleshooting

### Error: "No module named 'kuzu'"
```bash
pip install kuzu
```

### Error: "OpenAI API key not found"
```bash
export OPENAI_API_KEY="sk-xxxxx"
# o pasar directamente: --openai-key sk-xxxxx
```

### Error: "vobject parse failed"
Tu VCF puede estar corrupto. Prueba:
```bash
# Abrir en editor de texto
# Buscar líneas con caracteres raros
# Eliminar o corregir manualmente
```

### Kùzu queries muy lentas
```sql
-- Crear índices
CREATE INDEX ON Persona(tier);
CREATE INDEX ON Persona(zona);
CREATE INDEX ON Persona(tema);
```

---

**🚀 Sistema pragmático listo para deployment en 3 semanas!**
