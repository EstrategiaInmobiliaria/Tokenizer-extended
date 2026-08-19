-- Schema para Supabase: Sistema de gestión de red de contactos
-- Ejecutar en el SQL Editor de Supabase

-- =====================================================
-- TABLA PRINCIPAL: CONTACTOS
-- =====================================================

CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Información básica
    full_name TEXT,
    first_name TEXT,
    last_name TEXT,
    company TEXT,
    title TEXT,
    
    -- Contacto
    email_primary TEXT,
    phone_primary TEXT,
    emails TEXT[], -- Array de emails adicionales
    phones TEXT[], -- Array de teléfonos adicionales
    addresses TEXT[], -- Array de direcciones
    
    -- Clasificación (desde GPT)
    tier TEXT CHECK (tier IN ('Tier 1', 'Tier 2', 'Tier 3')),
    temas TEXT[], -- Array de temas de interés
    zona TEXT,
    
    -- Metadata
    notes TEXT,
    source TEXT, -- 'vcf', 'linkedin', 'instagram', 'whatsapp'
    cluster_id INTEGER, -- ID de cluster de Splink para duplicados
    classification_reasoning TEXT,
    
    -- Engagement tracking
    last_contact_date TIMESTAMP,
    contact_frequency_days INTEGER, -- Cada cuántos días hay contacto promedio
    total_interactions INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Índices para búsquedas
    CONSTRAINT email_or_phone_required CHECK (
        email_primary IS NOT NULL OR phone_primary IS NOT NULL
    )
);

-- Índices para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email_primary);
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone_primary);
CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company);
CREATE INDEX IF NOT EXISTS idx_contacts_tier ON contacts(tier);
CREATE INDEX IF NOT EXISTS idx_contacts_zona ON contacts(zona);
CREATE INDEX IF NOT EXISTS idx_contacts_cluster ON contacts(cluster_id);

-- Índice para búsqueda full-text
CREATE INDEX IF NOT EXISTS idx_contacts_fulltext ON contacts 
USING gin(to_tsvector('spanish', coalesce(full_name, '') || ' ' || 
                                  coalesce(company, '') || ' ' || 
                                  coalesce(title, '') || ' ' || 
                                  coalesce(notes, '')));

-- =====================================================
-- TABLA: INTERACCIONES (WhatsApp, reuniones, etc.)
-- =====================================================

CREATE TABLE IF NOT EXISTS interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    
    -- Tipo de interacción
    interaction_type TEXT CHECK (interaction_type IN (
        'whatsapp_voice', 'whatsapp_text', 'meeting', 'call', 'email', 'other'
    )),
    
    -- Contenido
    content TEXT, -- Transcripción o notas
    summary TEXT, -- Resumen generado por GPT
    sentiment TEXT, -- 'positive', 'neutral', 'negative'
    
    -- Metadata
    duration_seconds INTEGER, -- Para llamadas/reuniones
    location TEXT, -- Para reuniones presenciales
    
    -- Timestamps
    interaction_date TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Almacenamiento
    audio_url TEXT, -- URL del archivo de audio en storage
    transcript_embedding vector(1536) -- Embedding de OpenAI para búsqueda semántica
);

CREATE INDEX IF NOT EXISTS idx_interactions_contact ON interactions(contact_id);
CREATE INDEX IF NOT EXISTS idx_interactions_date ON interactions(interaction_date);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON interactions(interaction_type);

-- Índice para búsqueda vectorial (pgvector)
CREATE INDEX IF NOT EXISTS idx_interactions_embedding ON interactions 
USING ivfflat (transcript_embedding vector_cosine_ops)
WITH (lists = 100);

-- =====================================================
-- TABLA: RELACIONES (Grafo de conexiones)
-- =====================================================

CREATE TABLE IF NOT EXISTS relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Nodos
    contact_from_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    contact_to_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    
    -- Tipo de relación
    relationship_type TEXT CHECK (relationship_type IN (
        'colleague', 'client', 'supplier', 'partner', 'friend', 'family', 'other'
    )),
    
    -- Fuerza de la relación (0-1)
    strength FLOAT DEFAULT 0.5 CHECK (strength >= 0 AND strength <= 1),
    
    -- Contexto
    context TEXT, -- Cómo se conocen
    source TEXT, -- De dónde se infirió esta relación
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT no_self_relationship CHECK (contact_from_id != contact_to_id),
    CONSTRAINT unique_relationship UNIQUE (contact_from_id, contact_to_id)
);

CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(contact_from_id);
CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(contact_to_id);
CREATE INDEX IF NOT EXISTS idx_relationships_strength ON relationships(strength);

-- =====================================================
-- TABLA: COMUNIDADES (Clusters detectados)
-- =====================================================

CREATE TABLE IF NOT EXISTS communities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Metadata
    name TEXT,
    description TEXT,
    
    -- Análisis
    size INTEGER, -- Número de miembros
    avg_tier FLOAT, -- Tier promedio de miembros
    dominant_temas TEXT[], -- Temas más comunes
    dominant_zona TEXT, -- Zona geográfica predominante
    
    -- Algoritmo de detección
    detection_algorithm TEXT, -- 'louvain', 'label_propagation', etc.
    modularity FLOAT, -- Calidad del clustering
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- TABLA: MEMBRESÍA EN COMUNIDADES
-- =====================================================

CREATE TABLE IF NOT EXISTS community_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    
    -- Centralidad del miembro en la comunidad
    centrality_score FLOAT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_community_member UNIQUE (community_id, contact_id)
);

CREATE INDEX IF NOT EXISTS idx_community_members_community ON community_members(community_id);
CREATE INDEX IF NOT EXISTS idx_community_members_contact ON community_members(contact_id);

-- =====================================================
-- FUNCIONES Y TRIGGERS
-- =====================================================

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_relationships_updated_at BEFORE UPDATE ON relationships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_communities_updated_at BEFORE UPDATE ON communities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Función para actualizar total_interactions
CREATE OR REPLACE FUNCTION increment_contact_interactions()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE contacts
    SET 
        total_interactions = total_interactions + 1,
        last_contact_date = NEW.interaction_date
    WHERE id = NEW.contact_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER increment_interactions AFTER INSERT ON interactions
    FOR EACH ROW EXECUTE FUNCTION increment_contact_interactions();

-- =====================================================
-- VISTAS ÚTILES
-- =====================================================

-- Vista: Contactos con última interacción
CREATE OR REPLACE VIEW contacts_with_last_interaction AS
SELECT 
    c.*,
    i.interaction_date as last_interaction_date,
    i.interaction_type as last_interaction_type,
    i.summary as last_interaction_summary,
    EXTRACT(DAY FROM NOW() - i.interaction_date) as days_since_last_contact
FROM contacts c
LEFT JOIN LATERAL (
    SELECT interaction_date, interaction_type, summary
    FROM interactions
    WHERE contact_id = c.id
    ORDER BY interaction_date DESC
    LIMIT 1
) i ON true;

-- Vista: Top contactos por tier y zona
CREATE OR REPLACE VIEW top_contacts_by_tier_zona AS
SELECT 
    tier,
    zona,
    COUNT(*) as count,
    ARRAY_AGG(full_name ORDER BY last_contact_date DESC NULLS LAST) as recent_contacts
FROM contacts
GROUP BY tier, zona
ORDER BY tier, count DESC;

-- Vista: Contactos inactivos (sin contacto en 6+ meses)
CREATE OR REPLACE VIEW inactive_contacts AS
SELECT 
    c.*,
    EXTRACT(DAY FROM NOW() - c.last_contact_date) as days_inactive
FROM contacts c
WHERE 
    c.last_contact_date IS NULL 
    OR c.last_contact_date < NOW() - INTERVAL '6 months'
ORDER BY c.tier, c.last_contact_date DESC NULLS LAST;

-- =====================================================
-- FUNCIONES DE BÚSQUEDA
-- =====================================================

-- Búsqueda semántica por embeddings
CREATE OR REPLACE FUNCTION search_interactions_by_embedding(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    interaction_id UUID,
    contact_id UUID,
    contact_name TEXT,
    content TEXT,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        i.id,
        i.contact_id,
        c.full_name,
        i.content,
        1 - (i.transcript_embedding <=> query_embedding) as similarity
    FROM interactions i
    JOIN contacts c ON i.contact_id = c.id
    WHERE 1 - (i.transcript_embedding <=> query_embedding) > match_threshold
    ORDER BY i.transcript_embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Búsqueda full-text
CREATE OR REPLACE FUNCTION search_contacts_fulltext(search_query TEXT)
RETURNS TABLE (
    id UUID,
    full_name TEXT,
    company TEXT,
    title TEXT,
    tier TEXT,
    zona TEXT,
    rank float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.full_name,
        c.company,
        c.title,
        c.tier,
        c.zona,
        ts_rank(
            to_tsvector('spanish', 
                coalesce(c.full_name, '') || ' ' || 
                coalesce(c.company, '') || ' ' || 
                coalesce(c.title, '') || ' ' || 
                coalesce(c.notes, '')
            ),
            plainto_tsquery('spanish', search_query)
        ) as rank
    FROM contacts c
    WHERE to_tsvector('spanish', 
        coalesce(c.full_name, '') || ' ' || 
        coalesce(c.company, '') || ' ' || 
        coalesce(c.title, '') || ' ' || 
        coalesce(c.notes, '')
    ) @@ plainto_tsquery('spanish', search_query)
    ORDER BY rank DESC;
END;
$$;

-- =====================================================
-- POLÍTICAS RLS (Row Level Security) - OPCIONAL
-- =====================================================

-- Si quieres habilitar RLS por usuario:
-- ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE interactions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE relationships ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY "Users can view their own contacts" ON contacts
--     FOR SELECT USING (auth.uid() = user_id);

-- =====================================================
-- EXTENSIONES REQUERIDAS
-- =====================================================

-- Habilitar pgvector (para embeddings)
CREATE EXTENSION IF NOT EXISTS vector;

-- Habilitar uuid (para IDs)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- COMENTARIOS
-- =====================================================

COMMENT ON TABLE contacts IS 'Tabla principal de contactos con clasificación y metadata';
COMMENT ON TABLE interactions IS 'Registro de interacciones (WhatsApp, reuniones, etc.)';
COMMENT ON TABLE relationships IS 'Grafo de relaciones entre contactos';
COMMENT ON TABLE communities IS 'Comunidades detectadas automáticamente';
COMMENT ON COLUMN interactions.transcript_embedding IS 'Embedding de OpenAI (1536 dims) para búsqueda semántica';
COMMENT ON FUNCTION search_interactions_by_embedding IS 'Búsqueda semántica de interacciones usando embeddings';
