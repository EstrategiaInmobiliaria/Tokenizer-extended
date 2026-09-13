# Fundamentos Matemáticos: Navier-Stokes y PINNs

## 📐 Ecuaciones de Navier-Stokes

### Origen Físico

Las ecuaciones de Navier-Stokes describen cómo fluyen los fluidos (líquidos y gases) aplicando:

1. **Conservación de masa** (continuidad)
2. **Conservación de momento** (segunda ley de Newton para fluidos)
3. **Viscosidad** (resistencia interna al flujo)

### Forma General (3D, Incompresible)

**Continuidad:**
$$
\nabla \cdot \mathbf{v} = 0
$$

**Momento:**
$$
\rho\left(\frac{\partial \mathbf{v}}{\partial t} + \mathbf{v} \cdot \nabla \mathbf{v}\right) = -\nabla p + \mu \nabla^2 \mathbf{v} + \mathbf{f}
$$

Donde:
- $\mathbf{v} = (u, v, w)$ = vector de velocidad [m/s]
- $p$ = presión [Pa]
- $\rho$ = densidad [kg/m³]
- $\mu$ = viscosidad dinámica [Pa·s]
- $\mathbf{f}$ = fuerzas externas (gravedad, etc.) [N/m³]

### Interpretación Término a Término

$$
\underbrace{\rho\frac{\partial \mathbf{v}}{\partial t}}_{\text{Aceleración local}} + \underbrace{\rho\mathbf{v} \cdot \nabla \mathbf{v}}_{\text{Aceleración convectiva}} = \underbrace{-\nabla p}_{\text{Gradiente de presión}} + \underbrace{\mu \nabla^2 \mathbf{v}}_{\text{Difusión viscosa}} + \underbrace{\mathbf{f}}_{\text{Fuerzas externas}}
$$

1. **$\rho\frac{\partial \mathbf{v}}{\partial t}$**: Cambio de velocidad en el tiempo (estacionario → 0)
2. **$\rho\mathbf{v} \cdot \nabla \mathbf{v}$**: Término no lineal (hace que N-S sean tan difíciles)
3. **$-\nabla p$**: Presión empuja el fluido
4. **$\mu \nabla^2 \mathbf{v}$**: Viscosidad suaviza las diferencias de velocidad
5. **$\mathbf{f}$**: Gravedad, fuerzas eléctricas, etc.

### Adimensionalización: Número de Reynolds

Dividiendo por $\rho U^2 / L$ (escalas características):

$$
\frac{\partial \mathbf{v}^*}{\partial t^*} + \mathbf{v}^* \cdot \nabla \mathbf{v}^* = -\nabla p^* + \frac{1}{Re}\nabla^2 \mathbf{v}^*
$$

Donde:
$$
Re = \frac{\rho U L}{\mu} = \frac{UL}{\nu}
$$

**Interpretación física del Reynolds:**
- $Re \ll 1$: Viscosidad domina → flujo laminar suave
- $Re \gg 1$: Inercia domina → posible turbulencia

**Ejemplos:**
- Miel bajando: Re ≈ 0.1 (muy laminar)
- Nadar en piscina: Re ≈ 10,000 (transición)
- Avión: Re ≈ 10⁷ (turbulento)

## 🧠 Physics-Informed Neural Networks (PINNs)

### Idea Central

Una red neuronal $\mathcal{N}(x, y; \theta)$ aproxima la solución $\mathbf{v}(x,y), p(x,y)$.

**Pero en lugar de entrenar solo con datos**, también respeta la ecuación diferencial.

### Arquitectura

```
Input: (x, y) → Red Neuronal → Output: (u, v, p)
                    ↓
              [Autodiff]
                    ↓
    Calcula: ∂u/∂x, ∂²u/∂y², etc.
                    ↓
         Evalúa ecuación de N-S
                    ↓
          Loss de violación de PDE
```

### Función de Pérdida (Loss)

$$
\mathcal{L} = \underbrace{\mathcal{L}_{\text{data}}}_{\text{Error en mediciones}} + \lambda_1 \underbrace{\mathcal{L}_{\text{PDE}}}_{\text{Violación de N-S}} + \lambda_2 \underbrace{\mathcal{L}_{\text{BC}}}_{\text{Condiciones frontera}} + \lambda_3 \underbrace{\mathcal{L}_{\text{IC}}}_{\text{Condiciones iniciales}}
$$

#### 1. Loss de Datos (si existen)

$$
\mathcal{L}_{\text{data}} = \frac{1}{N_{\text{data}}} \sum_{i=1}^{N_{\text{data}}} \left\| \mathbf{v}(\mathbf{x}_i) - \mathbf{v}_i^{\text{obs}} \right\|^2
$$

#### 2. Loss de PDE

$$
\mathcal{L}_{\text{PDE}} = \frac{1}{N_f} \sum_{i=1}^{N_f} \left\| \mathcal{F}(\mathbf{v}, p; \mathbf{x}_i) \right\|^2
$$

Donde $\mathcal{F}$ es el residuo de Navier-Stokes evaluado en puntos de colocación.

Ejemplo para momento en x:
$$
\mathcal{F}_x = u\frac{\partial u}{\partial x} + v\frac{\partial u}{\partial y} + \frac{1}{\rho}\frac{\partial p}{\partial x} - \nu\left(\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2}\right)
$$

#### 3. Loss de Condiciones de Frontera

$$
\mathcal{L}_{\text{BC}} = \frac{1}{N_b} \sum_{i=1}^{N_b} \left\| \mathbf{v}(\mathbf{x}_i^b) - \mathbf{g}_i \right\|^2
$$

Donde $\mathbf{g}_i$ son valores prescritos (ej: no-slip → $u=v=0$).

#### 4. Loss de Condiciones Iniciales (para transitorios)

$$
\mathcal{L}_{\text{IC}} = \frac{1}{N_0} \sum_{i=1}^{N_0} \left\| \mathbf{v}(\mathbf{x}_i, t=0) - \mathbf{v}_i^0 \right\|^2
$$

### Diferenciación Automática

**Clave del PINN:** No calculas derivadas manualmente. TensorFlow/PyTorch lo hace:

```python
import tensorflow as tf

def compute_gradients(model, x, y):
    with tf.GradientTape(persistent=True) as tape:
        tape.watch([x, y])
        u = model([x, y])
    
    u_x = tape.gradient(u, x)   # ∂u/∂x
    u_y = tape.gradient(u, y)   # ∂u/∂y
    
    u_xx = tape.gradient(u_x, x)  # ∂²u/∂x²
    u_yy = tape.gradient(u_y, y)  # ∂²u/∂y²
    
    return u_x, u_y, u_xx, u_yy
```

## 🔬 Casos Específicos

### Caso 1: Flujo de Poiseuille

**Simplificaciones:**
- Estacionario: $\frac{\partial}{\partial t} = 0$
- 2D: $w = 0$, $\frac{\partial}{\partial z} = 0$
- Completamente desarrollado: $\frac{\partial}{\partial x} = 0$ (excepto presión)

**Ecuación resultante:**
$$
\mu \frac{d^2u}{dy^2} = \frac{dp}{dx} = \text{constante}
$$

**Solución analítica:**
$$
u(y) = -\frac{1}{2\mu}\frac{dp}{dx}(H^2 - y^2)
$$

**Por qué es útil:** Puedes verificar que tu PINN funciona comparando con esto.

### Caso 2: Lid-Driven Cavity

**Configuración:**
- Cavidad cuadrada $[0, L] \times [0, L]$
- Todas las paredes fijas excepto tapa superior
- Tapa se mueve con velocidad $U_{\text{lid}}$

**Condiciones de frontera:**
- $y = L$: $u = U_{\text{lid}}$, $v = 0$
- $x = 0, x = L, y = 0$: $u = 0$, $v = 0$

**No hay solución analítica**, pero existen benchmarks numéricos:
- Ghia et al. (1982) - Resultados de alta precisión

**Física interesante:**
- Re = 100: Un vórtice primario
- Re = 400: Vórtice primario + vórtices secundarios en esquinas
- Re = 1000+: Múltiples vórtices, transición a turbulencia

## 📊 Convergencia y Garantías Teóricas

### ¿Por qué funciona?

**Teorema de aproximación universal:**
- Una red neuronal con suficientes neuronas puede aproximar cualquier función continua

**En PINNs:**
- La red aprende la función $\mathbf{v}(x,y)$ que minimiza la violación de la PDE
- Autodiff garantiza que las derivadas son exactas (hasta precisión numérica)

### Limitaciones Teóricas

**Problema del Milenio de Clay:**
> ¿Existen soluciones suaves y globalmente definidas para Navier-Stokes 3D?

**Estado actual:** Nadie lo sabe. Premio de $1,000,000 sin reclamar.

**Implicación para PINNs:**
- PINNs aproximan soluciones **numéricas**, no prueban existencia matemática
- Para ciertos Re y condiciones, N-S pueden tener singularidades → PINN falla

### Desafíos Prácticos

1. **Puntos de colocación:** ¿Cuántos y dónde?
   - Más puntos = más lento pero más preciso
   - Adaptive sampling ayuda

2. **Pesos de loss:** $\lambda_1, \lambda_2, \lambda_3$ son hiperparámetros
   - Mal balance → red ignora PDE o ignora datos
   - Técnicas: gradient statistics, NTK analysis

3. **Turbulencia:** PINNs vanillla no capturan turbulencia bien
   - Requiere arquitecturas especiales (multi-scale, Fourier features)

## 🔗 Extensiones Avanzadas

### 1. Adaptive Sampling

Re-muestrear puntos de colocación donde el residuo es alto.

### 2. Transfer Learning

Entrenar PINN para Re=100, luego afinar para Re=200.

### 3. Inverse Problems

Dado datos de velocidad, inferir viscosidad o condiciones de frontera.

### 4. Data Assimilation

Fusionar mediciones experimentales con física (Navier-Stokes).

## 📚 Recursos para Profundizar

1. **Paper original de PINNs:** Raissi et al. (2019) - Journal of Computational Physics
2. **Review exhaustivo:** Karniadakis et al. (2021) - Nature Reviews Physics
3. **Libro:** "The Finite Element Method for Fluid Dynamics" - Zienkiewicz & Taylor
4. **Curso MIT:** 18.086 - Computational Science and Engineering

## 🎯 TL;DR

**Navier-Stokes:**
- Ecuaciones fundamentales de fluidos
- No lineales → difíciles de resolver analíticamente
- Reynolds determina régimen (laminar vs turbulento)

**PINNs:**
- Red neuronal + física
- Loss = error en datos + violación de ecuación diferencial
- No requiere mallado
- Diferenciación automática es la magia

**Limitación:**
- No resuelven el problema matemático fundamental
- Son métodos numéricos inteligentes, no soluciones analíticas
