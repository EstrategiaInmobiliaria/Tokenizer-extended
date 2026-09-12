"""
Practical Examples for the Optimization Solver

This file demonstrates various real-world scenarios and use cases
for the OptimalMixSolver class.
"""

import numpy as np
from optimization_solver import OptimalMixSolver


def example_1_standard_optimization():
    """
    Example 1: Standard optimization problem - finding critical point
    
    Problem: Find x and y that maximize f(x,y) = 152x + 80y - 2x² - y² - xy
    subject to the gradient being zero (critical point).
    
    This gives us the system:
    ∂f/∂x = 152 - 4x - y = 0  →  4x + y = 152
    ∂f/∂y = 80 - 2y - x = 0   →  x + 2y = 80
    """
    print("=" * 70)
    print("EXAMPLE 1: Standard Optimization - Finding Critical Point")
    print("=" * 70)
    
    A = np.array([[4, 1], [1, 2]])
    b = np.array([152, 80])
    
    solver = OptimalMixSolver(A, b)
    result = solver.solve_optimal_mix()
    
    print(f"\nConstraint System:")
    print(f"  4x + y = 152")
    print(f"  x + 2y = 80")
    
    print(f"\nResult:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    if result["status"] == "success":
        x = result["optimal_mix"]["x_commercial"]
        y = result["optimal_mix"]["y_residential"]
        print(f"\n✓ Optimal solution: Produce {x} commercial units and {y} residential units")
        print(f"✓ Expected profit: ${result['max_operating_benefit']:,.2f}")
    
    print()


def example_2_resource_constraints():
    """
    Example 2: Resource allocation with different constraints
    
    Scenario: A company has:
    - 200 labor hours available
    - 100 units of material available
    
    Constraints:
    - Each commercial unit needs 5 hours and 1 unit of material
    - Each residential unit needs 2 hours and 1 unit of material
    """
    print("=" * 70)
    print("EXAMPLE 2: Resource Allocation Problem")
    print("=" * 70)
    
    # 5x + 2y = 200 (labor)
    # x + y = 100 (material)
    A = np.array([[5, 2], [1, 1]])
    b = np.array([200, 100])
    
    solver = OptimalMixSolver(A, b)
    result = solver.solve_optimal_mix()
    
    print(f"\nConstraints:")
    print(f"  Labor:    5x + 2y ≤ 200 hours")
    print(f"  Material: x + y ≤ 100 units")
    
    print(f"\nResult:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    if result["status"] == "success":
        x = result["optimal_mix"]["x_commercial"]
        y = result["optimal_mix"]["y_residential"]
        
        labor_used = 5*x + 2*y
        material_used = x + y
        
        print(f"\n✓ Resource utilization:")
        print(f"  Labor: {labor_used:.1f} / 200 hours ({labor_used/200*100:.1f}%)")
        print(f"  Material: {material_used:.1f} / 100 units ({material_used/100*100:.1f}%)")
    
    print()


def example_3_infeasible_solution():
    """
    Example 3: Infeasible solution (negative values)
    
    This demonstrates what happens when the optimal mathematical solution
    violates the non-negativity constraints.
    """
    print("=" * 70)
    print("EXAMPLE 3: Infeasible Solution (Negative Values)")
    print("=" * 70)
    
    # System that yields negative x value
    A = np.array([[1, 0], [0, 1]])
    b = np.array([-10, 40])
    
    solver = OptimalMixSolver(A, b)
    result = solver.solve_optimal_mix()
    
    print(f"\nConstraint System:")
    print(f"  x = -10")
    print(f"  y = 40")
    
    print(f"\nResult:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print(f"\n✗ This solution is infeasible because x < 0")
    print(f"✗ In reality, you cannot produce a negative quantity")
    print()


def example_4_boundary_case():
    """
    Example 4: Boundary case where one variable is zero
    
    Sometimes the optimal solution lies on the boundary of the feasible region.
    """
    print("=" * 70)
    print("EXAMPLE 4: Boundary Case (One Variable Zero)")
    print("=" * 70)
    
    # Solution where x = 0
    A = np.array([[1, 0], [0, 1]])
    b = np.array([0, 30])
    
    solver = OptimalMixSolver(A, b)
    result = solver.solve_optimal_mix()
    
    print(f"\nConstraint System:")
    print(f"  x = 0")
    print(f"  y = 30")
    
    print(f"\nResult:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    if result["status"] == "success":
        print(f"\n✓ Solution is on the boundary (x = 0)")
        print(f"✓ Only residential units should be produced")
    
    print()


def example_5_singular_matrix_error():
    """
    Example 5: Error handling - Singular matrix
    
    Demonstrates how the solver handles a singular (non-invertible) matrix.
    """
    print("=" * 70)
    print("EXAMPLE 5: Error Handling - Singular Matrix")
    print("=" * 70)
    
    # Singular matrix (second row is twice the first)
    A = np.array([[1, 2], [2, 4]])
    b = np.array([10, 20])
    
    solver = OptimalMixSolver(A, b)
    result = solver.solve_optimal_mix()
    
    print(f"\nConstraint System:")
    print(f"  x + 2y = 10")
    print(f"  2x + 4y = 20  (same as 2 × first equation)")
    
    print(f"\nResult:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print(f"\n✗ Matrix is singular (linearly dependent rows)")
    print(f"✗ System has infinite solutions or no solution")
    print()


def example_6_comparing_scenarios():
    """
    Example 6: Comparing multiple scenarios
    
    Compare different resource allocation strategies to find the best one.
    """
    print("=" * 70)
    print("EXAMPLE 6: Comparing Multiple Scenarios")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "Conservative (Low resources)",
            "A": np.array([[3, 1], [1, 2]]),
            "b": np.array([90, 50])
        },
        {
            "name": "Moderate (Medium resources)",
            "A": np.array([[4, 1], [1, 2]]),
            "b": np.array([152, 80])
        },
        {
            "name": "Aggressive (High resources)",
            "A": np.array([[5, 2], [2, 3]]),
            "b": np.array([250, 180])
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        solver = OptimalMixSolver(scenario["A"], scenario["b"])
        result = solver.solve_optimal_mix()
        results.append({
            "name": scenario["name"],
            "result": result
        })
    
    print("\nScenario Comparison:")
    print("-" * 70)
    
    for item in results:
        print(f"\n{item['name']}:")
        if item['result']['status'] == 'success':
            x = item['result']['optimal_mix']['x_commercial']
            y = item['result']['optimal_mix']['y_residential']
            profit = item['result']['max_operating_benefit']
            print(f"  Mix: x={x}, y={y}")
            print(f"  Profit: ${profit:,.2f}")
            print(f"  Verified Maximum: {item['result']['is_global_maximum']}")
        else:
            print(f"  Status: {item['result']['status']}")
            print(f"  Message: {item['result']['msg']}")
    
    # Find best scenario
    successful = [r for r in results if r['result']['status'] == 'success']
    if successful:
        best = max(successful, key=lambda r: r['result']['max_operating_benefit'])
        print(f"\n✓ Best scenario: {best['name']}")
        print(f"✓ Maximum profit: ${best['result']['max_operating_benefit']:,.2f}")
    
    print()


def example_7_sensitivity_analysis():
    """
    Example 7: Sensitivity analysis
    
    Analyze how the solution changes with small perturbations in constraints.
    """
    print("=" * 70)
    print("EXAMPLE 7: Sensitivity Analysis")
    print("=" * 70)
    
    base_A = np.array([[4, 1], [1, 2]])
    base_b = np.array([152, 80])
    
    print("\nBase case:")
    solver = OptimalMixSolver(base_A, base_b)
    base_result = solver.solve_optimal_mix()
    
    if base_result['status'] == 'success':
        base_profit = base_result['max_operating_benefit']
        base_x = base_result['optimal_mix']['x_commercial']
        base_y = base_result['optimal_mix']['y_residential']
        print(f"  x={base_x}, y={base_y}, profit=${base_profit:,.2f}")
    
    # Test sensitivity to first constraint
    print("\nSensitivity to first constraint (b₁):")
    for delta in [-10, -5, 0, 5, 10]:
        b_test = base_b.copy()
        b_test[0] += delta
        
        solver = OptimalMixSolver(base_A, b_test)
        result = solver.solve_optimal_mix()
        
        if result['status'] == 'success':
            profit = result['max_operating_benefit']
            profit_change = profit - base_profit
            print(f"  b₁ = {b_test[0]:3.0f}: profit = ${profit:7.2f} "
                  f"(change: ${profit_change:+7.2f})")
    
    print()


def run_all_examples():
    """Run all examples in sequence."""
    examples = [
        example_1_standard_optimization,
        example_2_resource_constraints,
        example_3_infeasible_solution,
        example_4_boundary_case,
        example_5_singular_matrix_error,
        example_6_comparing_scenarios,
        example_7_sensitivity_analysis
    ]
    
    for i, example_func in enumerate(examples, 1):
        example_func()
        if i < len(examples):
            input("Press Enter to continue to next example...")
            print("\n\n")


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  OPTIMIZATION SOLVER - PRACTICAL EXAMPLES".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    run_all_examples()
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
