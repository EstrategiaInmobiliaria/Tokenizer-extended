#!/usr/bin/env python3
"""
SPARQL Query Executor for Automotive Knowledge Graph
Executes all competency questions and generates results
"""

from SPARQLWrapper import SPARQLWrapper, JSON
import json
import sys
from typing import Dict, List
import time

FUSEKI_ENDPOINT = "http://localhost:3030/automotive/query"

# Define all competency questions
COMPETENCY_QUERIES = {
    "CQ-A1": {
        "title": "Marcas del Grupo Volkswagen",
        "query": """
            PREFIX auto: <http://example.org/automotive#>
            SELECT ?marca ?nombreMarca ?paisOrigen
            WHERE {
              ?marca auto:perteneceA auto:GrupoVolkswagen ;
                     auto:nombreComercial ?nombreMarca .
              OPTIONAL { ?marca auto:paisOrigen ?paisOrigen }
            }
            ORDER BY ?nombreMarca
        """
    },
    "CQ-A2": {
        "title": "Empresas que fabrican vehículos híbridos",
        "query": """
            PREFIX auto: <http://example.org/automotive#>
            SELECT DISTINCT ?fabricante ?nombreFabricante (COUNT(?vehiculo) as ?numModelos)
            WHERE {
              ?vehiculo a auto:VehiculoHibrido ;
                        auto:fabricadoPor ?fabricante .
              ?fabricante auto:nombreComercial ?nombreFabricante .
            }
            GROUP BY ?fabricante ?nombreFabricante
            ORDER BY DESC(?numModelos)
        """
    },
    "CQ-B1": {
        "title": "SUVs lanzados después de 2020",
        "query": """
            PREFIX auto: <http://example.org/automotive#>
            SELECT ?vehiculo ?nombre ?fabricante ?año ?precio
            WHERE {
              ?vehiculo a auto:SUV ;
                        auto:nombreComercial ?nombre ;
                        auto:fabricadoPor ?fabUri ;
                        auto:añoLanzamiento ?año .
              ?fabUri auto:nombreComercial ?fabricante .
              OPTIONAL { ?vehiculo auto:precioBase ?precio }
              FILTER(?año > 2020)
            }
            ORDER BY DESC(?año) ?nombre
        """
    },
    "CQ-B2": {
        "title": "Vehículos eléctricos por autonomía",
        "query": """
            PREFIX auto: <http://example.org/automotive#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?nombre ?fabricante ?autonomia ?capacidadBateria ?precio
            WHERE {
              ?vehiculo rdf:type/rdfs:subClassOf* auto:VehiculoElectrico ;
                        auto:nombreComercial ?nombre ;
                        auto:autonomiaKm ?autonomia ;
                        auto:fabricadoPor ?fabUri .
              ?fabUri auto:nombreComercial ?fabricante .
              OPTIONAL { ?vehiculo auto:capacidadBateriaKWh ?capacidadBateria }
              OPTIONAL { ?vehiculo auto:precioBase ?precio }
            }
            ORDER BY DESC(?autonomia)
        """
    },
    "CQ-B3": {
        "title": "Vehículos que comparten plataforma técnica",
        "query": """
            PREFIX auto: <http://example.org/automotive#>
            SELECT ?nombrePlataforma 
                   (GROUP_CONCAT(DISTINCT ?nombreVehiculo; separator=", ") as ?vehiculos)
                   (COUNT(DISTINCT ?vehiculo) as ?numVehiculos)
            WHERE {
              ?plataforma a auto:PlataformaTecnica ;
                          auto:nombreComercial ?nombrePlataforma .
              ?vehiculo auto:compartePlataforma ?plataforma ;
                        auto:nombreComercial ?nombreVehiculo .
            }
            GROUP BY ?plataforma ?nombrePlataforma
            HAVING (COUNT(DISTINCT ?vehiculo) > 1)
            ORDER BY DESC(?numVehiculos)
        """
    },
    "CQ-C1": {
        "title": "Fabricantes que usan baterías CATL",
        "query": """
            PREFIX auto: <http://example.org/automotive#>
            SELECT DISTINCT ?nombreVehiculo ?fabricante
            WHERE {
              ?bateria auto:suministradoPor auto:CATL .
              ?vehiculo auto:usaComponente ?bateria ;
                        auto:nombreComercial ?nombreVehiculo ;
                        auto:fabricadoPor ?fabUri .
              ?fabUri auto:nombreComercial ?fabricante .
            }
            ORDER BY ?fabricante ?nombreVehiculo
        """
    },
    "CQ-D1": {
        "title": "Vehículos con más de 300 HP y tracción integral",
        "query": """
            PREFIX auto: <http://example.org/automotive#>
            SELECT ?nombre ?fabricante ?potencia ?aceleracion
            WHERE {
              ?vehiculo auto:nombreComercial ?nombre ;
                        auto:potenciaHP ?potencia ;
                        auto:tieneSistemaTraccion auto:TraccionIntegral ;
                        auto:fabricadoPor ?fabUri .
              ?fabUri auto:nombreComercial ?fabricante .
              OPTIONAL { ?vehiculo auto:aceleracion0a100 ?aceleracion }
              FILTER(?potencia > 300)
            }
            ORDER BY DESC(?potencia)
        """
    },
    "CQ-E2": {
        "title": "Vehículos discontinuados en últimos 3 años",
        "query": """
            PREFIX auto: <http://example.org/automotive#>
            SELECT ?nombre ?fabricante ?añoLanzamiento ?añoDescontinuacion
            WHERE {
              ?vehiculo auto:nombreComercial ?nombre ;
                        auto:añoDescontinuacion ?añoDescontinuacion ;
                        auto:añoLanzamiento ?añoLanzamiento ;
                        auto:fabricadoPor ?fabUri .
              ?fabUri auto:nombreComercial ?fabricante .
              FILTER(?añoDescontinuacion >= 2021 && ?añoDescontinuacion <= 2024)
            }
            ORDER BY DESC(?añoDescontinuacion)
        """
    }
}


def execute_query(endpoint: str, query: str) -> Dict:
    """Execute a SPARQL query and return results"""
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    try:
        start_time = time.time()
        results = sparql.query().convert()
        elapsed = (time.time() - start_time) * 1000  # Convert to ms
        
        return {
            "success": True,
            "results": results["results"]["bindings"],
            "elapsed_ms": round(elapsed, 2)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def print_results(query_id: str, query_info: Dict, result: Dict):
    """Pretty print query results"""
    print(f"\n{'='*80}")
    print(f"Query: {query_id} - {query_info['title']}")
    print(f"{'='*80}")
    
    if not result["success"]:
        print(f"❌ Error: {result['error']}")
        return
    
    bindings = result["results"]
    print(f"✅ Found {len(bindings)} results in {result['elapsed_ms']}ms\n")
    
    if len(bindings) == 0:
        print("No results found.")
        return
    
    # Get column names
    columns = list(bindings[0].keys())
    
    # Print results as table
    for binding in bindings[:10]:  # Limit to 10 results for display
        for col in columns:
            value = binding.get(col, {}).get("value", "N/A")
            print(f"  {col}: {value}")
        print()
    
    if len(bindings) > 10:
        print(f"  ... and {len(bindings) - 10} more results")


def main():
    """Main execution"""
    print("🔍 SPARQL Query Executor - Automotive Knowledge Graph")
    print("=" * 80)
    
    # Test endpoint connection
    test_query = "ASK { ?s ?p ?o }"
    sparql = SPARQLWrapper(FUSEKI_ENDPOINT)
    sparql.setQuery(test_query)
    
    try:
        sparql.query()
        print(f"✅ Connected to endpoint: {FUSEKI_ENDPOINT}\n")
    except Exception as e:
        print(f"❌ Cannot connect to endpoint: {e}")
        print(f"   Make sure Fuseki is running: docker-compose up -d")
        sys.exit(1)
    
    # Execute all queries
    results_summary = []
    
    for query_id, query_info in COMPETENCY_QUERIES.items():
        result = execute_query(FUSEKI_ENDPOINT, query_info["query"])
        print_results(query_id, query_info, result)
        
        results_summary.append({
            "id": query_id,
            "title": query_info["title"],
            "success": result["success"],
            "count": len(result["results"]) if result["success"] else 0,
            "elapsed_ms": result.get("elapsed_ms", 0)
        })
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total_queries = len(results_summary)
    successful = sum(1 for r in results_summary if r["success"])
    avg_time = sum(r["elapsed_ms"] for r in results_summary) / len(results_summary)
    
    print(f"Total queries executed: {total_queries}")
    print(f"Successful: {successful} / {total_queries}")
    print(f"Average query time: {avg_time:.2f}ms")
    print()
    
    for summary in results_summary:
        status = "✅" if summary["success"] else "❌"
        print(f"{status} {summary['id']}: {summary['count']} results in {summary['elapsed_ms']}ms")


if __name__ == "__main__":
    main()
