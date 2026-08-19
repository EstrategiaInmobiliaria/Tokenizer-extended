# Sistema de Gestión de Red de Contactos

**Sistema completo de CRM personal con clasificación inteligente, análisis de grafo y automatización con WhatsApp**

---

## 🎯 ¿Qué es esto?

Un sistema 100% legal para gestionar tu red profesional usando:

✅ **VCF** (exportación oficial de contactos)  
✅ **LinkedIn CSV** (export oficial de conexiones)  
✅ **Instagram JSON** (export oficial desde la app)  
✅ **WhatsApp** (integración en vivo con n8n)

**No hay scraping. Todo es legal y basado en exports oficiales.**

---

## 🚀 Quick Start (30 segundos)

```bash
# 1. Clonar e instalar
cd /workspace/backend
pip install -r requirements.txt

# 2. Configurar .env
cp .env.example .env
# Edita .env con tus keys de Supabase y OpenAI

# 3. Ejecutar schema en Supabase
# Copia backend/database/supabase_schema.sql
# Pégalo en Supabase SQL Editor y ejecuta

# 4. Procesar tus contactos
python main_pipeline.py --vcf /path/to/contacts.vcf

# 5. Listo! Ya tienes tu red clasificada
```

---

## 📊 ¿Qué hace?

### Fase 1: Construcción de Base (Días 1-7)

1. **VCF Processing**
   - Parsea contactos de iPhone/Android
   - Deduplica con Splink (probabilistic matching)
   - Clasifica en Tier 1/2/3 con GPT-4o-mini
   - Detecta temas (Inmobiliario, ESG, etc.) y zonas (CDMX, MTY, etc.)

2. **LinkedIn Integration**
   - Import de `Connections.csv` oficial
   - Análisis de empresas top
   - Merge inteligente con VCF

3. **Instagram Integration**
   - Procesa export JSON oficial (following/followers)
   - Detecta mutual follows
   - Clasifica por engagement

### Fase 2: Automatización WhatsApp (Días 8+)

- **n8n workflow** escucha notas de voz
- **Whisper** transcribe automáticamente
- **GPT-4o-mini** extrae:
  - Resumen ejecutivo
  - Contactos mencionados
  - Temas discutidos
  - Próximos pasos
  - Sentimiento
- Se guarda en **Supabase** + actualiza grafo **Kùzu**

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                   FUENTES DE DATOS                      │
├──────────┬──────────┬──────────┬─────────────────────────┤
│   VCF    │ LinkedIn │Instagram │      WhatsApp          │
│(iPhone/  │   CSV    │   JSON   │   (n8n webhook)        │
│ Android) │          │          │                        │
└────┬─────┴────┬─────┴────┬─────┴────┬──────────────────┘
     │          │          │          │
     ▼          ▼          ▼          ▼
┌────────────────────────────────────────────────┐
│         PROCESAMIENTO & CLASIFICACIÓN          │
├────────────────────────────────────────────────┤
│  • Splink (deduplicación)                      │
│  • GPT-4o-mini (Tier/Tema/Zona)                │
│  • Whisper (transcripción)                     │
│  • OpenAI Embeddings (búsqueda semántica)      │
└────┬───────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│              ALMACENAMIENTO                    │
├────────────────────────────────────────────────┤
│  • Supabase (PostgreSQL + pgvector)            │
│    - Tabla contacts (con clasificación)        │
│    - Tabla interactions (con embeddings)       │
│    - Tabla relationships (grafo)               │
│                                                │
│  • Kùzu (Graph Database)                       │
│    - Análisis de red                           │
│    - Detección de comunidades (Louvain)        │
│    - Consultas de grafo                        │
└────┬───────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────┐
│           CONSULTAS & ANÁLISIS                 │
├────────────────────────────────────────────────┤
│  • "¿Quién en MTY trabaja ESG?"                │
│  • "¿Contactos Tier 1 sin contacto 6 meses?"  │
│  • "¿Qué comunidades tengo?"                   │
│  • Búsqueda semántica de conversaciones        │
└────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
/workspace/
├── backend/
│   ├── vcf_processor/
│   │   ├── vcf_parser.py          # Parser VCF
│   │   ├── deduplicator.py        # Splink deduplication
│   │   ├── linkedin_processor.py   # LinkedIn CSV
│   │   └── instagram_processor.py  # Instagram JSON
│   │
│   ├── classification/
│   │   └── gpt_classifier.py      # GPT-4o-mini Tier/Tema/Zona
│   │
│   ├── database/
│   │   ├── supabase_schema.sql    # Schema completo
│   │   └── supabase_client.py     # Cliente Python
│   │
│   ├── graph_engine/
│   │   └── kuzu_graph.py          # Motor de grafo Kùzu
│   │
│   ├── whatsapp_integration/
│   │   └── whatsapp_processor.py  # Whisper + GPT analysis
│   │
│   ├── main_pipeline.py           # 🎯 SCRIPT PRINCIPAL
│   ├── requirements.txt
│   └── .env.example
│
├── n8n_workflows/
│   └── whatsapp_voice_note_workflow.json
│
├── data/
│   ├── raw/           # Datos crudos
│   ├── processed/     # Datos procesados
│   └── graph/         # Kùzu DB
│
└── docs/
    ├── INSTALACION.md  # Setup completo
    ├── USO.md          # Guía de uso
    └── ARQUITECTURA.md # Detalles técnicos
```

---

## 🔑 Tecnologías Clave

| Componente | Tecnología | ¿Por qué? |
|------------|------------|-----------|
| **Deduplicación** | Splink | Probabilistic matching (mejor que fuzzy matching simple) |
| **Clasificación** | GPT-4o-mini | Balance costo/calidad ($0.15/1M tokens) |
| **Base de datos** | Supabase | PostgreSQL + pgvector + API REST gratis |
| **Grafo** | Kùzu | Graph DB embebido (como DuckDB para grafos) |
| **Transcripción** | Whisper | Mejor STT del mercado |
| **Automatización** | n8n | Open source, self-hosted |
| **Embeddings** | OpenAI | Búsqueda semántica de conversaciones |

---

## 💡 Casos de Uso Reales

### 1. Pre-Reunión Prep
```python
# "Mañana tengo reunión con Empresa X, ¿qué sé de ellos?"
contacts = sb.search_contacts(query="Empresa X")
interactions = sb.get_contact_interactions(contacts[0]['id'])
network = graph.get_contact_network(contacts[0]['id'])
```

### 2. Entrada a Nueva Ciudad
```python
# "Voy a Querétaro, ¿a quién debo ver?"
qro_contacts = graph.query_contacts_by_criteria(
    zona="Querétaro",
    tier="Tier 1"
)
```

### 3. Reactivación de Inactivos
```python
# "¿Tier 1 que no veo hace 6+ meses?"
inactive = sb.get_inactive_contacts(days=180)
tier1_inactive = inactive[inactive['tier'] == 'Tier 1']
```

### 4. Descubrimiento de Comunidades
```python
# "¿Qué clusters hay en mi red que no sabía?"
communities = graph.detect_communities()
# Output: "Cluster 1: 34 personas de ESG Monterrey"
#         "Cluster 2: 87 personas de PropTech CDMX"
```

---

## 📈 Resultados Esperados

### Semana 1: Base de Datos
- ✅ 15k-25k contactos únicos (VCF + LinkedIn + Instagram)
- ✅ Clasificados en Tier 1/2/3
- ✅ Temas y zonas asignados

### Semana 2-3: Automatización
- ✅ WhatsApp conectado a n8n
- ✅ Notas de voz se transcriben automáticamente
- ✅ Grafo se actualiza en tiempo real

### Mes 1: Insights
- ✅ 3-5 comunidades detectadas
- ✅ Top 100 contactos más centrales identificados
- ✅ 20-30% de Tier 1 reactivados

---

## 🎓 Clasificación: Tier, Tema, Zona

### Tier (Prioridad)
- **Tier 1**: Decisores C-Level (CEOs, CFOs de inmobiliario/ESG)
- **Tier 2**: Partners estratégicos (consultores, gerentes, socios)
- **Tier 3**: Red general (networking, proveedores indirectos)

### Temas
- Inmobiliario
- ESG/Sustentabilidad
- Inversión/Fondos
- Construcción
- PropTech
- Consultoría Estratégica
- Legal/Regulatorio
- Arquitectura/Diseño
- Gobierno/Sector Público
- Academia

### Zonas
- CDMX
- Monterrey
- Guadalajara
- Querétaro
- Bajío (León, Aguascalientes)
- Península de Yucatán
- Internacional

---

## ⚖️ Legal & Privacidad

✅ **100% Legal**
- VCF: Tus propios contactos
- LinkedIn: Export oficial de LinkedIn
- Instagram: Export oficial de Instagram
- WhatsApp: Con tu propio número y consentimiento

❌ **NO hacemos:**
- Scraping de páginas web
- Uso de APIs no autorizadas
- Acceso a datos de terceros sin consentimiento

🔒 **Privacidad:**
- Datos almacenados en tu Supabase (tú controlas acceso)
- Kùzu embebido localmente
- No compartimos datos con terceros

---

## 🛠️ Instalación Rápida

Ver [docs/INSTALACION.md](docs/INSTALACION.md) para setup completo.

**TL;DR:**
```bash
# 1. Install
pip install -r backend/requirements.txt

# 2. Setup Supabase
# Ejecuta backend/database/supabase_schema.sql en Supabase

# 3. Configure
cp backend/.env.example backend/.env
# Edita con tus keys

# 4. Run
cd backend
python main_pipeline.py --vcf /path/to/contacts.vcf
```

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [INSTALACION.md](docs/INSTALACION.md) | Setup paso a paso (Supabase, n8n, etc.) |
| [USO.md](docs/USO.md) | Guía completa de uso y queries |
| [ARQUITECTURA.md](docs/ARQUITECTURA.md) | Detalles técnicos del sistema |

---

## 🐛 Troubleshooting

### "No module named 'splink'"
```bash
pip install splink
```

### "SUPABASE_URL not found"
```bash
cd backend
cp .env.example .env
# Edita .env con tus credenciales
```

### "pgvector extension not found"
En Supabase SQL Editor:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Ver [docs/INSTALACION.md](docs/INSTALACION.md#troubleshooting) para más.

---

## 🚦 Roadmap

### ✅ Fase 0: Base (Completo)
- VCF processing
- LinkedIn import
- Instagram import
- Deduplicación con Splink
- Clasificación GPT-4o-mini
- Supabase + Kùzu

### ✅ Fase 1: Automatización (Completo)
- n8n WhatsApp integration
- Whisper transcription
- Embedding search

### 🔄 Fase 2: Analytics (En progreso)
- Dashboard con Streamlit
- Visualización de grafo interactivo
- Reportes automáticos

### 📋 Fase 3: Features Avanzados
- Recomendaciones de conexiones
- Detección de oportunidades
- Calendar integration
- Email tracking

---

## 🤝 Contribuir

Este es un proyecto de código abierto. PRs bienvenidos.

**Áreas donde puedes ayudar:**
- Dashboard/UI con Streamlit o Next.js
- Más integraciones (Gmail, Outlook, etc.)
- Mejoras en clasificación
- Optimización de performance

---

## 📝 Licencia

MIT License - Ver [LICENSE](LICENSE)

---

## 👤 Autor

Desarrollado como solución práctica para gestión de red profesional en el contexto de estrategia inmobiliaria y ESG.

**Stack:** Python, Supabase, Kùzu, OpenAI, n8n

---

## 🙏 Agradecimientos

- [Splink](https://github.com/moj-analytical-services/splink) - Deduplication framework
- [Kùzu](https://kuzudb.com/) - Embedded graph database
- [Supabase](https://supabase.com/) - Backend as a service
- [n8n](https://n8n.io/) - Workflow automation
- [OpenAI](https://openai.com/) - GPT & Whisper APIs

---

## 📞 Soporte

Para preguntas o issues, abre un issue en GitHub o consulta la [documentación](docs/).

**Happy networking! 🚀**
