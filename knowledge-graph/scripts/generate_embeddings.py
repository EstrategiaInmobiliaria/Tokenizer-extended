"""
Generación de Embeddings Vectoriales para Búsqueda Semántica
Usa Sentence-BERT para crear representaciones de 768 dimensiones
"""

import pandas as pd
import numpy as np
import argparse
from sentence_transformers import SentenceTransformer
from pathlib import Path
import pickle
from tqdm import tqdm
import sys

sys.path.append('/workspace/knowledge-graph')
from queries.graphrag_contact_system import ContactVectorSearch


def generate_embeddings(input_csv: str, output_dir: str, model_name: str = 'paraphrase-multilingual-mpnet-base-v2'):
    """
    Genera embeddings vectoriales para todos los contactos
    
    Args:
        input_csv: Ruta al CSV de contactos unificados
        output_dir: Directorio de salida para embeddings
        model_name: Modelo de Sentence-BERT
    
    Outputs:
        - embeddings.npy: Matriz numpy (N × 768)
        - contact_ids.txt: IDs de contactos (orden correspondiente)
        - contact_index.faiss: Índice FAISS para búsqueda rápida
        - metadata.pkl: Metadata de contactos
    """
    
    print("="*80)
    print("GENERACIÓN DE EMBEDDINGS VECTORIALES")
    print("="*80 + "\n")
    
    # Cargar datos
    print(f"📂 Cargando: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"   Total contactos: {len(df)}\n")
    
    # Crear directorio de salida
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Cargar modelo
    print(f"🤖 Cargando modelo: {model_name}")
    print("   (Primera vez puede tardar ~2GB de descarga)")
    model = SentenceTransformer(model_name)
    print("   ✅ Modelo cargado\n")
    
    # Preparar textos para embedding
    print("📝 Preparando textos...")
    texts = []
    contact_ids = []
    metadata = {}
    
    for _, row in tqdm(df.iterrows(), total=len(df)):
        # Construir texto descriptivo
        contact_id = row.get('entidad_unificada_id', f"CONTACT-{row.name}")
        
        text_parts = []
        
        if pd.notna(row.get('nombre')):
            text_parts.append(f"Persona: {row['nombre']}")
        
        if pd.notna(row.get('puesto')):
            text_parts.append(f"Puesto: {row['puesto']}")
        
        if pd.notna(row.get('empresa')):
            text_parts.append(f"Empresa: {row['empresa']}")
        
        if pd.notna(row.get('industria')):
            text_parts.append(f"Industria: {row['industria']}")
        
        if pd.notna(row.get('biografia')):
            text_parts.append(f"Biografia: {row['biografia']}")
        
        if pd.notna(row.get('intereses_csr')):
            text_parts.append(f"Intereses: {row['intereses_csr']}")
        
        if pd.notna(row.get('ubicacion')):
            text_parts.append(f"Ubicación: {row['ubicacion']}")
        
        text = "\n".join(text_parts)
        
        if text.strip():
            texts.append(text)
            contact_ids.append(contact_id)
            
            metadata[contact_id] = {
                'nombre': row.get('nombre'),
                'empresa': row.get('empresa'),
                'score_comercial': row.get('score_comercial', 0),
                'tier': row.get('tier', 3)
            }
    
    print(f"   ✅ {len(texts)} textos preparados\n")
    
    # Generar embeddings
    print("🧠 Generando embeddings...")
    print("   (Esto puede tardar varios minutos para 45K contactos)")
    
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True
    )
    
    print(f"\n   ✅ Embeddings generados: shape {embeddings.shape}")
    
    # Guardar embeddings
    print("\n💾 Guardando archivos...")
    
    # 1. Embeddings numpy
    embeddings_file = output_path / 'embeddings.npy'
    np.save(embeddings_file, embeddings)
    print(f"   ✅ {embeddings_file}")
    
    # 2. Contact IDs
    ids_file = output_path / 'contact_ids.txt'
    with open(ids_file, 'w') as f:
        f.write('\n'.join(contact_ids))
    print(f"   ✅ {ids_file}")
    
    # 3. Metadata
    metadata_file = output_path / 'metadata.pkl'
    with open(metadata_file, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"   ✅ {metadata_file}")
    
    # Crear índice FAISS
    print("\n🔍 Creando índice FAISS (HNSW)...")
    
    vector_search = ContactVectorSearch(dimension=embeddings.shape[1])
    
    for i, contact_id in enumerate(tqdm(contact_ids)):
        # Agregar al índice
        embedding = embeddings[i]
        vector_search.index.add(embedding.reshape(1, -1))
        vector_search.contact_ids.append(contact_id)
        vector_search.contact_metadata[contact_id] = metadata[contact_id]
    
    # Guardar índice
    index_file = output_path / 'contact_index.faiss'
    vector_search.save_index(str(output_path))
    print(f"   ✅ {index_file}")
    
    # Estadísticas
    print("\n" + "="*80)
    print("✅ EMBEDDINGS GENERADOS")
    print("="*80)
    print(f"\nArchivos generados en: {output_path}/")
    print(f"   - embeddings.npy ({embeddings.nbytes / 1024 / 1024:.1f} MB)")
    print(f"   - contact_ids.txt")
    print(f"   - metadata.pkl")
    print(f"   - contact_index.faiss")
    print(f"   - contact_metadata.pkl")
    
    # Ejemplo de búsqueda
    print("\n🔍 Ejemplo de búsqueda:")
    query = "Expertos en economía circular y reciclaje industrial"
    results = vector_search.search_by_text(query, k=5)
    
    print(f"\nQuery: '{query}'")
    print("\nResultados:")
    for i, result in enumerate(results, 1):
        meta = result['metadata']
        print(f"   {i}. {meta['nombre']} ({meta['empresa']}) - "
              f"Relevancia: {result['relevance']:.1%}")
    
    print("\n📍 Sistema de búsqueda vectorial listo!")
    print("   Puedes consultar usando:")
    print("   python queries/graphrag_contact_system.py")


def main():
    parser = argparse.ArgumentParser(
        description="Genera embeddings vectoriales para contactos"
    )
    parser.add_argument(
        '--input',
        type=str,
        default='/workspace/knowledge-graph/data/contacts/contacts_unified.csv',
        help='CSV de contactos unificados'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='/workspace/knowledge-graph/data/embeddings',
        help='Directorio de salida para embeddings'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='paraphrase-multilingual-mpnet-base-v2',
        help='Modelo de Sentence-BERT'
    )
    
    args = parser.parse_args()
    
    generate_embeddings(
        input_csv=args.input,
        output_dir=args.output,
        model_name=args.model
    )


if __name__ == "__main__":
    main()
