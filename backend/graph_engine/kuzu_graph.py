"""
Motor de grafo con Kùzu - Análisis de red y detección de comunidades
"""
import os
import kuzu
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import pandas as pd
import networkx as nx
from community import community_louvain
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()
console = Console()


class KuzuGraphEngine:
    """Motor de grafo para análisis de red de contactos"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.getenv("KUZU_DB_PATH", "../data/graph/kuzu_db")
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db = kuzu.Database(str(self.db_path))
        self.conn = kuzu.Connection(self.db)
        
        self._initialize_schema()
        
        console.print(f"[green]✓ Kùzu graph database initialized at {self.db_path}[/green]")
    
    def _initialize_schema(self):
        """Crea el schema del grafo si no existe"""
        
        try:
            self.conn.execute("""
                CREATE NODE TABLE IF NOT EXISTS Contact (
                    contact_id STRING PRIMARY KEY,
                    full_name STRING,
                    company STRING,
                    title STRING,
                    tier STRING,
                    zona STRING,
                    email STRING,
                    phone STRING,
                    total_interactions INT64,
                    last_contact_date STRING
                )
            """)
            
            self.conn.execute("""
                CREATE REL TABLE IF NOT EXISTS KNOWS (
                    FROM Contact TO Contact,
                    relationship_type STRING,
                    strength DOUBLE,
                    context STRING
                )
            """)
            
            console.print("[cyan]Schema initialized[/cyan]")
            
        except Exception as e:
            console.print(f"[yellow]Schema already exists or error: {e}[/yellow]")
    
    def load_contacts_from_df(self, df: pd.DataFrame):
        """Carga contactos desde DataFrame"""
        
        console.print(f"\n[cyan]Loading {len(df)} contacts into Kùzu...[/cyan]")
        
        self.conn.execute("MATCH (c:Contact) DELETE c")
        
        for _, row in df.iterrows():
            contact_id = str(row.get('id', row.name))
            
            params = {
                'contact_id': contact_id,
                'full_name': str(row.get('full_name', '')),
                'company': str(row.get('company', '')),
                'title': str(row.get('title', '')),
                'tier': str(row.get('tier', 'Tier 3')),
                'zona': str(row.get('zona', 'Desconocida')),
                'email': str(row.get('email_primary', '')),
                'phone': str(row.get('phone_primary', '')),
                'total_interactions': int(row.get('total_interactions', 0)),
                'last_contact_date': str(row.get('last_contact_date', ''))
            }
            
            try:
                self.conn.execute("""
                    CREATE (:Contact {
                        contact_id: $contact_id,
                        full_name: $full_name,
                        company: $company,
                        title: $title,
                        tier: $tier,
                        zona: $zona,
                        email: $email,
                        phone: $phone,
                        total_interactions: $total_interactions,
                        last_contact_date: $last_contact_date
                    })
                """, params)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not insert {contact_id}: {e}[/yellow]")
        
        console.print("[green]✓ Contacts loaded[/green]")
    
    def load_relationships_from_df(self, df: pd.DataFrame):
        """Carga relaciones desde DataFrame"""
        
        console.print(f"\n[cyan]Loading {len(df)} relationships into Kùzu...[/cyan]")
        
        self.conn.execute("MATCH ()-[r:KNOWS]->() DELETE r")
        
        for _, row in df.iterrows():
            params = {
                'from_id': str(row['contact_from_id']),
                'to_id': str(row['contact_to_id']),
                'relationship_type': str(row.get('relationship_type', 'colleague')),
                'strength': float(row.get('strength', 0.5)),
                'context': str(row.get('context', ''))
            }
            
            try:
                self.conn.execute("""
                    MATCH (a:Contact {contact_id: $from_id}), (b:Contact {contact_id: $to_id})
                    CREATE (a)-[:KNOWS {
                        relationship_type: $relationship_type,
                        strength: $strength,
                        context: $context
                    }]->(b)
                """, params)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not create relationship: {e}[/yellow]")
        
        console.print("[green]✓ Relationships loaded[/green]")
    
    def query_contacts_by_criteria(
        self,
        tier: Optional[str] = None,
        zona: Optional[str] = None,
        company: Optional[str] = None,
        min_interactions: Optional[int] = None
    ) -> pd.DataFrame:
        """Query contacts with multiple filters"""
        
        query = "MATCH (c:Contact) WHERE 1=1"
        params = {}
        
        if tier:
            query += " AND c.tier = $tier"
            params['tier'] = tier
        
        if zona:
            query += " AND c.zona = $zona"
            params['zona'] = zona
        
        if company:
            query += " AND c.company CONTAINS $company"
            params['company'] = company
        
        if min_interactions is not None:
            query += " AND c.total_interactions >= $min_interactions"
            params['min_interactions'] = min_interactions
        
        query += " RETURN c.contact_id, c.full_name, c.company, c.title, c.tier, c.zona, c.total_interactions"
        
        result = self.conn.execute(query, params)
        
        columns = ['contact_id', 'full_name', 'company', 'title', 'tier', 'zona', 'total_interactions']
        data = []
        
        while result.has_next():
            row = result.get_next()
            data.append(row)
        
        return pd.DataFrame(data, columns=columns)
    
    def get_contact_network(self, contact_id: str, depth: int = 2) -> Dict:
        """Obtiene la red de un contacto hasta cierta profundidad"""
        
        query = f"""
            MATCH path = (start:Contact {{contact_id: $contact_id}})-[:KNOWS*1..{depth}]-(connected:Contact)
            RETURN DISTINCT
                connected.contact_id as contact_id,
                connected.full_name as name,
                connected.company as company,
                connected.tier as tier,
                LENGTH(path) as distance
            ORDER BY distance, connected.tier
        """
        
        result = self.conn.execute(query, {'contact_id': contact_id})
        
        network = []
        while result.has_next():
            row = result.get_next()
            network.append({
                'contact_id': row[0],
                'name': row[1],
                'company': row[2],
                'tier': row[3],
                'distance': row[4]
            })
        
        return {
            'center': contact_id,
            'network_size': len(network),
            'connections': network
        }
    
    def find_common_connections(self, contact_id1: str, contact_id2: str) -> List[Dict]:
        """Encuentra conexiones en común entre dos contactos"""
        
        query = """
            MATCH (a:Contact {contact_id: $id1})-[:KNOWS]-(common:Contact)-[:KNOWS]-(b:Contact {contact_id: $id2})
            RETURN DISTINCT
                common.contact_id as contact_id,
                common.full_name as name,
                common.company as company
        """
        
        result = self.conn.execute(query, {'id1': contact_id1, 'id2': contact_id2})
        
        connections = []
        while result.has_next():
            row = result.get_next()
            connections.append({
                'contact_id': row[0],
                'name': row[1],
                'company': row[2]
            })
        
        return connections
    
    def export_to_networkx(self) -> nx.Graph:
        """Exporta el grafo a NetworkX para análisis avanzado"""
        
        console.print("\n[cyan]Exporting to NetworkX...[/cyan]")
        
        G = nx.Graph()
        
        result = self.conn.execute("MATCH (c:Contact) RETURN c.contact_id, c.full_name, c.tier, c.zona")
        while result.has_next():
            row = result.get_next()
            G.add_node(row[0], name=row[1], tier=row[2], zona=row[3])
        
        result = self.conn.execute("""
            MATCH (a:Contact)-[r:KNOWS]->(b:Contact)
            RETURN a.contact_id, b.contact_id, r.strength
        """)
        while result.has_next():
            row = result.get_next()
            G.add_edge(row[0], row[1], weight=row[2])
        
        console.print(f"[green]✓ Exported graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges[/green]")
        
        return G
    
    def detect_communities(self) -> Dict[str, int]:
        """Detecta comunidades usando algoritmo Louvain"""
        
        console.print("\n[cyan]Detecting communities with Louvain algorithm...[/cyan]")
        
        G = self.export_to_networkx()
        
        if G.number_of_nodes() == 0:
            console.print("[yellow]No nodes to cluster[/yellow]")
            return {}
        
        partition = community_louvain.best_partition(G)
        
        num_communities = len(set(partition.values()))
        console.print(f"[green]✓ Found {num_communities} communities[/green]")
        
        for community_id in range(num_communities):
            members = [node for node, comm in partition.items() if comm == community_id]
            console.print(f"  Community {community_id}: {len(members)} members")
        
        return partition
    
    def get_central_contacts(self, limit: int = 10) -> pd.DataFrame:
        """Obtiene los contactos más centrales (más conexiones)"""
        
        query = """
            MATCH (c:Contact)-[r:KNOWS]-()
            RETURN 
                c.contact_id as contact_id,
                c.full_name as name,
                c.company as company,
                c.tier as tier,
                COUNT(r) as connection_count
            ORDER BY connection_count DESC
            LIMIT $limit
        """
        
        result = self.conn.execute(query, {'limit': limit})
        
        data = []
        while result.has_next():
            data.append(result.get_next())
        
        return pd.DataFrame(
            data,
            columns=['contact_id', 'name', 'company', 'tier', 'connection_count']
        )
    
    def close(self):
        """Cierra la conexión"""
        self.conn.close()
        console.print("[yellow]Kùzu connection closed[/yellow]")


if __name__ == "__main__":
    console.print("[red]This module should be imported, not run directly[/red]")
    console.print("Use: from kuzu_graph import KuzuGraphEngine")
