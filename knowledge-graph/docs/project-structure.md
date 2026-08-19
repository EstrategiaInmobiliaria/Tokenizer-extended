# Knowledge Graph Project Structure

## Directory Organization

```
knowledge-graph/
├── README.md                          # Main documentation and usage guide
├── docker-compose.yml                 # Docker orchestration configuration
├── requirements.txt                   # Python dependencies
│
├── config/                            # Configuration files
│   ├── fuseki-config.ttl             # Apache Jena Fuseki triplestore config
│   └── setup.sh                      # Automated setup and data loading script
│
├── ontology/                          # OWL/RDFS ontology definitions
│   └── automotive-ontology.ttl       # Core ontology (classes, properties, axioms)
│
├── data/                              # RDF instance data
│   └── automotive-instances.ttl      # Sample data (vehicles, companies, components)
│
├── queries/                           # SPARQL queries
│   ├── sparql-queries.rq             # Collection of competency questions queries
│   └── execute-queries.py            # Python script to batch execute queries
│
├── validation/                        # Data validation rules
│   ├── shacl-shapes.ttl              # SHACL constraint definitions
│   ├── validate.py                   # SHACL validation script
│   └── validation-results.json       # Output of validation (generated)
│
├── docs/                              # Documentation
│   ├── 01-competency-questions.md    # Domain specification and CQs
│   └── architecture-diagram.md       # System architecture (optional)
│
└── notebooks/                         # Jupyter notebooks (mounted in Docker)
    └── (user-created notebooks)       # Exploratory analysis and testing
```

## File Descriptions

### Root Level

- **README.md**: Complete implementation guide with architecture, installation, usage examples, and SPARQL query documentation
- **docker-compose.yml**: Defines 4 services: Fuseki (triplestore), YASGUI (SPARQL IDE), Jupyter (notebooks), and configuration
- **requirements.txt**: Python dependencies for RDFLib, pyshacl, SPARQLWrapper, and Jupyter

### config/

Contains triplestore configuration and deployment automation:

- **fuseki-config.ttl**: Jena Fuseki dataset configuration with OWL reasoner (OWLFBRuleReasoner)
- **setup.sh**: Bash script to:
  1. Start Docker containers
  2. Wait for Fuseki readiness
  3. Create dataset
  4. Load ontology and instance data
  5. Verify triple count

### ontology/

Formal OWL/RDFS ontology definition:

- **automotive-ontology.ttl**: 
  - 45 classes (Vehiculo, Empresa, Componente hierarchies)
  - 18 object properties (fabricadoPor, usaComponente, etc.)
  - 22 datatype properties (añoLanzamiento, potenciaHP, autonomiaKm, etc.)
  - OWL axioms: inverseOf, TransitiveProperty, SymmetricProperty
  - Domain/range restrictions and cardinality constraints

### data/

RDF instance data (A-Box):

- **automotive-instances.ttl**:
  - 5 corporate groups (Volkswagen, Toyota, Hyundai, BMW, Stellantis)
  - 13 brands (VW, Audi, Toyota, Lexus, Hyundai, Kia, BMW, Ford, Tesla, etc.)
  - 15 vehicle instances (RAV4 Hybrid, Model 3, IONIQ 5, etc.)
  - 6 suppliers (Bosch, CATL, LG Energy Solution, Harman, ZF, Panasonic)
  - 8 components (batteries, motors, transmissions, infotainment)
  - 4 technical platforms (MQB, TNGA, E-GMP, CLAR)

### queries/

SPARQL queries organized by competency question categories:

- **sparql-queries.rq**: 15+ queries covering:
  - **Category A**: Corporate hierarchy (brands per group, joint ventures)
  - **Category B**: Vehicle taxonomy (SUVs by year, EVs by range, shared platforms)
  - **Category C**: Supply chain (components by supplier, multi-brand parts)
  - **Category D**: Technical specs (HP + AWD filters, weight/power ratios, emissions compliance)
  - **Category E**: Temporal evolution (launches per year, discontinued models)
  - **Advanced**: Inference queries (subclass reasoning, inverse properties)
  - **Diagnostics**: Triple counts, class instances, integrity checks

- **execute-queries.py**: Python script using SPARQLWrapper to:
  - Execute all 15 competency questions
  - Measure query execution time
  - Pretty-print results
  - Generate summary statistics

### validation/

SHACL-based data integrity validation:

- **shacl-shapes.ttl**: 13 shape definitions:
  1. **VehiculoShape**: Mandatory fields, year ranges, HP/weight limits
  2. **VehiculoElectricoShape**: Autonomy and battery capacity requirements
  3. **VehiculoHibridoShape**: Hybrid-specific emissions rules
  4. **OrganizacionShape**: Company name and founding year validation
  5. **MarcaShape**: Brand-to-group relationship constraints
  6. **ComponenteShape**: Supplier association rules
  7. **BateriaShape**: Battery capacity ranges
  8. **MotorCombustionShape**: Engine displacement and power rules
  9. **PlataformaTecnicaShape**: Platform must be used by vehicles
  10. **ConsistenciaVehiculoShape**: Logical consistency (weight/power ratio, EV emissions)
  11. **PrecioVehiculoShape**: Business rules (e.g., premium EV range warnings)
  12. **EspecificacionesTecnicasShape**: Acceleration, top speed, CO2 ranges
  13. **CodigoModeloShape**: Model code format validation (regex)

- **validate.py**: pyshacl wrapper script to:
  - Load ontology + data graphs
  - Execute SHACL validation with RDFS inference
  - Parse and categorize violations (errors vs. warnings)
  - Output detailed JSON report

- **validation-results.json**: Generated output with violation details

### docs/

Project documentation:

- **01-competency-questions.md**: 
  - Domain scope definition
  - 15 competency questions across 5 categories
  - Expected query results
  - Use case scenarios (competitive analysis, supply chain optimization, platform sharing)
  - Success metrics (query performance, inference correctness)

### notebooks/

(Directory created by Docker mount, initially empty)

Users can create Jupyter notebooks for:
- Exploratory RDF queries with RDFLib
- Graph visualization with NetworkX
- Custom Python SPARQL queries
- Statistical analysis of vehicle specifications
- Ontology extension experiments

## Data Flow

```
1. Ontology Definition (ontology/*.ttl)
   ↓
2. Instance Data (data/*.ttl)
   ↓
3. Validation (validation/shacl-shapes.ttl)
   ↓ (if valid)
4. Loading into Triplestore (config/setup.sh)
   ↓
5. Inference Application (OWL Reasoner)
   ↓
6. SPARQL Queries (queries/*.rq)
   ↓
7. Results Presentation (YASGUI, Jupyter, Python scripts)
```

## Service Ports

| Service | Internal Port | External Port | Purpose |
|---------|---------------|---------------|---------|
| Fuseki | 3030 | 3030 | SPARQL endpoint and admin UI |
| YASGUI | 80 | 8080 | Web-based SPARQL query interface |
| Jupyter | 8888 | 8888 | Notebook environment (no auth) |

## Key Technologies

- **Apache Jena TDB2**: Native RDF triple store with indexing
- **Jena OWLFBRuleReasoner**: Forward-chaining OWL reasoner (RDFS + OWL subset)
- **YASGUI**: JavaScript SPARQL IDE with syntax highlighting and result export
- **pyshacl**: Python SHACL validator with RDFS/OWL inference support
- **RDFLib**: Python library for RDF parsing, querying, and serialization
- **Docker Compose**: Multi-container orchestration

## Getting Started

1. **Deploy**: `docker-compose up -d`
2. **Load Data**: `./config/setup.sh`
3. **Query**: Open http://localhost:8080
4. **Validate**: `cd validation && python3 validate.py`
5. **Explore**: Open http://localhost:8888 for Jupyter

## Extending the System

### Add a New Vehicle Class

1. Edit `ontology/automotive-ontology.ttl` → add class definition
2. Create instances in `data/automotive-instances.ttl`
3. Add SHACL constraints in `validation/shacl-shapes.ttl`
4. Write queries in `queries/sparql-queries.rq`
5. Reload: `docker-compose restart fuseki && ./config/setup.sh`

### Connect External Data

- Use R2RML mapping to convert relational databases to RDF
- Implement ETL pipelines with `rdflib` and `pandas`
- Set up federated SPARQL queries with `SERVICE` keyword

## Troubleshooting

- **Fuseki won't start**: Check port 3030 availability with `netstat -tulpn | grep 3030`
- **Data not loading**: Verify Turtle syntax with `rapper -i turtle -o ntriples <file.ttl>`
- **Validation errors**: Review `validation/validation-results.json` for specific violations
- **Query timeout**: Add `LIMIT` clauses or optimize with `FILTER` before joins

## License

MIT License - Free for academic and commercial use
