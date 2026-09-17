#!/bin/bash

# ============================================
# Knowledge Graph Setup Script
# Initializes triplestore and loads ontology/data
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KG_DIR="$(dirname "$SCRIPT_DIR")"
FUSEKI_URL="http://localhost:3030"
DATASET="automotive"

echo "🚀 Knowledge Graph Setup Script"
echo "================================"
echo ""

# Function to check if Fuseki is running
wait_for_fuseki() {
    echo "⏳ Waiting for Fuseki to be ready..."
    MAX_ATTEMPTS=30
    ATTEMPT=0
    
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        if curl -s -f "$FUSEKI_URL/$/ping" > /dev/null 2>&1; then
            echo "✅ Fuseki is ready!"
            return 0
        fi
        ATTEMPT=$((ATTEMPT + 1))
        echo "   Attempt $ATTEMPT/$MAX_ATTEMPTS..."
        sleep 2
    done
    
    echo "❌ Fuseki failed to start after $MAX_ATTEMPTS attempts"
    return 1
}

# Function to load RDF data into Fuseki
load_data() {
    local file=$1
    local graph=$2
    local filename=$(basename "$file")
    
    echo "📥 Loading $filename into graph: $graph"
    
    curl -X POST "$FUSEKI_URL/$DATASET/data?graph=$graph" \
         -H "Content-Type: text/turtle" \
         --data-binary "@$file" \
         -s -w "   HTTP Status: %{http_code}\n" \
         -o /dev/null
}

# Function to create dataset if it doesn't exist
create_dataset() {
    echo "🔧 Creating dataset '$DATASET'..."
    
    curl -X POST "$FUSEKI_URL/$/datasets" \
         -H "Content-Type: application/x-www-form-urlencoded" \
         -d "dbName=$DATASET&dbType=tdb2" \
         -s -w "   HTTP Status: %{http_code}\n" \
         -o /dev/null || true
}

# Main execution
main() {
    echo "1️⃣  Starting Docker containers..."
    cd "$KG_DIR"
    docker-compose up -d
    
    echo ""
    wait_for_fuseki || exit 1
    
    echo ""
    echo "2️⃣  Creating dataset (if not exists)..."
    create_dataset
    
    echo ""
    echo "3️⃣  Loading ontology..."
    load_data "$KG_DIR/ontology/automotive-ontology.ttl" "http://example.org/automotive/ontology"
    
    echo ""
    echo "4️⃣  Loading instance data..."
    load_data "$KG_DIR/data/automotive-instances.ttl" "http://example.org/automotive/data"
    
    echo ""
    echo "5️⃣  Verifying data load..."
    TRIPLE_COUNT=$(curl -s -X POST "$FUSEKI_URL/$DATASET/query" \
                         -H "Accept: application/sparql-results+json" \
                         --data-urlencode "query=SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" | \
                    grep -o '"value":"[0-9]*"' | grep -o '[0-9]*' || echo "0")
    
    echo "   Total triples loaded: $TRIPLE_COUNT"
    
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "🌐 Access Points:"
    echo "   - Fuseki Web UI:    http://localhost:3030"
    echo "   - SPARQL Endpoint:  http://localhost:3030/automotive/query"
    echo "   - YASGUI Interface: http://localhost:8080"
    echo "   - Jupyter Notebook: http://localhost:8888"
    echo ""
    echo "📖 Example SPARQL query:"
    echo "   PREFIX auto: <http://example.org/automotive#>"
    echo "   SELECT ?vehicle ?brand ?year WHERE {"
    echo "     ?vehicle a auto:VehiculoElectrico ;"
    echo "              auto:fabricadoPor ?brand ;"
    echo "              auto:añoLanzamiento ?year ."
    echo "   } LIMIT 10"
    echo ""
    echo "🛑 To stop: docker-compose down"
    echo "🗑️  To reset: docker-compose down -v (WARNING: deletes all data)"
}

# Run main function
main
