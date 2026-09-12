"""
Unit tests for the OperationsOptimizer class.
"""

import numpy as np
import pytest
from optimization_solver import OperationsOptimizer


class TestOperationsOptimizer:
    """Test suite for OperationsOptimizer."""
    
    def test_initialization_valid(self):
        """Test successful initialization with default gradient system."""
        optimizer = OperationsOptimizer()
        
        assert optimizer.A.shape == (2, 2)
        assert optimizer.b.shape == (2,)
        
        # Verify it's the gradient system
        expected_A = np.array([[4.0, 1.0], [1.0, 2.0]])
        expected_b = np.array([152.0, 80.0])
        np.testing.assert_array_equal(optimizer.A, expected_A)
        np.testing.assert_array_equal(optimizer.b, expected_b)
    
    def test_matrices_are_correct_type(self):
        """Test that matrices are float type."""
        optimizer = OperationsOptimizer()
        
        assert optimizer.A.dtype == np.float64
        assert optimizer.b.dtype == np.float64
    
    def test_objective_function(self):
        """Test objective function calculation."""
        optimizer = OperationsOptimizer()
        
        # Test at origin
        result = optimizer._objective_function(0, 0)
        assert result == 0
        
        # Test at a known point: f(10, 20) = 152(10) + 80(20) - 2(100) - 400 - 200
        result = optimizer._objective_function(10, 20)
        expected = 152*10 + 80*20 - 2*10**2 - 20**2 - 10*20
        assert abs(result - expected) < 1e-10
    
    def test_gradient(self):
        """Test gradient calculation."""
        optimizer = OperationsOptimizer()
        
        # Test at origin: ∇f(0,0) = [152, 80]
        grad = optimizer._gradient(0, 0)
        np.testing.assert_array_almost_equal(grad, [152, 80])
        
        # Test at (10, 20): ∇f = [152 - 40 - 20, 80 - 40 - 10] = [92, 30]
        grad = optimizer._gradient(10, 20)
        np.testing.assert_array_almost_equal(grad, [92, 30])
    
    def test_hessian(self):
        """Test Hessian matrix calculation."""
        optimizer = OperationsOptimizer()
        
        H = optimizer._hessian()
        expected = np.array([[-4, -1], [-1, -2]])
        np.testing.assert_array_equal(H, expected)
        
        # Verify Hessian is negative definite (for maximum)
        eigenvalues = np.linalg.eigvals(H)
        assert all(eigenvalues < 0), "Hessian should be negative definite"
    
    def test_solve_optimal_mix_success(self):
        """Test successful optimization with the standard gradient system."""
        # The default system solves ∇f = 0: [4 1][x] = [152]
        #                                     [1 2][y]   [80]
        optimizer = OperationsOptimizer()
        
        result = optimizer.solve_optimal_mix()
        
        assert result["status"] == "success"
        assert result["is_global_maximum"] is True
        
        # Solution should be: x ≈ 32, y ≈ 24
        x = result["optimal_mix"]["x_commercial"]
        y = result["optimal_mix"]["y_residential"]
        
        assert x == 32.0
        assert y == 24.0
        
        # Verify the solution satisfies Ax = b
        solution = np.array([x, y])
        np.testing.assert_array_almost_equal(optimizer.A @ solution, optimizer.b, decimal=1)
        
        # Verify gradient is near zero at the solution
        assert result["gradient_norm"] < 1e-5
        
        # Verify benefit is positive
        assert result["max_operating_benefit"] > 0
        assert result["max_operating_benefit"] == 3392.0
    
    def test_solve_optimal_mix_with_custom_tolerance(self):
        """Test optimization with custom gradient tolerance."""
        optimizer = OperationsOptimizer()
        
        result = optimizer.solve_optimal_mix(gradient_tolerance=1e-10)
        
        assert result["status"] == "success"
        assert result["gradient_norm"] < 1e-5
    
    def test_solve_optimal_mix_singular_matrix(self):
        """Test error handling when matrix becomes singular."""
        optimizer = OperationsOptimizer()
        
        # Make matrix singular by setting it to linearly dependent rows
        optimizer.A = np.array([[1, 2], [2, 4]])
        optimizer.b = np.array([10, 20])
        
        result = optimizer.solve_optimal_mix()
        
        assert result["status"] == "error"
        assert "singular" in result["msg"].lower()
    
    def test_solve_optimal_mix_negative_solution(self):
        """Test case where optimal solution has negative values (infeasible)."""
        optimizer = OperationsOptimizer()
        
        # System that yields negative solution
        optimizer.A = np.array([[1, 0], [0, 1]])
        optimizer.b = np.array([-10, 20])  # x = -10, y = 20
        
        result = optimizer.solve_optimal_mix()
        
        assert result["status"] == "infeasible"
        assert "dominio operativo" in result["msg"].lower()
    
    def test_is_maximum_at_critical_point(self):
        """Test maximum verification at actual critical point."""
        optimizer = OperationsOptimizer()
        
        # Solve to get the critical point
        solution = np.linalg.solve(optimizer.A, optimizer.b)
        x, y = solution
        
        is_max, msg = optimizer._is_maximum(x, y)
        
        assert is_max is True
        assert "negative definite" in msg.lower()
    
    def test_is_maximum_not_critical_point(self):
        """Test maximum verification at non-critical point."""
        optimizer = OperationsOptimizer()
        
        # Test at origin (not a critical point)
        is_max, msg = optimizer._is_maximum(0, 0)
        
        assert is_max is False
        assert "not a critical point" in msg.lower()
    
    def test_rounding_precision(self):
        """Test that results are properly rounded to 2 decimal places."""
        optimizer = OperationsOptimizer()
        
        result = optimizer.solve_optimal_mix()
        
        x = result["optimal_mix"]["x_commercial"]
        y = result["optimal_mix"]["y_residential"]
        benefit = result["max_operating_benefit"]
        
        # Check that values have at most 2 decimal places
        assert x == round(x, 2)
        assert y == round(y, 2)
        assert benefit == round(benefit, 2)
    
    def test_feasible_solution_at_boundary(self):
        """Test solution exactly at boundary (x=0 or y=0)."""
        optimizer = OperationsOptimizer()
        
        # Solution where x = 0
        optimizer.A = np.array([[1, 0], [0, 1]])
        optimizer.b = np.array([0, 40])
        
        result = optimizer.solve_optimal_mix()
        
        # Should be feasible (x=0 is allowed)
        assert result["status"] == "success"
        assert result["optimal_mix"]["x_commercial"] == 0.0
        assert result["optimal_mix"]["y_residential"] == 40.0


class TestIntegration:
    """Integration tests for realistic scenarios."""
    
    def test_realistic_business_scenario(self):
        """Test with the standard gradient system (realistic business case)."""
        # Standard scenario: Find optimal mix given the gradient system
        # 4x + y = 152 (from ∂f/∂x = 0)
        # x + 2y = 80 (from ∂f/∂y = 0)
        
        optimizer = OperationsOptimizer()
        
        result = optimizer.solve_optimal_mix()
        
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
        optimizer = OperationsOptimizer()
        
        # Create a scenario where optimal point gives zero or near-zero benefit
        optimizer.A = np.array([[1, 0], [0, 1]])
        optimizer.b = np.array([0, 0])
        
        result = optimizer.solve_optimal_mix()
        
        assert result["status"] == "success"
        assert result["optimal_mix"]["x_commercial"] == 0.0
        assert result["optimal_mix"]["y_residential"] == 0.0
        assert result["max_operating_benefit"] == 0.0
    
    def test_compatibility_with_original_interface(self):
        """Test that the new implementation maintains compatibility with original output format."""
        optimizer = OperationsOptimizer()
        result = optimizer.solve_optimal_mix()
        
        # Check all original keys are present
        assert "status" in result
        assert "optimal_mix" in result
        assert "x_commercial" in result["optimal_mix"]
        assert "y_residential" in result["optimal_mix"]
        assert "max_operating_benefit" in result
        assert "gradient_norm" in result
        assert "is_global_maximum" in result
        
        # New key added for verification
        assert "verification_details" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
