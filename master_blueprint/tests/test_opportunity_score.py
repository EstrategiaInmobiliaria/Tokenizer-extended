"""Tests del Læds Opportunity Score v1."""

from datetime import date

import pytest

from core.easybroker_adapter import from_easybroker_property
from core.opportunity_score import (
    ANOMALY_WEIGHTS,
    APPRECIATION_WEIGHTS,
    BASIS_KNOTS,
    FORMULA_VERSION,
    INVESTMENT_WEIGHTS,
    LIQUIDITY_WEIGHTS,
    OPPORTUNITY_WEIGHTS,
    PROPERTY_WEIGHTS,
    InvestmentThesis,
    Listing,
    OpportunityEngine,
    ScoreAssumptions,
    Signal,
    listing_from_dict,
    load_book,
    piecewise,
    sample_book_path,
    score_inventory,
    weighted_blend,
)


def _apartment(**overrides) -> Listing:
    payload = {
        "id": "A",
        "property_type": "apartment",
        "ask_price": 8_000_000,
        "construction_m2": 100,
        "bedrooms": 2,
        "bathrooms": 2,
        "parking_spaces": 1,
        "age_years": 10,
        "features": [],
        "city": "CDMX",
        "neighborhood": "Norte",
        "microzone": "Norte",
        "published_at": "2026-07-01",
        "currency": "MXN",
    }
    payload.update(overrides)
    return listing_from_dict(payload)


def _market():
    listings = [
        _apartment(id=f"C{i}", ask_price=8_000_000, published_at="2026-08-01")
        for i in range(1, 5)
    ]
    listings.append(
        _apartment(
            id="SUB",
            ask_price=7_000_000,
            original_price=7_600_000,
            published_at="2026-06-27",
            rent_monthly=40_000,
        )
    )
    return listings


class TestCurves:
    def test_piecewise_clamps_and_interpolates(self):
        knots = ((0.0, 0.0), (10.0, 100.0))
        assert piecewise(-5, knots) == 0
        assert piecewise(10, knots) == 100
        assert piecewise(25, knots) == 100
        assert piecewise(2.5, knots) == 25

    def test_weights_sum_to_one(self):
        for weights in (
            PROPERTY_WEIGHTS,
            APPRECIATION_WEIGHTS,
            INVESTMENT_WEIGHTS,
            LIQUIDITY_WEIGHTS,
            ANOMALY_WEIGHTS,
            OPPORTUNITY_WEIGHTS,
        ):
            assert sum(weights.values()) == pytest.approx(1)

    def test_blend_renormalizes_missing_component(self):
        score = weighted_blend({"gross_yield": None, "basis_discount": 80}, INVESTMENT_WEIGHTS)
        assert score == pytest.approx(80)


class TestComparableMarket:
    def setup_method(self):
        self.engine = OpportunityEngine(_market(), as_of=date(2026, 10, 5))
        self.subject = next(item for item in self.engine.listings if item.id == "SUB")
        self.result = self.engine.score_listing(self.subject)

    def test_discount_against_identical_comps(self):
        assert self.result.comp_count == 4
        assert self.result.estimated_value == pytest.approx(8_000_000)
        assert self.result.discount_vs_market == pytest.approx(0.125)
        assert self.result.signals["basis_discount"].score == pytest.approx(piecewise(0.125, BASIS_KNOTS))

    def test_yield_and_cap_rate_identity(self):
        assert self.result.monthly_rent == pytest.approx(40_000)
        assert self.result.gross_yield == pytest.approx(480_000 / 7_000_000)
        assert self.result.cap_rate == pytest.approx(self.result.gross_yield * 0.92 * 0.75)

    def test_opportunity_is_the_published_blend(self):
        scores = {
            name: signal.score if signal.observed else None
            for name, signal in self.result.signals.items()
        }
        anomaly = weighted_blend(scores, ANOMALY_WEIGHTS)
        investment = weighted_blend(scores, INVESTMENT_WEIGHTS)
        appreciation = weighted_blend(scores, APPRECIATION_WEIGHTS)
        liquidity = weighted_blend(scores, LIQUIDITY_WEIGHTS)
        property_score = weighted_blend(scores, PROPERTY_WEIGHTS)
        expected = weighted_blend(
            {
                "anomaly": anomaly,
                "investment": investment,
                "appreciation": appreciation,
                "liquidity": liquidity,
                "property": property_score,
            },
            OPPORTUNITY_WEIGHTS,
        )
        assert self.result.anomaly_score == pytest.approx(anomaly)
        assert self.result.opportunity_score == pytest.approx(expected)
        assert 0 <= self.result.opportunity_score <= 100

    def test_negotiation_window_beats_a_fresh_listing(self):
        fresh = _apartment(id="NEW", ask_price=8_000_000, published_at="2026-09-25")
        peers = [item for item in _market() if item.id != "SUB"]
        engine = OpportunityEngine(peers + [fresh], as_of=date(2026, 10, 5))
        fresh_score = engine.score_listing(fresh).signals["dom_window"].score
        stale_score = self.result.signals["dom_window"].score
        assert stale_score > fresh_score

    def test_missing_size_is_not_scored(self):
        broken = _apartment(id="BAD", construction_m2=None)
        result = OpportunityEngine([broken], as_of=date(2026, 10, 5)).score_listing(broken)
        assert result.status == "unscored"
        assert result.opportunity_score is None

    def test_without_rent_investment_falls_back_to_discount(self):
        listings = [item for item in _market() if item.id != "SUB"]
        listings.append(_apartment(id="NOR", ask_price=7_000_000, original_price=7_600_000))
        result = OpportunityEngine(listings, as_of=date(2026, 10, 5)).score_listing(listings[-1])
        assert result.gross_yield is None
        assert result.signals["gross_yield"].observed is False
        assert result.investment_score == pytest.approx(result.signals["basis_discount"].score)

    def test_thesis_rejects_price_and_unknown_yield(self):
        thesis = InvestmentThesis(
            city="CDMX",
            budget_min=5_000_000,
            budget_max=6_500_000,
            min_gross_yield=0.05,
            objective="appreciation",
            horizon_years=5,
        )
        ranked = self.engine.rank(thesis)
        subject = next(item for item in ranked if item.listing_id == "SUB")
        assert subject.matches_thesis is False
        assert any("presupuesto" in reason for reason in subject.reject_reasons)


class TestSampleBook:
    def test_sample_is_labeled_and_ranks_discount_over_full_price(self):
        payload = load_book(sample_book_path())
        assert payload["formula_version"] == FORMULA_VERSION
        by_id = {item["listing_id"]: item for item in payload["results"]}
        assert "PD-R1" not in by_id
        assert by_id["PD-X1"]["status"] == "unscored"
        bargain = by_id["PD-08"]
        trophy = by_id["PD-09"]
        assert bargain["discount_vs_market"] > 0.10
        assert bargain["opportunity_score"] > trophy["opportunity_score"]
        assert trophy["property_score"] > bargain["property_score"]
        span_days = (date(2026, 10, 5) - date(2025, 10, 5)).days
        expected_momentum = (56200 / 52000) ** (365.25 / span_days) - 1
        assert bargain["illustrative_annual_appreciation"] == pytest.approx(expected_momentum, abs=5e-5)
        assert "por debajo del valor estimado" in bargain["narrative"]
        houses = by_id["PD-H1"]
        assert houses["signals"]["basis_discount"]["observed"] is False
        assert houses["data_confidence"] < bargain["data_confidence"]

    def test_thesis_can_request_yield_and_budget(self):
        book = sample_book_path().read_text(encoding="utf-8")
        import json

        payload = json.loads(book)
        result = score_inventory(
            payload["listings"],
            thesis={
                "city": "Acapulco",
                "budget_min": 4_000_000,
                "budget_max": 5_500_000,
                "min_gross_yield": 0.05,
                "objective": "appreciation",
                "horizon_years": 5,
            },
            assumptions=payload["assumptions"],
            price_index=payload["price_index"],
            as_of=payload["as_of"],
        )
        matched = [item for item in result["results"] if item["matches_thesis"]]
        assert matched
        assert matched[0]["listing_id"] == "PD-08"
        assert all(item["sale_price"] <= 5_500_000 for item in matched)
        assert all(item["gross_yield"] >= 0.05 for item in matched)


class TestEasyBrokerAdapter:
    def test_maps_partner_property_payload(self):
        listing = from_easybroker_property(
            {
                "public_id": "EB-1001",
                "title": "Departamento en Condesa",
                "property_type": "Departamento",
                "bedrooms": 2,
                "bathrooms": 2,
                "half_bathrooms": 1,
                "parking_spaces": 1,
                "construction_size": 85,
                "age": 5,
                "features": ["Terraza", "Elevador", "Seguridad 24h"],
                "location": {
                    "name": "Condesa, Cuauhtémoc",
                    "latitude": 19.41,
                    "longitude": -99.17,
                },
                "operations": [
                    {
                        "type": "sale",
                        "amount": 6_200_000,
                        "currency": "MXN",
                        "unit": "total",
                    },
                    {
                        "type": "rental",
                        "amount": 35_000,
                        "currency": "MXN",
                        "unit": "total",
                    },
                ],
                "published_at": "2026-01-15T12:00:00Z",
                "agency": {"name": "Agencia Norte"},
            }
        )
        assert listing.id == "EB-1001"
        assert listing.property_type == "apartment"
        assert listing.sale_price == 6_200_000
        assert listing.rent_monthly == 35_000
        assert listing.bathrooms == pytest.approx(2.5)
        assert listing.construction_m2 == 85
        assert listing.neighborhood == "Condesa"
        assert listing.microzone == "Condesa"
        assert listing.city == "Cuauhtémoc"
        assert listing.published_at == date(2026, 1, 15)
        assert "terrace" in listing.features
        assert "elevator" in listing.features
        assert "security" in listing.features
        assert listing.agency == "Agencia Norte"

    def test_square_meter_price_uses_construction_size(self):
        listing = from_easybroker_property(
            {
                "public_id": "EB-M2",
                "property_type": "Casa",
                "construction_size": 200,
                "operations": [
                    {"type": "sale", "amount": 40_000, "currency": "MXN", "unit": "square_meter"}
                ],
            }
        )
        assert listing.sale_price == pytest.approx(8_000_000)
        assert listing.property_type == "house"


def test_assumptions_reject_invalid_vacancy():
    with pytest.raises(ValueError):
        ScoreAssumptions(vacancy_rate=1)


def test_score_endpoint_returns_formula_and_ranking():
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)
    response = client.post(
        "/api/v1/opportunity/score",
        json={
            "as_of": "2026-10-05",
            "top_n": 1,
            "listings": [
                {
                    "id": "C1",
                    "ask_price": 8000000,
                    "construction_m2": 100,
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "parking_spaces": 1,
                    "age_years": 10,
                    "features": [],
                    "city": "CDMX",
                    "microzone": "Norte",
                    "published_at": "2026-08-01",
                },
                {
                    "id": "C2",
                    "ask_price": 8000000,
                    "construction_m2": 100,
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "parking_spaces": 1,
                    "age_years": 10,
                    "features": [],
                    "city": "CDMX",
                    "microzone": "Norte",
                    "published_at": "2026-08-01",
                },
                {
                    "id": "C3",
                    "ask_price": 8000000,
                    "construction_m2": 100,
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "parking_spaces": 1,
                    "age_years": 10,
                    "features": [],
                    "city": "CDMX",
                    "microzone": "Norte",
                    "published_at": "2026-08-01",
                },
                {
                    "id": "SUB",
                    "ask_price": 7000000,
                    "construction_m2": 100,
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "parking_spaces": 1,
                    "age_years": 10,
                    "features": [],
                    "city": "CDMX",
                    "microzone": "Norte",
                    "published_at": "2026-06-27",
                    "rent_monthly": 40000,
                },
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["formula_version"] == FORMULA_VERSION
    assert body["results"][0]["listing_id"] == "SUB"
    assert body["results"][0]["discount_vs_market"] == pytest.approx(0.125)


def test_signal_roundtrip_shape():
    payload = Signal("basis_discount", 88.5, True, raw=0.125, unit="fraction", detail="ok").to_dict()
    assert payload["observed"] is True
    assert payload["score"] == 88.5
