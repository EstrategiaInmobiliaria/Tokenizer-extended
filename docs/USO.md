# Guía de Uso - Sistema de Gestión de Red de Contactos

## Pipeline Completo: De 0 a Red Operativa en 7 Días

---

## 📁 Semana 1: Contactos + LinkedIn (Días 1-2)

### Paso 1: Exportar VCF de tu Teléfono

**iPhone:**
1. Configuración → Contactos → Cuentas
2. iCloud → Contactos (asegúrate que esté activado)
3. Desde Mac/PC: iCloud.com → Contactos → Seleccionar todos → Export vCard

**Android:**
1. Contactos → ⋮ → Configuración → Exportar
2. Selecciona "Exportar a archivo VCF"
3. Guarda en Google Drive o transfiere a PC

### Paso 2: Procesar VCF

```bash
cd /workspace/backend

# Procesar VCF completo (con clasificación GPT)
python main_pipeline.py --vcf /path/to/contacts.vcf

# O sin clasificación (más rápido para pruebas)
python main_pipeline.py --vcf /path/to/contacts.vcf --skip-classification
```

**Esto hace:**
1. ✅ Parsea todos los contactos
2. ✅ Deduplica con Splink (probabilistic matching)
3. ✅ Clasifica en Tier 1/2/3 con GPT-4o-mini
4. ✅ Detecta temas y zonas
5. ✅ Sube a Supabase
6. ✅ Construye grafo en Kùzu

**Salida esperada:**
```
VCF PROCESSING PIPELINE
================================
✓ Parsed 2,450 contacts
✓ After deduplication: 1,890 unique contacts
✓ Uploaded to Supabase: 1,890 contacts
✓ Kùzu graph built

Distribution by Tier:
  • Tier 1: 87 contacts
  • Tier 2: 245 contacts
  • Tier 3: 1,558 contacts
```

### Paso 3: Procesar LinkedIn

**Exportar desde LinkedIn:**
1. LinkedIn → Configuración y Privacidad
2. Privacidad de datos → **Obtener una copia de tus datos**
3. Selecciona **solo "Conexiones"**
4. Descarga (llega por email en ~10 min)
5. Extrae `Connections.csv`

**Procesar:**
```bash
python main_pipeline.py --linkedin /path/to/Connections.csv
```

---

## 📷 Semana 2: Instagram (Día 3-7)

### Paso 1: Solicitar Export de Instagram

**⚠️ IMPORTANTE: Esto tarda 2-48 horas**

1. Instagram → Configuración → Tu actividad
2. **Descargar tu información**
3. Selecciona:
   - Formato: **JSON** (no HTML)
   - Rango: **Todo el tiempo**
4. Solicita descarga
5. Espera email de Instagram

### Paso 2: Procesar Export

Una vez descargues el ZIP:

```bash
unzip instagram-export.zip -d instagram_data/

python main_pipeline.py --instagram instagram_data/
```

**Qué incluye:**
- Following (personas que sigues)
- Followers (quienes te siguen)
- Mutual follows (marcados como Tier 2)

---

## 🎤 Semana 3: WhatsApp en Vivo (Días 8-14)

### Configuración One-Time

```bash
# Asegúrate que n8n esté corriendo
n8n start &

# Verifica webhook
curl http://localhost:5678/webhook/whatsapp-voice
```

### Flujo de Trabajo

**Cada vez que grabes una reunión:**

1. 📱 Graba nota de voz en WhatsApp
2. 🤖 n8n la recibe automáticamente
3. 🎙️ Whisper transcribe
4. 🧠 GPT-4o-mini extrae:
   - Resumen
   - Personas mencionadas
   - Temas discutidos
   - Próximos pasos
   - Sentimiento
5. 💾 Se guarda en Supabase → `interactions`
6. 🕸️ Actualiza grafo Kùzu

### Procesar Audio Manualmente (Sin WhatsApp)

```bash
cd backend/whatsapp_integration

python whatsapp_processor.py /path/to/audio.ogg +521234567890
```

---

## 🔍 Análisis de Red

### Análisis Completo

```bash
python main_pipeline.py --analyze
```

**Output:**
```
NETWORK ANALYSIS
================================
Total contacts: 3,840

Distribution by Tier:
  • Tier 1: 142 contacts (decisores)
  • Tier 2: 687 contacts (partners)
  • Tier 3: 3,011 contacts (red general)

Top Zones:
  • CDMX: 1,245
  • Monterrey: 892
  • Guadalajara: 387
  • Querétaro: 264

Detecting communities...
✓ Found 8 communities
  Community 0: 487 members (Inmobiliario CDMX)
  Community 1: 324 members (ESG Monterrey)
  Community 2: 189 members (Construcción Nacional)
  ...

Most connected contacts:
  Juan Pérez | Agartha | Tier 1 | 87 connections
  María López | CANADEVI | Tier 1 | 65 connections
  ...

Inactive contacts (6+ months): 1,234
```

### Consultas Específicas

**Python REPL:**

```python
from database.supabase_client import SupabaseContactManager
from graph_engine.kuzu_graph import KuzuGraphEngine

sb = SupabaseContactManager()
graph = KuzuGraphEngine()

# 1. Buscar contactos
results = sb.search_contacts(
    query="sustentabilidad inmobiliaria",
    tier="Tier 1",
    zona="Monterrey"
)
print(results)

# 2. Contactos inactivos Tier 1 en Monterrey
df = graph.query_contacts_by_criteria(
    tier="Tier 1",
    zona="Monterrey",
    min_interactions=0
)
inactive = df[df['total_interactions'] == 0]
print(f"Tier 1 sin contacto: {len(inactive)}")

# 3. Red de un contacto específico
network = graph.get_contact_network(contact_id="uuid-aqui", depth=2)
print(f"Red de {network['center']}: {network['network_size']} conexiones")

# 4. Conexiones en común entre dos personas
common = graph.find_common_connections(
    "contact-id-1",
    "contact-id-2"
)
print(f"Conexiones mutuas: {len(common)}")
```

---

## 📊 Queries de Negocio

### Query 1: "¿Quién en Monterrey trabaja ESG y no he visto en 6 meses?"

```python
sb = SupabaseContactManager()

inactive = sb.get_inactive_contacts(days=180)

mty_esg = inactive[
    (inactive['zona'] == 'Monterrey') &
    (inactive['temas'].str.contains('ESG', na=False))
]

print(mty_esg[['full_name', 'company', 'title', 'days_inactive']])
```

### Query 2: "Dame Tier 1 de inmobiliario en Bajío"

```python
df = graph.query_contacts_by_criteria(
    tier="Tier 1",
    zona="Bajío"
)

bajio_inmo = df[df['title'].str.contains('inmobil|desarrollo|construc', case=False, na=False)]
print(bajio_inmo)
```

### Query 3: "¿Qué comunidades tengo que no sabía?"

```python
communities = graph.detect_communities()

# Ver miembros de cada comunidad
for comm_id in set(communities.values()):
    members = [node for node, c in communities.items() if c == comm_id]
    
    # Obtener info de miembros
    member_data = []
    for m in members[:10]:
        contact = sb.client.table('contacts').select('*').eq('id', m).execute()
        if contact.data:
            member_data.append(contact.data[0])
    
    print(f"\n Community {comm_id}: {len(members)} miembros")
    for m in member_data:
        print(f"  - {m['full_name']} | {m['company']} | {m['tier']}")
```

---

## 🔄 Mantenimiento

### Actualizar Base de Datos

```bash
# Agregar nuevos contactos
python main_pipeline.py --vcf new_contacts.vcf

# Re-clasificar todos
python scripts/reclassify_all.py

# Reconstruir grafo
python scripts/rebuild_graph.py
```

### Backup

```bash
# Backup Supabase
# En Supabase Dashboard → Database → Backups

# Backup Kùzu
tar -czf kuzu_backup_$(date +%Y%m%d).tar.gz data/graph/kuzu_db
```

---

## 🎯 Casos de Uso

### Caso 1: Pre-Reunión
Antes de reunión con empresa X:

```python
# Buscar contactos en empresa X
contacts = sb.search_contacts(query="Empresa X")

# Ver red de decisor
ceo = contacts[contacts['title'].str.contains('CEO', na=False)].iloc[0]
network = graph.get_contact_network(ceo['id'], depth=2)

# Revisar interacciones pasadas
interactions = sb.get_contact_interactions(ceo['id'])
```

### Caso 2: Entrada a Nueva Ciudad

```python
# Querétaro: contactos Tier 1 y 2
qro = graph.query_contacts_by_criteria(zona="Querétaro")
qro_top = qro[qro['tier'].isin(['Tier 1', 'Tier 2'])]

# Ordenar por centralidad (más conexiones)
qro_top_sorted = qro_top.sort_values('connection_count', ascending=False)
```

### Caso 3: Reactivación de Inactivos

```bash
# Generar lista de reactivación
python scripts/generate_reactivation_list.py \
  --tier "Tier 1" \
  --days 180 \
  --output reactivation_q1_2024.csv
```

---

## 🚀 Queries Avanzadas con SQL

Puedes ejecutar SQL directo en Supabase:

```sql
-- Top 20 empresas en tu red
SELECT company, tier, COUNT(*) as count
FROM contacts
WHERE company IS NOT NULL
GROUP BY company, tier
ORDER BY count DESC
LIMIT 20;

-- Mapa de calor: Tier x Zona
SELECT tier, zona, COUNT(*) as count
FROM contacts
GROUP BY tier, zona
ORDER BY tier, count DESC;

-- Contactos con más interacciones
SELECT 
  c.full_name,
  c.company,
  c.tier,
  COUNT(i.id) as interaction_count,
  MAX(i.interaction_date) as last_interaction
FROM contacts c
LEFT JOIN interactions i ON c.id = i.contact_id
GROUP BY c.id, c.full_name, c.company, c.tier
ORDER BY interaction_count DESC
LIMIT 50;
```

---

## 💡 Tips

### Optimización de Clasificación GPT

Si tienes muchos contactos (>5k), clasifica por lotes:

```python
classifier = GPTClassifier()

# Procesar solo Tier 1 probables (con title o company)
important = df[df['title'].notna() | df['company'].notna()]
rest = df[~df.index.isin(important.index)]

# Clasificar importantes
important_classified = classifier.classify_batch(important.to_dict('records'))

# Asignar Tier 3 al resto
rest['tier'] = 'Tier 3'
```

### Rate Limits de OpenAI

- GPT-4o-mini: ~60 req/min
- Whisper: ~50 req/min

Si tienes muchos audios, procesa en lotes con sleep:

```python
import time

for audio in audio_files:
    processor.process_voice_note(audio)
    time.sleep(1)  # 1 segundo entre llamadas
```

---

## 🐛 Debugging

### Ver logs de n8n

```bash
# Logs en tiempo real
tail -f ~/.n8n/logs/n8n.log
```

### Probar webhook manualmente

```bash
curl -X POST http://localhost:5678/webhook/whatsapp-voice \
  -H "Content-Type: application/json" \
  -d '{
    "body": {
      "type": "voice",
      "from": "+521234567890",
      "media_url": "https://example.com/audio.ogg"
    }
  }'
```

---

## 📈 Métricas a Trackear

1. **Total de contactos** (objetivo: >15k en 3 meses)
2. **Ratio Tier 1:Tier 2:Tier 3** (objetivo: 5:15:80)
3. **Cobertura geográfica** (objetivo: 5+ ciudades con >100 contactos)
4. **Interacciones por mes** (objetivo: >50 interacciones/mes)
5. **Contactos inactivos Tier 1** (objetivo: <20%)

---

## Siguiente Paso

Ve a [ARQUITECTURA.md](./ARQUITECTURA.md) para entender cómo funciona el sistema internamente.
