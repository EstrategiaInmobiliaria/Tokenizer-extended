"""
Carga de Contactos Unificados a Neo4j
Crea nodos de Persona, Empresa, GeoHub y relaciones
"""

import pandas as pd
import argparse
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from tqdm import tqdm
import sys

sys.path.append('/workspace/knowledge-graph')
from queries.graphrag_contact_system import CommercialScoringEngine

load_dotenv()


class Neo4jContactLoader:
    """Carga contactos unificados a Neo4j"""
    
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'password')
        
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self.scorer = CommercialScoringEngine()
    
    def close(self):
        self.driver.close()
    
    def create_constraints(self):
        """Crea constraints e índices para performance"""
        
        with self.driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT persona_id IF NOT EXISTS FOR (p:Persona) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT empresa_nombre IF NOT EXISTS FOR (e:Empresa) REQUIRE e.nombre IS UNIQUE",
                "CREATE CONSTRAINT geohub_nombre IF NOT EXISTS FOR (g:GeoHub) REQUIRE g.nombre IS UNIQUE",
                "CREATE INDEX persona_email IF NOT EXISTS FOR (p:Persona) ON (p.email)",
                "CREATE INDEX persona_nombre IF NOT EXISTS FOR (p:Persona) ON (p.nombre)",
                "CREATE INDEX persona_tier IF NOT EXISTS FOR (p:Persona) ON (p.tier)",
                "CREATE INDEX persona_score IF NOT EXISTS FOR (p:Persona) ON (p.score_comercial)"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    print(f"⚠️  {e}")
        
        print("✅ Constraints e índices creados")
    
    def load_contacts(self, df: pd.DataFrame):
        """
        Carga contactos como nodos Persona en Neo4j
        
        Calcula score comercial y asigna tier
        """
        
        print(f"\n📥 Cargando {len(df)} contactos a Neo4j...")
        
        with self.driver.session() as session:
            for _, row in tqdm(df.iterrows(), total=len(df)):
                # Calcular score comercial
                score = self.scorer.calculate_commercial_score({
                    'puesto': row.get('puesto', ''),
                    'empresa': row.get('empresa', ''),
                    'industria': row.get('industria', ''),
                    'dias_sin_contacto': row.get('dias_sin_contacto', 365)
                })
                
                # Asignar tier basado en score
                if score >= 80:
                    tier = 1
                elif score >= 50:
                    tier = 2
                else:
                    tier = 3
                
                # Crear nodo Persona
                session.execute_write(
                    self._create_persona_tx,
                    {
                        'id': row.get('entidad_unificada_id', f"CONTACT-{row.name}"),
                        'nombre': row.get('nombre'),
                        'email': row.get('email'),
                        'telefono': row.get('telefono'),
                        'empresa': row.get('empresa'),
                        'puesto': row.get('puesto'),
                        'linkedin_url': row.get('linkedin_url'),
                        'twitter_handle': row.get('twitter_handle'),
                        'whatsapp': row.get('whatsapp'),
                        'score_comercial': score,
                        'tier': tier,
                        'fuentes': str(row.get('fuentes', [])),
                        'num_fuentes': row.get('num_fuentes', 1),
                        'confianza_deduplicacion': row.get('confianza_deduplicacion', 1.0)
                    }
                )
                
                # Crear nodo Empresa si no existe
                if pd.notna(row.get('empresa')):
                    session.execute_write(
                        self._create_empresa_tx,
                        empresa_nombre=row['empresa']
                    )
                    
                    # Crear relación TRABAJA_EN
                    session.execute_write(
                        self._create_trabaja_en_tx,
                        persona_id=row.get('entidad_unificada_id', f"CONTACT-{row.name}"),
                        empresa_nombre=row['empresa']
                    )
        
        print("✅ Contactos cargados")
    
    @staticmethod
    def _create_persona_tx(tx, data):
        """Transacción: crear nodo Persona"""
        query = """
        MERGE (p:Persona {id: $id})
        SET p.nombre = $nombre,
            p.email = $email,
            p.telefono = $telefono,
            p.empresa = $empresa,
            p.puesto = $puesto,
            p.linkedin_url = $linkedin_url,
            p.twitter_handle = $twitter_handle,
            p.whatsapp = $whatsapp,
            p.score_comercial = $score_comercial,
            p.tier = $tier,
            p.fuentes = $fuentes,
            p.num_fuentes = $num_fuentes,
            p.confianza_deduplicacion = $confianza_deduplicacion,
            p.fecha_carga = datetime()
        """
        tx.run(query, **data)
    
    @staticmethod
    def _create_empresa_tx(tx, empresa_nombre):
        """Transacción: crear nodo Empresa"""
        query = """
        MERGE (e:Empresa {nombre: $nombre})
        """
        tx.run(query, nombre=empresa_nombre)
    
    @staticmethod
    def _create_trabaja_en_tx(tx, persona_id, empresa_nombre):
        """Transacción: crear relación TRABAJA_EN"""
        query = """
        MATCH (p:Persona {id: $persona_id})
        MATCH (e:Empresa {nombre: $empresa_nombre})
        MERGE (p)-[:TRABAJA_EN]->(e)
        """
        tx.run(query, persona_id=persona_id, empresa_nombre=empresa_nombre)
    
    def infer_relationships(self):
        """
        Infiere relaciones entre personas basado en datos
        
        Reglas:
        - Misma empresa → CONECTA_CON (colega)
        - Mismo dominio email → CONECTA_CON (organización)
        - LinkedIn connection → CONECTA_CON (explícito)
        """
        
        print("\n🔗 Infiriendo relaciones...")
        
        with self.driver.session() as session:
            # Regla 1: Misma empresa
            result1 = session.run("""
                MATCH (p1:Persona)-[:TRABAJA_EN]->(e:Empresa)<-[:TRABAJA_EN]-(p2:Persona)
                WHERE p1.id < p2.id
                MERGE (p1)-[r:CONECTA_CON {tipo: 'colega'}]-(p2)
                RETURN count(r) as new_connections
            """)
            count1 = result1.single()['new_connections']
            print(f"   Colegas (misma empresa): {count1}")
            
            # Regla 2: Mismo dominio de email
            result2 = session.run("""
                MATCH (p1:Persona), (p2:Persona)
                WHERE p1.id < p2.id
                  AND p1.email IS NOT NULL
                  AND p2.email IS NOT NULL
                  AND split(p1.email, '@')[1] = split(p2.email, '@')[1]
                MERGE (p1)-[r:CONECTA_CON {tipo: 'mismo_dominio'}]-(p2)
                RETURN count(r) as new_connections
            """)
            count2 = result2.single()['new_connections']
            print(f"   Mismo dominio email: {count2}")
        
        print("✅ Relaciones inferidas")
    
    def create_graph_projection(self):
        """
        Crea proyección de grafo para algoritmos GDS
        
        Necesario para PageRank, Betweenness, Community Detection
        """
        
        print("\n📊 Creando proyección de grafo...")
        
        with self.driver.session() as session:
            # Eliminar proyección previa si existe
            try:
                session.run("CALL gds.graph.drop('contactGraph', false)")
            except:
                pass
            
            # Crear nueva proyección
            session.run("""
                CALL gds.graph.project(
                    'contactGraph',
                    'Persona',
                    {
                        CONECTA_CON: {
                            orientation: 'UNDIRECTED'
                        }
                    }
                )
            """)
        
        print("✅ Proyección creada: 'contactGraph'")


def main():
    parser = argparse.ArgumentParser(
        description="Carga contactos unificados a Neo4j"
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Ruta al CSV de contactos unificados'
    )
    parser.add_argument(
        '--uri',
        type=str,
        help='Neo4j URI (default: bolt://localhost:7687)'
    )
    parser.add_argument(
        '--user',
        type=str,
        help='Neo4j user (default: neo4j)'
    )
    parser.add_argument(
        '--password',
        type=str,
        help='Neo4j password (default: from .env)'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("CARGA DE CONTACTOS A NEO4J")
    print("="*80)
    
    # Cargar datos
    print(f"\n📂 Cargando: {args.input}")
    df = pd.read_csv(args.input)
    print(f"   Total contactos: {len(df)}")
    
    # Conectar a Neo4j
    loader = Neo4jContactLoader(
        uri=args.uri,
        user=args.user,
        password=args.password
    )
    
    try:
        # 1. Crear constraints
        loader.create_constraints()
        
        # 2. Cargar contactos
        loader.load_contacts(df)
        
        # 3. Inferir relaciones
        loader.infer_relationships()
        
        # 4. Crear proyección para GDS
        loader.create_graph_projection()
        
        print("\n" + "="*80)
        print("✅ CARGA COMPLETA")
        print("="*80)
        
        print("\n📍 Siguiente paso:")
        print("   python scripts/calculate_network_metrics.py")
        
    finally:
        loader.close()


if __name__ == "__main__":
    main()
