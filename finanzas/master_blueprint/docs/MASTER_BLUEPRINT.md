# 🏗️ Master Blueprint: Del Marco Teórico al Despliegue Tecnológico

**Arquitectura Integral para Evaluación de Proyectos de Inversión Inmobiliaria**

---

## 📋 Índice

1. [Visión General](#visión-general)
2. [Arquitectura en Tres Capas](#arquitectura-en-tres-capas)
3. [Marco Teórico Financiero](#marco-teórico-financiero)
4. [Implementación Tecnológica](#implementación-tecnológica)
5. [Casos de Uso](#casos-de-uso)
6. [Guía de Desarrollo](#guía-de-desarrollo)

---

## 🎯 Visión General

El **Master Blueprint** integra el rigor analítico académico con la escalabilidad de sistemas empresariales en un flujo continuo que transforma teoría financiera en decisiones operativas.

### Propuesta de Valor

Este framework unifica:
- ✅ **Fundamentos teóricos** de finanzas corporativas (CAPM, WACC, DCF)
- ✅ **Optimización matemática** con restricciones multivariables
- ✅ **Arquitectura tecnológica** escalable y desplegable en producción

---

## 🏛️ Arquitectura en Tres Capas

### Capa 1: Teórico-Financiera (El Núcleo Académico)

**Objetivo**: Sustentar la validez de la toma de decisiones bajo incertidumbre.

#### Componentes Teóricos

##### 1.1 CAPM (Capital Asset Pricing Model)

El modelo de valoración de activos de capital establece la relación entre riesgo y retorno esperado:

```
Re = Rf + β(Rm - Rf)
```

**Donde:**
- `Re` = Retorno esperado del patrimonio (Cost of Equity)
- `Rf` = Tasa libre de riesgo (bonos del tesoro a largo plazo)
- `β` = Beta del activo (medida del riesgo sistemático)
- `Rm` = Retorno esperado del mercado
- `(Rm - Rf)` = Prima de riesgo de mercado

**Interpretación Económica:**
- Si β > 1: El activo es más volátil que el mercado (mayor riesgo, mayor retorno esperado)
- Si β = 1: El activo se mueve con el mercado
- Si β < 1: El activo es menos volátil que el mercado (menor riesgo)

**Aplicación en Proyectos Inmobiliarios:**
Para un proyecto de desarrollo inmobiliario en Chile:
- `Rf` ≈ 5% (BCU 10 años)
- `Rm` ≈ 12% (IPSA histórico)
- `β` ≈ 1.15 (sector inmobiliario)
- `Re` = 0.05 + 1.15(0.12 - 0.05) = **13.05%**

##### 1.2 WACC (Weighted Average Cost of Capital)

El costo promedio ponderado de capital representa la tasa mínima de retorno que un proyecto debe generar:

```
WACC = (E/V) × Re + (D/V) × Rd × (1 - Tc)
```

**Donde:**
- `E` = Valor de mercado del patrimonio (Equity)
- `D` = Valor de mercado de la deuda (Debt)
- `V` = E + D (Valor total de la empresa)
- `Re` = Costo del patrimonio (de CAPM)
- `Rd` = Costo de la deuda (tasa de interés bancaria)
- `Tc` = Tasa impositiva corporativa

**Desglose de Componentes:**

1. **Componente de Patrimonio**: `(E/V) × Re`
   - Refleja el costo de oportunidad de los accionistas
   - No genera escudo fiscal

2. **Componente de Deuda**: `(D/V) × Rd × (1 - Tc)`
   - Refleja el costo de financiamiento externo
   - Beneficio del escudo fiscal: `Rd × Tc`

**Ejemplo Numérico:**

Proyecto con:
- Patrimonio: $800M CLP (66.7%)
- Deuda: $400M CLP (33.3%)
- Re = 13.05%
- Rd = 8%
- Tc = 27%

```
WACC = 0.667 × 0.1305 + 0.333 × 0.08 × (1 - 0.27)
WACC = 0.0871 + 0.0194 = 10.65%
```

**Interpretación:**
El proyecto debe generar un retorno mínimo del **10.65%** para:
1. Pagar el costo de la deuda (8% después de impuestos)
2. Satisfacer el retorno esperado de los accionistas (13.05%)
3. Crear valor económico (EVA positivo)

##### 1.3 DCF (Discounted Cash Flow Analysis)

El análisis de flujo de caja descontado es el método fundamental para valorar proyectos:

```
VPN = Σ(CFt / (1 + WACC)^t) - I₀ + VR / (1 + WACC)^n
```

**Donde:**
- `CFt` = Flujo de caja libre en el período t
- `WACC` = Tasa de descuento (del cálculo anterior)
- `I₀` = Inversión inicial
- `VR` = Valor Residual (Terminal Value)
- `n` = Número de períodos

**Métodos de Cálculo del Valor Residual:**

1. **Método de Perpetuidad:**
```
VR = CF_final × (1 + g) / (WACC - g)
```
Donde `g` = tasa de crecimiento perpetuo (típicamente 2-3%)

2. **Método Exit Multiple:**
```
VR = NOI_final / Cap Rate
```
Donde `Cap Rate` = tasa de capitalización del sector (8-10% inmobiliario)

**Métricas de Evaluación:**

1. **VPN (Valor Presente Neto)**
   - Si VPN > 0 → Proyecto crea valor, **ACEPTAR**
   - Si VPN < 0 → Proyecto destruye valor, **RECHAZAR**
   - Si VPN = 0 → Indiferente (retorno = WACC)

2. **TIR (Tasa Interna de Retorno)**
   - TIR es la tasa donde VPN = 0
   - Si TIR > WACC → **ACEPTAR**
   - Si TIR < WACC → **RECHAZAR**

3. **Índice de Rentabilidad (IR)**
```
IR = VP(Flujos) / Inversión Inicial
```
   - Si IR > 1 → **ACEPTAR**
   - Si IR < 1 → **RECHAZAR**

4. **Período de Recuperación (Payback)**
   - Años hasta recuperar la inversión inicial
   - Útil para evaluar riesgo de liquidez

---

### Capa 2: Analítico-Operativa (El Motor de Simulación)

**Objetivo**: Implementar algoritmos de optimización matemática para decisiones operativas.

#### 2.1 Optimización con Restricciones

**Función Objetivo (Maximizar Beneficio):**

```
max f(x, y) = Px·x + Py·y - Cx·x - Cy·y - CF
```

**Donde:**
- `x, y` = Cantidades de productos A y B
- `Px, Py` = Precios de venta unitarios
- `Cx, Cy` = Costos variables unitarios
- `CF` = Costos fijos totales

**Margen de Contribución:**
```
MCu = P - Cv (por unidad)
```

**Reformulación:**
```
max f(x, y) = MCu_A·x + MCu_B·y - CF
```

#### 2.2 Restricciones del Problema

**Restricciones de Recursos:**

1. **Restricción de Área Construible:**
```
a₁·x + b₁·y ≤ Área_total
```
Ejemplo: `45m²·x + 65m²·y ≤ 15,000m²`

2. **Restricción de Presupuesto:**
```
a₂·x + b₂·y ≤ Presupuesto_total
```
Ejemplo: `$2.8M·x + $3.5M·y ≤ $300M`

3. **Restricciones de Demanda:**
```
x_min ≤ x ≤ x_max
y_min ≤ y ≤ y_max
```

4. **No Negatividad:**
```
x ≥ 0, y ≥ 0
```

#### 2.3 Método de Solución: Programación Lineal

**Forma Estándar:**
```
min c^T · x
sujeto a: A · x ≤ b
          x ≥ 0
```

**Algoritmo Simplex:**
1. Encontrar una solución básica factible inicial
2. Verificar optimalidad (costos reducidos ≤ 0)
3. Si no es óptimo, pivotar a una solución adyacente mejor
4. Repetir hasta alcanzar el óptimo

**Condiciones de Karush-Kuhn-Tucker (KKT):**

Para un punto `x*` óptimo:
1. **Estacionariedad:** ∇f(x*) + Σλᵢ∇gᵢ(x*) = 0
2. **Factibilidad Primal:** gᵢ(x*) ≤ 0
3. **Factibilidad Dual:** λᵢ ≥ 0
4. **Holgura Complementaria:** λᵢ·gᵢ(x*) = 0

#### 2.4 Análisis de Sensibilidad

**Precios Sombra (Shadow Prices):**

El precio sombra `λᵢ` de una restricción indica cuánto aumentaría el objetivo si se incrementara el recurso en una unidad:

```
∂f_optimal/∂bᵢ = λᵢ
```

**Interpretación:**
- Si λ = $5,000/m², agregar 1m² aumenta el beneficio en $5,000
- Si λ = 0, la restricción no está activa (hay holgura)

**Rangos de Sensibilidad:**
- **Coeficientes de la función objetivo:** Rango donde la solución óptima actual permanece válida
- **Lados derechos (RHS):** Rango donde los precios sombra actuales son válidos

---

### Capa 3: Tecnológica y de Servidores (La Arquitectura Empresarial)

**Objetivo**: Desplegar la solución como servicio escalable y accesible.

#### 3.1 Stack Tecnológico

```
┌─────────────────────────────────────────────────────────┐
│                  CAPA DE PRESENTACIÓN                    │
│  React / Next.js / Dashboard de Usuario                 │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTPS/REST
┌─────────────────▼───────────────────────────────────────┐
│                   CAPA DE API (FastAPI)                  │
│  - Endpoints REST                                        │
│  - Validación (Pydantic)                                 │
│  - Autenticación/Autorización                            │
│  - Documentación automática (OpenAPI)                    │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                CAPA DE LÓGICA DE NEGOCIO                 │
│  - WACC Engine (wacc_engine.py)                          │
│  - Real Estate DCF (real_estate_dcf.py)                  │
│  - Operations Optimizer (ops_optimizer.py)               │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                 CAPA DE PERSISTENCIA                     │
│  - PostgreSQL (Proyectos, Análisis históricos)          │
│  - Redis (Caché, Sesiones)                              │
└──────────────────────────────────────────────────────────┘
```

#### 3.2 Infraestructura Docker

**Componentes Dockerizados:**

1. **API Service** (Puerto 8000)
   - FastAPI + Uvicorn
   - Python 3.11
   - Dependencias: NumPy, SciPy, SQLAlchemy

2. **PostgreSQL Database** (Puerto 5432)
   - Base de datos relacional
   - Persistencia de proyectos y análisis

3. **pgAdmin** (Puerto 5050)
   - Interfaz de administración de DB
   - Acceso web

**Ventajas del Enfoque Docker:**
- ✅ Portabilidad entre entornos
- ✅ Aislamiento de dependencias
- ✅ Escalabilidad horizontal (múltiples contenedores)
- ✅ CI/CD simplificado

#### 3.3 Flujo de Datos

```
Usuario → Solicita evaluación de proyecto
  ↓
API recibe request (JSON)
  ↓
Validación con Pydantic
  ↓
Ejecución de módulo core (WACC/DCF/Optimizer)
  ↓
Generación de resultados
  ↓
Persistencia en PostgreSQL (opcional)
  ↓
Response al usuario (JSON)
```

#### 3.4 Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/wacc/calculate` | Calcular WACC |
| POST | `/api/v1/dcf/analyze` | Análisis DCF completo |
| POST | `/api/v1/optimize/mix` | Optimización de mix |
| GET | `/health` | Health check |
| GET | `/docs` | Documentación interactiva |

**Ejemplo de Request (WACC):**

```json
POST /api/v1/wacc/calculate
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
  "equity_weight": 0.667,
  "debt_weight": 0.333,
  "detailed_breakdown": {...}
}
```

---

## 🎓 Marco Teórico para Tesis

### Justificación Académica

#### Problema de Investigación

**Pregunta Central:**
¿Cómo integrar los fundamentos teóricos de valoración de activos (CAPM, WACC, DCF) con algoritmos de optimización matemática en una plataforma tecnológica escalable para la evaluación de proyectos inmobiliarios?

**Hipótesis:**
La integración de modelos financieros con optimización matemática y arquitectura de microservicios mejora la precisión y velocidad de las decisiones de inversión inmobiliaria.

#### Objetivos

**Objetivo General:**
Desarrollar e implementar un framework computacional que integre teoría financiera y optimización operativa para evaluación de proyectos inmobiliarios en tiempo real.

**Objetivos Específicos:**
1. Implementar el cálculo del WACC considerando estructura de capital y riesgo sistemático
2. Desarrollar un motor DCF con análisis de escenarios para proyectos inmobiliarios
3. Crear algoritmos de optimización para mix de productos bajo restricciones
4. Diseñar una API REST escalable que exponga los cálculos como servicios
5. Validar el framework con casos de estudio reales

#### Metodología

1. **Revisión Bibliográfica:**
   - Modigliani-Miller (Teoría de estructura de capital)
   - Sharpe, Lintner, Mossin (CAPM)
   - Markowitz (Teoría de portafolio)
   - Programación lineal y no lineal

2. **Desarrollo de Software:**
   - Lenguaje: Python 3.11
   - Framework Web: FastAPI
   - Optimización: SciPy
   - Base de datos: PostgreSQL

3. **Validación:**
   - Casos de estudio de proyectos inmobiliarios chilenos
   - Comparación con métodos tradicionales (Excel)
   - Análisis de sensibilidad de parámetros

#### Contribución Esperada

1. **Teórica:**
   - Integración formal de CAPM, WACC y DCF en un framework unificado
   - Extensión de programación lineal a decisiones inmobiliarias

2. **Práctica:**
   - Herramienta open-source para evaluación de proyectos
   - Reducción del tiempo de análisis de días a segundos
   - Interfaz accesible para stakeholders no técnicos

3. **Metodológica:**
   - Blueprint replicable para otras industrias
   - Patrones de arquitectura para finanzas computacionales

---

## 🚀 Casos de Uso

### Caso 1: Evaluación de Proyecto Residencial

**Contexto:**
Proyecto de 200 unidades en Las Condes, inversión $1,200M CLP.

**Workflow:**
1. Calcular WACC del proyecto (10.65%)
2. Proyectar flujos de caja 5 años
3. Calcular VPN, TIR
4. Optimizar mix de unidades (Tipo A vs B)
5. Análisis de escenarios (optimista, base, pesimista)

**Resultado:**
- VPN = $250M CLP (positivo → ACEPTAR)
- TIR = 15.8% (> WACC → ACEPTAR)
- Mix óptimo: 120 Tipo A, 80 Tipo B
- Sensibilidad: Proyecto viable con -15% de ingresos

### Caso 2: Optimización de Portafolio de Proyectos

**Contexto:**
Inmobiliaria con 5 proyectos posibles, presupuesto limitado $5,000M.

**Workflow:**
1. Calcular VPN de cada proyecto
2. Formular problema de optimización (mochila)
3. Maximizar VPN total sujeto a presupuesto
4. Considerar restricciones de timing y geografía

**Resultado:**
- Selección: Proyectos 1, 3, 5
- VPN total: $1,800M
- Utilización presupuesto: 98%

---

## 📊 Diagramas de Arquitectura

### Diagrama de Flujo de Decisión

```
┌─────────────────────┐
│   Datos de Mercado  │
│  (Rf, Rm, Tc, β)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Cálculo de WACC    │
│  (Tasa Descuento)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Proyección de      │
│  Flujos de Caja     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Análisis DCF      │
│  (VPN, TIR, IR)     │
└──────────┬──────────┘
           │
      ┌────┴────┐
      │ VPN > 0?│
      └────┬────┘
           │
    ┌──────┼──────┐
    Sí             No
    │              │
    ▼              ▼
┌─────────┐  ┌─────────┐
│ ACEPTAR │  │RECHAZAR │
└─────────┘  └─────────┘
```

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────┐
│                  USUARIO FINAL                  │
└────────────────────┬────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │  Web   │  │  API   │  │ Mobile │
    │  App   │  │ Client │  │  App   │
    └───┬────┘  └───┬────┘  └───┬────┘
        │           │           │
        └───────────┼───────────┘
                    │ REST API
                    ▼
        ┌───────────────────────┐
        │    FastAPI Service    │
        │  ┌─────────────────┐  │
        │  │ WACC Endpoint   │  │
        │  ├─────────────────┤  │
        │  │  DCF Endpoint   │  │
        │  ├─────────────────┤  │
        │  │  Opt Endpoint   │  │
        │  └─────────────────┘  │
        └───────────┬───────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │  WACC  │  │  DCF   │  │  OPT   │
   │ Engine │  │ Engine │  │ Engine │
   └───┬────┘  └───┬────┘  └───┬────┘
       │           │           │
       └───────────┼───────────┘
                   │
                   ▼
          ┌────────────────┐
          │   PostgreSQL   │
          │   (Historial)  │
          └────────────────┘
```

---

## 🛠️ Guía de Desarrollo en PyCharm

### Estructura de Directorios

```
master_blueprint/
│
├── core/                      # Módulos de lógica de negocio
│   ├── __init__.py
│   ├── wacc_engine.py        # Cálculo de WACC y CAPM
│   ├── real_estate_dcf.py    # Análisis DCF inmobiliario
│   └── ops_optimizer.py      # Optimización con restricciones
│
├── api/                       # Capa de API REST
│   ├── __init__.py
│   └── main.py               # FastAPI application
│
├── database/                  # Persistencia
│   ├── __init__.py
│   ├── models.py             # SQLAlchemy models
│   └── database.py           # DB configuration
│
├── tests/                     # Tests unitarios y de integración
│   ├── test_wacc.py
│   ├── test_dcf.py
│   └── test_optimizer.py
│
├── docs/                      # Documentación
│   ├── MASTER_BLUEPRINT.md   # Este documento
│   ├── API_GUIDE.md
│   └── THEORETICAL_FRAMEWORK.md
│
├── config/                    # Configuraciones
│   └── settings.py
│
├── requirements.txt           # Dependencias Python
├── Dockerfile                 # Docker image
├── docker-compose.yml         # Orquestación de servicios
├── .env.example               # Variables de entorno
└── README.md                  # Introducción del proyecto
```

### Comandos Esenciales

#### Instalación

```bash
# Clonar repositorio
git clone <url-repo>
cd master_blueprint

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

#### Ejecución Local

```bash
# Iniciar API
cd api
uvicorn main:app --reload --port 8000

# Acceder a documentación
# http://localhost:8000/docs
```

#### Docker

```bash
# Construir imagen
docker build -t master-blueprint .

# Ejecutar con docker-compose
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Detener
docker-compose down
```

#### Tests

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=core --cov-report=html

# Test específico
pytest tests/test_wacc.py -v
```

---

## 📚 Referencias Bibliográficas

1. **Sharpe, W. F.** (1964). "Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk". *Journal of Finance*, 19(3), 425-442.

2. **Modigliani, F., & Miller, M. H.** (1958). "The Cost of Capital, Corporation Finance and the Theory of Investment". *American Economic Review*, 48(3), 261-297.

3. **Damodaran, A.** (2012). *Investment Valuation: Tools and Techniques for Determining the Value of Any Asset*. John Wiley & Sons.

4. **Brealey, R. A., Myers, S. C., & Allen, F.** (2020). *Principles of Corporate Finance* (13th ed.). McGraw-Hill Education.

5. **Luenberger, D. G., & Ye, Y.** (2016). *Linear and Nonlinear Programming* (4th ed.). Springer.

6. **Ramírez, J.** (2018). "Evaluación de Proyectos Inmobiliarios en Chile: Metodologías y Casos de Estudio". *Revista Chilena de Ingeniería*, 26(2), 245-260.

---

## ✅ Checklist de Implementación

### Fase 1: Desarrollo Core (Completado ✅)
- [x] Módulo `wacc_engine.py`
- [x] Módulo `real_estate_dcf.py`
- [x] Módulo `ops_optimizer.py`

### Fase 2: API y Servicios (Completado ✅)
- [x] FastAPI `main.py`
- [x] Modelos Pydantic
- [x] Endpoints REST
- [x] Documentación OpenAPI

### Fase 3: Infraestructura (Completado ✅)
- [x] Dockerfile
- [x] docker-compose.yml
- [x] PostgreSQL models
- [x] Database configuration

### Fase 4: Documentación (En Progreso 🔄)
- [x] Master Blueprint teórico
- [ ] Guía de API
- [ ] Tutorial de uso

### Fase 5: Testing y Validación
- [ ] Tests unitarios core
- [ ] Tests de integración API
- [ ] Casos de estudio reales
- [ ] Benchmarking de performance

---

**Última actualización**: `datetime.now()`  
**Versión**: 1.0.0  
**Autor**: Master Blueprint Project Team
