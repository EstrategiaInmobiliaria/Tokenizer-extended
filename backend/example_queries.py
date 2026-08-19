#!/usr/bin/env python3
"""
Ejemplos de Queries Útiles - Casos de uso reales

Ejecuta este script para ver ejemplos de queries que puedes hacer
con tu red de contactos.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def main():
    console.print("\n[bold cyan]=" * 60)
    console.print("[bold cyan]QUERIES ÚTILES - Sistema de Gestión de Red[/bold cyan]")
    console.print("[bold cyan]=" * 60 + "\n")
    
    queries = [
        {
            "titulo": "1. Pre-Reunión: Contexto de Contacto",
            "caso": "Mañana tengo reunión con alguien de Empresa X",
            "codigo": """from database.supabase_client import SupabaseContactManager
from graph_engine.kuzu_graph import KuzuGraphEngine

sb = SupabaseContactManager()
graph = KuzuGraphEngine()

# Buscar contactos de Empresa X
empresa = sb.search_contacts(query="Empresa X", limit=10)

for contacto in empresa.itertuples():
    print(f"\\n{contacto.full_name} - {contacto.title}")
    print(f"Tier: {contacto.tier} | Zona: {contacto.zona}")
    
    # Ver su red (conexiones de 2do grado)
    red = graph.get_contact_network(contacto.id, depth=2)
    print(f"Red: {red['network_size']} personas")
    
    # Últimas interacciones
    interacciones = sb.get_contact_interactions(contacto.id)
    if len(interacciones) > 0:
        print(f"Última interacción: {interacciones.iloc[0]['interaction_date']}")
        print(f"Resumen: {interacciones.iloc[0]['summary']}")"""
        },
        {
            "titulo": "2. Entrada a Nueva Ciudad",
            "caso": "Voy a Querétaro, ¿a quién debo ver?",
            "codigo": """from graph_engine.kuzu_graph import KuzuGraphEngine

graph = KuzuGraphEngine()

# Top contactos en Querétaro (Tier 1 y 2)
qro = graph.query_contacts_by_criteria(
    zona="Querétaro",
    min_interactions=0
)

# Filtrar Tier 1 y 2
qro_top = qro[qro['tier'].isin(['Tier 1', 'Tier 2'])]

# Ordenar por total_interactions descendente
qro_top = qro_top.sort_values('total_interactions', ascending=False)

print(f"\\n{len(qro_top)} contactos top en Querétaro:\\n")
print(qro_top[['full_name', 'company', 'tier', 'total_interactions']])"""
        },
        {
            "titulo": "3. Reactivación: Inactivos Tier 1",
            "caso": "¿Tier 1 sin contacto en 6+ meses?",
            "codigo": """from database.supabase_client import SupabaseContactManager

sb = SupabaseContactManager()

# Contactos inactivos 180+ días
inactive = sb.get_inactive_contacts(days=180)

# Filtrar Tier 1
tier1_inactive = inactive[
    inactive['tier'] == 'Tier 1'
].sort_values('days_inactive', ascending=False)

print(f"\\n{len(tier1_inactive)} Tier 1 inactivos:\\n")

for _, contact in tier1_inactive.head(20).iterrows():
    print(f"{contact['full_name']:30} | {contact['company']:25} | {contact['days_inactive']:.0f} días")"""
        },
        {
            "titulo": "4. Reactivación por Zona",
            "caso": "Tier 1 inactivos en Monterrey (viaje planeado)",
            "codigo": """from database.supabase_client import SupabaseContactManager

sb = SupabaseContactManager()

inactive = sb.get_inactive_contacts(days=180)

# Tier 1 en Monterrey
mty_tier1 = inactive[
    (inactive['tier'] == 'Tier 1') &
    (inactive['zona'] == 'Monterrey')
]

print(f"\\n{len(mty_tier1)} Tier 1 inactivos en MTY:")
print(mty_tier1[['full_name', 'company', 'title', 'days_inactive']])"""
        },
        {
            "titulo": "5. Búsqueda Temática",
            "caso": "¿Quién trabaja sustentabilidad/ESG?",
            "codigo": """from database.supabase_client import SupabaseContactManager

sb = SupabaseContactManager()

# Búsqueda full-text
esg = sb.search_contacts(
    query="sustentabilidad ESG certificación",
    limit=50
)

# Filtrar por Tier
esg_tier1 = esg[esg['tier'] == 'Tier 1']

print(f"\\n{len(esg)} contactos relacionados con ESG")
print(f"{len(esg_tier1)} son Tier 1\\n")

for _, c in esg_tier1.iterrows():
    print(f"{c['full_name']:30} | {c['company']:25} | {c['zona']}")"""
        },
        {
            "titulo": "6. Descubrimiento de Comunidades",
            "caso": "¿Qué clusters tengo que no sabía?",
            "codigo": """from graph_engine.kuzu_graph import KuzuGraphEngine
from database.supabase_client import SupabaseContactManager
import pandas as pd

graph = KuzuGraphEngine()
sb = SupabaseContactManager()

# Detectar comunidades
communities = graph.detect_communities()

# Analizar cada comunidad
df_contacts = sb.get_all_contacts()

for comm_id in range(max(communities.values()) + 1):
    members = [node for node, c in communities.items() if c == comm_id]
    
    # Get member details
    member_info = df_contacts[df_contacts['id'].isin(members)]
    
    # Análisis
    top_temas = member_info['temas'].str.split(',').explode().value_counts().head(3)
    top_zona = member_info['zona'].value_counts().iloc[0] if len(member_info) > 0 else 'N/A'
    avg_tier = member_info['tier'].value_counts()
    
    print(f"\\nComunidad {comm_id}: {len(members)} miembros")
    print(f"  Zona dominante: {top_zona}")
    print(f"  Temas top: {', '.join(top_temas.index.tolist())}")
    print(f"  Distribución Tier: {dict(avg_tier)}")"""
        },
        {
            "titulo": "7. Conexiones en Común",
            "caso": "¿Qué conexiones tengo en común con Juan?",
            "codigo": """from graph_engine.kuzu_graph import KuzuGraphEngine
from database.supabase_client import SupabaseContactManager

graph = KuzuGraphEngine()
sb = SupabaseContactManager()

# Buscar Juan
juan = sb.search_contacts(query="Juan", limit=1)
juan_id = juan.iloc[0]['id']

# Buscar yo (tu contacto principal)
yo_id = "tu-id-aqui"  # O buscar por nombre

# Conexiones en común
common = graph.find_common_connections(yo_id, juan_id)

print(f"\\n{len(common)} conexiones en común con Juan:")
for c in common:
    print(f"  • {c['name']} ({c['company']})")"""
        },
        {
            "titulo": "8. Contactos Más Centrales (Influencers)",
            "caso": "¿Quiénes son los super-conectores en mi red?",
            "codigo": """from graph_engine.kuzu_graph import KuzuGraphEngine

graph = KuzuGraphEngine()

# Top 20 más conectados
central = graph.get_central_contacts(limit=20)

print("\\nTop 20 super-conectores:\\n")
print(central.to_string(index=False))"""
        },
        {
            "titulo": "9. Búsqueda Semántica en Conversaciones",
            "caso": "¿En qué reuniones se habló de certificación LEED?",
            "codigo": """from database.supabase_client import SupabaseContactManager
from openai import OpenAI

sb = SupabaseContactManager()
client = OpenAI()

# Crear embedding de la query
query = "certificación LEED edificios sustentables"
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=query
)
query_embedding = response.data[0].embedding

# Búsqueda semántica
results = sb.semantic_search_interactions(
    query_embedding=query_embedding,
    threshold=0.7,
    limit=10
)

print(f"\\n{len(results)} conversaciones relevantes:\\n")

for _, r in results.iterrows():
    print(f"Contacto: {r['contact_name']}")
    print(f"Similarity: {r['similarity']:.2f}")
    print(f"Contenido: {r['content'][:200]}...\\n")"""
        },
        {
            "titulo": "10. SQL Directo: Top Empresas",
            "caso": "¿Cuáles son las 20 empresas más presentes?",
            "codigo": """# Ejecutar en Supabase SQL Editor:

SELECT 
    company,
    tier,
    COUNT(*) as contact_count,
    COUNT(CASE WHEN total_interactions > 0 THEN 1 END) as active_count
FROM contacts
WHERE company IS NOT NULL
GROUP BY company, tier
ORDER BY contact_count DESC
LIMIT 20;"""
        }
    ]
    
    for i, q in enumerate(queries, 1):
        console.print(f"\n[bold green]{q['titulo']}[/bold green]")
        console.print(f"[yellow]Caso de uso:[/yellow] {q['caso']}\n")
        
        panel = Panel(
            q['codigo'],
            title="Código",
            border_style="cyan",
            expand=False
        )
        console.print(panel)
        
        if i < len(queries):
            console.print("\n" + "─" * 80)
    
    console.print("\n\n[bold cyan]=" * 60)
    console.print("[bold cyan]Para más información:[/bold cyan]")
    console.print("  • Guía completa: docs/USO.md")
    console.print("  • Arquitectura: docs/ARQUITECTURA.md")
    console.print("[bold cyan]=" * 60 + "\n")


if __name__ == "__main__":
    main()
