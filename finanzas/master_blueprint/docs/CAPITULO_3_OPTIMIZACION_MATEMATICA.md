# Capítulo 3: Modelado Matemático y Optimización Operativa

## Formulación del Problema de Optimización No Lineal

### 3.1 Definición de Variables de Decisión

Sea un proyecto de desarrollo inmobiliario mixto compuesto por:
- **x**: Cantidad de unidades comerciales (tipo A)
- **y**: Cantidad de unidades residenciales (tipo B)

### 3.2 Función Objetivo con Rendimientos Marginales Decrecientes

La función de beneficio operativo incorpora efectos de saturación de mercado y costos marginales crecientes:

```
f(x, y) = 152x + 80y - 2x² - y² - xy
```

**Interpretación Económica de los Componentes:**

1. **Término Lineal (152x + 80y)**:
   - Representa el margen de contribución unitario base
   - 152: Margen bruto por unidad comercial
   - 80: Margen bruto por unidad residencial

2. **Términos Cuadráticos (-2x², -y²)**:
   - Modelan rendimientos marginales decrecientes
   - Capturan efectos de:
     * Saturación de demanda local
     * Costos de construcción no lineales (economías/deseconomías de escala)
     * Competencia interna entre unidades

3. **Término de Interacción (-xy)**:
   - Representa canibalización entre tipos de unidades
   - Efecto de sustitución en la demanda
   - Competencia por recursos compartidos (estacionamientos, áreas comunes)

### 3.3 Restricciones del Problema

**Restricciones de No Negatividad:**
```
x ≥ 0
y ≥ 0
```

**Restricciones de Factibilidad Física:**
(Estas pueden incorporarse posteriormente según el caso específico)
```
a₁x + b₁y ≤ Área_total
a₂x + b₂y ≤ Presupuesto_total
x_min ≤ x ≤ x_max
y_min ≤ y ≤ y_max
```

Para el análisis teórico base, trabajamos con el problema no restringido para demostrar la existencia de un máximo interior.

---

## 3.4 Condiciones de Optimalidad de Primer Orden

### Teorema (Condiciones Necesarias de Primer Orden)

Si (x*, y*) es un óptimo local de f(x, y), entonces:

```
∇f(x*, y*) = 0
```

Es decir:
```
∂f/∂x = 0
∂f/∂y = 0
```

### Cálculo del Gradiente

**Derivada Parcial respecto a x:**
```
∂f/∂x = ∂/∂x[152x + 80y - 2x² - y² - xy]
      = 152 - 4x - y
```

**Derivada Parcial respecto a y:**
```
∂f/∂y = ∂/∂y[152x + 80y - 2x² - y² - xy]
      = 80 - 2y - x
```

### Sistema de Ecuaciones del Punto Crítico

Igualando el gradiente a cero:
```
∂f/∂x = 0  →  152 - 4x - y = 0     (Ecuación 1)
∂f/∂y = 0  →  80 - 2y - x = 0      (Ecuación 2)
```

Reordenando:
```
4x + y = 152    (Ecuación 1')
x + 2y = 80     (Ecuación 2')
```

**Representación Matricial:**
```
[4  1] [x]   [152]
[1  2] [y] = [80]
```

O compactamente: **Ax = b**

---

## 3.5 Resolución Analítica del Sistema

### Método de Sustitución

**De la Ecuación 1':**
```
y = 152 - 4x
```

**Sustituyendo en la Ecuación 2':**
```
x + 2(152 - 4x) = 80
x + 304 - 8x = 80
-7x = 80 - 304
-7x = -224
x* = 224/7 = 32
```

**Sustituyendo x* en la expresión de y:**
```
y* = 152 - 4(32)
y* = 152 - 128
y* = 24
```

### Punto Crítico Obtenido

```
(x*, y*) = (32, 24)
```

### Evaluación de la Función Objetivo

```
f(32, 24) = 152(32) + 80(24) - 2(32)² - (24)² - (32)(24)
          = 4,864 + 1,920 - 2,048 - 576 - 768
          = 3,392
```

**Por lo tanto, el beneficio operativo máximo es de $3,392 (en miles de USD o unidades monetarias relevantes).**

---

## 3.6 Condiciones de Suficiencia de Segundo Orden

### Teorema (Condición Suficiente para Máximo Local)

Sea f(x, y) una función con derivadas parciales de segundo orden continuas. Si en un punto crítico (x*, y*):

1. **∇f(x*, y*) = 0** (condición necesaria)
2. **La matriz Hessiana H es negativa definida**

Entonces (x*, y*) es un **máximo local estricto**.

### Definición de la Matriz Hessiana

```
H = [∂²f/∂x²    ∂²f/∂x∂y]
    [∂²f/∂y∂x   ∂²f/∂y²]
```

### Cálculo de las Derivadas Parciales de Segundo Orden

Recordemos:
```
∂f/∂x = 152 - 4x - y
∂f/∂y = 80 - 2y - x
```

**Derivadas de segundo orden:**

```
∂²f/∂x² = ∂/∂x(152 - 4x - y) = -4

∂²f/∂y² = ∂/∂y(80 - 2y - x) = -2

∂²f/∂x∂y = ∂/∂y(152 - 4x - y) = -1

∂²f/∂y∂x = ∂/∂x(80 - 2y - x) = -1  (Teorema de Schwarz: simetría)
```

**Matriz Hessiana:**
```
H = [-4  -1]
    [-1  -2]
```

**Nota importante:** Esta matriz es **constante** (no depende de x ni y), lo que implica que la función tiene curvatura uniforme en todo su dominio.

---

## 3.7 Test de Definitud Negativa

### Criterio de Sylvester para Matrices Simétricas

Una matriz simétrica H es **negativa definida** si y solo si:

1. El primer menor principal (esquina superior izquierda) es **negativo**:
   ```
   H₁ = -4 < 0  ✓
   ```

2. El determinante de la matriz completa es **positivo**:
   ```
   det(H) = |H| = (-4)(-2) - (-1)(-1)
          = 8 - 1
          = 7 > 0  ✓
   ```

### Conclusión Matemática

**Dado que:**
- H₁ = -4 < 0
- det(H) = 7 > 0

**La matriz Hessiana H es negativa definida.**

**Por lo tanto:**
```
∀(Δx, Δy) ≠ (0, 0):  [Δx  Δy] H [Δx] < 0
                                    [Δy]
```

Esto significa que **cualquier desviación** del punto (32, 24) **reduce el beneficio**, confirmando que (32, 24) es un **máximo global estricto**.

---

## 3.8 Interpretación Geométrica

La función f(x, y) representa una **paraboloide elíptico invertido** (superficie cóncava hacia abajo) con:

- **Vértice (máximo global):** (32, 24, 3392)
- **Eje principal de máxima curvatura:** Dirección del eigenvector asociado al eigenvalor más negativo de H
- **Sin puntos de silla:** det(H) > 0 garantiza que no hay direcciones mixtas de curvatura

---

## 3.9 Análisis de Sensibilidad

### Efecto Marginal de Aumentar x en 1 unidad

Evaluando el gradiente en el óptimo:
```
∂f/∂x|_(32,24) = 152 - 4(32) - 24 = 152 - 128 - 24 = 0
```

El gradiente nulo confirma que estamos en el óptimo. Para analizar sensibilidad, evaluamos cerca del óptimo:

```
∂f/∂x|_(33,24) = 152 - 4(33) - 24 = 152 - 132 - 24 = -4
```

**Interpretación:** Aumentar x de 32 a 33 (manteniendo y = 24) **reduce** el beneficio en aproximadamente $4 por unidad.

### Matriz de Elasticidades en el Óptimo

La Hessiana nos da las elasticidades de segundo orden:
```
ε_xx = ∂²f/∂x² = -4  (Cada unidad adicional de x reduce su margen en $4)
ε_yy = ∂²f/∂y² = -2  (Cada unidad adicional de y reduce su margen en $2)
ε_xy = ∂²f/∂x∂y = -1 (Interacción: agregar x reduce el margen de y en $1)
```

---

## 3.10 Extensión: Problema con Restricciones Lineales

### Formulación con Restricciones de Desigualdad

```
max f(x, y) = 152x + 80y - 2x² - y² - xy

s.a.:
  45x + 65y ≤ 15,000     (Restricción de área en m²)
  2.8x + 3.5y ≤ 300      (Restricción de presupuesto en M$)
  x ≥ 20, y ≥ 15         (Demanda mínima)
  x ≤ 200, y ≤ 150       (Demanda máxima)
```

### Condiciones de Karush-Kuhn-Tucker (KKT)

Para el problema con restricciones gi(x, y) ≤ 0, las condiciones KKT son:

1. **Estacionariedad:**
   ```
   ∇f(x*, y*) + Σ λᵢ ∇gᵢ(x*, y*) = 0
   ```

2. **Factibilidad Primal:**
   ```
   gᵢ(x*, y*) ≤ 0,  ∀i
   ```

3. **Factibilidad Dual:**
   ```
   λᵢ ≥ 0,  ∀i
   ```

4. **Holgura Complementaria:**
   ```
   λᵢ gᵢ(x*, y*) = 0,  ∀i
   ```

**Interpretación del Multiplicador de Lagrange λᵢ:**

λᵢ representa el **precio sombra** de la restricción i:
- Si λᵢ > 0: La restricción está activa (binding) y aumentar el recurso incrementa el beneficio
- Si λᵢ = 0: La restricción no está activa (hay holgura)

**Ejemplo:** Si λ_área = 5.2, entonces relajar la restricción de área en 1 m² aumenta el beneficio en $5.2

---

## 3.11 Implementación Computacional Determinista

### Código Python para Resolución Analítica

```python
import numpy as np
from typing import Dict, Tuple

class MathematicalOptimizerCore:
    """
    Implementación determinista del problema de optimización cuadrático.
    
    Función objetivo:
        f(x, y) = 152x + 80y - 2x² - y² - xy
    
    Sistema de primer orden (gradiente = 0):
        4x + y = 152
        x + 2y = 80
    """
    
    def __init__(self):
        # Matriz del sistema Ax = b derivada del gradiente
        self.A = np.array([
            [4.0, 1.0],   # Coeficientes de ∂f/∂x = 0
            [1.0, 2.0]    # Coeficientes de ∂f/∂y = 0
        ])
        
        self.b = np.array([152.0, 80.0])  # Términos independientes
        
        # Matriz Hessiana (constante para función cuadrática)
        self.H = np.array([
            [-4.0, -1.0],
            [-1.0, -2.0]
        ])
    
    def solve_analytical(self) -> Tuple[float, float]:
        """
        Resuelve el sistema lineal Ax = b para obtener el punto crítico.
        
        Returns:
            (x*, y*): Punto crítico (óptimo si H es negativa definida)
        """
        solution = np.linalg.solve(self.A, self.b)
        return solution[0], solution[1]
    
    def objective_function(self, x: float, y: float) -> float:
        """
        Evalúa la función objetivo en (x, y).
        
        f(x, y) = 152x + 80y - 2x² - y² - xy
        """
        return 152*x + 80*y - 2*x**2 - y**2 - x*y
    
    def gradient(self, x: float, y: float) -> np.ndarray:
        """
        Calcula el gradiente ∇f en (x, y).
        
        ∇f = [∂f/∂x, ∂f/∂y] = [152 - 4x - y, 80 - 2y - x]
        """
        grad_x = 152 - 4*x - y
        grad_y = 80 - 2*y - x
        return np.array([grad_x, grad_y])
    
    def check_optimality(self) -> Dict[str, any]:
        """
        Verifica condiciones de optimalidad de segundo orden.
        
        Returns:
            Dict con análisis de la matriz Hessiana
        """
        # Menores principales
        H1 = self.H[0, 0]  # Primer menor principal
        det_H = np.linalg.det(self.H)  # Determinante
        
        # Eigenvalores (otra forma de verificar definitud)
        eigenvalues = np.linalg.eigvals(self.H)
        
        # Clasificación
        is_negative_definite = (H1 < 0) and (det_H > 0)
        
        return {
            "first_principal_minor": H1,
            "determinant": det_H,
            "eigenvalues": eigenvalues.tolist(),
            "is_negative_definite": is_negative_definite,
            "classification": "Maximum (negative definite)" if is_negative_definite else "Not a maximum"
        }
    
    def get_complete_solution(self) -> Dict[str, any]:
        """
        Retorna solución completa con análisis de optimalidad.
        """
        # Resolver sistema
        x_opt, y_opt = self.solve_analytical()
        
        # Evaluar función objetivo
        f_opt = self.objective_function(x_opt, y_opt)
        
        # Verificar gradiente en el óptimo (debe ser ~0)
        grad_at_opt = self.gradient(x_opt, y_opt)
        
        # Análisis de Hessiana
        optimality = self.check_optimality()
        
        return {
            "optimal_solution": {
                "x_commercial": round(x_opt, 2),
                "y_residential": round(y_opt, 2)
            },
            "optimal_objective_value": round(f_opt, 2),
            "gradient_at_optimum": {
                "grad_x": round(grad_at_opt[0], 6),
                "grad_y": round(grad_at_opt[1], 6),
                "norm": round(np.linalg.norm(grad_at_opt), 6)
            },
            "second_order_analysis": optimality,
            "interpretation": self._generate_interpretation(x_opt, y_opt, f_opt, optimality)
        }
    
    def _generate_interpretation(self, x: float, y: float, f_val: float, opt_analysis: Dict) -> str:
        """Genera interpretación en lenguaje natural."""
        if opt_analysis["is_negative_definite"]:
            return (
                f"El mix óptimo es producir {x:.0f} unidades comerciales y {y:.0f} unidades residenciales, "
                f"generando un beneficio operativo máximo de ${f_val:,.2f}. "
                f"La matriz Hessiana negativa definida (det={opt_analysis['determinant']:.2f}) "
                f"garantiza que este es un máximo global estricto."
            )
        else:
            return "El punto crítico no corresponde a un máximo. Revisar la formulación del problema."


# Función de uso rápido
def solve_optimal_mix() -> Dict[str, any]:
    """
    Función wrapper para uso directo desde la API.
    """
    optimizer = MathematicalOptimizerCore()
    return optimizer.get_complete_solution()


if __name__ == "__main__":
    # Demostración del análisis completo
    print("=" * 80)
    print("CAPÍTULO 3: OPTIMIZACIÓN MATEMÁTICA - SOLUCIÓN ANALÍTICA")
    print("=" * 80)
    
    optimizer = MathematicalOptimizerCore()
    solution = optimizer.get_complete_solution()
    
    print("\n📊 SOLUCIÓN ÓPTIMA:")
    print(f"   x* (Comerciales):  {solution['optimal_solution']['x_commercial']} unidades")
    print(f"   y* (Residenciales): {solution['optimal_solution']['y_residential']} unidades")
    print(f"   f(x*, y*):          ${solution['optimal_objective_value']:,.2f}")
    
    print("\n∇f GRADIENTE EN EL ÓPTIMO:")
    print(f"   ∂f/∂x = {solution['gradient_at_optimum']['grad_x']}")
    print(f"   ∂f/∂y = {solution['gradient_at_optimum']['grad_y']}")
    print(f"   ||∇f|| = {solution['gradient_at_optimum']['norm']}")
    
    print("\n🔍 ANÁLISIS DE SEGUNDO ORDEN (Matriz Hessiana):")
    hess = solution['second_order_analysis']
    print(f"   H₁ (Primer menor):  {hess['first_principal_minor']}")
    print(f"   det(H):             {hess['determinant']}")
    print(f"   Eigenvalores:       {hess['eigenvalues']}")
    print(f"   Negativa Definida:  {hess['is_negative_definite']}")
    print(f"   Clasificación:      {hess['classification']}")
    
    print("\n💡 INTERPRETACIÓN:")
    print(f"   {solution['interpretation']}")
    
    print("\n" + "=" * 80)
```

---

## 3.12 Verificación Numérica vs Analítica

### Test de Consistencia

```python
def verify_solution():
    """Verifica que la solución analítica coincida con métodos numéricos."""
    from scipy.optimize import minimize
    
    # Solución analítica
    optimizer = MathematicalOptimizerCore()
    x_anal, y_anal = optimizer.solve_analytical()
    f_anal = optimizer.objective_function(x_anal, y_anal)
    
    # Solución numérica (scipy)
    def objective_neg(vars):
        return -optimizer.objective_function(vars[0], vars[1])
    
    result_numeric = minimize(objective_neg, x0=[30, 20], method='SLSQP')
    x_num, y_num = result_numeric.x
    f_num = -result_numeric.fun
    
    # Comparación
    error_x = abs(x_anal - x_num)
    error_y = abs(y_anal - y_num)
    error_f = abs(f_anal - f_num)
    
    print(f"Solución Analítica:  x={x_anal:.6f}, y={y_anal:.6f}, f={f_anal:.6f}")
    print(f"Solución Numérica:   x={x_num:.6f}, y={y_num:.6f}, f={f_num:.6f}")
    print(f"Error Absoluto:      Δx={error_x:.9f}, Δy={error_y:.9f}, Δf={error_f:.9f}")
    
    assert error_x < 1e-6 and error_y < 1e-6, "¡Inconsistencia entre soluciones!"
    print("✓ Verificación exitosa: Soluciones coinciden.")

if __name__ == "__main__":
    verify_solution()
```

---

## 3.13 Resumen del Capítulo

### Resultados Principales

1. **Función Objetivo Cuadrática:**
   ```
   f(x, y) = 152x + 80y - 2x² - y² - xy
   ```

2. **Punto Óptimo (Solución Analítica):**
   ```
   (x*, y*) = (32, 24)
   f(32, 24) = 3,392
   ```

3. **Verificación de Optimalidad:**
   - Gradiente nulo: ∇f(32, 24) = (0, 0) ✓
   - Hessiana negativa definida: H₁ = -4 < 0, det(H) = 7 > 0 ✓
   - **Conclusión:** Máximo global estricto

4. **Implementación Computacional:**
   - Resolución exacta mediante `np.linalg.solve`
   - Sin iteraciones numéricas (método directo)
   - Tiempo de ejecución: O(n³) para matriz nxn (n=2: constante)

### Aportación al Master Blueprint

Este capítulo establece los **fundamentos matemáticos rigurosos** que sostienen el módulo `ops_optimizer.py`, garantizando que:

- La API devuelve soluciones **matemáticamente correctas** (no aproximaciones)
- Los resultados son **reproducibles y verificables**
- El código es una **traducción directa** de la teoría (no heurística)
- La documentación permite **validación académica** para tesis

---

**Próximo Paso:** Integración de este modelo cerrado con restricciones de desigualdad (problema KKT) para casos realistas con límites de área, presupuesto y demanda.

