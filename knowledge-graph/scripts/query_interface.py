"""
Query Interface for Kùzu Contact Graph
Simple CLI para consultas comunes sin escribir SQL
"""

import kuzu
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional

class ContactQueryInterface:
    """Interfaz simplificada para consultas comunes"""
    
    def __init__(self, db_path: str):
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)
        print(f"✅ Conectado a: {db_path}\n")
    
    def tier1_in_zone(self, zona: str = "CDMX", limit: int = 20):
        """Tier 1 (decisores) en una zona específica"""
        
        print(f"🔍 Buscando Tier 1 en {zona}...\n")
        
        result = self.conn.execute(f"""
            MATCH (p:Persona)
            WHERE p.tier = 1 AND p.zona = '{zona}'
            RETURN p.nombre as nombre,
                   p.empresa as empresa,
                   p.puesto as puesto,
                   p.score_estimado as score
            ORDER BY p.score_estimado DESC
            LIMIT {limit}
        """)
        
        df = result.get_as_df()
        
        if len(df) == 0:
            print(f"❌ No se encontraron Tier 1 en {zona}")
            return
        
        print(f"📊 Encontrados {len(df)} contactos Tier 1 en {zona}:\n")
        print(df.to_string(index=False))
        print()
    
    def experts_in_tema(self, tema: str, min_tier: int = 2, limit: int = 20):
        """Expertos en un tema específico"""
        
        print(f"🔍 Buscando expertos en {tema} (Tier ≤{min_tier})...\n")
        
        result = self.conn.execute(f"""
            MATCH (p:Persona)
            WHERE p.tema = '{tema}' AND p.tier <= {min_tier}
            RETURN p.nombre as nombre,
                   p.empresa as empresa,
                   p.puesto as puesto,
                   p.zona as zona,
                   p.score_estimado as score
            ORDER BY p.score_estimado DESC
            LIMIT {limit}
        """)
        
        df = result.get_as_df()
        
        if len(df) == 0:
            print(f"❌ No se encontraron expertos en {tema}")
            return
        
        print(f"📊 Encontrados {len(df)} expertos en {tema}:\n")
        print(df.to_string(index=False))
        print()
    
    def contacts_not_seen_in(self, months: int = 6, min_tier: int = 2, zona: Optional[str] = None, limit: int = 20):
        """Contactos sin interacción reciente"""
        
        zona_filter = f"AND p.zona = '{zona}'" if zona else ""
        zona_text = f" en {zona}" if zona else ""
        
        print(f"🔍 Buscando contactos sin ver en {months} meses{zona_text} (Tier ≤{min_tier})...\n")
        
        # Calcular fecha hace N meses
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
        
        result = self.conn.execute(f"""
            MATCH (p:Persona)
            WHERE p.tier <= {min_tier}
              {zona_filter}
              AND (p.ultima_interaccion IS NULL OR p.ultima_interaccion < '{cutoff_str}')
            RETURN p.nombre as nombre,
                   p.empresa as empresa,
                   p.telefono as telefono,
                   p.zona as zona,
                   p.ultima_interaccion as ultima_vez,
                   p.score_estimado as score
            ORDER BY p.score_estimado DESC
            LIMIT {limit}
        """)
        
        df = result.get_as_df()
        
        if len(df) == 0:
            print(f"✅ Todos tus contactos Tier {min_tier} están al día!")
            return
        
        print(f"📊 Encontrados {len(df)} contactos sin ver en {months} meses{zona_text}:\n")
        print(df.to_string(index=False))
        print()
    
    def introduction_path(self, target_name: str):
        """Encuentra ruta de introducción a un contacto"""
        
        print(f"🔍 Buscando ruta de introducción a {target_name}...\n")
        
        # Buscar contacto por nombre (fuzzy)
        result = self.conn.execute(f"""
            MATCH (target:Persona)
            WHERE target.nombre LIKE '%{target_name}%'
            RETURN target.nombre as nombre,
                   target.empresa as empresa
            LIMIT 5
        """)
        
        matches = result.get_as_df()
        
        if len(matches) == 0:
            print(f"❌ No se encontró contacto con nombre similar a '{target_name}'")
            return
        
        if len(matches) > 1:
            print("🤔 Múltiples matches encontrados:")
            print(matches.to_string(index=False))
            print("\nEspecifica el nombre completo.\n")
            return
        
        target = matches.iloc[0]['nombre']
        
        # Buscar ruta (2 grados máximo)
        # Nota: Kùzu no tiene shortestPath nativo como Neo4j
        # Simulamos con 2 hops
        result = self.conn.execute(f"""
            MATCH (me:Persona {{nombre: 'Jaime Wilk'}})
                  -[:CONECTA_CON]-(puente:Persona)
                  -[:CONECTA_CON]-(target:Persona {{nombre: '{target}'}})
            RETURN DISTINCT puente.nombre as introductor,
                   puente.empresa as empresa_introductor,
                   puente.telefono as telefono
            LIMIT 5
        """)
        
        df = result.get_as_df()
        
        if len(df) == 0:
            print(f"❌ No se encontró ruta de introducción a {target} (máximo 2 grados)")
            print("   Intenta contacto directo o busca otro intermediario.\n")
            return
        
        print(f"✅ Rutas de introducción a {target}:\n")
        for i, row in df.iterrows():
            print(f"   {i+1}. Vía {row['introductor']} ({row['empresa_introductor']})")
            print(f"      Tel: {row['telefono']}\n")
    
    def top_contacts(self, limit: int = 20):
        """Top contactos por score"""
        
        print(f"🔍 Top {limit} contactos por score estimado...\n")
        
        result = self.conn.execute(f"""
            MATCH (p:Persona)
            WHERE p.tier <= 2
            RETURN p.nombre as nombre,
                   p.empresa as empresa,
                   p.puesto as puesto,
                   p.tema as tema,
                   p.zona as zona,
                   p.score_estimado as score
            ORDER BY p.score_estimado DESC
            LIMIT {limit}
        """)
        
        df = result.get_as_df()
        
        print(f"📊 Top {len(df)} contactos de alto valor:\n")
        print(df.to_string(index=False))
        print()
    
    def stats(self):
        """Estadísticas generales del grafo"""
        
        print("📊 ESTADÍSTICAS DEL GRAFO")
        print("="*70 + "\n")
        
        # Total
        result = self.conn.execute("MATCH (p:Persona) RETURN COUNT(*) as total")
        total = result.get_next()[0]
        print(f"Total contactos: {total:,}\n")
        
        # Por tier
        result = self.conn.execute("""
            MATCH (p:Persona)
            RETURN p.tier as tier, COUNT(*) as count
            ORDER BY tier
        """)
        print("Por Tier:")
        for row in result.get_as_df().itertuples():
            pct = row.count / total * 100
            print(f"  Tier {row.tier}: {row.count:,} ({pct:.1f}%)")
        
        # Top temas
        result = self.conn.execute("""
            MATCH (p:Persona)
            WHERE p.tier <= 2
            RETURN p.tema as tema, COUNT(*) as count
            ORDER BY count DESC
            LIMIT 10
        """)
        print("\nTop 10 Temas (Tier 1-2):")
        for row in result.get_as_df().itertuples():
            print(f"  {row.tema}: {row.count:,}")
        
        # Top zonas
        result = self.conn.execute("""
            MATCH (p:Persona)
            WHERE p.tier <= 2
            RETURN p.zona as zona, COUNT(*) as count
            ORDER BY count DESC
            LIMIT 10
        """)
        print("\nTop 10 Zonas (Tier 1-2):")
        for row in result.get_as_df().itertuples():
            print(f"  {row.zona}: {row.count:,}")
        
        print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(
        description="Query Interface for Kùzu Contact Graph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Tier 1 en CDMX
  python query_interface.py --db ./output/contact_graph_db --tier1 --zona CDMX

  # Expertos en ESG
  python query_interface.py --db ./output/contact_graph_db --expertos ESG

  # Contactos sin ver en 6 meses en Monterrey
  python query_interface.py --db ./output/contact_graph_db --no-vistos 6 --zona Monterrey

  # Ruta de introducción
  python query_interface.py --db ./output/contact_graph_db --intro "Juan López"

  # Top 20 contactos
  python query_interface.py --db ./output/contact_graph_db --top 20

  # Estadísticas
  python query_interface.py --db ./output/contact_graph_db --stats
        """
    )
    
    parser.add_argument(
        '--db',
        type=str,
        required=True,
        help='Path to Kùzu database directory'
    )
    
    # Queries
    parser.add_argument('--tier1', action='store_true', help='Tier 1 contacts')
    parser.add_argument('--expertos', type=str, help='Experts in tema (e.g., ESG, Inmobiliario)')
    parser.add_argument('--no-vistos', type=int, metavar='MONTHS', help='Contacts not seen in N months')
    parser.add_argument('--intro', type=str, metavar='NAME', help='Introduction path to contact')
    parser.add_argument('--top', type=int, metavar='N', help='Top N contacts by score')
    parser.add_argument('--stats', action='store_true', help='Graph statistics')
    
    # Filters
    parser.add_argument('--zona', type=str, help='Filter by zona (e.g., CDMX, Monterrey)')
    parser.add_argument('--min-tier', type=int, default=2, help='Minimum tier (default: 2)')
    parser.add_argument('--limit', type=int, default=20, help='Result limit (default: 20)')
    
    args = parser.parse_args()
    
    # Create interface
    qi = ContactQueryInterface(db_path=args.db)
    
    # Execute queries
    if args.stats:
        qi.stats()
    
    if args.tier1:
        zona = args.zona or "CDMX"
        qi.tier1_in_zone(zona=zona, limit=args.limit)
    
    if args.expertos:
        qi.experts_in_tema(tema=args.expertos, min_tier=args.min_tier, limit=args.limit)
    
    if args.no_vistos:
        qi.contacts_not_seen_in(months=args.no_vistos, min_tier=args.min_tier, zona=args.zona, limit=args.limit)
    
    if args.intro:
        qi.introduction_path(target_name=args.intro)
    
    if args.top:
        qi.top_contacts(limit=args.top)
    
    # If no query specified, show stats
    if not any([args.stats, args.tier1, args.expertos, args.no_vistos, args.intro, args.top]):
        print("⚠️  No query specified. Showing stats:\n")
        qi.stats()


if __name__ == "__main__":
    main()
