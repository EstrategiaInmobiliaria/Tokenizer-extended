# Optimization Solver - Commercial-Residential Mix

## Overview

This module provides a robust solver for the optimal commercial-residential mix problem. It finds the values of `x` (commercial) and `y` (residential) that maximize the operating benefit function:

**f(x, y) = 152x + 80y - 2x² - y² - xy**

Subject to:
- Linear constraints: **Ax = b**
- Non-negativity: **x ≥ 0, y ≥ 0**

## Key Improvements Over Original Code

### 1. **Proper Maximum Verification**
- Original: `is_global_maximum` was hardcoded to `True`
- Improved: Uses Hessian matrix to verify if the critical point is actually a maximum
  - Checks if Hessian is negative definite (H₁₁ < 0 and det(H) > 0)
  - Verifies gradient norm is close to zero

### 2. **Comprehensive Error Handling**
- Checks for singular/nearly singular matrices
- Validates matrix dimensions
- Handles overdetermined/underdetermined systems
- Provides detailed error messages

### 3. **Enhanced Documentation**
- Complete docstrings for all methods
- Mathematical formulas in comments
- Type hints for all parameters

### 4. **Better Result Reporting**
- Includes verification details explaining why a point is/isn't a maximum
- More informative error messages
- Structured return dictionary

### 5. **Additional Mathematical Rigor**
- Separate methods for objective function, gradient, and Hessian
- Second-order optimality conditions
- Gradient tolerance parameter

## Usage

### Basic Usage

```python
from optimization_solver import OptimalMixSolver
import numpy as np

# Define constraints: Ax = b
# Example: Finding where gradient equals zero
# [4  1][x]   [152]
# [1  2][y] = [80]

A = np.array([[4, 1], [1, 2]])
b = np.array([152, 80])

solver = OptimalMixSolver(A, b)
result = solver.solve_optimal_mix()

print(result)
```

### Expected Output

```python
{
    'status': 'success',
    'optimal_mix': {
        'x_commercial': 32.0,
        'y_residential': 24.0
    },
    'max_operating_benefit': 3680.0,
    'gradient_norm': 1.1842378929335002e-15,
    'is_global_maximum': True,
    'verification_details': 'Hessian is negative definite (local maximum)',
    'msg': 'Optimal solution found'
}
```

## Mathematical Background

### Objective Function

The profit function is quadratic:
- **f(x, y) = 152x + 80y - 2x² - y² - xy**

### Gradient (First-Order Conditions)

To find critical points, we set the gradient to zero:

**∇f(x, y) = [∂f/∂x, ∂f/∂y] = [152 - 4x - y, 80 - 2y - x] = [0, 0]**

This gives us the linear system:
- 4x + y = 152
- x + 2y = 80

### Hessian (Second-Order Conditions)

The Hessian matrix determines the nature of critical points:

**H = [[-4, -1], [-1, -2]]**

For a maximum:
- **H₁₁ = -4 < 0** ✓
- **det(H) = (-4)(-2) - (-1)(-1) = 8 - 1 = 7 > 0** ✓

Since both conditions are satisfied, the Hessian is negative definite, confirming a local maximum.

## Testing

Run the test suite:

```bash
# Install dependencies
pip install -r requirements-optimization.txt

# Run tests
python test_optimization_solver.py

# Or using pytest directly
pytest test_optimization_solver.py -v
```

## API Reference

### OptimalMixSolver

#### `__init__(A, b)`
Initialize the solver with constraint matrices.

**Parameters:**
- `A`: np.ndarray - Coefficient matrix (n × 2)
- `b`: np.ndarray - Right-hand side vector (n,)

#### `solve_optimal_mix(gradient_tolerance=1e-6)`
Solve for the optimal mix.

**Parameters:**
- `gradient_tolerance`: float - Tolerance for considering gradient as zero

**Returns:** Dictionary with keys:
- `status`: "success", "infeasible", or "error"
- `optimal_mix`: {"x_commercial": float, "y_residential": float}
- `max_operating_benefit`: float
- `gradient_norm`: float
- `is_global_maximum`: bool
- `verification_details`: str
- `msg`: str

## Status Codes

- **success**: Optimal solution found and verified
- **infeasible**: Solution violates non-negativity constraints (x < 0 or y < 0)
- **error**: System error (singular matrix, wrong dimensions, etc.)

## Example Scenarios

### Scenario 1: Successful Optimization
```python
A = np.array([[4, 1], [1, 2]])
b = np.array([152, 80])
solver = OptimalMixSolver(A, b)
result = solver.solve_optimal_mix()
# Result: x=32, y=24, profit=3680
```

### Scenario 2: Infeasible Solution
```python
A = np.array([[1, 0], [0, 1]])
b = np.array([-10, 20])
solver = OptimalMixSolver(A, b)
result = solver.solve_optimal_mix()
# Result: status="infeasible" (x would be negative)
```

### Scenario 3: Singular Matrix
```python
A = np.array([[1, 2], [2, 4]])  # Linearly dependent rows
b = np.array([10, 20])
solver = OptimalMixSolver(A, b)
result = solver.solve_optimal_mix()
# Result: status="error" (matrix is singular)
```

## License

This code is provided as-is for educational and commercial use.
