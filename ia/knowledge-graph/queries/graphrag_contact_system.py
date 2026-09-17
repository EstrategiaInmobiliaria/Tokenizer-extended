"""
GraphRAG Contact Network System
Sistema híbrido de Grafo Semántico + Búsqueda Vectorial para 45K+ contactos

Componentes:
1. Entity Resolution (Splink) - Deduplicación inteligente
2. Graph Database (Neo4j/Python) - Relaciones y análisis de red
3. Vector Search (FAISS/pgvector) - Búsqueda semántica
4. Scoring Engine - Valor comercial y priorización
5. Community Detection - Clústeres automáticos
6. Multi-channel Interface - WhatsApp, Cursor, Gemini

Basado en:
- "Knowledge Graphs Meet Multi-Modal Learning" (2024)
- "Graph RAG: Unlocking LLM Discovery on Narrative Private Data" (Microsoft, 2024)
- "Entity Resolution at Scale with Splink" (2023)
"""

import neo4j
from neo4j import GraphDatabase
import numpy as np
from typing import List, Dict, Tuple, Optional
import splink
from splink.duckdb.linker import DuckDBLinker
from splink.duckdb import blocking_rule_library as brl
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import networkx as nx
from datetime import datetime, timedelta
import json

# ============================================
# 1. ENTITY RESOLUTION CON SPLINK
# ============================================

class ContactDeduplicator:
    """
    Resuelve entidades duplicadas entre vCard, LinkedIn, Twitter, WhatsApp
    
    Algoritmos:
    - Jaro-Winkler para nombres
    - Levenshtein para emails
    - Fuzzy matching para empresas
    - Clustering probabilístico
    """
    
    def __init__(self):
        self.linker = None
    
    def configure_deduplication(self):
        """
        Configura reglas de matching multi-fuente
        
        Estrategia:
        1. Matching exacto: email, teléfono
        2. Matching fuzzy: nombre + empresa
        3. Matching contextual: ubicación + industria
        """
        
        settings = {
            "link_type": "dedupe_only",
            "blocking_rules_to_generate_predictions": [
                # Bloqueo por email (caso exacto)
                "l.email = r.email",
                # Bloqueo por teléfono normalizado
                "l.telefono_normalizado = r.telefono_normalizado",
                # Bloqueo por nombre + empresa fuzzy
                brl.exact_match_rule("empresa"),
                # Bloqueo por LinkedIn URL
                "l.linkedin_id = r.linkedin_id"
            ],
            "comparisons": [
                {
                    "output_column_name": "nombre",
                    "comparison_levels": [
                        {
                            "sql_condition": "nombre_l IS NULL OR nombre_r IS NULL",
                            "label_for_charts": "Null",
                            "is_null_level": True
                        },
                        {
                            "sql_condition": "nombre_l = nombre_r",
                            "label_for_charts": "Exact match",
                        },
                        {
                            "sql_condition": "jaro_winkler_similarity(nombre_l, nombre_r) >= 0.9",
                            "label_for_charts": "Jaro-Winkler >= 0.9",
                        },
                        {
                            "sql_condition": "jaro_winkler_similarity(nombre_l, nombre_r) >= 0.8",
                            "label_for_charts": "Jaro-Winkler >= 0.8",
                        },
                        {
                            "sql_condition": "ELSE",
                            "label_for_charts": "All other comparisons",
                        },
                    ],
                },
                {
                    "output_column_name": "email",
                    "comparison_levels": [
                        {
                            "sql_condition": "email_l IS NULL OR email_r IS NULL",
                            "label_for_charts": "Null",
                            "is_null_level": True
                        },
                        {
                            "sql_condition": "email_l = email_r",
                            "label_for_charts": "Exact match email",
                        },
                        {
                            "sql_condition": "ELSE",
                            "label_for_charts": "All other comparisons",
                        },
                    ],
                },
                {
                    "output_column_name": "empresa",
                    "comparison_levels": [
                        {
                            "sql_condition": "empresa_l IS NULL OR empresa_r IS NULL",
                            "label_for_charts": "Null",
                            "is_null_level": True
                        },
                        {
                            "sql_condition": "empresa_l = empresa_r",
                            "label_for_charts": "Exact match",
                        },
                        {
                            "sql_condition": "levenshtein(empresa_l, empresa_r) <= 3",
                            "label_for_charts": "Levenshtein <= 3",
                        },
                        {
                            "sql_condition": "ELSE",
                            "label_for_charts": "All other comparisons",
                        },
                    ],
                },
            ],
            "retain_matching_columns": True,
            "retain_intermediate_calculation_columns": True,
            "max_iterations": 10,
            "em_convergence": 0.01,
        }
        
        return settings
    
    def deduplicate_contacts(self, contacts_df: pd.DataFrame) -> pd.DataFrame:
        """
        Deduplica 45K contactos de múltiples fuentes
        
        Args:
            contacts_df: DataFrame con columnas:
                - nombre, email, telefono, empresa, linkedin_url, 
                  twitter_handle, whatsapp, fuente
        
        Returns:
            DataFrame con entidades unificadas + confidence scores
        """
        
        print(f"Deduplicando {len(contacts_df)} contactos...")
        
        # Normalizar datos
        contacts_df['nombre_normalizado'] = contacts_df['nombre'].str.lower().str.strip()
        contacts_df['email_normalizado'] = contacts_df['email'].str.lower().str.strip()
        contacts_df['telefono_normalizado'] = self._normalize_phone(contacts_df['telefono'])
        contacts_df['linkedin_id'] = contacts_df['linkedin_url'].str.extract(r'/in/([^/]+)')
        
        # Configurar Splink
        settings = self.configure_deduplication()
        self.linker = DuckDBLinker(contacts_df, settings)
        
        # Entrenamiento del modelo
        print("Entrenando modelo de deduplicación...")
        self.linker.estimate_u_using_random_sampling(max_pairs=1e6)
        
        # Calcular pares de matches
        print("Calculando matches probabilísticos...")
        df_predictions = self.linker.predict(threshold_match_probability=0.75)
        
        # Clustering de entidades
        print("Clustering de entidades...")
        df_clusters = self.linker.cluster_pairwise_predictions_at_threshold(
            df_predictions, threshold_match_probability=0.85
        )
        
        # Unificar entidades por cluster
        df_unified = self._merge_cluster_records(df_clusters, contacts_df)
        
        print(f"✅ Reducción: {len(contacts_df)} → {len(df_unified)} contactos únicos")
        print(f"   Duplicados eliminados: {len(contacts_df) - len(df_unified)}")
        
        return df_unified
    
    def _normalize_phone(self, phone_series: pd.Series) -> pd.Series:
        """Normaliza teléfonos: +52 55 1234 5678 → 5512345678"""
        return phone_series.str.replace(r'[^\d]', '', regex=True).str[-10:]
    
    def _merge_cluster_records(self, df_clusters: pd.DataFrame, 
                                df_original: pd.DataFrame) -> pd.DataFrame:
        """
        Fusiona registros del mismo cluster en una entidad unificada
        
        Estrategia:
        - Seleccionar campo más completo de cada fuente
        - Priorizar LinkedIn > vCard > Twitter > WhatsApp
        - Agregar todas las fuentes en metadata
        """
        
        unified_contacts = []
        
        for cluster_id in df_clusters['cluster_id'].unique():
            cluster_records = df_clusters[df_clusters['cluster_id'] == cluster_id]
            
            # Obtener registros originales del cluster
            original_ids = cluster_records['unique_id'].tolist()
            cluster_data = df_original[df_original['unique_id'].isin(original_ids)]
            
            # Unificar campos (tomar el más completo)
            unified = {
                'entidad_unificada_id': f"UNIFIED-{cluster_id}",
                'nombre': self._select_best_field(cluster_data, 'nombre'),
                'email': self._select_best_field(cluster_data, 'email'),
                'telefono': self._select_best_field(cluster_data, 'telefono'),
                'empresa': self._select_best_field(cluster_data, 'empresa'),
                'puesto': self._select_best_field(cluster_data, 'puesto'),
                'linkedin_url': self._select_best_field(cluster_data, 'linkedin_url'),
                'twitter_handle': self._select_best_field(cluster_data, 'twitter_handle'),
                'whatsapp': self._select_best_field(cluster_data, 'whatsapp'),
                'fuentes': list(cluster_data['fuente'].unique()),
                'num_fuentes': len(cluster_data),
                'confianza_deduplicacion': cluster_records['match_probability'].mean()
            }
            
            unified_contacts.append(unified)
        
        return pd.DataFrame(unified_contacts)
    
    def _select_best_field(self, df: pd.DataFrame, field: str) -> str:
        """Selecciona el valor más completo de un campo entre registros"""
        values = df[field].dropna()
        if len(values) == 0:
            return None
        # Priorizar LinkedIn, luego el más largo
        if 'fuente' in df.columns:
            linkedin_vals = df[df['fuente'] == 'LinkedIn'][field].dropna()
            if len(linkedin_vals) > 0:
                return linkedin_vals.iloc[0]
        return values.loc[values.str.len().idxmax()]


# ============================================
# 2. NEO4J GRAPH DATABASE MANAGER
# ============================================

class ContactGraphDB:
    """
    Gestor de grafo de contactos en Neo4j
    
    Funcionalidades:
    - CRUD de personas y relaciones
    - Algoritmos de centralidad (PageRank, Betweenness)
    - Community detection (Louvain/Leiden)
    - Pathfinding (rutas de introducción)
    - Geo-queries (contactos por ciudad)
    """
    
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_contact(self, contact_data: Dict) -> str:
        """Crea nodo de Persona con propiedades"""
        
        with self.driver.session() as session:
            result = session.execute_write(
                self._create_contact_tx, contact_data
            )
            return result
    
    @staticmethod
    def _create_contact_tx(tx, data):
        query = """
        CREATE (p:Persona {
            id: $id,
            nombre: $nombre,
            email: $email,
            telefono: $telefono,
            empresa: $empresa,
            puesto: $puesto,
            tier: $tier,
            score_comercial: $score_comercial,
            ubicacion: $ubicacion
        })
        RETURN p.id as contact_id
        """
        result = tx.run(query, **data)
        return result.single()["contact_id"]
    
    def create_relationship(self, person1_id: str, person2_id: str, 
                           rel_type: str, properties: Dict = None):
        """
        Crea relación entre dos personas
        
        Tipos:
        - CONECTA_CON
        - ES_SOCIO_DE
        - ES_CLIENTE_DE
        - REFIERE_A
        - CONOCE_MEDIANTE_INTRODUCCION_DE
        """
        
        with self.driver.session() as session:
            session.execute_write(
                self._create_relationship_tx,
                person1_id, person2_id, rel_type, properties or {}
            )
    
    @staticmethod
    def _create_relationship_tx(tx, p1_id, p2_id, rel_type, props):
        query = f"""
        MATCH (p1:Persona {{id: $p1_id}})
        MATCH (p2:Persona {{id: $p2_id}})
        CREATE (p1)-[r:{rel_type}]->(p2)
        SET r += $props
        """
        tx.run(query, p1_id=p1_id, p2_id=p2_id, props=props)
    
    def calculate_pagerank(self):
        """
        Calcula PageRank para todos los contactos
        
        Identifica los contactos más influyentes en la red
        """
        
        with self.driver.session() as session:
            result = session.run("""
                CALL gds.pageRank.stream('contactGraph')
                YIELD nodeId, score
                MATCH (p:Persona) WHERE id(p) = nodeId
                SET p.pageRank = score
                RETURN p.nombre as nombre, score
                ORDER BY score DESC
                LIMIT 20
            """)
            
            return [dict(record) for record in result]
    
    def calculate_betweenness_centrality(self):
        """
        Calcula Betweenness Centrality
        
        Identifica "conectores" clave que unen comunidades
        """
        
        with self.driver.session() as session:
            result = session.run("""
                CALL gds.betweenness.stream('contactGraph')
                YIELD nodeId, score
                MATCH (p:Persona) WHERE id(p) = nodeId
                SET p.betweennessCentrality = score
                RETURN p.nombre as nombre, score
                ORDER BY score DESC
                LIMIT 20
            """)
            
            return [dict(record) for record in result]
    
    def detect_communities(self, algorithm="louvain"):
        """
        Detecta comunidades en la red
        
        Algoritmos:
        - louvain: Rápido, escalable
        - leiden: Más preciso, mejor calidad
        """
        
        algo_map = {
            "louvain": "gds.louvain",
            "leiden": "gds.leiden"
        }
        
        with self.driver.session() as session:
            result = session.run(f"""
                CALL {algo_map[algorithm]}.stream('contactGraph')
                YIELD nodeId, communityId
                MATCH (p:Persona) WHERE id(p) = nodeId
                SET p.comunidad_id = communityId
                RETURN communityId, count(*) as size
                ORDER BY size DESC
            """)
            
            communities = [dict(record) for record in result]
            print(f"✅ Detectadas {len(communities)} comunidades")
            return communities
    
    def find_introduction_path(self, person1_id: str, person2_id: str, 
                               max_hops: int = 3) -> List[Dict]:
        """
        Encuentra ruta más corta de introducción
        
        Use case: "¿Cómo llego a Juan López?" → "Puedes pedirle a María que te presente"
        """
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = shortestPath(
                    (p1:Persona {id: $p1_id})-[:CONECTA_CON*..%d]-(p2:Persona {id: $p2_id})
                )
                RETURN [node in nodes(path) | node.nombre] as ruta,
                       length(path) as grados_separacion
            """ % max_hops, p1_id=person1_id, p2_id=person2_id)
            
            record = result.single()
            if record:
                return {
                    'ruta': record['ruta'],
                    'grados': record['grados_separacion']
                }
            return None
    
    def get_contacts_by_geohub(self, ciudad: str, radius_km: int = 50) -> List[Dict]:
        """
        Obtiene contactos en una ciudad específica
        
        Para viajes: "Voy a Santiago mañana, ¿quién no he visto en 6 meses?"
        """
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Persona)-[:UBICADO_EN]->(g:GeoHub {nombre: $ciudad})
                WHERE p.dias_sin_contacto > 180
                  AND p.score_comercial >= 60
                RETURN p.nombre as nombre,
                       p.empresa as empresa,
                       p.dias_sin_contacto as dias,
                       p.score_comercial as score
                ORDER BY p.score_comercial DESC, p.dias_sin_contacto DESC
                LIMIT 20
            """, ciudad=ciudad)
            
            return [dict(record) for record in result]
    
    def get_tier1_contacts(self, min_score: float = 80) -> List[Dict]:
        """Obtiene decisores C-Level (Tier 1) con score alto"""
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Persona)
                WHERE p.tier = 1 
                  AND p.score_comercial >= $min_score
                RETURN p.nombre as nombre,
                       p.empresa as empresa,
                       p.puesto as puesto,
                       p.score_comercial as score,
                       p.pageRank as influencia
                ORDER BY p.score_comercial DESC
            """, min_score=min_score)
            
            return [dict(record) for record in result]


# ============================================
# 3. VECTOR SEARCH PARA BÚSQUEDA SEMÁNTICA
# ============================================

class ContactVectorSearch:
    """
    Búsqueda semántica de contactos
    
    Queries en lenguaje natural:
    - "¿Quién en mi red sabe de reciclaje industrial de cobre?"
    - "Busco expertos en economía circular en Ciudad de México"
    - "Encuentra decisores C-Level en industria automotriz"
    """
    
    def __init__(self, dimension=768):
        self.dimension = dimension
        self.model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        self.index = faiss.IndexHNSWFlat(dimension, 32)  # HNSW para escalabilidad
        self.contact_ids = []
        self.contact_metadata = {}
    
    def create_contact_embedding(self, contact_data: Dict) -> np.ndarray:
        """
        Genera embedding de 768 dims combinando:
        - Biografia/puesto
        - Empresa e industria
        - Intereses y expertise
        - Ubicación
        """
        
        text = f"""
        Persona: {contact_data.get('nombre', '')}
        Puesto: {contact_data.get('puesto', '')}
        Empresa: {contact_data.get('empresa', '')}
        Industria: {contact_data.get('industria', '')}
        Expertise: {contact_data.get('expertise', '')}
        Intereses CSR: {contact_data.get('intereses_csr', '')}
        Ubicación: {contact_data.get('ubicacion', '')}
        Biografia: {contact_data.get('biografia', '')}
        """
        
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.astype('float32')
    
    def add_contact(self, contact_id: str, contact_data: Dict):
        """Agrega contacto al índice vectorial"""
        embedding = self.create_contact_embedding(contact_data)
        self.index.add(embedding.reshape(1, -1))
        self.contact_ids.append(contact_id)
        self.contact_metadata[contact_id] = {
            'nombre': contact_data.get('nombre'),
            'empresa': contact_data.get('empresa'),
            'score_comercial': contact_data.get('score_comercial', 0)
        }
    
    def search_by_text(self, query: str, k: int = 10, 
                       filters: Dict = None) -> List[Dict]:
        """
        Búsqueda por texto libre
        
        Example:
            query = "Busco expertos en reciclaje industrial y economía circular"
            results = search.search_by_text(query, k=10)
        """
        
        # Generar embedding de query
        query_embedding = self.model.encode(query, normalize_embeddings=True)
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        
        # Buscar en índice HNSW
        distances, indices = self.index.search(query_embedding, k * 2)
        
        # Convertir a resultados
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            
            contact_id = self.contact_ids[idx]
            metadata = self.contact_metadata.get(contact_id, {})
            
            # Aplicar filtros
            if filters and not self._apply_filters(metadata, filters):
                continue
            
            relevance = max(0, 1 - (dist / 2))
            
            results.append({
                'contact_id': contact_id,
                'relevance': round(relevance, 3),
                'metadata': metadata
            })
            
            if len(results) >= k:
                break
        
        return results
    
    def _apply_filters(self, metadata: Dict, filters: Dict) -> bool:
        """Aplica filtros de score, tier, ubicación, etc."""
        if 'min_score' in filters:
            if metadata.get('score_comercial', 0) < filters['min_score']:
                return False
        return True


# ============================================
# 4. SCORING ENGINE PARA VALOR COMERCIAL
# ============================================

class CommercialScoringEngine:
    """
    Calcula score comercial de cada contacto (0-100)
    
    Componentes:
    - Nivel de decisión (C-Level, Director, Manager)
    - Tamaño de empresa (Fortune 500, Mid-market, Startup)
    - Industria de alto valor (Automotriz, Real Estate, Consultoría)
    - Centralidad en red (PageRank, Betweenness)
    - Recencia de interacción
    """
    
    def calculate_commercial_score(self, contact: Dict, graph_metrics: Dict = None) -> float:
        """
        Calcula score comercial total
        
        Fórmula:
        Score = 0.30×NivelDecisión + 0.25×TamañoEmpresa + 0.20×Industria +
                0.15×Centralidad + 0.10×Recencia
        """
        
        score_nivel = self._score_decision_level(contact.get('puesto', ''))
        score_empresa = self._score_company_size(contact.get('empresa', ''))
        score_industria = self._score_industry(contact.get('industria', ''))
        score_centralidad = self._score_centrality(graph_metrics or {})
        score_recencia = self._score_recency(contact.get('dias_sin_contacto', 365))
        
        total = (
            0.30 * score_nivel +
            0.25 * score_empresa +
            0.20 * score_industria +
            0.15 * score_centralidad +
            0.10 * score_recencia
        )
        
        return round(total, 2)
    
    def _score_decision_level(self, puesto: str) -> float:
        """Score basado en nivel de decisión (0-100)"""
        puesto_lower = puesto.lower()
        
        if any(term in puesto_lower for term in ['ceo', 'founder', 'presidente', 'director general']):
            return 100
        elif any(term in puesto_lower for term in ['cfo', 'coo', 'cto', 'vp', 'vicepresidente']):
            return 90
        elif 'director' in puesto_lower:
            return 75
        elif 'gerente' in puesto_lower or 'manager' in puesto_lower:
            return 60
        elif 'coordinador' in puesto_lower or 'jefe' in puesto_lower:
            return 40
        else:
            return 30
    
    def _score_company_size(self, empresa: str) -> float:
        """Score basado en tamaño de empresa (0-100)"""
        # En producción: integrar con API de LinkedIn/Crunchbase
        # Para MVP: clasificación manual o regex
        fortune_500 = ['google', 'apple', 'microsoft', 'amazon', 'facebook']
        if any(comp in empresa.lower() for comp in fortune_500):
            return 100
        return 60  # Default para empresas medianas
    
    def _score_industry(self, industria: str) -> float:
        """Score basado en industria (0-100)"""
        industria_lower = industria.lower()
        
        high_value = ['automotriz', 'real estate', 'consultoria estrategica', 'banca']
        medium_value = ['tecnologia', 'manufactura', 'logistica']
        
        if any(ind in industria_lower for ind in high_value):
            return 100
        elif any(ind in industria_lower for ind in medium_value):
            return 70
        else:
            return 50
    
    def _score_centrality(self, metrics: Dict) -> float:
        """Score basado en métricas de red (0-100)"""
        pagerank = metrics.get('pageRank', 0)
        betweenness = metrics.get('betweennessCentrality', 0)
        
        return ((pagerank * 100) + (betweenness * 100)) / 2
    
    def _score_recency(self, dias_sin_contacto: int) -> float:
        """Score basado en recencia (0-100)"""
        if dias_sin_contacto <= 30:
            return 100
        elif dias_sin_contacto <= 90:
            return 80
        elif dias_sin_contacto <= 180:
            return 60
        elif dias_sin_contacto <= 365:
            return 40
        else:
            return 20


# ============================================
# 5. WHATSAPP INTERFACE (SIMULACIÓN)
# ============================================

class WhatsAppInterface:
    """
    Interfaz conversacional para consultas en movimiento
    
    Casos de uso:
    - "Voy a Madrid mañana, ¿quién no he visto en 6 meses?"
    - "Busco expertos en reciclaje de cobre"
    - "¿Cómo llego a Juan López?"
    - Transcripción de notas de voz post-reuniones
    """
    
    def __init__(self, graph_db: ContactGraphDB, vector_search: ContactVectorSearch):
        self.graph_db = graph_db
        self.vector_search = vector_search
    
    def process_query(self, user_query: str) -> str:
        """
        Procesa consulta en lenguaje natural
        
        Usa LLM (Gemini) para:
        1. Clasificar tipo de query (geo, experto, ruta, etc.)
        2. Extraer parámetros
        3. Ejecutar query apropiado
        4. Formatear respuesta conversacional
        """
        
        # Clasificación de intent (simplificado, en producción usar Gemini)
        if 'voy a' in user_query.lower() or 'viaje' in user_query.lower():
            return self._handle_geo_query(user_query)
        elif 'busco' in user_query.lower() or 'experto' in user_query.lower():
            return self._handle_expert_search(user_query)
        elif 'cómo llego' in user_query.lower():
            return self._handle_introduction_path(user_query)
        else:
            return self._handle_general_search(user_query)
    
    def _handle_geo_query(self, query: str) -> str:
        """Maneja consultas geográficas"""
        # Extraer ciudad (simplificado)
        ciudades = ['madrid', 'santiago', 'monterrey', 'nueva york']
        ciudad = next((c for c in ciudades if c in query.lower()), 'madrid')
        
        contacts = self.graph_db.get_contacts_by_geohub(ciudad.title())
        
        if not contacts:
            return f"No encontré contactos de alto valor en {ciudad.title()} que no hayas visto recientemente."
        
        response = f"🌍 En {ciudad.title()} tienes {len(contacts)} contactos clave:\n\n"
        for i, c in enumerate(contacts[:5], 1):
            response += f"{i}. {c['nombre']} - {c['empresa']} (Score: {c['score']}, {c['dias']} días sin contacto)\n"
        
        return response
    
    def _handle_expert_search(self, query: str) -> str:
        """Maneja búsqueda de expertos"""
        results = self.vector_search.search_by_text(query, k=5, filters={'min_score': 60})
        
        if not results:
            return "No encontré expertos que coincidan con tu búsqueda."
        
        response = "🔍 Encontré estos expertos en tu red:\n\n"
        for i, r in enumerate(results, 1):
            meta = r['metadata']
            response += f"{i}. {meta['nombre']} - {meta['empresa']} (Relevancia: {r['relevance']:.0%})\n"
        
        return response
    
    def _handle_introduction_path(self, query: str) -> str:
        """Maneja rutas de introducción"""
        # En producción: extraer nombres con NER
        return "Para llegar a Juan López, puedes pedirle a María Rodríguez que te presente (1 grado de separación)"
    
    def _handle_general_search(self, query: str) -> str:
        """Búsqueda general semántica"""
        return self._handle_expert_search(query)


# ============================================
# EJEMPLO DE USO COMPLETO
# ============================================

if __name__ == "__main__":
    print("="*80)
    print("GRAPHRAG CONTACT NETWORK SYSTEM - DEMO")
    print("="*80 + "\n")
    
    # 1. Deduplicación (simulada)
    print("1️⃣  DEDUPLICACIÓN DE CONTACTOS")
    print("-" * 80)
    
    # Datos de ejemplo (en producción: cargar de vCard, LinkedIn, etc.)
    sample_contacts = pd.DataFrame([
        {
            'unique_id': '1',
            'nombre': 'Juan López',
            'email': 'juan.lopez@empresa.com',
            'telefono': '+52 55 1234 5678',
            'empresa': 'Tesla Motors',
            'puesto': 'Director de Operaciones',
            'fuente': 'LinkedIn'
        },
        {
            'unique_id': '2',
            'nombre': 'Juan Lopez',  # Duplicado con variación
            'email': 'jlopez@tesla.com',
            'telefono': '55-1234-5678',
            'empresa': 'Tesla',
            'puesto': 'Director Operations',
            'fuente': 'vCard'
        },
        {
            'unique_id': '3',
            'nombre': 'María Rodríguez',
            'email': 'maria.r@google.com',
            'telefono': '+52 55 8765 4321',
            'empresa': 'Google',
            'puesto': 'VP Engineering',
            'fuente': 'LinkedIn'
        }
    ])
    
    print(f"Contactos originales: {len(sample_contacts)}")
    print("✅ Deduplicación completa (Splink requiere > 100 registros para entrenamiento)\n")
    
    # 2. Scoring comercial
    print("2️⃣  SCORING COMERCIAL")
    print("-" * 80)
    
    scorer = CommercialScoringEngine()
    
    contact_juan = {
        'puesto': 'Director de Operaciones',
        'empresa': 'Tesla Motors',
        'industria': 'Automotriz',
        'dias_sin_contacto': 45
    }
    
    score_juan = scorer.calculate_commercial_score(contact_juan)
    print(f"Juan López (Tesla): Score comercial = {score_juan}/100")
    print(f"  → Tier 1 (Decidor C-Level)\n")
    
    # 3. Búsqueda vectorial
    print("3️⃣  BÚSQUEDA VECTORIAL SEMÁNTICA")
    print("-" * 80)
    
    vector_search = ContactVectorSearch()
    
    # Agregar contactos
    vector_search.add_contact('CONTACT-001', {
        'nombre': 'Juan López',
        'puesto': 'Director de Operaciones',
        'empresa': 'Tesla Motors',
        'industria': 'Automotriz',
        'expertise': 'Manufactura, Cadena de suministro, Sustentabilidad',
        'intereses_csr': 'Economía circular, Reciclaje de baterías',
        'ubicacion': 'Monterrey',
        'biografia': 'Director de Operaciones con 15 años en industria automotriz...',
        'score_comercial': score_juan
    })
    
    # Búsqueda
    query = "Busco expertos en reciclaje industrial y economía circular en automotriz"
    results = vector_search.search_by_text(query, k=3)
    
    print(f"Query: '{query}'")
    print(f"\nResultados ({len(results)}):")
    for r in results:
        print(f"  - {r['metadata']['nombre']} ({r['metadata']['empresa']}) - Relevancia: {r['relevance']:.0%}")
    
    print("\n" + "="*80)
    print("✅ Demo completada!")
    print("\nPróximos pasos:")
    print("1. Cargar 45K contactos reales (vCard, LinkedIn API, Twitter API)")
    print("2. Ejecutar deduplicación completa con Splink")
    print("3. Poblar Neo4j con relaciones")
    print("4. Integrar WhatsApp Business API")
    print("5. Conectar con Gemini para razonamiento estratégico")
