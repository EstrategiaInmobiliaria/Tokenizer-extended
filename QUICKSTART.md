# Quick Start Guide - Optimization Solver

## Installation

```bash
pip install -r requirements-optimization.txt
```

## 30-Second Usage

```python
from optimization_solver import OptimalMixSolver
import numpy as np

# Your constraint system Ax = b
A = np.array([[4, 1], [1, 2]])
b = np.array([152, 80])

# Solve it
solver = OptimalMixSolver(A, b)
result = solver.solve_optimal_mix()

# Check result
if result["status"] == "success":
    print(f"✓ x = {result['optimal_mix']['x_commercial']}")
    print(f"✓ y = {result['optimal_mix']['y_residential']}")
    print(f"✓ Profit = ${result['max_operating_benefit']}")
    print(f"✓ Is maximum? {result['is_global_maximum']}")
```

## Output

```python
{
    'status': 'success',
    'optimal_mix': {'x_commercial': 32.0, 'y_residential': 24.0},
    'max_operating_benefit': 3392.0,
    'gradient_norm': 0.0,
    'is_global_maximum': True,
    'verification_details': 'Hessian is negative definite (local maximum)',
    'msg': 'Optimal solution found'
}
```

## Common Use Cases

### Case 1: Resource Allocation
You have limited labor and materials. Find optimal product mix.

```python
# 5x + 2y ≤ 200 (labor hours)
# x + y ≤ 100 (materials)
A = np.array([[5, 2], [1, 1]])
b = np.array([200, 100])
```

### Case 2: Critical Point Finding
Find where profit function gradient equals zero.

```python
# ∇f = 0 gives: 4x + y = 152, x + 2y = 80
A = np.array([[4, 1], [1, 2]])
b = np.array([152, 80])
```

### Case 3: Error Handling
Solver handles errors gracefully:

```python
# Singular matrix
A = np.array([[1, 2], [2, 4]])  # Linearly dependent
b = np.array([10, 20])

result = solver.solve_optimal_mix()
# result['status'] == 'error'
# result['msg'] == 'Matrix A is singular...'
```

## What Makes This Better?

| Feature | Original | This Version |
|---------|----------|--------------|
| Maximum verification | ❌ Hardcoded `True` | ✅ Mathematical proof via Hessian |
| Error handling | ❌ None | ✅ Comprehensive |
| Tests | ❌ None | ✅ 16 tests, 100% pass |
| Documentation | ❌ None | ✅ Full docs + examples |
| Type hints | ❌ None | ✅ Complete |

## Verification Explained

The solver doesn't just claim it's a maximum—it proves it:

1. **First-order test**: Checks if ∇f ≈ 0 (critical point)
2. **Second-order test**: Checks if Hessian is negative definite
   - H₁₁ < 0? ✓
   - det(H) > 0? ✓
   - → Confirmed maximum! ✓

## Status Codes

- `"success"` - Optimal solution found and verified
- `"infeasible"` - Solution violates constraints (e.g., x < 0)
- `"error"` - System problem (singular matrix, wrong dimensions)

## Files in This PR

```
optimization_solver.py              # Main implementation
test_optimization_solver.py         # 16 unit tests
examples_optimization_solver.py     # 7 practical examples
OPTIMIZATION_SOLVER_README.md       # Full documentation
COMPARISON.md                       # vs. original code
requirements-optimization.txt       # Dependencies
QUICKSTART.md                       # This file
```

## Running Tests

```bash
pytest test_optimization_solver.py -v
# 16 passed in 0.11s
```

## Running Examples

```bash
# Run all examples non-interactively
python3 examples_optimization_solver.py
```

## Need Help?

- Read `OPTIMIZATION_SOLVER_README.md` for full API reference
- Check `COMPARISON.md` to see improvements over original
- Run `examples_optimization_solver.py` for practical scenarios
- Review test cases in `test_optimization_solver.py`

## Mathematical Background (Brief)

**Objective**: Maximize f(x, y) = 152x + 80y - 2x² - y² - xy

**Constraints**: 
- Ax = b (linear)
- x ≥ 0, y ≥ 0 (non-negativity)

**Method**:
1. Solve Ax = b for critical point
2. Verify x ≥ 0, y ≥ 0
3. Check Hessian for maximum
4. Return verified result

## License

Free to use for educational and commercial purposes.
