# Complete Walkthrough - Automotive Knowledge Graph

## 🎓 Learning Path: From Zero to Knowledge Graph Expert

This walkthrough guides you through the complete knowledge graph implementation, explaining **why** each component exists and **how** they work together.

---

## 📚 Table of Contents

1. [Understanding Knowledge Graphs](#1-understanding-knowledge-graphs)
2. [The 5-Stage Workflow](#2-the-5-stage-workflow)
3. [Stage 1: Domain Definition](#3-stage-1-domain-definition)
4. [Stage 2: OWL Ontology Design](#4-stage-2-owl-ontology-design)
5. [Stage 3: RDF Data Creation](#5-stage-3-rdf-data-creation)
6. [Stage 4: Triplestore Setup](#6-stage-4-triplestore-setup)
7. [Stage 5: SPARQL Queries](#7-stage-5-sparql-queries)
8. [Bonus: SHACL Validation](#8-bonus-shacl-validation)
9. [Practical Examples](#9-practical-examples)
10. [Extending the System](#10-extending-the-system)

---

## 1. Understanding Knowledge Graphs

### What is a Knowledge Graph?

A **knowledge graph** is a structured representation of knowledge where:
- **Entities** are represented as nodes (e.g., Tesla Model 3, Toyota)
- **Relationships** are represented as edges (e.g., "fabricado por", "usa componente")
- **Properties** are represented as attributes (e.g., autonomía: 629 km, precio: $49,990)

### Why RDF and OWL?

- **RDF (Resource Description Framework)**: Universal data model for the web
  - Everything is a triple: `<Subject> <Predicate> <Object>`
  - Example: `<TeslaModel3> <fabricadoPor> <Tesla>`
  
- **OWL (Web Ontology Language)**: Logic layer on top of RDF
  - Defines formal semantics (classes, properties, axioms)
  - Enables automated reasoning and inference
  - Example: "If X is a SUV, then X is also a Vehicle" (subclass inference)

### Benefits of Semantic Knowledge Graphs

1. **Machine-Readable**: Computers can understand and reason about data
2. **Inference**: Deduce new facts from existing ones automatically
3. **Integration**: Easily merge data from multiple sources
4. **Querying**: Powerful graph pattern matching with SPARQL
5. **Validation**: Enforce data quality constraints with SHACL

---

## 2. The 5-Stage Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE GRAPH WORKFLOW                      │
└─────────────────────────────────────────────────────────────────┘

Stage 1: Domain Definition & Competency Questions
   ↓    (What questions should the KG answer?)
   
Stage 2: OWL/RDFS Ontology Modeling
   ↓    (Define classes, properties, logical rules)
   
Stage 3: RDF Data Triplification
   ↓    (Convert data into RDF triples)
   
Stage 4: Triplestore + Inference Engine
   ↓    (Load data, enable reasoning)
   
Stage 5: SPARQL Queries
   ↓    (Query and exploit knowledge)
   
Bonus: SHACL Validation
   ↓    (Validate data integrity)
```

---

## 3. Stage 1: Domain Definition

**File**: `docs/01-competency-questions.md`

### Purpose

Define **what** the knowledge graph should know by writing **competency questions** (CQs).

### Example Competency Questions

**CQ-A1**: "¿Qué marcas pertenecen al Grupo Volkswagen?"
- **Why?** Users need to understand corporate structure
- **Expected Answer**: Volkswagen, Audi, Porsche, SEAT, Škoda

**CQ-B2**: "¿Cuáles son los vehículos eléctricos con mayor autonomía?"
- **Why?** Buyers compare EVs by range
- **Expected Answer**: Tesla Model 3 (629 km), Kia EV6 (528 km)

**CQ-C1**: "¿Qué fabricantes usan baterías de CATL?"
- **Why?** Analyze supply chain dependencies
- **Expected Answer**: BMW iX3 uses CATL NCM811 batteries

### How to Write Good CQs

1. **Be specific**: "What is the average horsepower of SUVs?" (good) vs "Tell me about cars" (bad)
2. **Cover different aspects**: Hierarchy, taxonomy, relationships, specs, temporal
3. **Think about real users**: What would a market analyst ask? A car buyer? A supply chain manager?

---

## 4. Stage 2: OWL Ontology Design

**File**: `ontology/automotive-ontology.ttl`

### Purpose

Create a **formal model** that defines:
- What entities exist (classes)
- How they relate (properties)
- What rules apply (axioms)

### Example 1: Class Hierarchy

```turtle
auto:Vehiculo a owl:Class ;
    rdfs:label "Vehículo"@es .

auto:SUV a owl:Class ;
    rdfs:subClassOf auto:Vehiculo ;
    rdfs:label "SUV"@es .

auto:VehiculoElectrico a owl:Class ;
    rdfs:subClassOf auto:Vehiculo ;
    rdfs:label "Vehículo Eléctrico"@es .
```

**What this means**: 
- Every SUV is automatically a Vehicle (inheritance)
- Reasoner will infer: `TeslaModelY rdf:type auto:Vehiculo` from `TeslaModelY rdf:type auto:SUV`

### Example 2: Object Property with Inverse

```turtle
auto:fabricadoPor a owl:ObjectProperty ;
    rdfs:domain auto:Vehiculo ;
    rdfs:range auto:Fabricante ;
    owl:inverseOf auto:produceModelo .
```

**What this means**:
- If we state: `<RAV4> auto:fabricadoPor <Toyota>`
- Reasoner infers: `<Toyota> auto:produceModelo <RAV4>` (automatically!)

### Example 3: Datatype Property with Range

```turtle
auto:autonomiaKm a owl:DatatypeProperty ;
    rdfs:domain auto:VehiculoElectrico ;
    rdfs:range xsd:decimal ;
    rdfs:label "autonomía (km)"@es .
```

**What this means**:
- Only electric vehicles can have this property
- Value must be a decimal number
- SHACL can validate these constraints

### Example 4: Cardinality Restriction

```turtle
auto:Vehiculo rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty auto:fabricadoPor ;
    owl:cardinality 1
] .
```

**What this means**:
- Every vehicle **must** be manufactured by **exactly one** company
- Invalid: A car with no manufacturer or two manufacturers

---

## 5. Stage 3: RDF Data Creation

**File**: `data/automotive-instances.ttl`

### Purpose

Convert real-world data into **RDF triples** that conform to the ontology.

### Example: Complete Vehicle Instance

```turtle
auto:TeslaModel3LongRange_2024
    a auto:Sedan, auto:VehiculoElectrico, auto:VehiculoLargaAutonomia ;
    auto:nombreComercial "Tesla Model 3 Long Range AWD" ;
    auto:fabricadoPor auto:Tesla ;
    auto:comercializadoBajo auto:Tesla ;
    auto:tienePropulsion auto:PropulsionElectrica ;
    auto:tieneSistemaTraccion auto:TraccionIntegral ;
    auto:añoLanzamiento 2023 ;
    auto:potenciaHP 366 ;
    auto:pesoKg 1844 ;
    auto:numeroPlazas 5 ;
    auto:precioBase 49990.00 ;
    auto:capacidadBateriaKWh 82.0 ;
    auto:autonomiaKm 629 ;
    auto:emisionesCO2 0 ;
    auto:aceleracion0a100 4.4 ;
    auto:velocidadMaxima 201 ;
    auto:usaComponente auto:BateriaPanasonic_2170 .
```

**What this creates**:
- 14 RDF triples about the Tesla Model 3
- Connects to other entities (Tesla company, Panasonic battery)
- Can be queried, reasoned about, validated

### Data Modeling Best Practices

1. **Use URIs consistently**: `auto:TeslaModel3LongRange_2024` (good) vs random IDs (bad)
2. **Include multiple types**: Vehicle can be both Sedan AND Electric
3. **Link to other entities**: Don't duplicate company info, reference it
4. **Optional properties**: Not all vehicles have `aceleracion0a100` (OK)
5. **Accurate data**: Real specifications from manufacturer websites

---

## 6. Stage 4: Triplestore Setup

**Files**: `docker-compose.yml`, `config/fuseki-config.ttl`, `config/setup.sh`

### Purpose

Deploy a **database** that can:
- Store millions of RDF triples efficiently
- Execute SPARQL queries in milliseconds
- Perform OWL reasoning (inference)
- Expose HTTP API for applications

### Architecture

```
Docker Container: fuseki
├── Apache Jena Fuseki (web server)
├── TDB2 (native RDF storage)
├── OWL Reasoner (inference engine)
└── SPARQL Endpoint (HTTP API)
```

### Configuration Example

```turtle
:automotive_inf_model a ja:InfModel ;
    ja:baseModel :tdb_graph ;
    ja:reasoner [
        ja:reasonerURL <http://jena.hpl.hp.com/2003/OWLFBRuleReasoner>
    ] .
```

**What this does**:
- Wraps the base RDF graph with an inference layer
- When you query, you get both explicit AND inferred triples
- Example: Query for "all Vehicles" returns SUVs, Sedans, etc. (because they're subclasses)

### Loading Data

```bash
# setup.sh does this automatically:

# 1. Wait for Fuseki to start
curl http://localhost:3030/$/ping

# 2. Load ontology into named graph
curl -X POST http://localhost:3030/automotive/data?graph=ontology \
     -H "Content-Type: text/turtle" \
     --data-binary @automotive-ontology.ttl

# 3. Load instance data into named graph
curl -X POST http://localhost:3030/automotive/data?graph=data \
     -H "Content-Type: text/turtle" \
     --data-binary @automotive-instances.ttl

# 4. Verify triple count
curl http://localhost:3030/automotive/query \
     --data-urlencode "query=SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
```

---

## 7. Stage 5: SPARQL Queries

**File**: `queries/sparql-queries.rq`

### Purpose

Extract knowledge by matching **graph patterns**.

### Example 1: Simple Query

**Question**: "¿Qué vehículos eléctricos existen?"

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?nombre ?fabricante
WHERE {
  ?vehiculo a auto:VehiculoElectrico ;
            auto:nombreComercial ?nombre ;
            auto:fabricadoPor ?fabUri .
  ?fabUri auto:nombreComercial ?fabricante .
}
```

**How it works**:
1. Find all instances of type `auto:VehiculoElectrico`
2. Get their commercial name
3. Follow `fabricadoPor` link to find manufacturer
4. Get manufacturer's commercial name

**Results**:
```
nombre                            fabricante
---------------------------------+----------------
Tesla Model 3 Long Range AWD      Tesla, Inc.
Tesla Model Y Long Range AWD      Tesla, Inc.
Hyundai IONIQ 5 Long Range AWD    Hyundai
Kia EV6 GT-Line AWD               Kia
BMW iX3                           BMW
```

### Example 2: Filtering and Ordering

**Question**: "¿Qué vehículos eléctricos tienen más de 500 km de autonomía?"

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?nombre ?autonomia ?precio
WHERE {
  ?vehiculo a auto:VehiculoElectrico ;
            auto:nombreComercial ?nombre ;
            auto:autonomiaKm ?autonomia .
  OPTIONAL { ?vehiculo auto:precioBase ?precio }
  FILTER(?autonomia > 500)
}
ORDER BY DESC(?autonomia)
```

**New concepts**:
- `OPTIONAL`: Get price if available, but don't exclude vehicles without it
- `FILTER`: Only vehicles with autonomy > 500 km
- `ORDER BY DESC`: Highest autonomy first

**Results**:
```
nombre                         autonomia    precio
------------------------------+-----------+----------
Tesla Model 3 Long Range       629          49990.00
Tesla Model Y Long Range       533          54990.00
Kia EV6 GT-Line AWD            528          54900.00
Hyundai IONIQ 5 Long Range     507          52500.00
```

### Example 3: Aggregation

**Question**: "¿Cuántos modelos tiene cada fabricante?"

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?fabricante (COUNT(?vehiculo) as ?numModelos)
WHERE {
  ?vehiculo auto:fabricadoPor ?fabUri .
  ?fabUri auto:nombreComercial ?fabricante .
}
GROUP BY ?fabricante
ORDER BY DESC(?numModelos)
```

**New concepts**:
- `COUNT(?vehiculo)`: Count distinct vehicles
- `GROUP BY`: Aggregate by manufacturer
- `as ?numModelos`: Name the aggregated column

**Results**:
```
fabricante               numModelos
-----------------------+------------
Toyota                   3
Tesla                    2
Volkswagen               2
Hyundai                  1
Kia                      1
```

### Example 4: Inference Query

**Question**: "¿Qué tipos tiene el RAV4?" (exploiting subclass inference)

```sparql
PREFIX auto: <http://example.org/automotive#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?tipo
WHERE {
  auto:ToyotaRAV4_2024 rdf:type ?tipo .
}
```

**Results** (with reasoning enabled):
```
tipo
---------------------------------
auto:SUV                    (explicit)
auto:VehiculoHibrido        (explicit)
auto:VehiculoPasajeros      (INFERRED from SUV subclass)
auto:Vehiculo               (INFERRED from SUV → VehiculoPasajeros → Vehiculo)
```

---

## 8. Bonus: SHACL Validation

**File**: `validation/shacl-shapes.ttl`

### Purpose

Ensure data **quality** and **consistency** by defining **constraints**.

### Example 1: Mandatory Property

```turtle
auto:VehiculoShape
    sh:property [
        sh:path auto:fabricadoPor ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Todo vehículo debe ser fabricado por exactamente un fabricante"@es ;
    ] .
```

**What this validates**:
- Every vehicle **must have** a manufacturer (`minCount 1`)
- Every vehicle **can have only one** manufacturer (`maxCount 1`)
- If violated, show Spanish error message

### Example 2: Range Validation

```turtle
auto:VehiculoElectricoShape
    sh:property [
        sh:path auto:autonomiaKm ;
        sh:datatype xsd:decimal ;
        sh:minExclusive 0 ;
        sh:maxInclusive 1500 ;
        sh:message "Autonomía debe estar entre 0 y 1500 km"@es ;
    ] .
```

**What this validates**:
- Autonomy must be a decimal number
- Must be greater than 0 km (no negative or zero range)
- Must be less than 1500 km (realistic upper bound)

### Example 3: Business Logic Validation

```turtle
auto:VehiculoShape
    sh:sparql [
        sh:message "Año de discontinuación debe ser posterior al año de lanzamiento"@es ;
        sh:select """
            PREFIX auto: <http://example.org/automotive#>
            SELECT $this
            WHERE {
                $this auto:añoLanzamiento ?lanzamiento ;
                      auto:añoDescontinuacion ?discontinuacion .
                FILTER(?discontinuacion <= ?lanzamiento)
            }
        """ ;
    ] .
```

**What this validates**:
- If a vehicle has both launch year and discontinuation year
- Discontinuation year must be **after** launch year
- Uses SPARQL query to check logic

### Running Validation

```bash
cd validation
python3 validate.py
```

**Output if data is valid**:
```
✅ VALIDATION PASSED
   Total triples validated: 847
   Errors: 0
   Warnings: 0
```

**Output if data is invalid** (example):
```
❌ VALIDATION FAILED

Focus Node: auto:InvalidVehicle
Path: auto:fabricadoPor
Severity: Violation
Message: Todo vehículo debe ser fabricado por exactamente un fabricante
```

---

## 9. Practical Examples

### Use Case 1: Competitive EV Analysis

**Goal**: Compare all electric SUVs by range, price, and performance.

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?nombre ?fabricante ?autonomia ?precio ?aceleracion
WHERE {
  ?vehiculo a auto:SUV, auto:VehiculoElectrico ;
            auto:nombreComercial ?nombre ;
            auto:fabricadoPor ?fabUri ;
            auto:autonomiaKm ?autonomia .
  ?fabUri auto:nombreComercial ?fabricante .
  OPTIONAL { ?vehiculo auto:precioBase ?precio }
  OPTIONAL { ?vehiculo auto:aceleracion0a100 ?aceleracion }
}
ORDER BY DESC(?autonomia)
```

**Business Value**: 
- Market analysts identify competitive gaps
- Car buyers compare models side-by-side
- Reveals price/performance trade-offs

### Use Case 2: Supply Chain Mapping

**Goal**: Find all vehicles using batteries from specific supplier.

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?vehiculo ?proveedor ?capacidad
WHERE {
  ?bateria a auto:Bateria ;
           auto:suministradoPor ?provUri ;
           auto:capacidadBateriaKWh ?capacidad .
  ?provUri auto:nombreComercial ?proveedor .
  ?vehiculo auto:usaComponente ?bateria ;
            auto:nombreComercial ?nombreVehiculo .
  FILTER(CONTAINS(LCASE(?proveedor), "catl"))
}
```

**Business Value**:
- Identify supply chain dependencies
- Find alternative suppliers
- Risk analysis (what if CATL has production issues?)

### Use Case 3: Platform Economies

**Goal**: Analyze cost savings from shared platforms.

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?plataforma 
       (COUNT(?vehiculo) as ?numVehiculos)
       (GROUP_CONCAT(?marca; separator=", ") as ?marcas)
WHERE {
  ?plataforma a auto:PlataformaTecnica ;
              auto:nombreComercial ?nombrePlataforma .
  ?vehiculo auto:compartePlataforma ?plataforma ;
            auto:comercializadoBajo ?marcaUri .
  ?marcaUri auto:nombreComercial ?marca .
}
GROUP BY ?plataforma ?nombrePlataforma
HAVING (COUNT(?vehiculo) > 1)
```

**Business Value**:
- Volkswagen's MQB platform shared across 4 models → massive R&D savings
- Toyota's TNGA enables faster launches
- Identifies collaboration opportunities

---

## 10. Extending the System

### Adding a New Class

**Scenario**: Add support for autonomous vehicles.

**Step 1**: Update ontology (`ontology/automotive-ontology.ttl`):

```turtle
auto:VehiculoAutonomo
    a owl:Class ;
    rdfs:subClassOf auto:Vehiculo ;
    rdfs:label "Vehículo Autónomo"@es ;
    rdfs:comment "Vehículo con capacidad de conducción autónoma nivel 4 o 5 (SAE)"@es .

auto:nivelAutonomia
    a owl:DatatypeProperty ;
    rdfs:domain auto:VehiculoAutonomo ;
    rdfs:range xsd:integer ;
    rdfs:label "nivel de autonomía (SAE)"@es ;
    rdfs:comment "Nivel SAE: 0 (ninguno) a 5 (completamente autónomo)"@es .
```

**Step 2**: Add instance data (`data/automotive-instances.ttl`):

```turtle
auto:WaymoJaguarIPace
    a auto:SUV, auto:VehiculoElectrico, auto:VehiculoAutonomo ;
    auto:nombreComercial "Waymo Jaguar I-PACE" ;
    auto:fabricadoPor auto:Jaguar ;
    auto:añoLanzamiento 2020 ;
    auto:nivelAutonomia 4 ;
    auto:autonomiaKm 400 .
```

**Step 3**: Add SHACL validation (`validation/shacl-shapes.ttl`):

```turtle
auto:VehiculoAutonomoShape
    sh:property [
        sh:path auto:nivelAutonomia ;
        sh:minCount 1 ;
        sh:datatype xsd:integer ;
        sh:minInclusive 0 ;
        sh:maxInclusive 5 ;
        sh:message "Nivel de autonomía debe ser 0-5 (escala SAE)"@es ;
    ] .
```

**Step 4**: Add query (`queries/sparql-queries.rq`):

```sparql
## Query: Vehículos autónomos por nivel SAE
PREFIX auto: <http://example.org/automotive#>

SELECT ?nombre ?nivel ?fabricante
WHERE {
  ?vehiculo a auto:VehiculoAutonomo ;
            auto:nombreComercial ?nombre ;
            auto:nivelAutonomia ?nivel ;
            auto:fabricadoPor ?fabUri .
  ?fabUri auto:nombreComercial ?fabricante .
}
ORDER BY DESC(?nivel)
```

**Step 5**: Reload data:

```bash
docker-compose restart fuseki
./config/setup.sh
```

---

## 🎓 Key Takeaways

### What You Learned

1. **Domain Modeling**: How to define competency questions that drive ontology design
2. **OWL Semantics**: Classes, properties, axioms, inference rules
3. **RDF Triples**: Converting real-world data into machine-readable format
4. **Reasoning**: How OWL reasoners deduce new facts automatically
5. **SPARQL**: Graph pattern matching, filtering, aggregation, ordering
6. **Validation**: Ensuring data quality with SHACL constraints
7. **Architecture**: How triplestores, reasoners, and query engines work together

### Why This Matters

- **Interoperability**: Your data can integrate with any RDF-compatible system
- **Scalability**: TDB2 handles billions of triples efficiently
- **Intelligence**: Reasoning discovers implicit knowledge automatically
- **Flexibility**: Add new classes/properties without breaking existing queries
- **Standards**: W3C technologies ensure long-term compatibility

### Next Steps

1. **Explore data**: Try queries in YASGUI (http://localhost:8080)
2. **Add more vehicles**: Extend `automotive-instances.ttl`
3. **Create visualizations**: Use Jupyter notebook tutorial
4. **Integrate APIs**: Fetch live pricing data from automotive APIs
5. **Deploy to production**: Scale Fuseki with clustering and replication
6. **Federate queries**: Connect multiple knowledge graphs with SPARQL 1.1 Federation

---

## 📚 Further Reading

### Books
- *Knowledge Graphs* by Hogan et al. (2021) - comprehensive academic overview
- *Semantic Web for the Working Ontologist* by Allemang & Hendler - practical guide
- *Learning SPARQL* by Bob DuCharme - SPARQL query cookbook

### Online Resources
- [W3C OWL 2 Primer](https://www.w3.org/TR/owl2-primer/)
- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/)
- [Apache Jena Documentation](https://jena.apache.org/documentation/)
- [Knowledge Graph Conference](https://www.knowledgegraph.tech/)

### Tools
- [Protégé](https://protege.stanford.edu/) - Ontology editor with visual tools
- [GraphDB](https://www.ontotext.com/products/graphdb/) - Commercial triplestore with advanced features
- [TopBraid Composer](https://www.topquadrant.com/) - SHACL and OWL development environment

---

**You now have a complete understanding of semantic knowledge graphs!** 🎉

This implementation demonstrates enterprise-grade patterns used by companies like Google (Knowledge Graph), Amazon (Neptune), and Microsoft (Graph Engine).

**Happy querying!** 🚀
