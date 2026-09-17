#!/usr/bin/env python3
"""
SHACL Validator for Automotive Knowledge Graph
Validates RDF data against SHACL shapes
"""

import sys
from pyshacl import validate
from rdflib import Graph
import json

def load_graph(file_path: str) -> Graph:
    """Load RDF graph from file"""
    g = Graph()
    try:
        g.parse(file_path, format='turtle')
        print(f"✅ Loaded {len(g)} triples from {file_path}")
        return g
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        sys.exit(1)

def validate_data(data_graph: Graph, shapes_graph: Graph, ontology_graph: Graph = None):
    """Validate data graph against SHACL shapes"""
    print("\n" + "="*80)
    print("SHACL VALIDATION")
    print("="*80 + "\n")
    
    try:
        conforms, results_graph, results_text = validate(
            data_graph,
            shacl_graph=shapes_graph,
            ont_graph=ontology_graph,
            inference='rdfs',
            abort_on_first=False,
            allow_warnings=True,
            meta_shacl=False,
            advanced=True,
            js=False,
            debug=False
        )
        
        if conforms:
            print("✅ VALIDATION PASSED - Data conforms to all SHACL shapes!")
            print(f"   Total triples validated: {len(data_graph)}")
        else:
            print("❌ VALIDATION FAILED - Constraint violations found:\n")
            print(results_text)
            
            # Parse violations for structured output
            violations = []
            for row in results_graph.query("""
                PREFIX sh: <http://www.w3.org/ns/shacl#>
                SELECT ?focusNode ?resultPath ?value ?message ?severity
                WHERE {
                    ?result a sh:ValidationResult ;
                            sh:focusNode ?focusNode ;
                            sh:resultMessage ?message ;
                            sh:resultSeverity ?severity .
                    OPTIONAL { ?result sh:resultPath ?resultPath }
                    OPTIONAL { ?result sh:value ?value }
                }
            """):
                violations.append({
                    "focusNode": str(row.focusNode),
                    "path": str(row.resultPath) if row.resultPath else "N/A",
                    "value": str(row.value) if row.value else "N/A",
                    "message": str(row.message),
                    "severity": str(row.severity)
                })
            
            print(f"\n📊 Total violations: {len(violations)}\n")
            
            # Group by severity
            errors = [v for v in violations if 'Violation' in v['severity']]
            warnings = [v for v in violations if 'Warning' in v['severity']]
            
            print(f"   Errors: {len(errors)}")
            print(f"   Warnings: {len(warnings)}")
            
            # Save violations to JSON
            with open('/workspace/knowledge-graph/validation/validation-results.json', 'w') as f:
                json.dump({
                    "conforms": conforms,
                    "total_violations": len(violations),
                    "errors": len(errors),
                    "warnings": len(warnings),
                    "violations": violations
                }, f, indent=2)
            
            print("\n💾 Detailed results saved to: validation/validation-results.json")
        
        return conforms
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def main():
    """Main execution"""
    print("🔍 SHACL Validator - Automotive Knowledge Graph")
    print("="*80 + "\n")
    
    # Paths
    base_path = "/workspace/knowledge-graph"
    ontology_path = f"{base_path}/ontology/automotive-ontology.ttl"
    data_path = f"{base_path}/data/automotive-instances.ttl"
    shapes_path = f"{base_path}/validation/shacl-shapes.ttl"
    
    # Load graphs
    print("📚 Loading RDF graphs...\n")
    ontology_graph = load_graph(ontology_path)
    data_graph = load_graph(data_path)
    shapes_graph = load_graph(shapes_path)
    
    # Combine ontology and data for validation
    combined_graph = ontology_graph + data_graph
    print(f"✅ Combined graph: {len(combined_graph)} triples\n")
    
    # Validate
    conforms = validate_data(combined_graph, shapes_graph, ontology_graph)
    
    # Exit code
    sys.exit(0 if conforms else 1)

if __name__ == "__main__":
    main()
