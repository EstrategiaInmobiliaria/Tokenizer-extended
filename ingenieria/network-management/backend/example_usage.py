#!/usr/bin/env python3
"""
Ejemplos de uso del sistema - Testing rápido

IMPORTANTE: Asegúrate de tener configurado .env antes de ejecutar
"""
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def show_example(title: str, code: str, description: str):
    """Muestra un ejemplo con formato"""
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]{title}[/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
    
    console.print(f"[yellow]{description}[/yellow]\n")
    
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Código", border_style="green"))


def main():
    console.print("\n[bold green]Sistema de Gestión de Red de Contactos - Ejemplos[/bold green]\n")
    
    show_example(
        "1. Procesar VCF Completo",
        """# Procesar archivo VCF con clasificación GPT
python main_pipeline.py --vcf /path/to/contacts.vcf

# Procesar sin clasificación (más rápido)
python main_pipeline.py --vcf /path/to/contacts.vcf --skip-classification

# Procesar directorio con múltiples VCFs
python main_pipeline.py --vcf /path/to/vcf_folder/""",
        "Pipeline completo: Parse → Deduplicate → Classify → Upload → Build Graph"
    )
    
    show_example(
        "2. Procesar LinkedIn",
        """# Descargar Connections.csv de LinkedIn primero
# LinkedIn → Settings → Get a copy of your data → Connections

python main_pipeline.py --linkedin /path/to/Connections.csv""",
        "Importa conexiones de LinkedIn con análisis de empresas"
    )
    
    show_example(
        "3. Procesar Instagram",
        """# Solicitar export de Instagram primero (tarda 2-48h)
# Instagram → Settings → Download Your Information → JSON

python main_pipeline.py --instagram /path/to/instagram_export/""",
        "Procesa following/followers con detección de mutual follows"
    )
    
    show_example(
        "4. Análisis de Red",
        """# Ver estadísticas completas y detectar comunidades
python main_pipeline.py --analyze""",
        "Análisis completo: distribución Tier/Zona, comunidades, contactos centrales"
    )
    
    show_example(
        "5. Búsqueda de Contactos",
        """from database.supabase_client import SupabaseContactManager

sb = SupabaseContactManager()

# Búsqueda full-text
results = sb.search_contacts(
    query="sustentabilidad inmobiliaria",
    tier="Tier 1",
    zona="Monterrey",
    limit=20
)

print(results[['full_name', 'company', 'title']])""",
        "Buscar contactos con filtros múltiples"
    )
    
    show_example(
        "6. Consultas de Grafo",
        """from graph_engine.kuzu_graph import KuzuGraphEngine

graph = KuzuGraphEngine()

# Red de un contacto específico (depth=2)
network = graph.get_contact_network(
    contact_id="uuid-del-contacto",
    depth=2
)

print(f"Red de {network['center']}: {network['network_size']} conexiones")

# Conexiones en común entre dos personas
common = graph.find_common_connections(
    "contact-id-1",
    "contact-id-2"
)

print(f"Conexiones mutuas: {len(common)}")""",
        "Análisis de red social con Kùzu"
    )
    
    show_example(
        "7. Detectar Comunidades",
        """from graph_engine.kuzu_graph import KuzuGraphEngine

graph = KuzuGraphEngine()

# Detectar clusters con algoritmo Louvain
communities = graph.detect_communities()

print(f"Encontradas {len(set(communities.values()))} comunidades")

# Ver miembros de comunidad 0
members = [node for node, comm in communities.items() if comm == 0]
print(f"Comunidad 0: {len(members)} miembros")""",
        "Clustering automático de tu red"
    )
    
    show_example(
        "8. Contactos Inactivos",
        """from database.supabase_client import SupabaseContactManager

sb = SupabaseContactManager()

# Contactos sin interacción en 6+ meses
inactive = sb.get_inactive_contacts(days=180)

# Filtrar Tier 1 en zona específica
tier1_mty = inactive[
    (inactive['tier'] == 'Tier 1') &
    (inactive['zona'] == 'Monterrey')
]

print(f"Tier 1 inactivos en MTY: {len(tier1_mty)}")
print(tier1_mty[['full_name', 'company', 'days_inactive']])""",
        "Identificar contactos para reactivar"
    )
    
    show_example(
        "9. Procesar Nota de Voz WhatsApp",
        """from whatsapp_integration.whatsapp_processor import WhatsAppProcessor

processor = WhatsAppProcessor()

# Procesar audio
result = processor.process_voice_note(
    audio_path=Path("/path/to/audio.ogg"),
    sender_phone="+521234567890"
)

print(f"Resumen: {result['summary']}")
print(f"Sentimiento: {result['sentiment']}")
print(f"Temas: {', '.join(result['topics'])}")
print(f"Próximos pasos: {result['next_steps']}")""",
        "Transcribe y analiza audio con Whisper + GPT"
    )
    
    show_example(
        "10. Query SQL Directo en Supabase",
        """-- Ejecutar en Supabase SQL Editor

-- Top 20 empresas en tu red
SELECT company, tier, COUNT(*) as count
FROM contacts
WHERE company IS NOT NULL
GROUP BY company, tier
ORDER BY count DESC
LIMIT 20;

-- Contactos por Tier y Zona
SELECT tier, zona, COUNT(*) as count
FROM contacts
GROUP BY tier, zona
ORDER BY tier, count DESC;

-- Búsqueda full-text en español
SELECT * FROM search_contacts_fulltext('sustentabilidad CDMX')
LIMIT 10;""",
        "Queries avanzados directamente en Supabase"
    )
    
    console.print("\n[bold green]{'='*60}[/bold green]")
    console.print("[bold green]Para más información:[/bold green]")
    console.print("  • Instalación: docs/INSTALACION.md")
    console.print("  • Guía de uso: docs/USO.md")
    console.print("  • Arquitectura: docs/ARQUITECTURA.md")
    console.print("[bold green]{'='*60}[/bold green]\n")


if __name__ == "__main__":
    main()
