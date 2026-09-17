"""
Vector Search Engine para Leads Inmobiliarios
Implementación de búsqueda semántica con FAISS + Sentence-BERT

Basado en:
- "Billion-scale similarity search with GPUs" (Facebook AI, 2019)
- "Vector Embeddings for Customer Similarity in CRM" (ACM RecSys, 2023)

Permite:
1. Encontrar leads similares ("clientes como María")
2. Búsqueda por texto libre ("busco inversionistas en Polanco")
3. Detección de duplicados
4. Clustering automático de segmentos
"""

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import pickle
import json
from datetime import datetime

class VectorLeadSearch:
    """
    Motor de búsqueda vectorial para leads con FAISS
    """
    
    def __init__(self, dimension=768, use_gpu=False):
        """
        Args:
            dimension: Dimensión de vectores (768 para mpnet-base-v2)
            use_gpu: Usar GPU para indexación (más rápido)
        """
        self.dimension = dimension
        self.use_gpu = use_gpu
        
        # Cargar modelo de embeddings (multilenguaje)
        print("Cargando modelo Sentence-BERT...")
        self.model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        print(f"✅ Modelo cargado (dimensión: {self.dimension})")
        
        # Inicializar índice FAISS
        self.index = self._create_index()
        
        # Mapeo posición → lead_id
        self.lead_ids = []
        
        # Metadata de leads (para retrieval rápido)
        self.lead_metadata = {}
    
    def _create_index(self):
        """Crea índice FAISS optimizado"""
        
        if self.use_gpu and faiss.get_num_gpus() > 0:
            print("Usando GPU para indexación...")
            # Índice en GPU
            res = faiss.StandardGpuResources()
            index = faiss.IndexFlatL2(self.dimension)
            gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
            return gpu_index
        else:
            # Para datasets pequeños (<100K): IndexFlatL2 (exacto)
            # Para datasets grandes: IndexIVFPQ (aproximado pero rápido)
            
            print("Usando CPU para indexación...")
            
            # Opción 1: Búsqueda exacta (para <100K leads)
            # index = faiss.IndexFlatL2(self.dimension)
            
            # Opción 2: Búsqueda aproximada con IVF + PQ (para >100K leads)
            quantizer = faiss.IndexFlatL2(self.dimension)
            index = faiss.IndexIVFPQ(
                quantizer,
                self.dimension,
                100,  # nlist: número de clusters
                8,    # M: bytes por vector (compresión)
                8     # nbits: bits por sub-vector
            )
            
            # Nota: IVF requiere entrenamiento antes de agregar vectores
            # Llamar train() con datos de muestra después
            
            return index
    
    def create_lead_embedding(self, lead_data: Dict) -> np.ndarray:
        """
        Genera vector embedding de 768 dimensiones para un lead
        
        Combina:
        - Información demográfica
        - Preferencias de propiedad
        - Comportamiento (propiedades vistas)
        - Capacidad financiera
        """
        
        # Crear descripción textual del lead
        text_representation = f"""
        Lead: {lead_data.get('nombre', 'Desconocido')}
        
        Motivación: {lead_data.get('motivación', 'No especificada')}
        
        Ubicación de interés: {lead_data.get('zona_preferida', 'Cualquier zona')}
        
        Tipo de propiedad: {lead_data.get('tipo_propiedad_preferida', 'No especificado')}
        
        Presupuesto: ${lead_data.get('presupuesto_min', 0):,.0f} - ${lead_data.get('presupuesto_max', 0):,.0f} MXN
        
        Recámaras deseadas: {lead_data.get('recámaras_deseadas', 'No especificado')}
        
        Plazo de compra: {lead_data.get('plazo_compra', 'No definido')}
        
        Madurez financiera: {lead_data.get('madurez_financiera', 'Desconocida')}
        
        Propiedades vistas: {self._format_propiedades_vistas(lead_data.get('propiedades_vistas', []))}
        
        Ocupación: {lead_data.get('ocupación', 'No especificada')}
        
        Edad aproximada: {lead_data.get('edad_aproximada', 'No especificada')}
        """
        
        # Generar embedding
        embedding = self.model.encode(
            text_representation,
            convert_to_numpy=True,
            normalize_embeddings=True  # Importante para L2 distance
        )
        
        return embedding.astype('float32')
    
    def add_lead(self, lead_id: str, lead_data: Dict):
        """
        Agrega lead al índice vectorial
        
        Args:
            lead_id: Identificador único del lead
            lead_data: Diccionario con información del lead
        """
        
        # Generar embedding
        embedding = self.create_lead_embedding(lead_data)
        
        # Agregar a índice
        if isinstance(self.index, faiss.IndexIVFPQ) and not self.index.is_trained:
            print("⚠️ Índice IVF no entrenado. Entrenar primero con train_index()")
            return
        
        self.index.add(embedding.reshape(1, -1))
        
        # Guardar mapeo
        self.lead_ids.append(lead_id)
        
        # Guardar metadata
        self.lead_metadata[lead_id] = {
            'nombre': lead_data.get('nombre'),
            'zona_preferida': lead_data.get('zona_preferida'),
            'presupuesto_max': lead_data.get('presupuesto_max'),
            'score_total': lead_data.get('score_total', 0),
            'timestamp': datetime.now().isoformat()
        }
    
    def bulk_add_leads(self, leads: List[Tuple[str, Dict]]):
        """
        Agrega múltiples leads de forma eficiente
        
        Args:
            leads: Lista de (lead_id, lead_data)
        """
        print(f"Agregando {len(leads)} leads al índice...")
        
        # Generar todos los embeddings
        embeddings = []
        for lead_id, lead_data in leads:
            emb = self.create_lead_embedding(lead_data)
            embeddings.append(emb)
            self.lead_ids.append(lead_id)
            self.lead_metadata[lead_id] = {
                'nombre': lead_data.get('nombre'),
                'zona_preferida': lead_data.get('zona_preferida'),
                'presupuesto_max': lead_data.get('presupuesto_max'),
                'score_total': lead_data.get('score_total', 0)
            }
        
        embeddings_array = np.vstack(embeddings)
        
        # Si es IVF, entrenar primero
        if isinstance(self.index, faiss.IndexIVFPQ) and not self.index.is_trained:
            print("Entrenando índice IVF...")
            self.index.train(embeddings_array)
            print("✅ Índice entrenado")
        
        # Agregar todos los vectores
        self.index.add(embeddings_array)
        print(f"✅ {len(leads)} leads agregados al índice")
    
    def find_similar_leads(self, lead_id: str, k: int = 10, 
                          min_similarity: float = 0.7) -> List[Dict]:
        """
        Encuentra los k leads más similares a un lead dado
        
        Args:
            lead_id: ID del lead query
            k: Número de resultados
            min_similarity: Similitud mínima (0-1)
        
        Returns:
            Lista de leads similares con scores
        """
        
        # Encontrar posición del lead en el índice
        try:
            idx = self.lead_ids.index(lead_id)
        except ValueError:
            return []
        
        # Obtener vector del lead
        query_vector = self.index.reconstruct(idx).reshape(1, -1)
        
        # Buscar similares
        distances, indices = self.index.search(query_vector, k + 1)
        
        # Convertir distancia L2 a similitud (0-1)
        # similarity = 1 - (distance / 2) para vectores normalizados
        
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1 or i == 0:  # Skip si es el mismo lead
                continue
            
            similarity = max(0, 1 - (dist / 2))
            
            if similarity >= min_similarity:
                similar_lead_id = self.lead_ids[idx]
                results.append({
                    'lead_id': similar_lead_id,
                    'similarity': round(similarity, 3),
                    'distance': round(float(dist), 3),
                    'metadata': self.lead_metadata.get(similar_lead_id, {})
                })
        
        return results
    
    def search_by_text(self, query: str, k: int = 10, 
                       filters: Dict = None) -> List[Dict]:
        """
        Búsqueda por texto libre
        
        Args:
            query: Texto de búsqueda (ej: "inversionista en Polanco con $10M")
            k: Número de resultados
            filters: Filtros adicionales (presupuesto, zona, etc.)
        
        Returns:
            Lista de leads relevantes
        """
        
        # Generar embedding de la query
        query_embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype('float32').reshape(1, -1)
        
        # Buscar en índice
        distances, indices = self.index.search(query_embedding, k * 2)  # 2x por filtros
        
        # Convertir a resultados
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            
            lead_id = self.lead_ids[idx]
            metadata = self.lead_metadata.get(lead_id, {})
            
            # Aplicar filtros
            if filters:
                if not self._apply_filters(metadata, filters):
                    continue
            
            relevance = max(0, 1 - (dist / 2))
            
            results.append({
                'lead_id': lead_id,
                'relevance': round(relevance, 3),
                'distance': round(float(dist), 3),
                'metadata': metadata
            })
            
            if len(results) >= k:
                break
        
        return results
    
    def find_duplicates(self, threshold: float = 0.95) -> List[Tuple]:
        """
        Encuentra leads duplicados (mismo perfil, diferente email/teléfono)
        
        Args:
            threshold: Umbral de similitud para considerar duplicado (0.95 = 95%)
        
        Returns:
            Lista de (lead_id1, lead_id2, similarity)
        """
        duplicates = []
        
        print(f"Buscando duplicados entre {len(self.lead_ids)} leads...")
        
        for i, lead_id in enumerate(self.lead_ids):
            similar = self.find_similar_leads(lead_id, k=5, min_similarity=threshold)
            
            for sim in similar:
                if sim['similarity'] >= threshold:
                    # Evitar duplicar (A, B) y (B, A)
                    pair = tuple(sorted([lead_id, sim['lead_id']]))
                    if pair not in [tuple(sorted([d[0], d[1]])) for d in duplicates]:
                        duplicates.append((
                            lead_id,
                            sim['lead_id'],
                            sim['similarity']
                        ))
        
        print(f"✅ Encontrados {len(duplicates)} posibles duplicados")
        return duplicates
    
    def cluster_leads(self, n_clusters: int = 10) -> Dict:
        """
        Agrupa leads en clusters semánticos usando K-Means
        
        Args:
            n_clusters: Número de clusters deseados
        
        Returns:
            Diccionario con clusters y sus miembros
        """
        print(f"Clustering {len(self.lead_ids)} leads en {n_clusters} grupos...")
        
        # Extraer todos los vectores
        vectors = np.vstack([
            self.index.reconstruct(i) for i in range(len(self.lead_ids))
        ])
        
        # K-Means
        kmeans = faiss.Kmeans(self.dimension, n_clusters, niter=20, verbose=False)
        kmeans.train(vectors)
        
        # Asignar leads a clusters
        _, labels = kmeans.index.search(vectors, 1)
        
        # Organizar resultados
        clusters = {i: [] for i in range(n_clusters)}
        for lead_id, cluster_id in zip(self.lead_ids, labels.flatten()):
            clusters[cluster_id].append({
                'lead_id': lead_id,
                'metadata': self.lead_metadata.get(lead_id, {})
            })
        
        print("✅ Clustering completado")
        return clusters
    
    def save_index(self, filepath: str):
        """Guarda índice a disco"""
        # Guardar índice FAISS
        faiss.write_index(self.index, f"{filepath}.index")
        
        # Guardar metadata
        with open(f"{filepath}.metadata.pkl", 'wb') as f:
            pickle.dump({
                'lead_ids': self.lead_ids,
                'lead_metadata': self.lead_metadata
            }, f)
        
        print(f"✅ Índice guardado en {filepath}")
    
    def load_index(self, filepath: str):
        """Carga índice desde disco"""
        # Cargar índice FAISS
        self.index = faiss.read_index(f"{filepath}.index")
        
        # Cargar metadata
        with open(f"{filepath}.metadata.pkl", 'rb') as f:
            data = pickle.load(f)
            self.lead_ids = data['lead_ids']
            self.lead_metadata = data['lead_metadata']
        
        print(f"✅ Índice cargado desde {filepath} ({len(self.lead_ids)} leads)")
    
    # Métodos auxiliares
    
    def _format_propiedades_vistas(self, propiedades: List[Dict]) -> str:
        """Formatea lista de propiedades vistas para embedding"""
        if not propiedades:
            return "Ninguna propiedad vista"
        
        descripciones = [
            f"{p.get('nombre', 'Propiedad')} (${p.get('precio', 0):,.0f})"
            for p in propiedades[:5]  # Limitar a 5 para no hacer embedding muy largo
        ]
        return ", ".join(descripciones)
    
    def _apply_filters(self, metadata: Dict, filters: Dict) -> bool:
        """Aplica filtros a metadata de lead"""
        
        if 'min_presupuesto' in filters:
            if metadata.get('presupuesto_max', 0) < filters['min_presupuesto']:
                return False
        
        if 'max_presupuesto' in filters:
            if metadata.get('presupuesto_max', float('inf')) > filters['max_presupuesto']:
                return False
        
        if 'zona' in filters:
            if filters['zona'].lower() not in metadata.get('zona_preferida', '').lower():
                return False
        
        if 'min_score' in filters:
            if metadata.get('score_total', 0) < filters['min_score']:
                return False
        
        return True


# ==============================================
# EJEMPLO DE USO
# ==============================================

if __name__ == "__main__":
    # Inicializar motor de búsqueda
    print("="*80)
    print("INICIALIZANDO VECTOR SEARCH ENGINE")
    print("="*80 + "\n")
    
    search_engine = VectorLeadSearch(use_gpu=False)
    
    # Datos de ejemplo
    ejemplo_leads = [
        ('LEAD-001', {
            'nombre': 'María Rodríguez',
            'motivación': 'Vivienda propia',
            'zona_preferida': 'Polanco',
            'tipo_propiedad_preferida': 'departamento',
            'presupuesto_min': 7000000,
            'presupuesto_max': 9000000,
            'recámaras_deseadas': 2,
            'plazo_compra': '0-3 meses',
            'madurez_financiera': 'Aprobado',
            'propiedades_vistas': [
                {'nombre': 'Depto Polanco 123', 'precio': 7500000},
                {'nombre': 'Depto Polanco 456', 'precio': 8200000}
            ],
            'ocupación': 'Gerente de Marketing',
            'edad_aproximada': 35,
            'score_total': 87
        }),
        ('LEAD-002', {
            'nombre': 'Carlos Martínez',
            'motivación': 'Inversión',
            'zona_preferida': 'Polanco',
            'tipo_propiedad_preferida': 'departamento',
            'presupuesto_min': 8000000,
            'presupuesto_max': 12000000,
            'recámaras_deseadas': 3,
            'plazo_compra': '0-3 meses',
            'madurez_financiera': 'Contado',
            'propiedades_vistas': [
                {'nombre': 'Depto Polanco 789', 'precio': 9500000}
            ],
            'ocupación': 'Empresario',
            'edad_aproximada': 42,
            'score_total': 92
        }),
        ('LEAD-003', {
            'nombre': 'Ana López',
            'motivación': 'Vivienda propia',
            'zona_preferida': 'Santa Fe',
            'tipo_propiedad_preferida': 'departamento',
            'presupuesto_min': 4000000,
            'presupuesto_max': 6000000,
            'recámaras_deseadas': 2,
            'plazo_compra': '3-6 meses',
            'madurez_financiera': 'En proceso',
            'propiedades_vistas': [],
            'ocupación': 'Contadora',
            'edad_aproximada': 28,
            'score_total': 65
        }),
        ('LEAD-004', {
            'nombre': 'Roberto Sánchez',
            'motivación': 'Inversión',
            'zona_preferida': 'Roma Norte',
            'tipo_propiedad_preferida': 'local comercial',
            'presupuesto_min': 8000000,
            'presupuesto_max': 15000000,
            'recámaras_deseadas': 0,
            'plazo_compra': '0-3 meses',
            'madurez_financiera': 'Contado',
            'propiedades_vistas': [
                {'nombre': 'Local Roma 001', 'precio': 12000000}
            ],
            'ocupación': 'Empresario',
            'edad_aproximada': 50,
            'score_total': 88
        }),
        ('LEAD-005', {
            'nombre': 'Laura García',
            'motivación': 'Vivienda propia',
            'zona_preferida': 'Polanco',
            'tipo_propiedad_preferida': 'departamento',
            'presupuesto_min': 6500000,
            'presupuesto_max': 8500000,
            'recámaras_deseadas': 2,
            'plazo_compra': '0-3 meses',
            'madurez_financiera': 'Aprobado',
            'propiedades_vistas': [
                {'nombre': 'Depto Polanco 321', 'precio': 7800000}
            ],
            'ocupación': 'Doctora',
            'edad_aproximada': 37,
            'score_total': 85
        })
    ]
    
    # Agregar leads al índice
    print("\n" + "="*80)
    print("AGREGANDO LEADS AL ÍNDICE")
    print("="*80)
    search_engine.bulk_add_leads(ejemplo_leads)
    
    # Ejemplo 1: Encontrar leads similares a María
    print("\n" + "="*80)
    print("EJEMPLO 1: LEADS SIMILARES A MARÍA")
    print("="*80)
    similares = search_engine.find_similar_leads('LEAD-001', k=3)
    print(json.dumps(similares, indent=2, ensure_ascii=False))
    
    # Ejemplo 2: Búsqueda por texto
    print("\n" + "="*80)
    print("EJEMPLO 2: BÚSQUEDA POR TEXTO")
    print("="*80)
    query = "Busco inversionista con presupuesto alto en Polanco"
    resultados = search_engine.search_by_text(query, k=3)
    print(f"Query: '{query}'\n")
    print(json.dumps(resultados, indent=2, ensure_ascii=False))
    
    # Ejemplo 3: Encontrar duplicados
    print("\n" + "="*80)
    print("EJEMPLO 3: DETECCIÓN DE DUPLICADOS")
    print("="*80)
    duplicados = search_engine.find_duplicates(threshold=0.90)
    if duplicados:
        for lead1, lead2, similarity in duplicados:
            print(f"Posible duplicado: {lead1} ↔ {lead2} (similitud: {similarity:.3f})")
    else:
        print("No se encontraron duplicados")
    
    # Ejemplo 4: Clustering
    print("\n" + "="*80)
    print("EJEMPLO 4: CLUSTERING DE LEADS")
    print("="*80)
    clusters = search_engine.cluster_leads(n_clusters=2)
    for cluster_id, members in clusters.items():
        print(f"\nCluster {cluster_id} ({len(members)} leads):")
        for member in members:
            print(f"  - {member['lead_id']}: {member['metadata'].get('nombre')}")
    
    # Guardar índice
    print("\n" + "="*80)
    print("GUARDANDO ÍNDICE")
    print("="*80)
    search_engine.save_index("leads_index")
    
    print("\n✅ Demo completada!")
    print("\nPara usar en producción:")
    print("1. Instalar: pip install faiss-cpu sentence-transformers")
    print("2. Cargar índice: search_engine.load_index('leads_index')")
    print("3. Buscar: search_engine.find_similar_leads('LEAD-XXX')")
