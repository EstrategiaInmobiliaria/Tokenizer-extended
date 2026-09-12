# Guía Rápida de Inicio - Knowledge Graph Automotriz

## 🚀 Inicio Rápido (5 minutos)

### Paso 1: Verificar Prerrequisitos

```bash
# Verificar Docker
docker --version
# Esperado: Docker version 20.10+ 

# Verificar Docker Compose
docker-compose --version
# Esperado: docker-compose version 1.29+

# Verificar puertos disponibles
netstat -tulpn | grep -E '3030|8080|8888'
# Debería estar vacío
```

### Paso 2: Desplegar Sistema

```bash
cd /workspace/knowledge-graph

# Iniciar contenedores (toma ~30 segundos)
docker-compose up -d

# Esperar 10 segundos para que Fuseki arranque
sleep 10

# Cargar ontología y datos
./config/setup.sh
```

**Salida esperada**:
```
✅ Fuseki is ready!
📥 Loading automotive-ontology.ttl into graph: http://example.org/automotive/ontology
   HTTP Status: 200
📥 Loading automotive-instances.ttl into graph: http://example.org/automotive/data
   HTTP Status: 200
   Total triples loaded: 847
✅ Setup complete!
```

### Paso 3: Verificar Servicios

```bash
# Test Fuseki endpoint
curl -s http://localhost:3030/$/ping

# Test YASGUI
curl -s http://localhost:8080 | grep -q "YASGUI" && echo "YASGUI OK"

# Test Jupyter
curl -s http://localhost:8888 | grep -q "Jupyter" && echo "Jupyter OK"
```

---

## 🔍 Primera Consulta SPARQL

### Opción A: Interfaz Web (Recomendado)

1. Abre http://localhost:8080 en tu navegador
2. Configura endpoint: `http://fuseki:3030/automotive/query`
3. Pega esta consulta:

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?nombre ?fabricante ?autonomia
WHERE {
  ?vehiculo a auto:VehiculoElectrico ;
            auto:nombreComercial ?nombre ;
            auto:autonomiaKm ?autonomia ;
            auto:fabricadoPor ?fabUri .
  ?fabUri auto:nombreComercial ?fabricante .
}
ORDER BY DESC(?autonomia)
LIMIT 5
```

4. Presiona **▶ Run Query**

**Resultado esperado**: Top 5 vehículos eléctricos por autonomía

### Opción B: Línea de Comandos

```bash
curl -X POST http://localhost:3030/automotive/query \
     -H "Accept: text/csv" \
     --data-urlencode "query=PREFIX auto: <http://example.org/automotive#>
SELECT ?nombre ?fabricante ?autonomia
WHERE {
  ?vehiculo a auto:VehiculoElectrico ;
            auto:nombreComercial ?nombre ;
            auto:autonomiaKm ?autonomia ;
            auto:fabricadoPor ?fabUri .
  ?fabUri auto:nombreComercial ?fabricante .
}
ORDER BY DESC(?autonomia)"
```

---

## 📊 Ejecutar Todas las Consultas

```bash
cd /workspace/knowledge-graph/queries

# Instalar dependencias (primera vez)
pip3 install -r ../requirements.txt

# Ejecutar script de pruebas
python3 execute-queries.py
```

**Salida esperada**:
```
🔍 SPARQL Query Executor - Automotive Knowledge Graph
✅ Connected to endpoint: http://localhost:3030/automotive/query

Query: CQ-B2 - Vehículos eléctricos por autonomía
✅ Found 5 results in 42.15ms

  nombre: Tesla Model 3 Long Range AWD
  fabricante: Tesla, Inc.
  autonomia: 629

  nombre: Kia EV6 GT-Line AWD
  fabricante: Kia
  autonomia: 528

...

SUMMARY
Total queries executed: 8
Successful: 8 / 8
Average query time: 38.27ms
```

---

## ✅ Validar Datos con SHACL

```bash
cd /workspace/knowledge-graph/validation

# Instalar pyshacl (primera vez)
pip3 install pyshacl rdflib

# Ejecutar validación
python3 validate.py
```

**Salida esperada (datos válidos)**:
```
🔍 SHACL Validator - Automotive Knowledge Graph
📚 Loading RDF graphs...
✅ Loaded 423 triples from automotive-ontology.ttl
✅ Loaded 424 triples from automotive-instances.ttl
✅ Loaded 158 triples from shacl-shapes.ttl
✅ Combined graph: 847 triples

SHACL VALIDATION
✅ VALIDATION PASSED - Data conforms to all SHACL shapes!
   Total triples validated: 847
```

---

## 🧪 Jupyter Notebook (Exploración Interactiva)

1. Abre http://localhost:8888
2. Crea un nuevo notebook Python 3
3. Ejecuta este código:

```python
from rdflib import Graph, Namespace
from SPARQLWrapper import SPARQLWrapper, JSON

# Cargar datos localmente
g = Graph()
g.parse("/home/jovyan/ontology/automotive-ontology.ttl", format="turtle")
g.parse("/home/jovyan/data/automotive-instances.ttl", format="turtle")

print(f"✅ Loaded {len(g)} triples")

# Consulta con RDFLib
AUTO = Namespace("http://example.org/automotive#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

electric_vehicles = []
for s in g.subjects(RDF.type, AUTO.VehiculoElectrico):
    name = g.value(s, AUTO.nombreComercial)
    autonomy = g.value(s, AUTO.autonomiaKm)
    electric_vehicles.append((str(name), float(autonomy)))

# Ordenar por autonomía
electric_vehicles.sort(key=lambda x: x[1], reverse=True)

print("\n🚗 Vehículos Eléctricos por Autonomía:")
for name, autonomy in electric_vehicles:
    print(f"  {name}: {autonomy} km")
```

**Salida esperada**:
```
✅ Loaded 847 triples

🚗 Vehículos Eléctricos por Autonomía:
  Tesla Model 3 Long Range AWD: 629.0 km
  Tesla Model Y Long Range AWD: 533.0 km
  Kia EV6 GT-Line AWD: 528.0 km
  Hyundai IONIQ 5 Long Range AWD: 507.0 km
  BMW iX3: 461.0 km
```

---

## 🎯 Consultas Recomendadas para Empezar

### 1. Ver todas las marcas del Grupo Volkswagen

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?nombreMarca ?paisOrigen
WHERE {
  ?marca auto:perteneceA auto:GrupoVolkswagen ;
         auto:nombreComercial ?nombreMarca ;
         auto:paisOrigen ?paisOrigen .
}
```

### 2. Vehículos con más de 300 HP

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?nombre ?fabricante ?potencia ?aceleracion
WHERE {
  ?vehiculo auto:nombreComercial ?nombre ;
            auto:potenciaHP ?potencia ;
            auto:fabricadoPor ?fabUri .
  ?fabUri auto:nombreComercial ?fabricante .
  OPTIONAL { ?vehiculo auto:aceleracion0a100 ?aceleracion }
  FILTER(?potencia > 300)
}
ORDER BY DESC(?potencia)
```

### 3. Modelos que comparten plataforma MQB

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?nombreVehiculo ?fabricante
WHERE {
  ?vehiculo auto:compartePlataforma auto:PlataformaMQB ;
            auto:nombreComercial ?nombreVehiculo ;
            auto:fabricadoPor ?fabUri .
  ?fabUri auto:nombreComercial ?fabricante .
}
```

### 4. Proveedores de baterías

```sparql
PREFIX auto: <http://example.org/automotive#>

SELECT ?proveedor ?bateria ?vehiculo
WHERE {
  ?bateria a auto:Bateria ;
           auto:suministradoPor ?provUri ;
           auto:nombreComercial ?nombreBateria .
  ?provUri auto:nombreComercial ?proveedor .
  
  OPTIONAL {
    ?vehiculo auto:usaComponente ?bateria ;
              auto:nombreComercial ?nombreVehiculo .
  }
}
```

---

## 🛑 Detener y Limpiar

```bash
# Detener contenedores (conserva datos)
docker-compose stop

# Detener y eliminar contenedores (conserva volúmenes)
docker-compose down

# CUIDADO: Eliminar TODO (incluyendo datos cargados)
docker-compose down -v
```

---

## ❓ Problemas Comunes

### Error: "Port 3030 already in use"

```bash
# Encontrar proceso usando el puerto
sudo lsof -i :3030

# Matar proceso o cambiar puerto en docker-compose.yml
ports:
  - "3031:3030"  # Usa puerto externo 3031
```

### Error: "Cannot connect to endpoint"

```bash
# Verificar que Fuseki esté corriendo
docker-compose ps

# Ver logs de Fuseki
docker-compose logs fuseki

# Reintentar setup
./config/setup.sh
```

### Error: "Validation fails with import errors"

```bash
# Instalar dependencias Python
pip3 install --upgrade rdflib pyshacl SPARQLWrapper

# Verificar sintaxis Turtle
rapper -i turtle -o ntriples ontology/automotive-ontology.ttl
```

---

## 📚 Próximos Pasos

1. **Explorar más consultas**: Revisa `queries/sparql-queries.rq`
2. **Añadir tus propios vehículos**: Edita `data/automotive-instances.ttl`
3. **Crear nuevas clases**: Modifica `ontology/automotive-ontology.ttl`
4. **Validar reglas de negocio**: Agrega shapes en `validation/shacl-shapes.ttl`
5. **Leer documentación completa**: Abre `README.md`

---

## 🎓 Recursos de Aprendizaje

- **SPARQL Tutorial**: https://www.w3.org/TR/sparql11-query/
- **OWL Primer**: https://www.w3.org/TR/owl2-primer/
- **SHACL Reference**: https://www.w3.org/TR/shacl/
- **RDFLib Docs**: https://rdflib.readthedocs.io/

---

**¡Listo! Ya tienes un grafo de conocimiento funcional.** 🎉

Ahora puedes explorar las 800+ tripletas RDF con consultas SPARQL o en Jupyter.
