"""
Unit tests for the OptimalMixSolver class.
"""

import numpy as np
import pytest
from optimization_solver import OptimalMixSolver


class TestOptimalMixSolver:
    """Test suite for OptimalMixSolver."""
    
    def test_initialization_valid(self):
        """Test successful initialization with valid inputs."""
        A = np.array([[4, 1], [1, 2]])
        b = np.array([152, 80])
        solver = OptimalMixSolver(A, b)
        
        assert solver.A.shape == (2, 2)
        assert solver.b.shape == (2,)
        np.testing.assert_array_equal(solver.A, A)
        np.testing.assert_array_equal(solver.b, b)
    
    def test_initialization_incompatible_dimensions(self):
        """Test initialization with incompatible A and b dimensions."""
        A = np.array([[4, 1], [1, 2]])
        b = np.array([152, 80, 100])  # Wrong size
        
        with pytest.raises(ValueError, match="Incompatible dimensions"):
            OptimalMixSolver(A, b)
    
    def test_objective_function(self):
        """Test objective function calculation."""
        A = np.array([[4, 1], [1, 2]])
        b = np.array([152, 80])
        solver = OptimalMixSolver(A, b)
        
        # Test at origin
        result = solver._objective_function(0, 0)
        assert result == 0
        
        # Test at a known point: f(10, 20) = 152(10) + 80(20) - 2(100) - 400 - 200
        result = solver._objective_function(10, 20)
        expected = 152*10 + 80*20 - 2*10**2 - 20**2 - 10*20
        assert abs(result - expected) < 1e-10
    
    def test_gradient(self):
        """Test gradient calculation."""
        A = np.array([[4, 1], [1, 2]])
        b = np.array([152, 80])
        solver = OptimalMixSolver(A, b)
        
        # Test at origin: ∇f(0,0) = [152, 80]
        grad = solver._gradient(0, 0)
        np.testing.assert_array_almost_equal(grad, [152, 80])
        
        # Test at (10, 20): ∇f = [152 - 40 - 20, 80 - 40 - 10] = [92, 30]
        grad = solver._gradient(10, 20)
        np.testing.assert_array_almost_equal(grad, [92, 30])
    
    def test_hessian(self):
        """Test Hessian matrix calculation."""
        A = np.array([[4, 1], [1, 2]])
        b = np.array([152, 80])
        solver = OptimalMixSolver(A, b)
        
        H = solver._hessian()
        expected = np.array([[-4, -1], [-1, -2]])
        np.testing.assert_array_equal(H, expected)
        
        # Verify Hessian is negative definite (for maximum)
        eigenvalues = np.linalg.eigvals(H)
        assert all(eigenvalues < 0), "Hessian should be negative definite"
    
    def test_solve_optimal_mix_success(self):
        """Test successful optimization with the canonical problem."""
        # Solve ∇f = 0: [4 1][x] = [152]
        #                [1 2][y]   [80]
        A = np.array([[4, 1], [1, 2]])
        b = np.array([152, 80])
        solver = OptimalMixSolver(A, b)
        
        result = solver.solve_optimal_mix()
        
        assert result["status"] == "success"
        assert result["is_global_maximum"] is True
        
        # Solution should be: x = (2*152 - 80) / 7 ≈ 32, y = (4*80 - 152) / 7 ≈ 24
        x = result["optimal_mix"]["x_commercial"]
        y = result["optimal_mix"]["y_residential"]
        
        # Verify the solution satisfies Ax = b
        solution = np.array([x, y])
        np.testing.assert_array_almost_equal(A @ solution, b, decimal=1)
        
        # Verify gradient is near zero at the solution
        assert result["gradient_norm"] < 1e-5
        
        # Verify benefit is positive
        assert result["max_operating_benefit"] > 0
    
    def test_solve_optimal_mix_negative_solution(self):
        """Test case where optimal solution has negative values (infeasible)."""
        # System that yields negative solution
        A = np.array([[1, 0], [0, 1]])
        b = np.array([-10, 20])  # x = -10, y = 20
        solver = OptimalMixSolver(A, b)
        
        result = solver.solve_optimal_mix()
        
        assert result["status"] == "infeasible"
        assert "non-negativity" in result["msg"].lower()
    
    def test_solve_optimal_mix_singular_matrix(self):
        """Test with singular matrix."""
        # Singular matrix (second row is twice the first)
        A = np.array([[1, 2], [2, 4]])
        b = np.array([10, 20])
        solver = OptimalMixSolver(A, b)
        
        result = solver.solve_optimal_mix()
        
        assert result["status"] == "error"
        assert "singular" in result["msg"].lower()
    
    def test_solve_optimal_mix_wrong_dimensions(self):
        """Test with matrix of wrong dimensions."""
        # 3x2 matrix (overdetermined system)
        A = np.array([[1, 2], [3, 4], [5, 6]])
        b = np.array([10, 20, 30])
        solver = OptimalMixSolver(A, b)
        
        result = solver.solve_optimal_mix()
        
        assert result["status"] == "error"
        assert "2 equations" in result["msg"]
    
    def test_solve_optimal_mix_one_column(self):
        """Test with matrix having wrong number of columns."""
        A = np.array([[1], [2]])
        b = np.array([10, 20])
        solver = OptimalMixSolver(A, b)
        
        result = solver.solve_optimal_mix()
        
        assert result["status"] == "error"
        assert "2 columns" in result["msg"]
    
    def test_is_maximum_at_critical_point(self):
        """Test maximum verification at actual critical point."""
        A = np.array([[4, 1], [1, 2]])
        b = np.array([152, 80])
        solver = OptimalMixSolver(A, b)
        
        # Solve to get the critical point
        solution = np.linalg.solve(A, b)
        x, y = solution
        
        is_max, msg = solver._is_maximum(x, y)
        
        assert is_max is True
        assert "negative definite" in msg.lower()
    
    def test_is_maximum_not_critical_point(self):
        """Test maximum verification at non-critical point."""
        A = np.array([[4, 1], [1, 2]])
        b = np.array([152, 80])
        solver = OptimalMixSolver(A, b)
        
        # Test at origin (not a critical point)
        is_max, msg = solver._is_maximum(0, 0)
        
        assert is_max is False
        assert "not a critical point" in msg.lower()
    
    def test_rounding_precision(self):
        """Test that results are properly rounded to 2 decimal places."""
        A = np.array([[4, 1], [1, 2]])
        b = np.array([152, 80])
        solver = OptimalMixSolver(A, b)
        
        result = solver.solve_optimal_mix()
        
        x = result["optimal_mix"]["x_commercial"]
        y = result["optimal_mix"]["y_residential"]
        benefit = result["max_operating_benefit"]
        
        # Check that values have at most 2 decimal places
        assert x == round(x, 2)
        assert y == round(y, 2)
        assert benefit == round(benefit, 2)
    
    def test_feasible_solution_at_boundary(self):
        """Test solution exactly at boundary (x=0 or y=0)."""
        # Solution where x = 0
        A = np.array([[1, 0], [0, 1]])
        b = np.array([0, 40])
        solver = OptimalMixSolver(A, b)
        
        result = solver.solve_optimal_mix()
        
        # Should be feasible (x=0 is allowed)
        assert result["status"] == "success"
        assert result["optimal_mix"]["x_commercial"] == 0.0
        assert result["optimal_mix"]["y_residential"] == 40.0


class TestIntegration:
    """Integration tests for realistic scenarios."""
    
    def test_realistic_business_scenario(self):
        """Test with realistic business constraints."""
        # Scenario: Find optimal mix given resource constraints
        # 4x + y ≤ 152 (labor hours constraint at equality)
        # x + 2y ≤ 80 (material constraint at equality)
        
        A = np.array([[4, 1], [1, 2]])
        b = np.array([152, 80])
        solver = OptimalMixSolver(A, b)
        
        result = solver.solve_optimal_mix()
        
        assert result["status"] == "success"
        
        x = result["optimal_mix"]["x_commercial"]
        y = result["optimal_mix"]["y_residential"]
        
        # Verify constraints are satisfied
        assert 4*x + y <= 152 + 0.1  # Small tolerance for rounding
        assert x + 2*y <= 80 + 0.1
        
        # Verify positive quantities
        assert x > 0
        assert y > 0
        
        # Verify maximum is found
        assert result["is_global_maximum"] is True
    
    def test_edge_case_zero_benefit(self):
        """Test edge case where optimal benefit might be zero."""
        # Create a scenario where optimal point gives zero or near-zero benefit
        A = np.array([[1, 0], [0, 1]])
        b = np.array([0, 0])
        solver = OptimalMixSolver(A, b)
        
        result = solver.solve_optimal_mix()
        
        assert result["status"] == "success"
        assert result["optimal_mix"]["x_commercial"] == 0.0
        assert result["optimal_mix"]["y_residential"] == 0.0
        assert result["max_operating_benefit"] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
