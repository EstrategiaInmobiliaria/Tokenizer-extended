"""
Unit Tests for WACC Engine
"""

import pytest
from core.wacc_engine import WACCEngine, MarketParameters, CapitalStructure, quick_wacc_calculation


class TestMarketParameters:
    """Tests for MarketParameters dataclass"""
    
    def test_valid_parameters(self):
        """Test creating valid market parameters"""
        market = MarketParameters(
            risk_free_rate=0.05,
            market_return=0.12,
            corporate_tax_rate=0.27
        )
        assert market.risk_free_rate == 0.05
        assert market.market_return == 0.12
        assert market.corporate_tax_rate == 0.27
    
    def test_invalid_risk_free_rate(self):
        """Test that invalid risk-free rate raises error"""
        with pytest.raises(ValueError):
            MarketParameters(
                risk_free_rate=1.5,  # > 1, invalid
                market_return=0.12,
                corporate_tax_rate=0.27
            )
    
    def test_negative_tax_rate(self):
        """Test that negative tax rate raises error"""
        with pytest.raises(ValueError):
            MarketParameters(
                risk_free_rate=0.05,
                market_return=0.12,
                corporate_tax_rate=-0.1
            )


class TestCapitalStructure:
    """Tests for CapitalStructure dataclass"""
    
    def test_total_value_calculation(self):
        """Test total value calculation"""
        capital = CapitalStructure(
            equity_value=800_000_000,
            debt_value=400_000_000,
            beta=1.15,
            debt_rate=0.08
        )
        assert capital.total_value == 1_200_000_000
    
    def test_weights_calculation(self):
        """Test equity and debt weight calculations"""
        capital = CapitalStructure(
            equity_value=800_000_000,
            debt_value=400_000_000,
            beta=1.15,
            debt_rate=0.08
        )
        assert abs(capital.equity_weight - 0.6667) < 0.01
        assert abs(capital.debt_weight - 0.3333) < 0.01
        assert abs(capital.equity_weight + capital.debt_weight - 1.0) < 0.0001
    
    def test_debt_to_equity_ratio(self):
        """Test D/E ratio calculation"""
        capital = CapitalStructure(
            equity_value=800_000_000,
            debt_value=400_000_000,
            beta=1.15,
            debt_rate=0.08
        )
        assert capital.debt_to_equity_ratio == 0.5


class TestWACCEngine:
    """Tests for WACC Engine"""
    
    @pytest.fixture
    def standard_market(self):
        """Standard market parameters"""
        return MarketParameters(
            risk_free_rate=0.05,
            market_return=0.12,
            corporate_tax_rate=0.27
        )
    
    @pytest.fixture
    def standard_capital(self):
        """Standard capital structure"""
        return CapitalStructure(
            equity_value=800_000_000,
            debt_value=400_000_000,
            beta=1.15,
            debt_rate=0.08
        )
    
    def test_cost_of_equity_calculation(self, standard_market, standard_capital):
        """Test CAPM cost of equity calculation"""
        engine = WACCEngine(standard_market, standard_capital)
        cost_of_equity = engine.calculate_cost_of_equity()
        
        # Re = Rf + β(Rm - Rf) = 0.05 + 1.15(0.12 - 0.05) = 0.1305
        expected = 0.05 + 1.15 * (0.12 - 0.05)
        assert abs(cost_of_equity - expected) < 0.0001
    
    def test_after_tax_cost_of_debt(self, standard_market, standard_capital):
        """Test after-tax cost of debt calculation"""
        engine = WACCEngine(standard_market, standard_capital)
        after_tax_debt_cost = engine.calculate_after_tax_cost_of_debt()
        
        # Rd(1 - Tc) = 0.08(1 - 0.27) = 0.0584
        expected = 0.08 * (1 - 0.27)
        assert abs(after_tax_debt_cost - expected) < 0.0001
    
    def test_wacc_calculation(self, standard_market, standard_capital):
        """Test full WACC calculation"""
        engine = WACCEngine(standard_market, standard_capital)
        wacc = engine.calculate_wacc()
        
        # Manual calculation
        cost_of_equity = 0.1305
        after_tax_debt = 0.0584
        equity_weight = 2/3
        debt_weight = 1/3
        expected_wacc = equity_weight * cost_of_equity + debt_weight * after_tax_debt
        
        assert abs(wacc - expected_wacc) < 0.01
        assert 0 < wacc < 1  # WACC should be between 0 and 100%
    
    def test_wacc_is_weighted_average(self, standard_market, standard_capital):
        """Test that WACC is between cost of equity and cost of debt"""
        engine = WACCEngine(standard_market, standard_capital)
        wacc = engine.calculate_wacc()
        cost_of_equity = engine.calculate_cost_of_equity()
        after_tax_debt = engine.calculate_after_tax_cost_of_debt()
        
        # WACC should be between the two costs
        assert after_tax_debt < wacc < cost_of_equity
    
    def test_detailed_breakdown_structure(self, standard_market, standard_capital):
        """Test that detailed breakdown contains all expected keys"""
        engine = WACCEngine(standard_market, standard_capital)
        breakdown = engine.get_detailed_breakdown()
        
        expected_keys = {
            'risk_free_rate', 'market_return', 'market_risk_premium',
            'corporate_tax_rate', 'equity_value', 'debt_value',
            'total_value', 'equity_weight', 'debt_weight',
            'debt_to_equity_ratio', 'beta', 'cost_of_equity',
            'cost_of_debt_before_tax', 'cost_of_debt_after_tax',
            'tax_shield_on_debt', 'wacc', 'wacc_percentage'
        }
        
        assert set(breakdown.keys()) == expected_keys
    
    def test_100_percent_equity(self):
        """Test WACC with 100% equity financing"""
        market = MarketParameters(0.05, 0.12, 0.27)
        capital = CapitalStructure(
            equity_value=1_000_000_000,
            debt_value=0,
            beta=1.15,
            debt_rate=0.08
        )
        
        engine = WACCEngine(market, capital)
        wacc = engine.calculate_wacc()
        cost_of_equity = engine.calculate_cost_of_equity()
        
        # With no debt, WACC should equal cost of equity
        assert abs(wacc - cost_of_equity) < 0.0001


class TestQuickWACCCalculation:
    """Tests for quick calculation function"""
    
    def test_quick_calculation_returns_dict(self):
        """Test that quick calculation returns a dictionary"""
        result = quick_wacc_calculation()
        assert isinstance(result, dict)
    
    def test_quick_calculation_contains_wacc(self):
        """Test that result contains WACC"""
        result = quick_wacc_calculation(
            equity_value=1_000_000,
            debt_value=500_000,
            beta=1.2
        )
        assert 'wacc' in result
        assert 'wacc_percentage' in result
        assert result['wacc_percentage'] == result['wacc'] * 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
