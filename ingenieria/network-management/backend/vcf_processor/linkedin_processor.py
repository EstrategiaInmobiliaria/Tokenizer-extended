"""
Procesador de exportaciones de LinkedIn - Conexiones CSV
"""
import pandas as pd
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table

console = Console()


class LinkedInProcessor:
    """
    Procesa el CSV de conexiones exportado desde LinkedIn
    
    Para obtener el CSV:
    1. Ve a LinkedIn → Configuración y Privacidad
    2. Privacidad de datos → Obtener una copia de tus datos
    3. Selecciona "Conexiones" y descarga
    4. Extrae el archivo Connections.csv
    """
    
    CSV_COLUMNS = [
        'First Name',
        'Last Name', 
        'Email Address',
        'Company',
        'Position',
        'Connected On'
    ]
    
    def __init__(self):
        self.connections = None
    
    def load_csv(self, csv_path: Path) -> pd.DataFrame:
        """Carga el CSV de conexiones de LinkedIn"""
        
        console.print(f"\n[cyan]Loading LinkedIn connections from:[/cyan] {csv_path}")
        
        try:
            df = pd.read_csv(csv_path, skiprows=3)
        except Exception:
            df = pd.read_csv(csv_path)
        
        console.print(f"[green]✓ Loaded {len(df)} connections[/green]")
        
        self.connections = df
        return df
    
    def normalize_to_contacts(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Convierte formato LinkedIn a formato de contactos estándar"""
        
        if df is None:
            df = self.connections
        
        if df is None:
            raise ValueError("No data loaded. Call load_csv() first.")
        
        console.print("\n[cyan]Normalizing LinkedIn data...[/cyan]")
        
        normalized = pd.DataFrame()
        
        normalized['first_name'] = df.get('First Name', '')
        normalized['last_name'] = df.get('Last Name', '')
        
        normalized['full_name'] = (
            df.get('First Name', '').fillna('') + ' ' + 
            df.get('Last Name', '').fillna('')
        ).str.strip()
        
        normalized['company'] = df.get('Company', '')
        normalized['title'] = df.get('Position', '')
        
        normalized['email_primary'] = df.get('Email Address', '')
        
        normalized['phone_primary'] = None
        normalized['phones'] = None
        normalized['emails'] = df.get('Email Address', '').apply(
            lambda x: x if pd.notna(x) else ''
        )
        normalized['addresses'] = None
        
        if 'Connected On' in df.columns:
            normalized['last_contact_date'] = pd.to_datetime(
                df['Connected On'],
                errors='coerce'
            )
        
        normalized['notes'] = 'Imported from LinkedIn on ' + pd.Timestamp.now().strftime('%Y-%m-%d')
        normalized['source'] = 'linkedin'
        
        normalized = normalized[normalized['full_name'].str.strip() != '']
        
        console.print(f"[green]✓ Normalized {len(normalized)} contacts[/green]")
        
        return normalized
    
    def get_top_companies(self, limit: int = 20) -> pd.DataFrame:
        """Obtiene las empresas con más conexiones"""
        
        if self.connections is None:
            raise ValueError("No data loaded")
        
        company_counts = self.connections['Company'].value_counts().head(limit)
        
        table = Table(title=f"Top {limit} Companies in Your Network")
        table.add_column("Company", style="cyan")
        table.add_column("Connections", style="green", justify="right")
        
        for company, count in company_counts.items():
            if pd.notna(company) and company:
                table.add_row(str(company), str(count))
        
        console.print(table)
        
        return pd.DataFrame({
            'company': company_counts.index,
            'count': company_counts.values
        })
    
    def get_connections_by_date(self) -> pd.DataFrame:
        """Analiza conexiones por fecha"""
        
        if self.connections is None or 'Connected On' not in self.connections.columns:
            console.print("[yellow]No date information available[/yellow]")
            return pd.DataFrame()
        
        df = self.connections.copy()
        df['Connected On'] = pd.to_datetime(df['Connected On'], errors='coerce')
        
        df = df.dropna(subset=['Connected On'])
        
        df['Year'] = df['Connected On'].dt.year
        df['Month'] = df['Connected On'].dt.to_period('M')
        
        by_year = df['Year'].value_counts().sort_index()
        
        console.print("\n[cyan]Connections by Year:[/cyan]")
        for year, count in by_year.items():
            console.print(f"  {year}: {count} connections")
        
        return df
    
    def export_for_upload(self, output_path: Optional[Path] = None) -> pd.DataFrame:
        """Exporta en formato listo para subir a Supabase"""
        
        df_normalized = self.normalize_to_contacts()
        
        if output_path:
            df_normalized.to_csv(output_path, index=False)
            console.print(f"\n[green]✓ Exported to: {output_path}[/green]")
        
        return df_normalized


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        console.print("[red]Usage: python linkedin_processor.py <Connections.csv>[/red]")
        console.print("\nTo get your LinkedIn connections CSV:")
        console.print("1. Go to LinkedIn → Settings & Privacy")
        console.print("2. Data Privacy → Get a copy of your data")
        console.print("3. Select 'Connections' and download")
        sys.exit(1)
    
    csv_path = Path(sys.argv[1])
    
    if not csv_path.exists():
        console.print(f"[red]File not found: {csv_path}[/red]")
        sys.exit(1)
    
    processor = LinkedInProcessor()
    processor.load_csv(csv_path)
    
    processor.get_top_companies(limit=20)
    processor.get_connections_by_date()
    
    output = csv_path.parent / "linkedin_contacts_normalized.csv"
    processor.export_for_upload(output)
