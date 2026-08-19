# Instalación del Sistema de Gestión de Red de Contactos

## Requisitos Previos

### Software Necesario

- **Python 3.10+**
- **PostgreSQL 14+** (con extensión pgvector)
- **Supabase** (cuenta activa)
- **n8n** (para integración WhatsApp)
- **OpenAI API Key** (para GPT-4o-mini y Whisper)

### Hardware Recomendado

- 4GB RAM mínimo
- 10GB espacio en disco
- Conexión a internet estable

---

## Paso 1: Configurar Python Environment

```bash
cd /workspace/backend

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Verificar Instalación

```bash
python -c "import splink; import kuzu; import openai; print('✓ Todas las librerías instaladas')"
```

---

## Paso 2: Configurar Supabase

### 2.1 Crear Proyecto en Supabase

1. Ve a [supabase.com](https://supabase.com)
2. Crea un nuevo proyecto
3. Anota tu `URL` y `anon/public key`

### 2.2 Ejecutar Schema SQL

1. En Supabase Dashboard → SQL Editor
2. Abre el archivo `backend/database/supabase_schema.sql`
3. Copia todo el contenido
4. Ejecuta en Supabase SQL Editor

### 2.3 Habilitar pgvector

```sql
-- En Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2.4 Configurar Variables de Entorno

Copia `.env.example` a `.env`:

```bash
cp backend/.env.example backend/.env
```

Edita `backend/.env`:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui

OPENAI_API_KEY=sk-tu-openai-key-aqui

KUZU_DB_PATH=../data/graph/kuzu_db

N8N_WEBHOOK_URL=http://localhost:5678/webhook/whatsapp

GPT_MODEL=gpt-4o-mini
GPT_MAX_TOKENS=150
GPT_TEMPERATURE=0.3
```

---

## Paso 3: Configurar Kùzu (Base de Datos de Grafo)

Kùzu se crea automáticamente al ejecutar el pipeline. Solo necesitas crear el directorio:

```bash
mkdir -p data/graph
```

---

## Paso 4: Configurar n8n (Integración WhatsApp)

### 4.1 Instalar n8n

```bash
npm install -g n8n
```

### 4.2 Iniciar n8n

```bash
n8n start
```

Abre: http://localhost:5678

### 4.3 Importar Workflow

1. En n8n, ve a **Workflows** → **Import from File**
2. Selecciona `n8n_workflows/whatsapp_voice_note_workflow.json`
3. Configura credenciales de Supabase en el workflow

### 4.4 Configurar WhatsApp Business API

**Opción A: Usar WhatsApp Business API oficial**
- Requiere cuenta de Facebook Business
- Configurar webhook apuntando a n8n

**Opción B: Usar Evolution API (más fácil)**
- Instalar Evolution API: https://github.com/EvolutionAPI/evolution-api
- Conectar QR de WhatsApp
- Configurar webhook hacia n8n

---

## Paso 5: Verificar Instalación

Ejecuta el script de prueba:

```bash
cd backend
python -c "
from database.supabase_client import SupabaseContactManager
from graph_engine.kuzu_graph import KuzuGraphEngine

print('Probando Supabase...')
sb = SupabaseContactManager()
print('✓ Supabase OK')

print('Probando Kùzu...')
graph = KuzuGraphEngine()
print('✓ Kùzu OK')

print('\\n✓ INSTALACIÓN COMPLETA')
"
```

---

## Troubleshooting

### Error: "SUPABASE_URL not found"

Verifica que `.env` esté en `backend/.env` y que las variables estén correctamente definidas.

```bash
cd backend
cat .env
```

### Error: "pgvector extension not found"

En Supabase SQL Editor:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Error: Splink falla en deduplicación

Splink requiere DuckDB. Reinstala:

```bash
pip install --upgrade splink duckdb
```

### Error: n8n no puede conectar con Supabase

1. Verifica que Supabase API key tenga permisos correctos
2. Revisa que la URL no tenga espacios o caracteres extra
3. Prueba la conexión manualmente:

```bash
curl -X GET "https://tu-proyecto.supabase.co/rest/v1/contacts?select=count" \
  -H "apikey: tu-anon-key" \
  -H "Authorization: Bearer tu-anon-key"
```

---

## Siguiente Paso

Ve a [USO.md](./USO.md) para aprender a usar el sistema.
