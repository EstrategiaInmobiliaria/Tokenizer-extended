# Arquitectura del Sistema

## Visión General

Este sistema está diseñado para gestionar redes profesionales de 15k-50k contactos con capacidades de:
- Deduplicación probabilística
- Clasificación inteligente multi-dimensional
- Análisis de grafo en tiempo real
- Búsqueda semántica
- Automatización de workflows

---

## Stack Tecnológico

### Capa de Ingesta

**VCF Parser** (`vcf_processor/vcf_parser.py`)
- **Librería:** vobject
- **Función:** Parsea archivos vCard (VCF) de iOS/Android
- **Normalización:** Teléfonos (+52), emails lowercase, merge de arrays

**LinkedIn Processor** (`vcf_processor/linkedin_processor.py`)
- **Input:** CSV de conexiones oficial
- **Output:** DataFrame normalizado con fechas de conexión

**Instagram Processor** (`vcf_processor/instagram_processor.py`)
- **Input:** JSON export oficial
- **Features:** Detección de mutual follows, análisis de engagement

**WhatsApp Processor** (`whatsapp_integration/whatsapp_processor.py`)
- **Input:** Audio (OGG, MP3, M4A)
- **Pipeline:** Whisper → GPT-4o-mini → Embeddings → Supabase

### Capa de Deduplicación

**Splink** (`vcf_processor/deduplicator.py`)
- **Algoritmo:** Fellegi-Sunter probabilistic record linkage
- **Backend:** DuckDB (in-memory SQL para matching)
- **Comparisons:**
  - Exact match en email
  - Levenshtein distance en nombres (threshold: 1-2 edits)
  - Jaro-Winkler en nombres (threshold: 0.8-0.9)
  - Exact match en teléfono
  - Jaro-Winkler en empresa
  
**Blocking Rules:**
```python
[
  "l.email_primary = r.email_primary",
  "l.phone_primary = r.phone_primary",
  "substr(l.full_name, 1, 3) = substr(r.full_name, 1, 3)",
  "l.company = r.company"
]
```

**Output:** `cluster_id` por contacto (mismo ID = duplicados)

### Capa de Clasificación

**GPT-4o-mini** (`classification/gpt_classifier.py`)

**Prompt Structure:**
```
Context: Agartha (estrategia inmobiliaria + ESG en México)

Input: 
  - full_name
  - company
  - title
  - notes

Output JSON:
  - tier: Tier 1|Tier 2|Tier 3
  - temas: ["Inmobiliario", "ESG", ...]
  - zona: "CDMX"|"Monterrey"|...
  - reasoning: "1 línea de justificación"
```

**Cost:** ~$0.15 por 1M tokens input = ~$0.50 por 10k contactos

**Optimizaciones:**
- Batch processing (10 por vez)
- Skip si title/company vacíos → auto Tier 3
- Response format: `{"type": "json_object"}` para JSON garantizado

### Capa de Almacenamiento

**Supabase (PostgreSQL 14+)**

Schema:

```
contacts (tabla principal)
├── id (UUID PK)
├── full_name, company, title
├── email_primary, phone_primary
├── emails[], phones[], addresses[] (arrays)
├── tier, temas[], zona (clasificación)
├── cluster_id (Splink)
├── total_interactions, last_contact_date
└── timestamps

interactions (interacciones)
├── id (UUID PK)
├── contact_id (FK → contacts)
├── interaction_type (whatsapp_voice|call|meeting|...)
├── content (transcript)
├── summary (GPT resumen)
├── sentiment (positive|neutral|negative)
├── transcript_embedding (vector(1536)) ← búsqueda semántica
└── interaction_date

relationships (grafo)
├── id (UUID PK)
├── contact_from_id (FK)
├── contact_to_id (FK)
├── relationship_type (colleague|client|partner|...)
├── strength (0-1)
└── context

communities (clusters detectados)
├── id (UUID PK)
├── name, description
├── size, avg_tier
├── dominant_temas[], dominant_zona
└── modularity (calidad del cluster)

community_members (N:N)
├── community_id (FK)
├── contact_id (FK)
└── centrality_score
```

**Extensiones:**
- `vector` (pgvector) para embeddings
- `uuid-ossp` para UUIDs

**Funciones Custom:**
- `search_contacts_fulltext(query TEXT)` → búsqueda en español
- `search_interactions_by_embedding(vector, threshold, limit)` → búsqueda semántica

**Kùzu (Graph Database)**

Schema:

```cypher
CREATE NODE TABLE Contact (
  contact_id STRING PRIMARY KEY,
  full_name STRING,
  tier STRING,
  zona STRING,
  total_interactions INT64
)

CREATE REL TABLE KNOWS (
  FROM Contact TO Contact,
  relationship_type STRING,
  strength DOUBLE
)
```

**Queries típicos:**

```cypher
// Red de un contacto (depth=2)
MATCH path = (start:Contact {contact_id: 'X'})-[:KNOWS*1..2]-(connected)
RETURN connected, LENGTH(path)

// Conexiones en común
MATCH (a:Contact {contact_id: 'X'})-[:KNOWS]-(common)-[:KNOWS]-(b:Contact {contact_id: 'Y'})
RETURN common

// Contactos más centrales
MATCH (c:Contact)-[r:KNOWS]-()
RETURN c, COUNT(r) as degree
ORDER BY degree DESC
```

### Capa de Grafo y Comunidades

**NetworkX** (para análisis)
- Exportamos desde Kùzu a NetworkX Graph
- Algoritmos disponibles:
  - `community_louvain` (detección de comunidades)
  - `betweenness_centrality` (influencers)
  - `pagerank` (importancia)
  - `connected_components` (sub-redes aisladas)

**Louvain Algorithm:**
- Detecta comunidades maximizando modularidad
- Modularidad Q ∈ [-0.5, 1] (>0.3 = bueno)
- Output: Dict `{contact_id: community_id}`

**Ejemplo de salida:**
```
Community 0: 487 miembros
  • Temas dominantes: Inmobiliario (78%), ESG (45%)
  • Zona: CDMX (62%)
  • Avg Tier: 2.3

Community 1: 324 miembros
  • Temas dominantes: ESG (91%), Sustentabilidad (67%)
  • Zona: Monterrey (88%)
  • Avg Tier: 1.8
```

### Capa de Búsqueda Semántica

**OpenAI Embeddings** (`text-embedding-3-small`)
- **Dimensiones:** 1536
- **Uso:** Transcripciones de interacciones
- **Storage:** Supabase pgvector con índice IVFFlat

**Cosine Similarity:**
```sql
SELECT 
  content,
  1 - (transcript_embedding <=> query_embedding) as similarity
FROM interactions
WHERE 1 - (transcript_embedding <=> query_embedding) > 0.7
ORDER BY transcript_embedding <=> query_embedding
LIMIT 10
```

**Caso de uso:**
```python
# "¿En qué reuniones se habló de certificación LEED?"
query = "certificación LEED sustentabilidad edificios"
embedding = openai.embeddings.create(input=query, model="text-embedding-3-small")

results = supabase.rpc(
  'search_interactions_by_embedding',
  {'query_embedding': embedding.data[0].embedding}
)
```

### Capa de Automatización

**n8n Workflow**

Flujo WhatsApp → Supabase:

```
1. Webhook recibe mensaje WhatsApp
2. IF type == 'voice':
3.   Download audio from media_url
4.   Save to /data/raw/whatsapp/
5.   Execute: whatsapp_processor.py {audio} {phone}
6.   Parse JSON output
7.   Find contact by phone in Supabase
8.   IF contact exists:
9.     Insert into interactions table
10.    Call HTTP endpoint to update Kùzu
11.    Return success
12.  ELSE:
13.    Return "contact not found"
```

**Trigger Options:**
- Webhook (n8n local)
- WhatsApp Business API
- Evolution API (más fácil, QR code)

---

## Flujos de Datos

### Pipeline VCF Completo

```
1. VCFParser.parse_file(vcf_path)
   ↓ List[Contact]
   
2. VCFParser.to_dataframe()
   ↓ DataFrame[2500 rows × 12 cols]
   
3. ContactDeduplicator.deduplicate(df, threshold=0.8)
   ↓ DataFrame + cluster_id
   
4. ContactDeduplicator.merge_duplicates()
   ↓ DataFrame[1890 unique contacts]
   
5. GPTClassifier.classify_batch(contacts)
   ↓ List[ContactClassification]
   
6. GPTClassifier.add_classifications_to_df()
   ↓ DataFrame + [tier, temas, zona]
   
7. SupabaseContactManager.upload_contacts(df)
   ↓ 1890 rows inserted
   
8. SupabaseContactManager.get_all_contacts()
   ↓ DataFrame with UUID ids
   
9. KuzuGraphEngine.load_contacts_from_df()
   ↓ Graph built in Kùzu
```

### Pipeline WhatsApp Voice Note

```
1. n8n webhook receives POST
   ↓ {type: 'voice', from: '+52...', media_url: '...'}
   
2. Download audio
   ↓ audio.ogg saved to disk
   
3. WhatsAppProcessor.transcribe_audio()
   ↓ Whisper API
   ↓ "Tuvimos reunión con Juan de Agartha..."
   
4. WhatsAppProcessor.extract_meeting_info()
   ↓ GPT-4o-mini structured output
   ↓ {resumen, contactos, temas, proximos_pasos, sentimiento}
   
5. WhatsAppProcessor.create_embedding()
   ↓ OpenAI Embeddings
   ↓ vector(1536)
   
6. Supabase: find contact by phone
   ↓ contact_id or null
   
7. IF found:
     Insert into interactions
     ↓ {contact_id, content, summary, embedding}
     
8. Update Kùzu graph
   ↓ Increment total_interactions
   
9. Return success
```

---

## Performance

### Benchmarks

**VCF Processing (10k contactos):**
- Parse: ~5 segundos
- Deduplication (Splink): ~60 segundos
- Classification (GPT): ~8 minutos (con rate limiting)
- Upload Supabase: ~10 segundos
- Kùzu load: ~3 segundos
- **Total: ~10 minutos**

**WhatsApp Voice Note (3 min audio):**
- Transcription (Whisper): ~15 segundos
- Analysis (GPT): ~3 segundos
- Embedding: ~1 segundo
- Supabase insert: <1 segundo
- **Total: ~20 segundos**

**Graph Queries:**
- Find contact network (depth=2): <100ms
- Detect communities (10k nodes): ~5 segundos
- Central contacts (top 100): <50ms

### Escalabilidad

**Límites actuales:**
- Contactos: Probado hasta 50k (Supabase + Kùzu manejan millones)
- Interacciones: Embeddings indexados con IVFFlat (hasta ~1M vectores eficientemente)
- Grafo: Kùzu embebido maneja ~10M edges sin problemas

**Optimizaciones futuras:**
- Batch classification: 100 contactos en paralelo
- Incremental graph updates (no rebuild completo)
- Materialized views en Supabase para queries frecuentes

---

## Seguridad

### Data at Rest
- Supabase: Encryption at rest (AES-256)
- Kùzu: Local filesystem (cifrar volumen si es necesario)

### Data in Transit
- Supabase: TLS 1.3
- OpenAI API: HTTPS

### Row Level Security (RLS)
Supabase permite RLS por usuario:

```sql
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see own contacts" ON contacts
  FOR SELECT USING (auth.uid() = user_id);
```

(Opcional, útil si hay múltiples usuarios)

### API Keys
- `.env` en `.gitignore`
- Variables de entorno en producción
- Rotate keys periódicamente

---

## Monitoreo

### Logs
- n8n: `~/.n8n/logs/n8n.log`
- Python: stdout/stderr (usar `rich.console` para formatting)

### Métricas Clave
1. **Tasa de deduplicación:** `(total - unique) / total`
2. **Precisión de clasificación:** Validar sample de 100 contactos manualmente
3. **Latencia WhatsApp:** webhook → respuesta (<30s esperado)
4. **Modularidad de grafo:** >0.3 indica comunidades bien definidas

### Alertas
- Splink threshold <0.5 → demasiados falsos positivos
- GPT classification >20s por contacto → revisar prompts o cambiar a batch
- Supabase >1000ms query → añadir índices

---

## Extensiones Futuras

### Analytics Dashboard
- Streamlit o Next.js
- Gráficos de distribución Tier/Zona
- Timeline de interacciones
- Visualización de grafo con D3.js o Cytoscape

### Recomendaciones
```python
# "¿Con quién debería conectar a Juan?"
# Encuentra contactos similares sin conexión directa
```

### Email Integration
- Gmail API para leer emails
- Classify senders automáticamente
- Añadir a `interactions`

### Calendar Sync
- Google Calendar / Outlook
- Detectar reuniones con contactos
- Auto-log interacciones

---

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────┐
│                  CLIENT LAYER                       │
├─────────────────────────────────────────────────────┤
│  • CLI (main_pipeline.py)                           │
│  • n8n UI (workflows)                               │
│  • (Future) Web Dashboard                           │
└────┬────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│               APPLICATION LAYER                     │
├─────────────────────────────────────────────────────┤
│  VCF Parser  │ LinkedIn │ Instagram │ WhatsApp      │
│  Deduplicator│ Processor│ Processor │ Processor     │
│  GPT Classifier                                     │
└────┬────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│                  DATA LAYER                         │
├─────────────────────────────────────────────────────┤
│  Supabase Client  │  Kùzu Graph Engine              │
│  (PostgreSQL)     │  (Embedded Graph DB)            │
└────┬──────────────┴──────────────────────────────┬──┘
     │                                             │
     ▼                                             ▼
┌──────────────────┐                    ┌──────────────────┐
│   Supabase       │                    │   Kùzu DB        │
│   (Cloud)        │                    │   (Local)        │
│                  │                    │                  │
│  • contacts      │                    │  • Contact nodes │
│  • interactions  │                    │  • KNOWS edges   │
│  • relationships │                    │                  │
│  • communities   │                    │                  │
└──────────────────┘                    └──────────────────┘
```

---

## Referencias

- [Splink Documentation](https://moj-analytical-services.github.io/splink/)
- [Kùzu Documentation](https://docs.kuzudb.com/)
- [Supabase Docs](https://supabase.com/docs)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [n8n Documentation](https://docs.n8n.io/)

---

## Créditos

Arquitectura diseñada para balance entre:
- **Costo:** Minimizar llamadas a APIs pagas
- **Performance:** Procesar 10k contactos en <15 min
- **Escalabilidad:** Soportar hasta 100k contactos
- **Privacidad:** Datos bajo control del usuario (self-hosted donde sea posible)
