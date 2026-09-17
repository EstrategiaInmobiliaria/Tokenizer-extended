"""
Cálculo de Métricas de Red en Neo4j
PageRank, Betweenness Centrality, Community Detection
"""

import argparse
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


class NetworkMetricsCalculator:
    """Calcula métricas de red usando Neo4j Graph Data Science"""
    
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'password')
        
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    
    def close(self):
        self.driver.close()
    
    def calculate_pagerank(self):
        """
        Calcula PageRank para identificar contactos más influyentes
        
        PageRank mide la "importancia" de un nodo basado en:
        - Cantidad de conexiones entrantes
        - Calidad de esas conexiones (conectados a otros nodos importantes)
        """
        
        print("\n📊 Calculando PageRank...")
        
        with self.driver.session() as session:
            result = session.run("""
                CALL gds.pageRank.write('contactGraph', {
                    writeProperty: 'pageRank',
                    maxIterations: 20,
                    dampingFactor: 0.85
                })
                YIELD nodePropertiesWritten, ranIterations
                RETURN nodePropertiesWritten, ranIterations
            """)
            
            record = result.single()
            print(f"   ✅ {record['nodePropertiesWritten']} nodos actualizados")
            print(f"   Iteraciones: {record['ranIterations']}")
            
            # Top 10 influencers
            top_influencers = session.run("""
                MATCH (p:Persona)
                WHERE p.pageRank IS NOT NULL
                RETURN p.nombre as nombre, 
                       p.empresa as empresa, 
                       p.pageRank as pagerank,
                       p.score_comercial as score
                ORDER BY p.pageRank DESC
                LIMIT 10
            """)
            
            print("\n   🏆 Top 10 Influencers (PageRank):")
            for i, record in enumerate(top_influencers, 1):
                print(f"   {i}. {record['nombre']} ({record['empresa']}) - "
                      f"PageRank: {record['pagerank']:.4f}, Score: {record['score']:.1f}")
    
    def calculate_betweenness_centrality(self):
        """
        Calcula Betweenness Centrality para identificar "conectores"
        
        Betweenness mide cuántos caminos más cortos pasan por un nodo.
        Contactos con alto betweenness son "puentes" entre comunidades.
        """
        
        print("\n🌉 Calculando Betweenness Centrality...")
        
        with self.driver.session() as session:
            result = session.run("""
                CALL gds.betweenness.write('contactGraph', {
                    writeProperty: 'betweennessCentrality'
                })
                YIELD nodePropertiesWritten, computeMillis
                RETURN nodePropertiesWritten, computeMillis
            """)
            
            record = result.single()
            print(f"   ✅ {record['nodePropertiesWritten']} nodos actualizados")
            print(f"   Tiempo: {record['computeMillis']/1000:.2f}s")
            
            # Top 10 connectors
            top_connectors = session.run("""
                MATCH (p:Persona)
                WHERE p.betweennessCentrality IS NOT NULL
                RETURN p.nombre as nombre, 
                       p.empresa as empresa, 
                       p.betweennessCentrality as betweenness,
                       size((p)-[:CONECTA_CON]-()) as num_conexiones
                ORDER BY p.betweennessCentrality DESC
                LIMIT 10
            """)
            
            print("\n   🔗 Top 10 Conectores (Betweenness):")
            for i, record in enumerate(top_connectors, 1):
                print(f"   {i}. {record['nombre']} ({record['empresa']}) - "
                      f"Betweenness: {record['betweenness']:.2f}, "
                      f"Conexiones: {record['num_conexiones']}")
    
    def detect_communities(self, algorithm='leiden'):
        """
        Detecta comunidades usando Leiden o Louvain
        
        Comunidades = grupos densamente conectados de contactos
        Útil para:
        - Identificar clústeres profesionales
        - Segmentar red por industria/geografía
        - Detectar "silos" organizacionales
        """
        
        print(f"\n🎯 Detectando comunidades ({algorithm})...")
        
        algo_call = {
            'leiden': 'gds.leiden',
            'louvain': 'gds.louvain'
        }[algorithm]
        
        with self.driver.session() as session:
            result = session.run(f"""
                CALL {algo_call}.write('contactGraph', {{
                    writeProperty: 'comunidad_id',
                    includeIntermediateCommunities: false
                }})
                YIELD communityCount, modularity, nodePropertiesWritten
                RETURN communityCount, modularity, nodePropertiesWritten
            """)
            
            record = result.single()
            print(f"   ✅ {record['communityCount']} comunidades detectadas")
            print(f"   Modularidad: {record['modularity']:.4f}")
            print(f"   Nodos: {record['nodePropertiesWritten']}")
            
            # Estadísticas de comunidades
            community_stats = session.run("""
                MATCH (p:Persona)
                WHERE p.comunidad_id IS NOT NULL
                WITH p.comunidad_id as comunidad, 
                     count(*) as size,
                     avg(p.score_comercial) as avg_score,
                     collect(p.empresa)[..5] as sample_empresas
                ORDER BY size DESC
                LIMIT 10
                RETURN comunidad, size, avg_score, sample_empresas
            """)
            
            print("\n   📦 Top 10 Comunidades:")
            for i, record in enumerate(community_stats, 1):
                empresas_str = ', '.join(set([e for e in record['sample_empresas'] if e]))
                print(f"   {i}. Comunidad {record['comunidad']}: "
                      f"{record['size']} miembros, "
                      f"Score promedio: {record['avg_score']:.1f}")
                print(f"      Empresas: {empresas_str}")
    
    def calculate_degree_centrality(self):
        """
        Calcula Degree Centrality (número de conexiones directas)
        
        Simples pero útiles: contactos con más conexiones directas
        """
        
        print("\n📈 Calculando Degree Centrality...")
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Persona)
                SET p.degree = size((p)-[:CONECTA_CON]-())
                RETURN count(p) as updated
            """)
            
            count = result.single()['updated']
            print(f"   ✅ {count} nodos actualizados")
            
            # Top 10 por conexiones
            top_degree = session.run("""
                MATCH (p:Persona)
                RETURN p.nombre as nombre,
                       p.empresa as empresa,
                       p.degree as conexiones,
                       p.tier as tier
                ORDER BY p.degree DESC
                LIMIT 10
            """)
            
            print("\n   🌐 Top 10 por Conexiones Directas:")
            for i, record in enumerate(top_degree, 1):
                print(f"   {i}. {record['nombre']} ({record['empresa']}) - "
                      f"{record['conexiones']} conexiones (Tier {record['tier']})")
    
    def export_metrics(self, output_path='/workspace/knowledge-graph/data/network_metrics.csv'):
        """Exporta métricas a CSV para análisis"""
        
        print(f"\n💾 Exportando métricas a {output_path}...")
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Persona)
                RETURN p.id as id,
                       p.nombre as nombre,
                       p.empresa as empresa,
                       p.tier as tier,
                       p.score_comercial as score_comercial,
                       p.pageRank as pagerank,
                       p.betweennessCentrality as betweenness,
                       p.degree as degree,
                       p.comunidad_id as comunidad
                ORDER BY p.score_comercial DESC
            """)
            
            df = pd.DataFrame([dict(record) for record in result])
            df.to_csv(output_path, index=False)
            
            print(f"   ✅ {len(df)} registros exportados")
    
    def create_tier1_subgraph(self):
        """
        Crea subgrafo solo de Tier 1 (decisores C-Level)
        
        Útil para análisis de alto valor
        """
        
        print("\n👑 Creando subgrafo Tier 1...")
        
        with self.driver.session() as session:
            # Eliminar proyección previa si existe
            try:
                session.run("CALL gds.graph.drop('tier1Graph', false)")
            except:
                pass
            
            result = session.run("""
                CALL gds.graph.project(
                    'tier1Graph',
                    {
                        Persona: {
                            properties: ['tier', 'score_comercial']
                        }
                    },
                    {
                        CONECTA_CON: {
                            orientation: 'UNDIRECTED'
                        }
                    },
                    {
                        nodeFilter: 'n.tier = 1'
                    }
                )
                YIELD nodeCount, relationshipCount
                RETURN nodeCount, relationshipCount
            """)
            
            record = result.single()
            print(f"   ✅ Subgrafo creado:")
            print(f"      Nodos Tier 1: {record['nodeCount']}")
            print(f"      Relaciones: {record['relationshipCount']}")


def main():
    parser = argparse.ArgumentParser(
        description="Calcula métricas de red en Neo4j"
    )
    parser.add_argument(
        '--algorithm',
        choices=['leiden', 'louvain'],
        default='leiden',
        help='Algoritmo para community detection'
    )
    parser.add_argument(
        '--export',
        type=str,
        default='/workspace/knowledge-graph/data/network_metrics.csv',
        help='Ruta para exportar métricas'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("CÁLCULO DE MÉTRICAS DE RED")
    print("="*80)
    
    calculator = NetworkMetricsCalculator()
    
    try:
        # 1. PageRank (influencers)
        calculator.calculate_pagerank()
        
        # 2. Betweenness Centrality (connectors)
        calculator.calculate_betweenness_centrality()
        
        # 3. Community Detection
        calculator.detect_communities(algorithm=args.algorithm)
        
        # 4. Degree Centrality
        calculator.calculate_degree_centrality()
        
        # 5. Export metrics
        calculator.export_metrics(output_path=args.export)
        
        # 6. Create Tier 1 subgraph
        calculator.create_tier1_subgraph()
        
        print("\n" + "="*80)
        print("✅ MÉTRICAS CALCULADAS")
        print("="*80)
        
        print("\n📊 Análisis disponibles:")
        print("   - PageRank: Identifica influencers globales")
        print("   - Betweenness: Identifica conectores entre comunidades")
        print("   - Communities: Clústeres profesionales detectados")
        print("   - Degree: Contactos con más conexiones directas")
        
        print("\n📍 Siguiente paso:")
        print("   python scripts/generate_embeddings.py")
        
    finally:
        calculator.close()


if __name__ == "__main__":
    main()
