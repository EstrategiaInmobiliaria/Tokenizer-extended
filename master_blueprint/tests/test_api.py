"""
Integration Tests for FastAPI Endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
sys.path.append('..')
from api.main import app


client = TestClient(app)


class TestHealthEndpoints:
    """Test health check and root endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns service info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Master Blueprint API"
        assert "version" in data
        assert "endpoints" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestWACCEndpoint:
    """Test WACC calculation endpoint"""
    
    def test_valid_wacc_request(self):
        """Test valid WACC calculation"""
        request_data = {
            "risk_free_rate": 0.05,
            "market_return": 0.12,
            "corporate_tax_rate": 0.27,
            "equity_value": 800000000,
            "debt_value": 400000000,
            "beta": 1.15,
            "debt_rate": 0.08
        }
        
        response = client.post("/api/v1/wacc/calculate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "wacc" in data
        assert "wacc_percentage" in data
        assert "cost_of_equity" in data
        assert 0 < data["wacc"] < 1
    
    def test_invalid_wacc_request_negative_rate(self):
        """Test WACC request with invalid negative rate"""
        request_data = {
            "risk_free_rate": -0.05,  # Invalid
            "market_return": 0.12,
            "corporate_tax_rate": 0.27,
            "equity_value": 800000000,
            "debt_value": 400000000,
            "beta": 1.15,
            "debt_rate": 0.08
        }
        
        response = client.post("/api/v1/wacc/calculate", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_wacc_response_structure(self):
        """Test that WACC response has expected structure"""
        request_data = {
            "risk_free_rate": 0.05,
            "market_return": 0.12,
            "corporate_tax_rate": 0.27,
            "equity_value": 1000000000,
            "debt_value": 500000000,
            "beta": 1.2,
            "debt_rate": 0.08
        }
        
        response = client.post("/api/v1/wacc/calculate", json=request_data)
        data = response.json()
        
        required_fields = [
            "wacc", "wacc_percentage", "cost_of_equity",
            "cost_of_debt_after_tax", "equity_weight",
            "debt_weight", "debt_to_equity_ratio"
        ]
        
        for field in required_fields:
            assert field in data


class TestDCFEndpoint:
    """Test DCF analysis endpoint"""
    
    def test_valid_dcf_request(self):
        """Test valid DCF analysis"""
        request_data = {
            "project_name": "Test Project",
            "initial_investment": 1200000000,
            "discount_rate": 0.096,
            "projection_years": 5,
            "rental_income": [150000000, 165000000, 180000000, 195000000, 210000000],
            "sales_revenue": [0, 0, 200000000, 300000000, 400000000],
            "operating_costs": [50000000, 52000000, 54000000, 56000000, 58000000],
            "capex": [20000000, 15000000, 15000000, 10000000, 10000000],
            "taxes": [25000000, 28000000, 35000000, 45000000, 55000000]
        }
        
        response = client.post("/api/v1/dcf/analyze", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "npv" in data
        assert "irr" in data
        assert "accept_project" in data
        assert isinstance(data["accept_project"], bool)
    
    def test_dcf_with_scenarios(self):
        """Test DCF with scenario analysis"""
        request_data = {
            "project_name": "Scenario Test",
            "initial_investment": 1000000000,
            "discount_rate": 0.1,
            "projection_years": 3,
            "rental_income": [100000000, 110000000, 120000000],
            "sales_revenue": [0, 0, 500000000],
            "operating_costs": [30000000, 32000000, 35000000],
            "capex": [10000000, 10000000, 10000000],
            "taxes": [20000000, 22000000, 25000000],
            "include_scenarios": True
        }
        
        response = client.post("/api/v1/dcf/analyze", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "scenarios" in data
        if data["scenarios"]:
            assert "optimistic" in data["scenarios"]
            assert "base" in data["scenarios"]
            assert "pessimistic" in data["scenarios"]


class TestOptimizationEndpoint:
    """Test optimization endpoint"""
    
    def test_valid_optimization_request(self):
        """Test valid optimization request"""
        request_data = {
            "products": [
                {
                    "name": "Product A",
                    "unit_price": 4500000,
                    "variable_cost": 2800000,
                    "fixed_cost_allocation": 0
                },
                {
                    "name": "Product B",
                    "unit_price": 6000000,
                    "variable_cost": 3500000,
                    "fixed_cost_allocation": 0
                }
            ],
            "resource_constraints": [
                {
                    "name": "Area",
                    "total_available": 15000,
                    "consumption_rates": [45, 65]
                },
                {
                    "name": "Budget",
                    "total_available": 300000000,
                    "consumption_rates": [2800000, 3500000]
                }
            ],
            "fixed_costs": 50000000,
            "min_demand": [20, 15],
            "max_demand": [200, 150]
        }
        
        response = client.post("/api/v1/optimize/mix", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        if data["success"]:
            assert "optimal_quantities" in data
            assert "optimal_profit" in data
            assert len(data["optimal_quantities"]) == 2
    
    def test_optimization_constraint_mismatch(self):
        """Test optimization with mismatched constraint rates"""
        request_data = {
            "products": [
                {"name": "A", "unit_price": 100, "variable_cost": 50},
                {"name": "B", "unit_price": 150, "variable_cost": 75}
            ],
            "resource_constraints": [
                {
                    "name": "Resource",
                    "total_available": 1000,
                    "consumption_rates": [1, 2, 3]  # 3 rates for 2 products (mismatch)
                }
            ],
            "fixed_costs": 0
        }
        
        response = client.post("/api/v1/optimize/mix", json=request_data)
        assert response.status_code == 400  # Bad request


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=api", "--cov-report=term-missing"])
