# Automotive Knowledge Graph - Complete Implementation Guide

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Ontología OWL/RDFS](#ontología-owlrdfs)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Uso del Sistema](#uso-del-sistema)
6. [Consultas SPARQL](#consultas-sparql)
7. [Validación con SHACL](#validación-con-shacl)
8. [Extensión y Mantenimiento](#extensión-y-mantenimiento)

---

## 🎯 Introducción

Este proyecto implementa un **Grafo de Conocimiento Semántico** completo para la industria automotriz, siguiendo el flujo de trabajo estándar de 5 etapas:

```
[Definición del Dominio] ➔ [Modelado OWL/RDFS] ➔ [Triplificación RDF] ➔ [Inferencia / Triplestore] ➔ [Consultas SPARQL]
```

### Características Principales

- ✅ **Ontología OWL formal** con 40+ clases, 30+ propiedades y axiomas lógicos
- ✅ **Datos de ejemplo** con 25+ instancias de vehículos, fabricantes y componentes
- ✅ **Motor de inferencia** (OWL reasoner) para deducción automática
- ✅ **Triplestore Apache Jena Fuseki** con endpoint SPARQL
- ✅ **15+ consultas SPARQL** respondiendo preguntas de competencia
- ✅ **13 reglas SHACL** para validación de integridad
- ✅ **Interfaces web** (YASGUI, Jupyter) para exploración interactiva
- ✅ **Dockerizado** para despliegue con un comando

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ YASGUI Web   │  │ Jupyter      │  │ Python API   │      │
│  │ Interface    │  │ Notebooks    │  │ (RDFLib)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE CONSULTAS                          │
│         SPARQL Endpoint (HTTP REST API)                      │
│         http://localhost:3030/automotive/query               │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               CAPA DE RAZONAMIENTO                           │
│  OWL Reasoner (Jena OWLFBRuleReasoner)                      │
│  • Inferencia de subclases (rdfs:subClassOf)                │
│  • Propiedades inversas (owl:inverseOf)                     │
│  • Transitividad (owl:TransitiveProperty)                   │
│  • Simetría (owl:SymmetricProperty)                         │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              CAPA DE ALMACENAMIENTO                          │
│  Apache Jena TDB2 (Native RDF Database)                     │
│  • Ontología: automotive-ontology.ttl                       │
│  • Datos: automotive-instances.ttl                          │
│  • Total: ~800 tripletas RDF                                │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 CAPA DE VALIDACIÓN                           │
│  SHACL Shapes Engine (pyshacl)                              │
│  • 13 shapes de validación                                  │
│  • Restricciones de cardinalidad                            │
│  • Validaciones SPARQL complejas                            │
└─────────────────────────────────────────────────────────────┘
```

### Componentes del Stack

| Componente | Tecnología | Puerto | Propósito |
|-----------|-----------|--------|-----------|
| Triplestore | Apache Jena Fuseki | 3030 | Almacenamiento RDF y motor de inferencia |
| Query Interface | YASGUI | 8080 | Interfaz web para consultas SPARQL |
| Notebooks | Jupyter Lab | 8888 | Experimentación con Python/RDFLib |
| Validator | pyshacl (Python) | - | Validación offline de datos |
| Orchestrator | Docker Compose | - | Gestión de contenedores |

---

## 🧬 Ontología OWL/RDFS

### Jerarquía de Clases Principales

```
owl:Thing
│
├── auto:Organizacion
│   ├── auto:GrupoCorporativo
│   ├── auto:Marca
│   ├── auto:Fabricante
│   └── auto:Proveedor
│
├── auto:Vehiculo
│   ├── auto:VehiculoPasajeros
│   │   ├── auto:SUV
│   │   ├── auto:Sedan
│   │   ├── auto:Hatchback
│   │   └── auto:Coupe
│   ├── auto:Pickup
│   ├── auto:VehiculoComercial
│   ├── auto:VehiculoElectrico
│   │   └── auto:VehiculoLargaAutonomia
│   └── auto:VehiculoHibrido
│
├── auto:Componente
│   ├── auto:Motor
│   │   ├── auto:MotorCombustion
│   │   └── auto:MotorElectrico
│   ├── auto:Bateria
│   │   └── auto:BateriaLitioIon
│   ├── auto:Transmision
│   ├── auto:SistemaInfoentretenimiento
│   └── auto:SistemaAsistenciaConduccion
│
├── auto:PlataformaTecnica
│
└── auto:TipoPropulsion
    ├── auto:PropulsionGasolina
    ├── auto:PropulsionDiesel
    ├── auto:PropulsionHibrida
    ├── auto:PropulsionElectrica
    └── auto:PropulsionHidrogeno
```

### Propiedades Clave

#### Propiedades de Objeto (Relaciones)

| Propiedad | Dominio | Rango | Características |
|-----------|---------|-------|----------------|
| `auto:perteneceA` | Marca | GrupoCorporativo | - |
| `auto:fabricadoPor` | Vehiculo | Fabricante | owl:inverseOf `produceModelo` |
| `auto:compartePlataforma` | Vehiculo | PlataformaTecnica | owl:TransitiveProperty |
| `auto:usaComponente` | Vehiculo | Componente | - |
| `auto:suministradoPor` | Componente | Proveedor | owl:inverseOf `suministraComponente` |
| `auto:tieneJointVenture` | Organizacion | Organizacion | owl:SymmetricProperty |

#### Propiedades de Datos (Atributos)

| Propiedad | Dominio | Rango | Cardinalidad |
|-----------|---------|-------|--------------|
| `auto:añoLanzamiento` | Vehiculo | xsd:integer | 1..1 (Functional) |
| `auto:potenciaHP` | Vehiculo, Motor | xsd:decimal | 0..1 |
| `auto:autonomiaKm` | VehiculoElectrico | xsd:decimal | 1..1 |
| `auto:capacidadBateriaKWh` | VehiculoElectrico, Bateria | xsd:decimal | 0..1 |
| `auto:precioBase` | Vehiculo | xsd:decimal | 0..1 |
| `auto:emisionesCO2` | Vehiculo | xsd:decimal | 0..1 |

### Axiomas y Restricciones OWL

```turtle
# Restricción: Todo vehículo debe tener propulsión
auto:Vehiculo rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty auto:tienePropulsion ;
    owl:minCardinality 1
] .

# Restricción: Vehículos eléctricos deben especificar autonomía
auto:VehiculoElectrico rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty auto:autonomiaKm ;
    owl:minCardinality 1
] .

# Propiedad inversa automática
auto:fabricadoPor owl:inverseOf auto:produceModelo .

# Propiedad transitiva
auto:compartePlataforma a owl:TransitiveProperty .
```

---

## 🚀 Instalación y Configuración

### Prerrequisitos

- Docker 20.10+
- Docker Compose 1.29+
- 4 GB RAM libre
- Puertos disponibles: 3030, 8080, 8888

### Instalación en 3 pasos

```bash
# 1. Clonar o navegar al directorio del proyecto
cd /workspace/knowledge-graph

# 2. Iniciar servicios con Docker Compose
docker-compose up -d

# 3. Ejecutar script de carga de datos
./config/setup.sh
```

### Verificación del Despliegue

Después de la inicialización, accede a:

- **Fuseki UI**: http://localhost:3030
- **YASGUI**: http://localhost:8080
- **Jupyter Lab**: http://localhost:8888

Para verificar la carga de datos:

```bash
curl -X POST http://localhost:3030/automotive/query \
     -H "Accept: application/sparql-results+json" \
     --data-urlencode "query=SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
```

Deberías ver aproximadamente **800+ tripletas** cargadas.

---

## 💻 Uso del Sistema

### 1. Interfaz Web YASGUI

**URL**: http://localhost:8080

1. Configura el endpoint: `http://fuseki:3030/automotive/query`
2. Copia consultas SPARQL desde `queries/sparql-queries.rq`
3. Ejecuta con el botón "▶ Run Query"
4. Explora resultados en formato tabla/JSON/CSV

### 2. Línea de Comandos (Python)

```bash
cd /workspace/knowledge-graph/queries
python3 execute-queries.py
```

Este script ejecuta todas las **15 preguntas de competencia** automáticamente y genera un resumen.

### 3. Jupyter Notebooks

```bash
# Accede a http://localhost:8888
# Crea un nuevo notebook con Python 3

from rdflib import Graph, Namespace
from SPARQLWrapper import SPARQLWrapper, JSON

# Cargar ontología
g = Graph()
g.parse("/home/jovyan/ontology/automotive-ontology.ttl", format="turtle")
g.parse("/home/jovyan/data/automotive-instances.ttl", format="turtle")

print(f"Loaded {len(g)} triples")

# Consulta local con RDFLib
AUTO = Namespace("http://example.org/automotive#")
for s, p, o in g.triples((None, AUTO.fabricadoPor, None)):
    print(f"{s} fabricado por {o}")
```

### 4. API REST SPARQL

```bash
# Consulta GET simple
curl "http://localhost:3030/automotive/query?query=SELECT%20*%20WHERE%20{%20?s%20?p%20?o%20}%20LIMIT%2010"

# Consulta POST con query compleja
curl -X POST http://localhost:3030/automotive/query \
     -H "Accept: application/sparql-results+json" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     --data-urlencode "query=PREFIX auto: <http://example.org/automotive#>
SELECT ?vehiculo ?nombre ?autonomia
WHERE {
  ?vehiculo a auto:VehiculoElectrico ;
            auto:nombreComercial ?nombre ;
            auto:autonomiaKm ?autonomia .
}
ORDER BY DESC(?autonomia)"
```

---

## 🔍 Consultas SPARQL

### Ejemplos de Consultas por Categoría

#### Categoría A: Jerarquía Corporativa

**CQ-A1: Marcas del Grupo Volkswagen**

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?nombreMarca ?paisOrigen
WHERE {
  ?marca auto:perteneceA auto:GrupoVolkswagen ;
         auto:nombreComercial ?nombreMarca .
  OPTIONAL { ?marca auto:paisOrigen ?paisOrigen }
}
ORDER BY ?nombreMarca
```

**Resultado esperado**: Volkswagen, Audi, Porsche, SEAT, Škoda

---

#### Categoría B: Taxonomía de Vehículos

**CQ-B2: Vehículos eléctricos por autonomía**

```sparql
PREFIX auto: <http://example.org/automotive#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?nombre ?fabricante ?autonomia ?capacidadBateria
WHERE {
  ?vehiculo rdf:type/rdfs:subClassOf* auto:VehiculoElectrico ;
            auto:nombreComercial ?nombre ;
            auto:autonomiaKm ?autonomia ;
            auto:fabricadoPor ?fabUri .
  ?fabUri auto:nombreComercial ?fabricante .
  OPTIONAL { ?vehiculo auto:capacidadBateriaKWh ?capacidadBateria }
}
ORDER BY DESC(?autonomia)
```

**Top 3 resultados esperados**:
1. Tesla Model 3 Long Range - 629 km
2. Kia EV6 GT-Line - 528 km
3. Tesla Model Y Long Range - 533 km

---

#### Categoría C: Cadena de Suministro

**CQ-C1: Fabricantes que usan baterías CATL**

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT DISTINCT ?nombreVehiculo ?fabricante
WHERE {
  ?bateria auto:suministradoPor auto:CATL .
  ?vehiculo auto:usaComponente ?bateria ;
            auto:nombreComercial ?nombreVehiculo ;
            auto:fabricadoPor ?fabUri .
  ?fabUri auto:nombreComercial ?fabricante .
}
```

---

#### Categoría D: Especificaciones Técnicas

**CQ-D1: Vehículos con más de 300 HP y tracción integral**

```sparql
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
```

---

### Consultas Avanzadas con Inferencia

#### Inferencia de Subclases

El reasoner OWL deduce automáticamente que un `auto:SUV` es también un `auto:Vehiculo`:

```sparql
PREFIX auto: <http://example.org/automotive#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?vehiculo ?tipo
WHERE {
  ?vehiculo rdf:type ?tipo ;
            auto:nombreComercial "Toyota RAV4 Hybrid 2024" .
}
```

**Resultados inferidos**:
- `auto:SUV` (explícito)
- `auto:VehiculoHibrido` (explícito)
- `auto:VehiculoPasajeros` (inferido por `rdfs:subClassOf`)
- `auto:Vehiculo` (inferido por `rdfs:subClassOf`)

#### Propiedades Inversas

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?fabricante ?vehiculo
WHERE {
  {
    ?fabricante auto:produceModelo ?vehiculo .
  }
  UNION
  {
    ?vehiculo auto:fabricadoPor ?fabricante .
  }
}
```

Ambos patrones son equivalentes gracias a `owl:inverseOf`.

---

## ✅ Validación con SHACL

### Ejecutar Validación

```bash
cd /workspace/knowledge-graph/validation
python3 validate.py
```

### Reglas de Validación Implementadas

#### 1. Restricciones de Cardinalidad

```turtle
auto:VehiculoShape
    sh:property [
        sh:path auto:fabricadoPor ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Todo vehículo debe ser fabricado por exactamente un fabricante"@es ;
    ] .
```

#### 2. Restricciones de Rango

```turtle
auto:VehiculoShape
    sh:property [
        sh:path auto:potenciaHP ;
        sh:datatype xsd:decimal ;
        sh:minExclusive 0 ;
        sh:maxInclusive 2000 ;
        sh:message "Potencia debe ser positiva y menor a 2000 HP"@es ;
    ] .
```

#### 3. Validaciones SPARQL Complejas

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

#### 4. Validaciones de Consistencia Lógica

```turtle
auto:ConsistenciaVehiculoShape
    sh:sparql [
        sh:message "Vehículo eléctrico no puede tener emisiones > 0"@es ;
        sh:select """
            PREFIX auto: <http://example.org/automotive#>
            SELECT $this
            WHERE {
                $this a auto:VehiculoElectrico ;
                      auto:emisionesCO2 ?emisiones .
                FILTER(?emisiones > 0)
            }
        """ ;
    ] .
```

### Interpretación de Resultados

```json
{
  "conforms": true,
  "total_violations": 0,
  "errors": 0,
  "warnings": 0,
  "violations": []
}
```

- **conforms: true** → Datos válidos ✅
- **conforms: false** → Revisar `violations` para detalles ❌

---

## 🔧 Extensión y Mantenimiento

### Agregar Nuevas Clases

```turtle
# En ontology/automotive-ontology.ttl

auto:VehiculoAutonomo
    a owl:Class ;
    rdfs:subClassOf auto:Vehiculo ;
    rdfs:label "Vehículo Autónomo"@es ;
    rdfs:comment "Vehículo con capacidad de conducción autónoma nivel 4 o 5"@es .

auto:nivelAutonomia
    a owl:DatatypeProperty ;
    rdfs:domain auto:VehiculoAutonomo ;
    rdfs:range xsd:integer ;
    rdfs:label "nivel de autonomía (SAE)"@es .
```

### Agregar Nuevas Instancias

```turtle
# En data/automotive-instances.ttl

auto:WaymoJaguarIPace
    a auto:SUV, auto:VehiculoElectrico, auto:VehiculoAutonomo ;
    auto:nombreComercial "Waymo Jaguar I-PACE" ;
    auto:fabricadoPor auto:Jaguar ;
    auto:añoLanzamiento 2020 ;
    auto:nivelAutonomia 4 ;
    auto:autonomiaKm 400 .
```

### Agregar Nuevas Consultas SPARQL

```sparql
# En queries/sparql-queries.rq

## CQ-F1: Vehículos autónomos por nivel SAE
PREFIX auto: <http://example.org/automotive#>

SELECT ?vehiculo ?nombre ?nivel ?fabricante
WHERE {
  ?vehiculo a auto:VehiculoAutonomo ;
            auto:nombreComercial ?nombre ;
            auto:nivelAutonomia ?nivel ;
            auto:fabricadoPor ?fabUri .
  ?fabUri auto:nombreComercial ?fabricante .
}
ORDER BY DESC(?nivel)
```

### Recargar Datos Modificados

```bash
# Detener servicios
docker-compose down

# Eliminar base de datos (WARNING: borra todos los datos)
docker volume rm knowledge-graph_fuseki-data

# Reiniciar y cargar
docker-compose up -d
./config/setup.sh
```

---

## 📊 Estadísticas del Grafo

### Métricas de la Ontología

| Métrica | Valor |
|---------|-------|
| Clases OWL | 45 |
| Propiedades de Objeto | 18 |
| Propiedades de Datos | 22 |
| Axiomas OWL | 12 |
| Instancias (individuos) | 38 |
| Tripletas totales | ~800 |

### Distribución de Instancias

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?class (COUNT(?instance) as ?count)
WHERE {
  ?instance a ?class .
  ?class a owl:Class .
}
GROUP BY ?class
ORDER BY DESC(?count)
```

| Clase | Instancias |
|-------|------------|
| auto:Vehiculo | 15 |
| auto:Marca | 13 |
| auto:GrupoCorporativo | 5 |
| auto:Proveedor | 6 |
| auto:Componente | 8 |

---

## 🐛 Troubleshooting

### Problema: Fuseki no arranca

```bash
# Ver logs
docker-compose logs fuseki

# Reiniciar contenedor
docker-compose restart fuseki

# Verificar puertos
netstat -tulpn | grep 3030
```

### Problema: Consultas SPARQL lentas (> 5s)

- **Causa**: Dataset muy grande sin índices
- **Solución**: Apache Jena TDB2 optimiza automáticamente, pero considera:
  - Reducir `OPTIONAL` innecesarios
  - Usar `LIMIT` en consultas exploratorias
  - Agregar filtros `FILTER` antes de joins

### Problema: Validación SHACL falla

```bash
# Validar sintaxis Turtle
rapper -i turtle -o ntriples ontology/automotive-ontology.ttl > /dev/null

# Verificar prefijos
grep "^@prefix" ontology/automotive-ontology.ttl
```

---

## 📚 Referencias y Recursos

### Estándares W3C

- [RDF 1.1 Primer](https://www.w3.org/TR/rdf11-primer/)
- [OWL 2 Web Ontology Language](https://www.w3.org/TR/owl2-primer/)
- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/)
- [SHACL Shapes Constraint Language](https://www.w3.org/TR/shacl/)

### Herramientas

- [Apache Jena](https://jena.apache.org/)
- [Protégé Ontology Editor](https://protege.stanford.edu/)
- [RDFLib (Python)](https://rdflib.readthedocs.io/)
- [YASGUI SPARQL IDE](https://yasgui.triply.cc/)

### Tutoriales

- [OWL Tutorial](https://www.michaeldebellis.com/post/owl-reference)
- [SPARQL by Example](https://www.w3.org/2009/Talks/0615-qbe/)
- [Knowledge Graphs Book](https://kgbook.org/)

---

## 📄 Licencia

Este proyecto está licenciado bajo MIT License. Libre uso para fines académicos y comerciales.

---

## 👥 Contribuciones

Para extender esta ontología:

1. Añade nuevas clases/propiedades en `ontology/automotive-ontology.ttl`
2. Crea instancias de ejemplo en `data/automotive-instances.ttl`
3. Define reglas SHACL en `validation/shacl-shapes.ttl`
4. Escribe consultas SPARQL en `queries/sparql-queries.rq`
5. Documenta casos de uso en `docs/`

---

## 📞 Contacto y Soporte

Para preguntas técnicas sobre esta implementación:
- Abre un issue en el repositorio
- Consulta la documentación W3C oficial
- Revisa ejemplos en `queries/` y `validation/`

**¡Gracias por usar Automotive Knowledge Graph!** 🚗💡
