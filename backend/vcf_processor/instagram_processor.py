"""
Procesador de exportaciones de Instagram - JSON oficial
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()


class InstagramProcessor:
    """
    Procesa el export JSON oficial de Instagram
    
    Para obtener los datos:
    1. Ve a Instagram → Configuración → Tu actividad
    2. Descargar tu información
    3. Selecciona "Descargar o transferir información"
    4. Formato JSON
    5. Espera el email de Instagram (puede tardar días)
    6. Extrae el ZIP y busca:
       - followers_1.json
       - following.json
       - recent_follow_requests.json
    """
    
    def __init__(self):
        self.following = []
        self.followers = []
        self.data_path = None
    
    def load_json_export(self, export_path: Path):
        """
        Carga el export completo de Instagram
        
        Args:
            export_path: Directorio raíz del export descomprimido
        """
        console.print(f"\n[cyan]Loading Instagram export from:[/cyan] {export_path}")
        
        self.data_path = export_path
        
        following_paths = [
            export_path / "connections" / "followers_and_following" / "following.json",
            export_path / "following.json"
        ]
        
        followers_paths = [
            export_path / "connections" / "followers_and_following" / "followers_1.json",
            export_path / "followers.json",
            export_path / "followers_1.json"
        ]
        
        for path in following_paths:
            if path.exists():
                self.following = self._load_following_file(path)
                console.print(f"[green]✓ Loaded {len(self.following)} following[/green]")
                break
        
        for path in followers_paths:
            if path.exists():
                self.followers = self._load_followers_file(path)
                console.print(f"[green]✓ Loaded {len(self.followers)} followers[/green]")
                break
        
        if not self.following and not self.followers:
            console.print("[yellow]Warning: No Instagram data found[/yellow]")
            console.print("Expected structure: connections/followers_and_following/*.json")
    
    def _load_following_file(self, path: Path) -> List[Dict]:
        """Carga el archivo de following"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict) and 'relationships_following' in data:
                return data['relationships_following']
            elif isinstance(data, list):
                return data
            else:
                console.print(f"[yellow]Unexpected format in {path}[/yellow]")
                return []
        except Exception as e:
            console.print(f"[red]Error loading {path}: {e}[/red]")
            return []
    
    def _load_followers_file(self, path: Path) -> List[Dict]:
        """Carga el archivo de followers"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                if 'relationships_followers' in data:
                    return data['relationships_followers']
                elif any(k.startswith('relationships') for k in data.keys()):
                    key = [k for k in data.keys() if k.startswith('relationships')][0]
                    return data[key]
            
            console.print(f"[yellow]Unexpected format in {path}[/yellow]")
            return []
        except Exception as e:
            console.print(f"[red]Error loading {path}: {e}[/red]")
            return []
    
    def get_mutual_follows(self) -> List[str]:
        """Encuentra usuarios que sigues y te siguen (conexiones mutuas)"""
        
        following_usernames = {
            item.get('string_list_data', [{}])[0].get('value', '')
            for item in self.following
        }
        
        follower_usernames = {
            item.get('string_list_data', [{}])[0].get('value', '')
            for item in self.followers
        }
        
        mutual = following_usernames & follower_usernames
        mutual = [u for u in mutual if u]
        
        console.print(f"\n[green]Found {len(mutual)} mutual connections[/green]")
        
        return sorted(mutual)
    
    def normalize_to_contacts(self) -> pd.DataFrame:
        """Convierte datos de Instagram a formato de contactos"""
        
        console.print("\n[cyan]Normalizing Instagram data...[/cyan]")
        
        contacts = []
        
        mutual = set(self.get_mutual_follows())
        
        processed_usernames = set()
        
        for item in self.following:
            username = item.get('string_list_data', [{}])[0].get('value', '')
            timestamp = item.get('string_list_data', [{}])[0].get('timestamp', None)
            
            if username and username not in processed_usernames:
                processed_usernames.add(username)
                
                contact = {
                    'full_name': username,
                    'first_name': None,
                    'last_name': None,
                    'company': None,
                    'title': None,
                    'email_primary': None,
                    'phone_primary': None,
                    'emails': None,
                    'phones': None,
                    'addresses': None,
                    'notes': f"Instagram: @{username}" + (
                        " (mutual follow)" if username in mutual else " (following only)"
                    ),
                    'source': 'instagram',
                    'instagram_username': username,
                    'is_mutual_follow': username in mutual
                }
                
                if timestamp:
                    contact['last_contact_date'] = pd.to_datetime(timestamp, unit='s')
                
                contacts.append(contact)
        
        df = pd.DataFrame(contacts)
        
        console.print(f"[green]✓ Normalized {len(df)} Instagram contacts[/green]")
        console.print(f"  • Mutual follows: {df['is_mutual_follow'].sum()}")
        console.print(f"  • Following only: {(~df['is_mutual_follow']).sum()}")
        
        return df
    
    def categorize_by_engagement(self) -> pd.DataFrame:
        """
        Categoriza contactos por tipo de engagement
        (Requiere datos adicionales del export)
        """
        
        df = self.normalize_to_contacts()
        
        df['tier'] = 'Tier 3'
        
        df.loc[df['is_mutual_follow'] == True, 'tier'] = 'Tier 2'
        
        return df
    
    def export_for_upload(self, output_path: Optional[Path] = None) -> pd.DataFrame:
        """Exporta en formato listo para subir"""
        
        df = self.normalize_to_contacts()
        
        df = df.drop(columns=['instagram_username', 'is_mutual_follow'], errors='ignore')
        
        if output_path:
            df.to_csv(output_path, index=False)
            console.print(f"\n[green]✓ Exported to: {output_path}[/green]")
        
        return df
    
    def show_stats(self):
        """Muestra estadísticas del export"""
        
        table = Table(title="Instagram Network Stats")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green", justify="right")
        
        table.add_row("Following", str(len(self.following)))
        table.add_row("Followers", str(len(self.followers)))
        
        mutual = self.get_mutual_follows()
        table.add_row("Mutual Follows", str(len(mutual)))
        
        following_only = len(self.following) - len(mutual)
        table.add_row("Following Only", str(following_only))
        
        followers_only = len(self.followers) - len(mutual)
        table.add_row("Followers Only", str(followers_only))
        
        console.print("\n")
        console.print(table)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        console.print("[red]Usage: python instagram_processor.py <instagram_export_folder>[/red]")
        console.print("\nTo get your Instagram data:")
        console.print("1. Instagram → Settings → Your Activity")
        console.print("2. Download Your Information")
        console.print("3. Select JSON format")
        console.print("4. Wait for email (can take days)")
        console.print("5. Extract ZIP and pass folder path here")
        sys.exit(1)
    
    export_path = Path(sys.argv[1])
    
    if not export_path.exists():
        console.print(f"[red]Folder not found: {export_path}[/red]")
        sys.exit(1)
    
    processor = InstagramProcessor()
    processor.load_json_export(export_path)
    
    processor.show_stats()
    
    output = Path("instagram_contacts_normalized.csv")
    processor.export_for_upload(output)
