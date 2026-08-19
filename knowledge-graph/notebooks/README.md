# Jupyter Notebooks - Automotive Knowledge Graph

This directory contains interactive Jupyter notebooks for exploring and analyzing the automotive knowledge graph using Python.

## 📓 Available Notebooks

### `automotive-kg-tutorial.ipynb`

**Complete interactive tutorial covering:**

1. **Setup & Dependencies**: Load RDFLib, SPARQLWrapper, Pandas, NetworkX
2. **Loading Data**: Parse ontology and instance data from Turtle files
3. **Namespaces**: Configure URI prefixes for querying
4. **Basic RDFLib Queries**: Traverse triples directly in Python
5. **SPARQL Queries**: Execute local queries with RDFLib
6. **Remote Fuseki Queries**: Connect to triplestore via HTTP
7. **Data Analysis**: Use Pandas for statistical analysis
8. **Visualizations**: Create plots with Matplotlib
9. **Graph Visualization**: Render corporate hierarchy with NetworkX
10. **Export Results**: Save to CSV and RDF formats

**Key Features:**
- ✅ Works offline (loads RDF files directly)
- ✅ Also works with Fuseki endpoint (when running)
- ✅ Includes visualizations (scatter plots, bar charts, network graphs)
- ✅ Demonstrates both RDFLib and SPARQLWrapper approaches
- ✅ Production-ready code snippets

## 🚀 Getting Started

### Option 1: Using Docker (Recommended)

```bash
# From project root
docker-compose up -d

# Access Jupyter Lab
open http://localhost:8888

# Navigate to /work/ and open automotive-kg-tutorial.ipynb
```

### Option 2: Local Installation

```bash
# Install dependencies
pip install -r ../requirements.txt

# Start Jupyter
jupyter lab

# Open automotive-kg-tutorial.ipynb
```

## 📚 Prerequisites

### Python Packages (Included in requirements.txt)

```
rdflib>=6.3.2         # RDF parsing and querying
SPARQLWrapper>=2.0.0  # Remote SPARQL queries
pandas>=2.0.0         # Data analysis
matplotlib>=3.7.0     # Plotting
networkx>=3.1         # Graph visualization
jupyter>=1.0.0        # Notebook environment
```

### Data Files (Auto-mounted in Docker)

- `/home/jovyan/ontology/automotive-ontology.ttl` - OWL ontology
- `/home/jovyan/data/automotive-instances.ttl` - Instance data
- `/home/jovyan/queries/sparql-queries.rq` - Query templates

## 🎯 Learning Objectives

After completing the tutorial notebook, you will be able to:

1. ✅ Load and parse RDF/Turtle files with RDFLib
2. ✅ Traverse RDF graphs using Python (subject, predicate, object)
3. ✅ Execute SPARQL queries locally and remotely
4. ✅ Connect to Fuseki triplestore via SPARQLWrapper
5. ✅ Convert RDF results to Pandas DataFrames
6. ✅ Create visualizations (scatter plots, bar charts)
7. ✅ Render knowledge graphs with NetworkX
8. ✅ Export results to CSV and RDF formats
9. ✅ Understand inference vs. explicit triples
10. ✅ Build production RDF applications in Python

## 📖 Usage Examples

### Example 1: List All Electric Vehicles

```python
from rdflib import Graph, Namespace

g = Graph()
g.parse("/home/jovyan/ontology/automotive-ontology.ttl", format="turtle")
g.parse("/home/jovyan/data/automotive-instances.ttl", format="turtle")

AUTO = Namespace("http://example.org/automotive#")

for s in g.subjects(RDF.type, AUTO.VehiculoElectrico):
    name = g.value(s, AUTO.nombreComercial)
    autonomy = g.value(s, AUTO.autonomiaKm)
    print(f"{name}: {autonomy} km")
```

### Example 2: Query Fuseki Endpoint

```python
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://fuseki:3030/automotive/query")
sparql.setQuery("""
    PREFIX auto: <http://example.org/automotive#>
    SELECT ?nombre ?autonomia
    WHERE {
      ?v a auto:VehiculoElectrico ;
         auto:nombreComercial ?nombre ;
         auto:autonomiaKm ?autonomia .
    }
    ORDER BY DESC(?autonomia)
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
```

### Example 3: Analyze with Pandas

```python
import pandas as pd

# Query results to DataFrame
data = []
for result in results["results"]["bindings"]:
    data.append({
        'Model': result['nombre']['value'],
        'Range (km)': float(result['autonomia']['value'])
    })

df = pd.DataFrame(data)
print(df.describe())
```

### Example 4: Visualize with NetworkX

```python
import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

# Query corporate hierarchy
query = """
    PREFIX auto: <http://example.org/automotive#>
    SELECT ?grupo ?marca
    WHERE {
      ?m auto:perteneceA ?g ;
         auto:nombreComercial ?marca .
      ?g auto:nombreComercial ?grupo .
    }
"""

for row in g.query(query):
    G.add_edge(str(row.grupo), str(row.marca))

pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue')
plt.show()
```

## 🔍 Common Use Cases

### Use Case 1: Competitive Analysis

**Goal**: Compare all EVs by range, price, and manufacturer

```python
query = """
    PREFIX auto: <http://example.org/automotive#>
    SELECT ?nombre ?fabricante ?autonomia ?precio
    WHERE {
      ?v a auto:VehiculoElectrico ;
         auto:nombreComercial ?nombre ;
         auto:autonomiaKm ?autonomia ;
         auto:fabricadoPor ?f .
      ?f auto:nombreComercial ?fabricante .
      OPTIONAL { ?v auto:precioBase ?precio }
    }
    ORDER BY DESC(?autonomia)
"""

results = g.query(query)
df = pd.DataFrame([(str(r.nombre), str(r.fabricante), 
                     float(r.autonomia), float(r.precio) if r.precio else None)
                   for r in results],
                  columns=['Model', 'Manufacturer', 'Range (km)', 'Price (USD)'])

# Visualize
df.plot(x='Range (km)', y='Price (USD)', kind='scatter', s=100, figsize=(10,6))
plt.title('Electric Vehicles: Range vs Price')
plt.show()
```

### Use Case 2: Supply Chain Analysis

**Goal**: Identify which suppliers provide components to which manufacturers

```python
query = """
    PREFIX auto: <http://example.org/automotive#>
    SELECT ?proveedor ?componente ?fabricante
    WHERE {
      ?c auto:suministradoPor ?p ;
         auto:nombreComercial ?componente .
      ?p auto:nombreComercial ?proveedor .
      ?v auto:usaComponente ?c ;
         auto:fabricadoPor ?f .
      ?f auto:nombreComercial ?fabricante .
    }
"""

results = g.query(query)
# Create bipartite graph: suppliers → manufacturers
# (implementation in tutorial notebook)
```

### Use Case 3: Platform Sharing Economics

**Goal**: Analyze which models share technical platforms

```python
query = """
    PREFIX auto: <http://example.org/automotive#>
    SELECT ?plataforma (COUNT(?v) as ?count)
    WHERE {
      ?plat a auto:PlataformaTecnica ;
            auto:nombreComercial ?plataforma .
      ?v auto:compartePlataforma ?plat .
    }
    GROUP BY ?plataforma
    HAVING (COUNT(?v) > 1)
"""

# Visualize platform sharing
# Bar chart: platform name vs. number of models
```

## 🛠️ Troubleshooting

### Issue: "Cannot connect to Fuseki"

**Solution**: Ensure Fuseki container is running:

```bash
docker-compose ps
# fuseki should be "Up"

# If not, start it:
docker-compose up -d fuseki
```

### Issue: "Module not found: rdflib"

**Solution**: Install dependencies inside Jupyter:

```python
!pip install rdflib SPARQLWrapper pandas matplotlib networkx
```

Or use terminal:

```bash
docker exec -it automotive-jupyter pip install -r /home/jovyan/requirements.txt
```

### Issue: "File not found: automotive-ontology.ttl"

**Solution**: Check volume mounts in `docker-compose.yml`:

```yaml
volumes:
  - ./ontology:/home/jovyan/ontology:ro
  - ./data:/home/jovyan/data:ro
```

Restart container:

```bash
docker-compose restart jupyter
```

### Issue: "Visualization not displaying"

**Solution**: Enable matplotlib backend:

```python
%matplotlib inline
import matplotlib.pyplot as plt
```

## 📝 Creating New Notebooks

### Template Structure

```python
# 1. Imports
from rdflib import Graph, Namespace, RDF, RDFS
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import matplotlib.pyplot as plt

# 2. Load data
g = Graph()
g.parse("/home/jovyan/ontology/automotive-ontology.ttl", format="turtle")
g.parse("/home/jovyan/data/automotive-instances.ttl", format="turtle")

# 3. Define namespaces
AUTO = Namespace("http://example.org/automotive#")

# 4. Your analysis code here
# ...

# 5. Visualizations
plt.figure(figsize=(10, 6))
# ...
plt.show()

# 6. Export results
df.to_csv('/home/jovyan/work/results.csv', index=False)
```

## 🎓 Additional Resources

### RDFLib Documentation
- [RDFLib Tutorial](https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html)
- [RDFLib SPARQL](https://rdflib.readthedocs.io/en/stable/intro_to_sparql.html)
- [RDFLib Graph Traversal](https://rdflib.readthedocs.io/en/stable/intro_to_graphs.html)

### SPARQLWrapper
- [SPARQLWrapper GitHub](https://github.com/RDFLib/sparqlwrapper)
- [SPARQLWrapper Examples](https://sparqlwrapper.readthedocs.io/en/latest/main.html)

### NetworkX
- [NetworkX Tutorial](https://networkx.org/documentation/stable/tutorial.html)
- [NetworkX Graph Drawing](https://networkx.org/documentation/stable/reference/drawing.html)

## 💡 Tips & Best Practices

### Performance

1. **Cache queries**: Store frequently used results in variables
2. **Limit results**: Use `LIMIT` in SPARQL for exploration
3. **Index DataFrames**: Set index for faster lookups
4. **Lazy evaluation**: Don't materialize all triples upfront

### Code Quality

1. **Use constants**: Define namespace prefixes once
2. **Error handling**: Wrap queries in try/except
3. **Documentation**: Add markdown cells explaining analysis
4. **Modularity**: Extract reusable functions

### Visualization

1. **Label axes**: Always add titles and axis labels
2. **Color scheme**: Use consistent colors across plots
3. **Font size**: Increase for readability (12-14pt)
4. **Export**: Save figures as PNG/SVG for presentations

## 📊 Example Outputs

The tutorial notebook produces:

- **5 DataFrames**: Electric vehicles, all vehicles, brands, performance specs, propulsion types
- **4 Visualizations**: Scatter plot (power vs price), bar chart (propulsion by manufacturer), network graph (corporate hierarchy), histogram (autonomy distribution)
- **3 Export files**: `electric_vehicles.csv`, `all_vehicles.csv`, `vehicles_manufacturers.ttl`

## 🚀 Next Steps

After completing the tutorial:

1. **Modify queries**: Change filters, add aggregations
2. **Add data**: Create new vehicle instances
3. **Custom visualizations**: Try seaborn, plotly, bokeh
4. **Machine learning**: Train models on vehicle specs
5. **API integration**: Fetch live pricing data
6. **Dashboard**: Build interactive Dash/Streamlit app

## 📄 License

MIT License - Free for academic and commercial use

---

**Happy exploring!** 🎉

For questions, refer to the main README or open a GitHub issue.
