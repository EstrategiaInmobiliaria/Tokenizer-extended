"""
Script de Deduplicación de Contactos
Usa Splink para unificar identidades entre vCard, LinkedIn, Twitter, WhatsApp
"""

import pandas as pd
import argparse
from pathlib import Path
import sys

# Agregar path del proyecto
sys.path.append('/workspace/knowledge-graph')

from queries.graphrag_contact_system import ContactDeduplicator

def main():
    parser = argparse.ArgumentParser(
        description="Deduplica contactos de múltiples fuentes usando Splink"
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Ruta al CSV de contactos crudos (output de ETL pipeline)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='/workspace/knowledge-graph/data/contacts/contacts_unified.csv',
        help='Ruta de salida para contactos unificados'
    )
    parser.add_argument(
        '--min-confidence',
        type=float,
        default=0.75,
        help='Confianza mínima para considerar match (0-1)'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("DEDUPLICACIÓN DE CONTACTOS CON SPLINK")
    print("="*80 + "\n")
    
    # Cargar datos
    print(f"📂 Cargando: {args.input}")
    df_raw = pd.read_csv(args.input)
    print(f"   Total registros: {len(df_raw)}\n")
    
    # Validar columnas requeridas
    required_cols = ['nombre', 'email', 'telefono', 'empresa', 'fuente']
    missing_cols = [col for col in required_cols if col not in df_raw.columns]
    
    if missing_cols:
        print(f"❌ ERROR: Columnas faltantes: {missing_cols}")
        print(f"   Columnas disponibles: {list(df_raw.columns)}")
        return
    
    # Agregar unique_id si no existe
    if 'unique_id' not in df_raw.columns:
        df_raw['unique_id'] = df_raw.index.astype(str)
    
    # Ejecutar deduplicación
    print("🔄 Ejecutando deduplicación...")
    print(f"   Confianza mínima: {args.min_confidence}")
    print(f"   Esto puede tomar varios minutos para datasets grandes...\n")
    
    deduplicator = ContactDeduplicator()
    df_unified = deduplicator.deduplicate_contacts(df_raw)
    
    # Estadísticas
    print("\n📊 RESULTADOS:")
    print("-" * 80)
    print(f"Registros originales: {len(df_raw)}")
    print(f"Registros unificados: {len(df_unified)}")
    print(f"Duplicados eliminados: {len(df_raw) - len(df_unified)}")
    print(f"Tasa de deduplicación: {(1 - len(df_unified)/len(df_raw)):.1%}")
    
    print(f"\nContactos con múltiples fuentes:")
    multi_source = df_unified[df_unified['num_fuentes'] > 1]
    print(f"   {len(multi_source)} contactos ({len(multi_source)/len(df_unified):.1%})")
    print(f"   Promedio de fuentes: {df_unified['num_fuentes'].mean():.2f}")
    
    # Top 10 contactos con más fuentes
    print(f"\n🏆 Top 10 contactos con más fuentes:")
    top_contacts = df_unified.nlargest(10, 'num_fuentes')[['nombre', 'empresa', 'num_fuentes', 'fuentes']]
    for i, row in top_contacts.iterrows():
        print(f"   {row['nombre']} ({row['empresa']}) - {row['num_fuentes']} fuentes: {row['fuentes']}")
    
    # Guardar resultado
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df_unified.to_csv(output_path, index=False)
    print(f"\n✅ Guardado: {output_path}")
    
    # Siguiente paso
    print("\n📍 Siguiente paso:")
    print("   python scripts/load_contacts_to_neo4j.py --input", output_path)
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
