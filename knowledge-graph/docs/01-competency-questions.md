# Preguntas de Competencia - Ontología Automotriz

## 1. Definición del Dominio

**Dominio**: Industria Automotriz - Fabricantes, Vehículos, Componentes y Relaciones Comerciales

**Alcance**: 
- Jerarquía de empresas automotrices (grupos corporativos, marcas, subsidiarias)
- Clasificación de vehículos (categorías, segmentos, tipos de propulsión)
- Componentes y sistemas compartidos entre modelos
- Relaciones de manufactura y cadena de suministro
- Especificaciones técnicas y atributos de productos

---

## 2. Preguntas de Competencia (Competency Questions)

### Categoría A: Jerarquía y Relaciones Corporativas

**CQ-A1**: ¿Qué marcas pertenecen a un grupo corporativo específico?
- **Ejemplo**: ¿Qué marcas pertenecen al Grupo Volkswagen?
- **Respuesta esperada**: Volkswagen, Audi, Porsche, Bentley, Lamborghini, SEAT, Škoda

**CQ-A2**: ¿Qué empresas fabrican vehículos híbridos?
- **Filtro**: Empresas con al menos un modelo híbrido en producción

**CQ-A3**: ¿Existe una relación de joint venture entre dos empresas?
- **Ejemplo**: ¿Toyota y Subaru tienen joint ventures?

---

### Categoría B: Taxonomía de Vehículos

**CQ-B1**: ¿Qué modelos pertenecen a la categoría SUV lanzados después de 2020?
- **Dimensiones de filtrado**: Categoría + fecha de lanzamiento

**CQ-B2**: ¿Cuáles son todos los vehículos eléctricos disponibles ordenados por autonomía?
- **Criterio de ordenamiento**: Rango de autonomía (km) descendente

**CQ-B3**: ¿Qué vehículos comparten la misma plataforma técnica?
- **Ejemplo**: VW MQB → Golf, Audi A3, SEAT León, Škoda Octavia

---

### Categoría C: Componentes y Proveedores

**CQ-C1**: ¿Qué fabricantes utilizan motores del proveedor X?
- **Ejemplo**: Modelos que usan motores Bosch, baterías CATL, sistemas de infoentretenimiento Harman

**CQ-C2**: ¿Qué componentes son compartidos entre modelos de diferentes marcas del mismo grupo?
- **Caso de uso**: Análisis de economías de escala

**CQ-C3**: ¿Qué proveedores suministran a más de 5 fabricantes diferentes?
- **Métrica**: Grado de conectividad en la red de suministro

---

### Categoría D: Especificaciones Técnicas

**CQ-D1**: ¿Qué vehículos tienen más de 400 HP y son tracción integral?
- **Filtros múltiples**: Potencia + sistema de tracción

**CQ-D2**: ¿Cuál es la relación peso/potencia promedio por segmento de vehículo?
- **Cálculo agregado**: Función aritmética sobre propiedades numéricas

**CQ-D3**: ¿Qué modelos cumplen con la norma de emisiones Euro 6d?
- **Inferencia regulatoria**: Cumplimiento normativo

---

### Categoría E: Evolución Temporal y Mercado

**CQ-E1**: ¿Cuántos modelos nuevos lanzó cada fabricante en 2023?
- **Agregación temporal**: Count por empresa + filtro de año

**CQ-E2**: ¿Qué vehículos han sido discontinuados en los últimos 3 años?
- **Estado del ciclo de vida**: Modelos con fecha de fin de producción

**CQ-E3**: ¿Qué tendencias de propulsión (gasolina → híbrido → eléctrico) muestra cada marca?
- **Análisis evolutivo**: Distribución de tecnologías por año

---

## 3. Requisitos Técnicos Derivados

De estas preguntas se derivan los siguientes requisitos ontológicos:

### Clases Principales
- `Empresa` (y subclases: `GrupoCorporativo`, `Marca`, `Proveedor`)
- `Vehiculo` (y subclases: `SUV`, `Sedan`, `Pickup`, etc.)
- `Componente` (y subclases: `Motor`, `Bateria`, `Transmision`, etc.)
- `PlataformaTecnica`
- `TipoPropulsion` (Gasolina, Diesel, Hibrido, Electrico, Hidrogeno)

### Propiedades de Objeto
- `perteneceA` (Marca → GrupoCorporativo)
- `fabricadoPor` (Vehiculo → Empresa)
- `compartePlataforma` (Vehiculo → PlataformaTecnica)
- `usaComponente` (Vehiculo → Componente)
- `suministradoPor` (Componente → Proveedor)
- `tieneJointVenture` (Empresa → Empresa) [simétrica]

### Propiedades de Datos
- `añoLanzamiento` (xsd:integer)
- `añoDescontinuacion` (xsd:integer, opcional)
- `potenciaHP` (xsd:decimal)
- `pesoKg` (xsd:decimal)
- `autonomiaKm` (xsd:decimal, para vehículos eléctricos)
- `numeroPlazas` (xsd:integer)
- `precioBase` (xsd:decimal)

### Reglas de Inferencia Necesarias
1. **Transitividad corporativa**: Si Marca A pertenece a Grupo B, y Grupo B es subsidiaria de Grupo C, entonces Marca A está relacionada con Grupo C
2. **Inversión automática**: `fabricadoPor` ↔ `produceModelo`
3. **Clasificación por rango**: Vehículos con autonomía > 500 km → `VehiculoLargaAutonomia`
4. **Cumplimiento normativo**: Si emisiones < X g/km → cumple norma Y

---

## 4. Casos de Uso Extendidos

### Caso de Uso 1: Análisis Competitivo
Un analista de mercado necesita identificar todos los SUV eléctricos premium (precio > $50,000) lanzados entre 2022-2024, sus especificaciones técnicas y qué componentes de batería utilizan.

### Caso de Uso 2: Optimización de Cadena de Suministro
Un ingeniero de procurement necesita identificar qué proveedores alternativos suministran componentes equivalentes para reducir dependencia de un solo proveedor.

### Caso de Uso 3: Investigación de Plataformas Compartidas
Un investigador automotriz analiza economías de escala: ¿Cuántos modelos comparten la misma plataforma técnica y cuál es el impacto en costos de desarrollo?

---

## 5. Métricas de Validación

La ontología será exitosa si puede responder:
- ✅ 100% de las preguntas de competencia categorías A-E
- ✅ Consultas SPARQL en < 500ms para datasets de ~10,000 vehículos
- ✅ Inferencias correctas validadas contra conocimiento experto
- ✅ Extensibilidad: agregar nuevas marcas/modelos sin rediseño ontológico
