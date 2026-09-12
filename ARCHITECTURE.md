# Visual Architecture - Optimization Solver

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OptimalMixSolver                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Input: A (2×2 matrix), b (2×1 vector)                    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  solve_optimal_mix()                                │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │ 1. Validate Input                            │  │   │
│  │  │    - Check dimensions (2×2 system)           │  │   │
│  │  │    - Check singularity (det ≠ 0)            │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │ 2. Solve Linear System                       │  │   │
│  │  │    - Compute x, y = A⁻¹b                    │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │ 3. Check Feasibility                         │  │   │
│  │  │    - Verify x ≥ 0, y ≥ 0                    │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │ 4. Calculate Metrics                         │  │   │
│  │  │    - f(x,y) = 152x+80y-2x²-y²-xy           │  │   │
│  │  │    - ∇f(x,y) = [152-4x-y, 80-2y-x]         │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │ 5. Verify Optimality                         │  │   │
│  │  │    - Check ‖∇f‖ ≈ 0 (critical point)       │  │   │
│  │  │    - Check H negative definite              │  │   │
│  │  │      • H₁₁ < 0                              │  │   │
│  │  │      • det(H) > 0                           │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │ 6. Return Result                             │  │   │
│  │  │    - Status, values, verification           │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  Helper Methods:                                            │
│  - _objective_function(x,y) → float                        │
│  - _gradient(x,y) → [∂f/∂x, ∂f/∂y]                        │
│  - _hessian() → [[∂²f/∂x², ∂²f/∂x∂y],                     │
│                   [∂²f/∂y∂x, ∂²f/∂y²]]                     │
│  - _is_maximum(x,y) → (bool, reason)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
INPUT                  VALIDATION              SOLUTION             OUTPUT
─────                  ──────────              ────────             ──────

┌───┐ ┌───┐                                                      ┌─────────┐
│ A │ │ b │           ┌──────────┐                              │ success │
└───┘ └───┘    ──────>│ Check    │──────>  ┌──────────┐  ──────>│ x, y    │
                       │ dims     │         │ Solve    │         │ profit  │
                       │ singular │         │ Ax = b   │         │ verified│
                       └──────────┘         └──────────┘         └─────────┘
                            │                    │
                            │ Error              │ Infeasible
                            v                    v
                       ┌──────────┐         ┌──────────┐
                       │ error    │         │infeasible│
                       │ message  │         │ x<0,y<0  │
                       └──────────┘         └──────────┘
```

## Verification Flow

```
Critical Point Check:
───────────────────────
    ∇f(x,y) ≈ 0?
        │
        ├─ NO ──> Return: Not a critical point ❌
        │
        └─ YES
           │
           v
    Second Order Check:
    ───────────────────
    H = [[-4, -1], [-1, -2]]
    
    H₁₁ < 0 AND det(H) > 0?
        │
        ├─ YES ──> Return: Maximum ✅
        │
        ├─ H₁₁ > 0, det > 0 ──> Return: Minimum ❌
        │
        ├─ det < 0 ──> Return: Saddle point ❌
        │
        └─ else ──> Return: Inconclusive ⚠️
```

## Comparison: Before vs After

```
ORIGINAL FUNCTION (15 lines)          IMPROVED SOLVER (210 lines)
────────────────────────────          ───────────────────────────

┌─────────────────────────┐          ┌──────────────────────────┐
│ Input: self.A, self.b   │          │ Input: A, b (validated)  │
└─────────────────────────┘          └──────────────────────────┘
           │                                      │
           v                                      v
┌─────────────────────────┐          ┌──────────────────────────┐
│ Solve Ax = b            │          │ Validate Input           │
│ (no error check)        │          │ - Dimensions ✓           │
└─────────────────────────┘          │ - Singularity ✓          │
           │                          └──────────────────────────┘
           v                                      │
┌─────────────────────────┐                      v
│ Check x,y ≥ 0           │          ┌──────────────────────────┐
└─────────────────────────┘          │ Solve with Error Handler │
           │                          │ try-catch ✓              │
           v                          └──────────────────────────┘
┌─────────────────────────┐                      │
│ Calculate profit        │                      v
│ Calculate gradient      │          ┌──────────────────────────┐
│ (but don't use it!)     │          │ Check Feasibility ✓      │
└─────────────────────────┘          └──────────────────────────┘
           │                                      │
           v                                      v
┌─────────────────────────┐          ┌──────────────────────────┐
│ Return:                 │          │ Calculate Metrics        │
│ - is_global_maximum:    │          │ - Objective function ✓   │
│   True (HARDCODED!) ❌  │          │ - Gradient ✓             │
│                         │          │ - Hessian ✓              │
└─────────────────────────┘          └──────────────────────────┘
                                                 │
                                                 v
                                    ┌──────────────────────────┐
                                    │ Verify Optimality        │
                                    │ - Gradient ≈ 0 ✓         │
                                    │ - Hessian test ✓         │
                                    │ - PROVEN maximum ✅       │
                                    └──────────────────────────┘
                                                 │
                                                 v
                                    ┌──────────────────────────┐
                                    │ Return Verified Result   │
                                    │ + explanation ✓          │
                                    └──────────────────────────┘
```

## Mathematical Foundation

```
Objective Function:
─────────────────
f(x, y) = 152x + 80y - 2x² - y² - xy

First Order (Gradient):
──────────────────────
∇f = [∂f/∂x]   [152 - 4x - y]
     [∂f/∂y] = [80 - 2y - x ]

Critical Point: ∇f = 0
────────────────────────
152 - 4x - y = 0  →  4x + y = 152
80 - 2y - x = 0   →  x + 2y = 80

Second Order (Hessian):
──────────────────────
H = [∂²f/∂x²    ∂²f/∂x∂y]   [-4  -1]
    [∂²f/∂y∂x   ∂²f/∂y²] = [-1  -2]

Maximum Test:
────────────
H₁₁ = -4 < 0 ✓
det(H) = (-4)(-2) - (-1)(-1) = 8 - 1 = 7 > 0 ✓

Conclusion: VERIFIED MAXIMUM ✅
```

## Test Coverage Map

```
┌────────────────────────────────────────────────────────┐
│                   Test Categories                       │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Initialization│  │  Success     │  │   Error     │ │
│  │              │  │  Cases       │  │  Handling   │ │
│  │ • Valid dims │  │ • Standard   │  │ • Singular  │ │
│  │ • Invalid    │  │ • Boundary   │  │ • Wrong dim │ │
│  └──────────────┘  │ • Feasible   │  │ • Infeasible│ │
│                    └──────────────┘  └─────────────┘ │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Mathematical │  │ Integration  │  │   Edge      │ │
│  │              │  │              │  │   Cases     │ │
│  │ • Objective  │  │ • Realistic  │  │ • Zero vals │ │
│  │ • Gradient   │  │ • Multi-     │  │ • Rounding  │ │
│  │ • Hessian    │  │   scenario   │  │ • Precision │ │
│  │ • Maximum    │  │ • Comparison │  └─────────────┘ │
│  └──────────────┘  └──────────────┘                   │
│                                                         │
│  Result: 16/16 Tests Passed ✅                         │
└────────────────────────────────────────────────────────┘
```

## Status Flow

```
                    solve_optimal_mix()
                           │
                           v
        ┌──────────────────┼──────────────────┐
        │                  │                   │
        v                  v                   v
   ┌─────────┐      ┌────────────┐      ┌──────────┐
   │ ERROR   │      │ INFEASIBLE │      │ SUCCESS  │
   │         │      │            │      │          │
   │ Matrix  │      │ x < 0 or   │      │ x, y ≥ 0 │
   │ singular│      │ y < 0      │      │ Verified │
   │ or wrong│      │            │      │ maximum  │
   │ dims    │      └────────────┘      └──────────┘
   └─────────┘
```

## File Organization

```
optimization_solver/
│
├── optimization_solver.py         ← Core implementation
│   ├── OptimalMixSolver class
│   ├── __init__(A, b)
│   ├── solve_optimal_mix()
│   ├── _objective_function()
│   ├── _gradient()
│   ├── _hessian()
│   └── _is_maximum()
│
├── test_optimization_solver.py    ← Test suite
│   ├── TestOptimalMixSolver
│   │   ├── 14 unit tests
│   └── TestIntegration
│       └── 2 integration tests
│
├── examples_optimization_solver.py ← Practical demos
│   ├── Example 1: Standard optimization
│   ├── Example 2: Resource allocation
│   ├── Example 3: Infeasible case
│   ├── Example 4: Boundary case
│   ├── Example 5: Error handling
│   ├── Example 6: Scenario comparison
│   └── Example 7: Sensitivity analysis
│
├── OPTIMIZATION_SOLVER_README.md  ← Full documentation
├── COMPARISON.md                  ← Before/after analysis
├── QUICKSTART.md                  ← Quick reference
├── IMPLEMENTATION_SUMMARY.md      ← Project overview
├── ARCHITECTURE.md                ← This file
└── requirements-optimization.txt  ← Dependencies
```
