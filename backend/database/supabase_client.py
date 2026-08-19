"""
Cliente de Supabase - Operaciones CRUD para contactos
"""
import os
from typing import List, Dict, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
from rich.console import Console
import pandas as pd

load_dotenv()
console = Console()


class SupabaseContactManager:
    """Gestor de contactos en Supabase"""
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY required in .env")
        
        self.client: Client = create_client(url, key)
        console.print("[green]✓ Connected to Supabase[/green]")
    
    def upload_contacts(self, df: pd.DataFrame, batch_size: int = 100) -> int:
        """
        Sube contactos al servidor Supabase en batches
        
        Returns:
            Número de contactos insertados
        """
        console.print(f"\n[cyan]Uploading {len(df)} contacts to Supabase...[/cyan]")
        
        df = df.copy()
        
        def convert_to_array(val):
            if pd.isna(val) or val is None:
                return []
            if isinstance(val, str):
                return [v.strip() for v in val.split('|') if v.strip()]
            if isinstance(val, list):
                return val
            return []
        
        for col in ['emails', 'phones', 'addresses', 'temas']:
            if col in df.columns:
                df[col] = df[col].apply(convert_to_array)
        
        records = df.to_dict('records')
        
        inserted = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            
            try:
                result = self.client.table('contacts').insert(batch).execute()
                inserted += len(result.data)
                console.print(f"  Uploaded batch {i//batch_size + 1}: {len(batch)} contacts")
            except Exception as e:
                console.print(f"[red]Error uploading batch {i//batch_size + 1}: {e}[/red]")
        
        console.print(f"[green]✓ Successfully uploaded {inserted} contacts[/green]")
        return inserted
    
    def get_all_contacts(self) -> pd.DataFrame:
        """Obtiene todos los contactos"""
        response = self.client.table('contacts').select('*').execute()
        return pd.DataFrame(response.data)
    
    def search_contacts(
        self,
        query: str,
        tier: Optional[str] = None,
        zona: Optional[str] = None,
        limit: int = 50
    ) -> pd.DataFrame:
        """Búsqueda full-text de contactos con filtros"""
        
        try:
            result = self.client.rpc(
                'search_contacts_fulltext',
                {'search_query': query}
            ).execute()
            
            df = pd.DataFrame(result.data)
            
            if not df.empty:
                if tier:
                    df = df[df['tier'] == tier]
                if zona:
                    df = df[df['zona'] == zona]
                
                df = df.head(limit)
            
            return df
            
        except Exception as e:
            console.print(f"[yellow]Search failed: {e}[/yellow]")
            return pd.DataFrame()
    
    def get_contacts_by_tier(self, tier: str) -> pd.DataFrame:
        """Obtiene contactos por tier"""
        response = self.client.table('contacts')\
            .select('*')\
            .eq('tier', tier)\
            .execute()
        return pd.DataFrame(response.data)
    
    def get_inactive_contacts(self, days: int = 180) -> pd.DataFrame:
        """Obtiene contactos sin interacciones recientes"""
        response = self.client.table('inactive_contacts')\
            .select('*')\
            .execute()
        
        df = pd.DataFrame(response.data)
        if not df.empty and 'days_inactive' in df.columns:
            df = df[df['days_inactive'] >= days]
        
        return df
    
    def add_interaction(
        self,
        contact_id: str,
        interaction_type: str,
        content: str,
        summary: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        embedding: Optional[List[float]] = None
    ) -> Dict:
        """Registra una nueva interacción"""
        
        data = {
            'contact_id': contact_id,
            'interaction_type': interaction_type,
            'content': content,
            'summary': summary,
            'duration_seconds': duration_seconds
        }
        
        if embedding:
            data['transcript_embedding'] = embedding
        
        result = self.client.table('interactions').insert(data).execute()
        
        console.print(f"[green]✓ Interaction added for contact {contact_id}[/green]")
        return result.data[0] if result.data else {}
    
    def get_contact_interactions(self, contact_id: str) -> pd.DataFrame:
        """Obtiene todas las interacciones de un contacto"""
        response = self.client.table('interactions')\
            .select('*')\
            .eq('contact_id', contact_id)\
            .order('interaction_date', desc=True)\
            .execute()
        
        return pd.DataFrame(response.data)
    
    def add_relationship(
        self,
        from_id: str,
        to_id: str,
        relationship_type: str = 'colleague',
        strength: float = 0.5,
        context: Optional[str] = None
    ) -> Dict:
        """Crea una relación entre dos contactos"""
        
        data = {
            'contact_from_id': from_id,
            'contact_to_id': to_id,
            'relationship_type': relationship_type,
            'strength': strength,
            'context': context,
            'source': 'manual'
        }
        
        result = self.client.table('relationships').insert(data).execute()
        return result.data[0] if result.data else {}
    
    def get_contact_network(self, contact_id: str) -> Dict:
        """Obtiene la red de conexiones de un contacto"""
        
        outgoing = self.client.table('relationships')\
            .select('contact_to_id, relationship_type, strength')\
            .eq('contact_from_id', contact_id)\
            .execute()
        
        incoming = self.client.table('relationships')\
            .select('contact_from_id, relationship_type, strength')\
            .eq('contact_to_id', contact_id)\
            .execute()
        
        return {
            'outgoing': outgoing.data,
            'incoming': incoming.data,
            'total_connections': len(outgoing.data) + len(incoming.data)
        }
    
    def semantic_search_interactions(
        self,
        query_embedding: List[float],
        threshold: float = 0.7,
        limit: int = 10
    ) -> pd.DataFrame:
        """Búsqueda semántica de interacciones por embedding"""
        
        try:
            result = self.client.rpc(
                'search_interactions_by_embedding',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold,
                    'match_count': limit
                }
            ).execute()
            
            return pd.DataFrame(result.data)
            
        except Exception as e:
            console.print(f"[yellow]Semantic search failed: {e}[/yellow]")
            return pd.DataFrame()


if __name__ == "__main__":
    console.print("[red]This module should be imported, not run directly[/red]")
    console.print("Use: from supabase_client import SupabaseContactManager")
