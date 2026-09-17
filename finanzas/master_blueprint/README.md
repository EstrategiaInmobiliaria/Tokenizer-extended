# 🏗️ Master Blueprint

**Arquitectura integral para evaluación de proyectos de inversión inmobiliaria**

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📋 Descripción

**Master Blueprint** es un framework computacional que integra fundamentos teóricos de finanzas corporativas (CAPM, WACC, DCF) con algoritmos de optimización matemática en una plataforma tecnológica escalable basada en FastAPI y Docker.

### 🎯 Objetivo

Proporcionar una herramienta profesional para la evaluación de proyectos inmobiliarios que:
- ✅ Calcula el **WACC** (Weighted Average Cost of Capital) considerando estructura de capital y riesgo
- ✅ Realiza **análisis DCF** (Discounted Cash Flow) completo con VPN, TIR, y análisis de escenarios
- ✅ Optimiza el **mix de productos** bajo restricciones de recursos y demanda
- ✅ Expone todos los cálculos como **API REST** accesible en tiempo real

---

## 🚀 Quick Start

### Opción 1: Docker (Recomendado)

```bash
# Clonar repositorio
git clone <url-repo>
cd master_blueprint

# Iniciar servicios
docker-compose up -d

# Acceder a la API
# http://localhost:8000/docs
```

### Opción 2: Instalación Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Iniciar API
cd api
uvicorn main:app --reload

# Acceder a documentación interactiva
# http://localhost:8000/docs
```

---

## 📦 Arquitectura del Proyecto

```
master_blueprint/
│
├── core/                      # 🧠 Módulos de lógica financiera
│   ├── wacc_engine.py        # WACC y CAPM
│   ├── real_estate_dcf.py    # Análisis DCF inmobiliario
│   └── ops_optimizer.py      # Optimización con restricciones
│
├── api/                       # 🌐 API REST con FastAPI
│   └── main.py               # Endpoints y modelos Pydantic
│
├── database/                  # 💾 Persistencia con PostgreSQL
│   ├── models.py             # SQLAlchemy ORM models
│   └── database.py           # Configuración de DB
│
├── tests/                     # ✅ Tests unitarios y de integración
│   ├── test_wacc.py
│   ├── test_dcf.py
│   └── test_api.py
│
├── docs/                      # 📚 Documentación
│   └── MASTER_BLUEPRINT.md   # Marco teórico completo
│
├── requirements.txt           # Dependencias Python
├── Dockerfile                 # Docker image
├── docker-compose.yml         # Orquestación de servicios
└── README.md                  # Este archivo
```

---

## 🔧 Tecnologías Utilizadas

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| **Lenguaje** | Python 3.11+ | Core de la aplicación |
| **Framework Web** | FastAPI | API REST de alta performance |
| **Cálculos Numéricos** | NumPy, SciPy | Optimización y álgebra lineal |
| **Base de Datos** | PostgreSQL | Persistencia de proyectos |
| **ORM** | SQLAlchemy | Mapeo objeto-relacional |
| **Contenedores** | Docker, Docker Compose | Despliegue y portabilidad |
| **Testing** | Pytest | Tests unitarios e integración |
| **Documentación** | OpenAPI (Swagger) | Docs interactivas automáticas |

---

## 📊 Endpoints de la API

### 1. Cálculo de WACC

```http
POST /api/v1/wacc/calculate
Content-Type: application/json

{
  "risk_free_rate": 0.05,
  "market_return": 0.12,
  "corporate_tax_rate": 0.27,
  "equity_value": 800000000,
  "debt_value": 400000000,
  "beta": 1.15,
  "debt_rate": 0.08
}
```

**Response:**
```json
{
  "wacc": 0.1065,
  "wacc_percentage": 10.65,
  "cost_of_equity": 0.1305,
  "cost_of_debt_after_tax": 0.0584,
  "detailed_breakdown": {...}
}
```

### 2. Análisis DCF

```http
POST /api/v1/dcf/analyze
Content-Type: application/json

{
  "project_name": "Edificio Las Condes",
  "initial_investment": 1200000000,
  "discount_rate": 0.096,
  "projection_years": 5,
  "rental_income": [150000000, 165000000, 180000000, 195000000, 210000000],
  "sales_revenue": [0, 0, 200000000, 300000000, 400000000],
  "operating_costs": [50000000, 52000000, 54000000, 56000000, 58000000],
  "capex": [20000000, 15000000, 15000000, 10000000, 10000000],
  "taxes": [25000000, 28000000, 35000000, 45000000, 55000000],
  "include_scenarios": true
}
```

**Response:**
```json
{
  "npv": 250000000,
  "irr": 0.158,
  "profitability_index": 1.21,
  "payback_period": 3.2,
  "accept_project": true,
  "decision_rationale": "✅ PROYECTO VIABLE: VPN positivo...",
  "year_by_year": [...],
  "scenarios": {
    "optimistic": {...},
    "base": {...},
    "pessimistic": {...}
  }
}
```

### 3. Optimización de Mix

```http
POST /api/v1/optimize/mix
Content-Type: application/json

{
  "products": [
    {
      "name": "Apartamento Tipo A",
      "unit_price": 4500000,
      "variable_cost": 2800000
    },
    {
      "name": "Apartamento Tipo B",
      "unit_price": 6000000,
      "variable_cost": 3500000
    }
  ],
  "resource_constraints": [
    {
      "name": "Área Total (m²)",
      "total_available": 15000,
      "consumption_rates": [45, 65]
    }
  ],
  "fixed_costs": 50000000
}
```

**Response:**
```json
{
  "success": true,
  "optimal_quantities": [120, 80],
  "optimal_profit": 180000000,
  "detailed_breakdown": {...}
}
```

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=core --cov=api --cov-report=html

# Tests específicos
pytest tests/test_wacc.py -v
pytest tests/test_api.py -v
```

---

## 📖 Documentación

### Documentación Interactiva (Swagger UI)

Una vez iniciada la API, accede a:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Documentación Teórica

Para el marco teórico completo, fundamentos matemáticos y guía de implementación:

📘 **[MASTER_BLUEPRINT.md](docs/MASTER_BLUEPRINT.md)**

Este documento incluye:
- Fundamentos de CAPM, WACC y DCF
- Optimización matemática con restricciones
- Arquitectura en tres capas
- Casos de uso y ejemplos
- Referencias bibliográficas

---

## 🎓 Casos de Uso

### Caso 1: Evaluación de Proyecto Residencial

```python
from core import WACCEngine, MarketParameters, CapitalStructure

# Calcular WACC
market = MarketParameters(
    risk_free_rate=0.05,
    market_return=0.12,
    corporate_tax_rate=0.27
)

capital = CapitalStructure(
    equity_value=800_000_000,
    debt_value=400_000_000,
    beta=1.15,
    debt_rate=0.08
)

engine = WACCEngine(market, capital)
wacc = engine.calculate_wacc()  # 10.65%
```

### Caso 2: Análisis DCF Completo

```python
from core import RealEstateDCF, ProjectAssumptions, RealEstateCashFlows

assumptions = ProjectAssumptions(
    project_name="Proyecto Las Condes",
    initial_investment=1_200_000_000,
    discount_rate=0.096,
    projection_years=5
)

cash_flows = RealEstateCashFlows(
    rental_income=[150e6, 165e6, 180e6, 195e6, 210e6],
    sales_revenue=[0, 0, 200e6, 300e6, 400e6],
    operating_costs=[50e6, 52e6, 54e6, 56e6, 58e6],
    capex=[20e6, 15e6, 15e6, 10e6, 10e6],
    taxes=[25e6, 28e6, 35e6, 45e6, 55e6]
)

dcf = RealEstateDCF(assumptions, cash_flows)
analysis = dcf.get_comprehensive_analysis()

print(f"VPN: ${analysis['npv']:,.0f}")
print(f"TIR: {analysis['irr']*100:.2f}%")
print(f"Decisión: {analysis['decision_rationale']}")
```

### Caso 3: Optimización de Mix

```python
from core import OperationsOptimizer, Product, ResourceConstraint

products = [
    Product("Tipo A", unit_price=4_500_000, variable_cost=2_800_000),
    Product("Tipo B", unit_price=6_000_000, variable_cost=3_500_000)
]

constraints = [
    ResourceConstraint("Área (m²)", total_available=15_000, consumption_rates=[45, 65]),
    ResourceConstraint("Presupuesto", total_available=300_000_000, consumption_rates=[2.8e6, 3.5e6])
]

optimizer = OperationsOptimizer(products, constraints, fixed_costs=50_000_000)
solution = optimizer.optimize_linear_programming()

print(f"Mix óptimo: {solution['optimal_quantities']}")
print(f"Beneficio: ${solution['optimal_profit']:,.0f}")
```

---

## 🐳 Docker Compose

El proyecto incluye orquestación completa de servicios:

```yaml
services:
  - api          # API FastAPI (puerto 8000)
  - db           # PostgreSQL (puerto 5432)
  - pgadmin      # Administración DB (puerto 5050)
```

**Comandos útiles:**

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Detener servicios
docker-compose down

# Reconstruir imágenes
docker-compose build --no-cache
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 📚 Referencias

1. **Sharpe, W. F.** (1964). Capital Asset Prices: A Theory of Market Equilibrium
2. **Modigliani, F., & Miller, M. H.** (1958). The Cost of Capital, Corporation Finance
3. **Damodaran, A.** (2012). Investment Valuation: Tools and Techniques
4. **Brealey, R. A., Myers, S. C., & Allen, F.** (2020). Principles of Corporate Finance

---

## 📧 Contacto

Para preguntas o soporte:
- 📧 Email: support@masterblueprint.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/master_blueprint/issues)
- 📖 Docs: [Documentación Completa](docs/MASTER_BLUEPRINT.md)

---

## ✨ Características Destacadas

- 🚀 **Alta Performance**: API asíncrona con FastAPI
- 📊 **Cálculos Rigurosos**: Basados en teoría financiera académica
- 🔧 **Fácil Despliegue**: Docker Compose con un comando
- 📚 **Documentación Completa**: Swagger UI + Marco teórico
- ✅ **Tests Completos**: Cobertura de core y API
- 🎯 **Production-Ready**: Logging, health checks, CORS configurado

---

**Desarrollado con ❤️ para la evaluación profesional de proyectos inmobiliarios**
