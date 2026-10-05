"""
Læds Opportunity Score v1

Ranking relativo de oportunidades de compra dentro de un inventario
normalizado. La fórmula es aditiva, con curvas y pesos publicados.
No imputa infraestructura, seguridad, usos de suelo ni demanda externa:
si un dato no está en el libro, la variable se omite y se renormalizan
los pesos. La confianza de datos viaja aparte del puntaje.

Doce variables:
    1. basis_discount      descuento vs. valor estimado de comparables
    2. price_cut           reducción del precio de lista
    3. dom_window          ventana de negociación por días publicado
    4. gross_yield         renta anual estimada / precio
    5. age_condition       antigüedad y renovación
    6. spec_fit            recámaras, baños y estacionamientos vs. tipo
    7. differentiators     características diferenciales
    8. zone_momentum       cambio del precio/m² de la microzona
    9. absorption          velocidad del mercado (días en mercado de pares)
   10. supply_scarcity     escasez de oferta activa
   11. market_depth        profundidad para salir
   12. price_band          cercanía a la banda líquida de precios

supply_scarcity y market_depth transforman el mismo conteo de anuncios
activos con curvas distintas. El cap rate se reporta, pero no entra como
variable propia: con vacancia y opex uniformes es un múltiplo del yield.
"""

from __future__ import annotations

import json
import statistics
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


FORMULA_VERSION = "laeds-opportunity-score-v1"

PROPERTY_WEIGHTS = {
    "age_condition": 0.45,
    "spec_fit": 0.35,
    "differentiators": 0.20,
}
APPRECIATION_WEIGHTS = {
    "zone_momentum": 0.45,
    "absorption": 0.30,
    "supply_scarcity": 0.25,
}
INVESTMENT_WEIGHTS = {
    "gross_yield": 0.70,
    "basis_discount": 0.30,
}
LIQUIDITY_WEIGHTS = {
    "absorption": 0.40,
    "market_depth": 0.30,
    "price_band": 0.30,
}
ANOMALY_WEIGHTS = {
    "basis_discount": 0.60,
    "price_cut": 0.25,
    "dom_window": 0.15,
}
OPPORTUNITY_WEIGHTS = {
    "anomaly": 0.35,
    "investment": 0.25,
    "appreciation": 0.20,
    "liquidity": 0.12,
    "property": 0.08,
}
THESIS_RANK_WEIGHTS = {
    "appreciation": {
        "appreciation": 0.50,
        "opportunity": 0.25,
        "investment": 0.15,
        "liquidity": 0.10,
    },
    "income": {
        "investment": 0.45,
        "opportunity": 0.25,
        "liquidity": 0.15,
        "appreciation": 0.15,
    },
    "opportunity": {"opportunity": 1.0},
    "balanced": {
        "opportunity": 0.40,
        "appreciation": 0.25,
        "investment": 0.25,
        "liquidity": 0.10,
    },
}
CONFIDENCE_WEIGHTS = {
    "cma": 0.25,
    "rent": 0.20,
    "momentum": 0.15,
    "published_at": 0.10,
    "price_history": 0.10,
    "age": 0.08,
    "features": 0.07,
    "size_and_price": 0.05,
}

BASIS_KNOTS = ((-0.20, 0.0), (0.0, 35.0), (0.10, 85.0), (0.20, 100.0))
PRICE_CUT_KNOTS = ((0.0, 25.0), (0.08, 80.0), (0.15, 100.0))
DOM_KNOTS = ((0.0, 35.0), (21.0, 35.0), (60.0, 75.0), (150.0, 100.0), (270.0, 55.0), (450.0, 20.0))
YIELD_KNOTS = ((0.0, 0.0), (0.03, 15.0), (0.05, 68.0), (0.08, 100.0))
MOMENTUM_KNOTS = ((-0.05, 15.0), (0.0, 48.0), (0.08, 100.0))
ABSORPTION_KNOTS = ((30.0, 100.0), (90.0, 62.0), (210.0, 20.0))
SCARCITY_KNOTS = ((5.0, 100.0), (25.0, 40.0), (40.0, 15.0))
DEPTH_KNOTS = ((1.0, 15.0), (3.0, 30.0), (8.0, 70.0), (20.0, 100.0))
PRICE_BAND_KNOTS = ((0.0, 100.0), (0.25, 25.0))

SPEC_BENCHMARKS = {
    "apartment": {"bedrooms": 2.0, "bathrooms": 2.0, "parking_spaces": 1.0},
    "house": {"bedrooms": 3.0, "bathrooms": 3.0, "parking_spaces": 2.0},
}
SPEC_PENALTIES = {"bedrooms": 18.0, "bathrooms": 15.0, "parking_spaces": 12.0}

FEATURE_CATALOG = {
    "apartment": ("elevator", "security", "gym", "balcony", "terrace", "view", "furnished", "storage"),
    "house": ("pool", "garden", "terrace", "view", "security", "furnished", "storage", "balcony"),
    "default": ("view", "security", "terrace", "furnished"),
}
FEATURE_ALIASES = {
    "view": ("view", "vista"),
    "pool": ("pool", "alberca", "piscina"),
    "garden": ("garden", "jardin"),
    "terrace": ("terrace", "terraza"),
    "balcony": ("balcony", "balcon"),
    "furnished": ("furnished", "amueblado", "amueblada"),
    "elevator": ("elevator", "elevador", "ascensor"),
    "security": ("security", "seguridad", "vigilancia"),
    "gym": ("gym", "gimnasio"),
    "storage": ("storage", "bodega"),
}
TYPE_ALIASES = (
    ("casa en condominio", "house"),
    ("departamento", "apartment"),
    ("apartment", "apartment"),
    ("depto", "apartment"),
    ("condominio", "apartment"),
    ("house", "house"),
    ("casa", "house"),
    ("terreno", "land"),
    ("land", "land"),
    ("oficina", "commercial"),
    ("local", "commercial"),
    ("commercial", "commercial"),
    ("bodega comercial", "commercial"),
)

VARIABLES = (
    "basis_discount",
    "price_cut",
    "dom_window",
    "gross_yield",
    "age_condition",
    "spec_fit",
    "differentiators",
    "zone_momentum",
    "absorption",
    "supply_scarcity",
    "market_depth",
    "price_band",
)


def piecewise(x: float, knots: Sequence[Tuple[float, float]]) -> float:
    """Interpolación lineal con clamp fuera del primer y último nudo."""
    if not knots:
        raise ValueError("La curva necesita al menos un nudo")
    if x <= knots[0][0]:
        return float(knots[0][1])
    if x >= knots[-1][0]:
        return float(knots[-1][1])
    for (x0, y0), (x1, y1) in zip(knots, knots[1:]):
        if x0 <= x <= x1:
            span = x1 - x0
            if span == 0:
                return float(y0)
            return float(y0 + ((x - x0) / span) * (y1 - y0))
    return float(knots[-1][1])


def weighted_blend(
    scores: Mapping[str, Optional[float]],
    weights: Mapping[str, float],
) -> Optional[float]:
    """Promedio ponderado. Los componentes ausentes se omiten y los pesos se renormalizan."""
    numerator = 0.0
    denominator = 0.0
    for name, weight in weights.items():
        value = scores.get(name)
        if value is None:
            continue
        numerator += weight * value
        denominator += weight
    if denominator == 0:
        return None
    return numerator / denominator


def fold_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.strip().lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def normalize_property_type(value: Optional[str]) -> str:
    text = fold_text(value or "")
    if not text:
        return "apartment"
    for alias, canonical in TYPE_ALIASES:
        if text == alias:
            return canonical
    return text


def canonicalize_features(features: Optional[Iterable[str]]) -> Optional[List[str]]:
    if features is None:
        return None
    found = []
    blobs = [fold_text(str(item)) for item in features if str(item).strip()]
    for canonical, aliases in FEATURE_ALIASES.items():
        if any(alias in blob for blob in blobs for alias in aliases):
            found.append(canonical)
    return found


def parse_date(value) -> Optional[date]:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return datetime.strptime(text[:10], "%Y-%m-%d").date()


def as_float(value) -> Optional[float]:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ValueError(f"Valor numérico inválido: {value!r}")
    return float(value)


def as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "si", "sí"}


def median(values: Sequence[float]) -> float:
    return float(statistics.median(values))


def percentile_rank(value: float, values: Sequence[float]) -> float:
    count = len(values)
    if count == 0:
        raise ValueError("No hay valores para el percentil")
    less = sum(1 for item in values if item < value)
    equal = sum(1 for item in values if item == value)
    return (less + 0.5 * equal) / count


def price_band_score(percentile: float) -> float:
    if 0.25 <= percentile <= 0.75:
        distance = 0.0
    elif percentile < 0.25:
        distance = 0.25 - percentile
    else:
        distance = percentile - 0.75
    return piecewise(distance, PRICE_BAND_KNOTS)


def formula_spec() -> Dict:
    return {
        "version": FORMULA_VERSION,
        "variables": list(VARIABLES),
        "weights": {
            "property": PROPERTY_WEIGHTS,
            "appreciation": APPRECIATION_WEIGHTS,
            "investment": INVESTMENT_WEIGHTS,
            "liquidity": LIQUIDITY_WEIGHTS,
            "anomaly": ANOMALY_WEIGHTS,
            "opportunity": OPPORTUNITY_WEIGHTS,
            "thesis_rank": THESIS_RANK_WEIGHTS,
        },
        "missing_data": "omit_and_renormalize",
        "cap_rate": "reported_only_noi_factor_times_gross_yield",
    }


@dataclass
class ScoreAssumptions:
    vacancy_rate: float = 0.08
    opex_ratio: float = 0.25
    comp_size_tolerance: float = 0.30
    rent_size_tolerance: float = 0.40
    min_comps: int = 3
    scarcity_min_listings: int = 5
    price_band_min_listings: int = 5
    absorption_min_observations: int = 3
    momentum_min_span_days: int = 90
    cohort_min_listings: int = 8

    def __post_init__(self) -> None:
        if not 0 <= self.vacancy_rate < 1:
            raise ValueError("vacancy_rate debe estar en [0, 1)")
        if not 0 <= self.opex_ratio < 1:
            raise ValueError("opex_ratio debe estar en [0, 1)")

    @property
    def noi_factor(self) -> float:
        return (1 - self.vacancy_rate) * (1 - self.opex_ratio)


@dataclass
class InvestmentThesis:
    city: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    min_gross_yield: Optional[float] = None
    min_cap_rate: Optional[float] = None
    horizon_years: int = 5
    objective: str = "balanced"
    property_types: Optional[List[str]] = None
    microzones: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.objective not in THESIS_RANK_WEIGHTS:
            allowed = ", ".join(THESIS_RANK_WEIGHTS)
            raise ValueError(f"objective debe ser uno de: {allowed}")
        if self.horizon_years <= 0:
            raise ValueError("horizon_years debe ser positivo")


@dataclass
class Listing:
    id: str
    property_type: str = "apartment"
    currency: str = "MXN"
    sale_price: Optional[float] = None
    original_price: Optional[float] = None
    rent_monthly: Optional[float] = None
    construction_m2: Optional[float] = None
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    parking_spaces: Optional[float] = None
    age_years: Optional[float] = None
    renovated: bool = False
    features: Optional[List[str]] = None
    features_provided: bool = False
    city: str = ""
    municipality: str = ""
    neighborhood: str = ""
    microzone: str = ""
    corridor: str = ""
    published_at: Optional[date] = None
    updated_at: Optional[date] = None
    agency: str = ""
    title: str = ""
    source: str = ""
    vacancy_rate: Optional[float] = None
    opex_ratio: Optional[float] = None

    @property
    def zone(self) -> str:
        return self.microzone or self.neighborhood or ""

    def market_key(self) -> Tuple[str, str, str, str]:
        return (
            fold_text(self.city),
            fold_text(self.zone),
            self.property_type,
            self.currency.upper(),
        )


@dataclass
class IndexPoint:
    microzone: str
    median_ppm2: float
    as_of: date
    city: str = ""
    property_type: Optional[str] = None

    def key(self) -> Tuple[str, str, str]:
        return (
            fold_text(self.city),
            fold_text(self.microzone),
            normalize_property_type(self.property_type) if self.property_type else "",
        )


@dataclass
class Signal:
    name: str
    score: Optional[float]
    observed: bool
    raw: Optional[float] = None
    unit: str = ""
    detail: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "score": _round(self.score, 2),
            "observed": self.observed,
            "raw": None if self.raw is None else round(self.raw, 6),
            "unit": self.unit,
            "detail": self.detail,
        }


@dataclass
class ListingScore:
    listing_id: str
    title: str
    status: str
    city: str
    municipality: str
    neighborhood: str
    microzone: str
    corridor: str
    property_type: str
    agency: str
    sale_price: Optional[float]
    currency: str
    estimated_value: Optional[float] = None
    discount_vs_market: Optional[float] = None
    gross_yield: Optional[float] = None
    cap_rate: Optional[float] = None
    monthly_rent: Optional[float] = None
    illustrative_annual_appreciation: Optional[float] = None
    appreciation_method: Optional[str] = None
    illustrative_horizon_change: Optional[float] = None
    property_score: Optional[float] = None
    appreciation_score: Optional[float] = None
    investment_score: Optional[float] = None
    liquidity_score: Optional[float] = None
    anomaly_score: Optional[float] = None
    opportunity_score: Optional[float] = None
    data_confidence: float = 0.0
    comp_count: int = 0
    rent_comp_count: int = 0
    signals: Dict[str, Signal] = field(default_factory=dict)
    confidence_parts: Dict[str, float] = field(default_factory=dict)
    narrative: str = ""
    matches_thesis: Optional[bool] = None
    thesis_rank_score: Optional[float] = None
    reject_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "listing_id": self.listing_id,
            "title": self.title,
            "status": self.status,
            "city": self.city,
            "municipality": self.municipality,
            "neighborhood": self.neighborhood,
            "microzone": self.microzone,
            "corridor": self.corridor,
            "property_type": self.property_type,
            "agency": self.agency,
            "sale_price": self.sale_price,
            "currency": self.currency,
            "estimated_value": _round(self.estimated_value, 2),
            "discount_vs_market": _round(self.discount_vs_market, 4),
            "gross_yield": _round(self.gross_yield, 4),
            "cap_rate": _round(self.cap_rate, 4),
            "monthly_rent": _round(self.monthly_rent, 2),
            "illustrative_annual_appreciation": _round(self.illustrative_annual_appreciation, 4),
            "appreciation_method": self.appreciation_method,
            "illustrative_horizon_change": _round(self.illustrative_horizon_change, 4),
            "property_score": _round(self.property_score, 2),
            "appreciation_score": _round(self.appreciation_score, 2),
            "investment_score": _round(self.investment_score, 2),
            "liquidity_score": _round(self.liquidity_score, 2),
            "anomaly_score": _round(self.anomaly_score, 2),
            "opportunity_score": _round(self.opportunity_score, 2),
            "data_confidence": _round(self.data_confidence, 4),
            "comp_count": self.comp_count,
            "rent_comp_count": self.rent_comp_count,
            "signals": {name: signal.to_dict() for name, signal in self.signals.items()},
            "confidence_parts": self.confidence_parts,
            "narrative": self.narrative,
            "matches_thesis": self.matches_thesis,
            "thesis_rank_score": _round(self.thesis_rank_score, 2),
            "reject_reasons": list(self.reject_reasons),
            "formula_version": FORMULA_VERSION,
        }


def listing_from_dict(raw: Mapping) -> Listing:
    if not raw.get("id"):
        raise ValueError("Cada inmueble necesita id")
    operation = fold_text(str(raw.get("operation") or "sale"))
    sale_price = as_float(raw.get("sale_price"))
    rent_monthly = as_float(raw.get("rent_monthly"))
    ask = as_float(raw.get("ask_price"))
    if operation in {"rent", "rental"}:
        if rent_monthly is None:
            rent_monthly = ask
    elif sale_price is None:
        sale_price = ask
    features_provided = "features" in raw and raw.get("features") is not None
    features = canonicalize_features(raw.get("features")) if features_provided else None
    microzone = str(raw.get("microzone") or "")
    neighborhood = str(raw.get("neighborhood") or raw.get("colonia") or "")
    if not microzone:
        microzone = neighborhood
    return Listing(
        id=str(raw["id"]),
        property_type=normalize_property_type(raw.get("property_type")),
        currency=str(raw.get("currency") or "MXN").upper(),
        sale_price=sale_price,
        original_price=as_float(raw.get("original_price")),
        rent_monthly=rent_monthly,
        construction_m2=as_float(raw.get("construction_m2", raw.get("construction_size"))),
        bedrooms=as_float(raw.get("bedrooms")),
        bathrooms=as_float(raw.get("bathrooms")),
        parking_spaces=as_float(raw.get("parking_spaces")),
        age_years=as_float(raw.get("age_years", raw.get("age"))),
        renovated=as_bool(raw.get("renovated")),
        features=features,
        features_provided=features_provided,
        city=str(raw.get("city") or ""),
        municipality=str(raw.get("municipality") or ""),
        neighborhood=neighborhood,
        microzone=microzone,
        corridor=str(raw.get("corridor") or ""),
        published_at=parse_date(raw.get("published_at")),
        updated_at=parse_date(raw.get("updated_at")),
        agency=str(raw.get("agency") or ""),
        title=str(raw.get("title") or ""),
        source=str(raw.get("source") or ""),
        vacancy_rate=as_float(raw.get("vacancy_rate")),
        opex_ratio=as_float(raw.get("opex_ratio")),
    )


def index_from_dict(raw: Mapping, default_city: str = "") -> IndexPoint:
    if raw.get("median_ppm2") is None or raw.get("as_of") is None:
        raise ValueError("Cada punto del índice necesita median_ppm2 y as_of")
    return IndexPoint(
        microzone=str(raw.get("microzone") or ""),
        median_ppm2=float(raw["median_ppm2"]),
        as_of=parse_date(raw.get("as_of")),
        city=str(raw.get("city") or default_city),
        property_type=raw.get("property_type"),
    )


class OpportunityEngine:
    def __init__(
        self,
        listings: Sequence[Listing],
        assumptions: Optional[ScoreAssumptions] = None,
        price_index: Optional[Sequence[IndexPoint]] = None,
        as_of: Optional[date] = None,
    ):
        self.assumptions = assumptions or ScoreAssumptions()
        self.as_of = as_of or date.today()
        self.listings = list(listings)
        self.price_index = list(price_index or [])
        ids = [item.id for item in self.listings]
        if len(ids) != len(set(ids)):
            raise ValueError("Hay ids de inmueble repetidos")

    def score_all(self) -> List[ListingScore]:
        return [self.score_listing(item) for item in self.listings if item.sale_price]

    def rank(
        self,
        thesis: Optional[InvestmentThesis] = None,
        top_n: Optional[int] = None,
    ) -> List[ListingScore]:
        scored = self.score_all()
        for item in scored:
            self._apply_thesis(item, thesis)
        ranked = sorted(scored, key=_sort_key)
        if top_n is not None:
            visible = [item for item in ranked if item.matches_thesis is not False]
            return visible[:top_n]
        return ranked

    def score_listing(self, listing: Listing) -> ListingScore:
        result = ListingScore(
            listing_id=listing.id,
            title=listing.title,
            status="scored",
            city=listing.city,
            municipality=listing.municipality,
            neighborhood=listing.neighborhood,
            microzone=listing.microzone,
            corridor=listing.corridor,
            property_type=listing.property_type,
            agency=listing.agency,
            sale_price=listing.sale_price,
            currency=listing.currency,
        )
        if not listing.sale_price or listing.sale_price <= 0 or not listing.construction_m2:
            result.status = "unscored"
            result.narrative = (
                "Sin precio de venta o metros de construcción no se calcula el score. "
                "Esas dos piezas anclan el valor estimado y el yield."
            )
            result.data_confidence = self._confidence(listing, cma=0, rent=0, momentum=0)
            return result

        signals: Dict[str, Signal] = {}
        value, discount, comp_count, value_detail = self._estimate_value(listing)
        result.estimated_value = value
        result.discount_vs_market = discount
        result.comp_count = comp_count
        signals["basis_discount"] = Signal(
            name="basis_discount",
            score=None if discount is None else piecewise(discount, BASIS_KNOTS),
            observed=discount is not None,
            raw=discount,
            unit="fraction_of_value",
            detail=value_detail,
        )
        cut, cut_detail = self._price_cut(listing)
        signals["price_cut"] = Signal(
            name="price_cut",
            score=None if cut is None else piecewise(cut, PRICE_CUT_KNOTS),
            observed=cut is not None,
            raw=cut,
            unit="fraction_of_original",
            detail=cut_detail,
        )
        dom, dom_detail = self._days_on_market(listing)
        signals["dom_window"] = Signal(
            name="dom_window",
            score=None if dom is None else piecewise(dom, DOM_KNOTS),
            observed=dom is not None,
            raw=dom,
            unit="days",
            detail=dom_detail,
        )
        rent, rent_count, rent_source = self._estimate_rent(listing)
        result.rent_comp_count = rent_count
        result.monthly_rent = rent
        gross_yield = (rent * 12 / listing.sale_price) if rent else None
        result.gross_yield = gross_yield
        vacancy = listing.vacancy_rate if listing.vacancy_rate is not None else self.assumptions.vacancy_rate
        opex = listing.opex_ratio if listing.opex_ratio is not None else self.assumptions.opex_ratio
        result.cap_rate = None if gross_yield is None else gross_yield * (1 - vacancy) * (1 - opex)
        signals["gross_yield"] = Signal(
            name="gross_yield",
            score=None if gross_yield is None else piecewise(gross_yield, YIELD_KNOTS),
            observed=gross_yield is not None,
            raw=gross_yield,
            unit="annual_fraction",
            detail=rent_source,
        )
        signals["age_condition"] = self._age_signal(listing)
        signals["spec_fit"] = self._spec_signal(listing)
        signals["differentiators"] = self._feature_signal(listing)

        momentum, method = self._momentum(listing)
        result.appreciation_method = method
        if method == "price_index":
            result.illustrative_annual_appreciation = momentum
        signals["zone_momentum"] = Signal(
            name="zone_momentum",
            score=None if momentum is None else piecewise(momentum, MOMENTUM_KNOTS),
            observed=momentum is not None and method == "price_index",
            raw=momentum,
            unit="annual_fraction",
            detail=method or "sin serie de precios",
        )
        # El proxy por cohorte se conserva en raw, pero no entra al score:
        # mezcla cambios de composición del inventario con plusvalía.
        if method == "listing_cohort_proxy":
            signals["zone_momentum"].score = None
            signals["zone_momentum"].observed = False
            signals["zone_momentum"].detail = (
                "proxy por cohorte de anuncios; no entra al score porque mezcla "
                f"composición y precio. Variación anualizada observada: {momentum:.1%}."
                if momentum is not None
                else "proxy por cohorte insuficiente"
            )

        absorption_days = self._absorption_days(listing)
        signals["absorption"] = Signal(
            name="absorption",
            score=None if absorption_days is None else piecewise(absorption_days, ABSORPTION_KNOTS),
            observed=absorption_days is not None,
            raw=absorption_days,
            unit="median_peer_days",
            detail="mediana de días publicado de los pares de la microzona",
        )
        active = self._active_count(listing)
        scarcity_observed = active >= self.assumptions.scarcity_min_listings
        signals["supply_scarcity"] = Signal(
            name="supply_scarcity",
            score=piecewise(active, SCARCITY_KNOTS) if scarcity_observed else None,
            observed=scarcity_observed,
            raw=float(active),
            unit="active_listings",
            detail=(
                f"{active} anuncios de venta activos en la microzona y tipo"
                if scarcity_observed
                else f"{active} anuncios; por debajo de {self.assumptions.scarcity_min_listings} no se interpreta como escasez"
            ),
        )
        signals["market_depth"] = Signal(
            name="market_depth",
            score=piecewise(float(active), DEPTH_KNOTS),
            observed=active > 0,
            raw=float(active),
            unit="active_listings",
            detail=f"{active} anuncios de venta activos en la microzona y tipo",
        )
        band = self._price_percentile(listing)
        signals["price_band"] = Signal(
            name="price_band",
            score=None if band is None else price_band_score(band),
            observed=band is not None,
            raw=band,
            unit="percentile",
            detail="percentil del precio pedido dentro de la microzona y tipo",
        )

        result.signals = signals
        score_of = {name: (signal.score if signal.observed else None) for name, signal in signals.items()}
        result.property_score = weighted_blend(score_of, PROPERTY_WEIGHTS)
        result.appreciation_score = weighted_blend(score_of, APPRECIATION_WEIGHTS)
        result.investment_score = weighted_blend(score_of, INVESTMENT_WEIGHTS)
        result.liquidity_score = weighted_blend(score_of, LIQUIDITY_WEIGHTS)
        result.anomaly_score = weighted_blend(score_of, ANOMALY_WEIGHTS)
        result.opportunity_score = weighted_blend(
            {
                "anomaly": result.anomaly_score,
                "investment": result.investment_score,
                "appreciation": result.appreciation_score,
                "liquidity": result.liquidity_score,
                "property": result.property_score,
            },
            OPPORTUNITY_WEIGHTS,
        )
        cma_quality = 1.0 if comp_count >= 5 else 0.6 if comp_count >= self.assumptions.min_comps else 0.0
        if rent and listing.rent_monthly:
            rent_quality = 1.0
        elif rent_count >= 3:
            rent_quality = 1.0
        elif rent_count >= 1:
            rent_quality = 0.5
        else:
            rent_quality = 0.0
        if method == "price_index":
            momentum_quality = 1.0
        elif method == "listing_cohort_proxy":
            momentum_quality = 0.45
        else:
            momentum_quality = 0.0
        result.confidence_parts = {
            "cma": cma_quality,
            "rent": rent_quality,
            "momentum": momentum_quality,
            "published_at": 1.0 if listing.published_at else 0.0,
            "price_history": 1.0 if listing.original_price else 0.0,
            "age": 1.0 if listing.age_years is not None else 0.0,
            "features": 1.0 if listing.features_provided else 0.0,
            "size_and_price": 1.0,
        }
        result.data_confidence = sum(
            CONFIDENCE_WEIGHTS[name] * value for name, value in result.confidence_parts.items()
        )
        result.narrative = self._narrative(result, vacancy, opex)
        return result

    def _apply_thesis(self, result: ListingScore, thesis: Optional[InvestmentThesis]) -> None:
        if thesis is None or result.status != "scored":
            return
        reasons = []
        if thesis.city and fold_text(thesis.city) not in fold_text(result.city):
            reasons.append(f"ciudad distinta de {thesis.city}")
        if thesis.budget_min is not None and (result.sale_price or 0) < thesis.budget_min:
            reasons.append("por debajo del presupuesto")
        if thesis.budget_max is not None and (result.sale_price or 0) > thesis.budget_max:
            reasons.append("por encima del presupuesto")
        if thesis.property_types:
            allowed = {normalize_property_type(item) for item in thesis.property_types}
            if result.property_type not in allowed:
                reasons.append("tipo de inmueble fuera de la tesis")
        if thesis.microzones:
            allowed_zones = {fold_text(item) for item in thesis.microzones}
            if fold_text(result.microzone) not in allowed_zones:
                reasons.append("microzona fuera de la tesis")
        if thesis.min_gross_yield is not None:
            if result.gross_yield is None:
                reasons.append("yield no observado; no cumple el mínimo de renta")
            elif result.gross_yield < thesis.min_gross_yield:
                reasons.append(
                    f"yield {result.gross_yield:.1%} bajo el mínimo {thesis.min_gross_yield:.1%}"
                )
        if thesis.min_cap_rate is not None:
            if result.cap_rate is None:
                reasons.append("cap rate no observado")
            elif result.cap_rate < thesis.min_cap_rate:
                reasons.append(
                    f"cap rate {result.cap_rate:.1%} bajo el mínimo {thesis.min_cap_rate:.1%}"
                )
        result.reject_reasons = reasons
        result.matches_thesis = not reasons
        if result.illustrative_annual_appreciation is not None:
            result.illustrative_horizon_change = (
                (1 + result.illustrative_annual_appreciation) ** thesis.horizon_years
            ) - 1
        composites = {
            "property": result.property_score,
            "appreciation": result.appreciation_score,
            "investment": result.investment_score,
            "liquidity": result.liquidity_score,
            "opportunity": result.opportunity_score,
        }
        result.thesis_rank_score = weighted_blend(composites, THESIS_RANK_WEIGHTS[thesis.objective])

    def _estimate_value(self, listing: Listing):
        comps = [other for other in self.listings if self._is_sale_comp(listing, other)]
        if len(comps) < self.assumptions.min_comps:
            return None, None, len(comps), f"{len(comps)} comparables; se necesitan {self.assumptions.min_comps}"
        ppm2 = [other.sale_price / other.construction_m2 for other in comps]
        base = median(ppm2) * listing.construction_m2
        total_adj, adj_detail = self._comp_adjustment(listing, comps)
        value = base * (1 + total_adj)
        discount = (value - listing.sale_price) / value
        detail = (
            f"{len(comps)} comps, mediana {median(ppm2):,.0f} {listing.currency}/m², "
            f"ajuste {total_adj:+.1%} ({adj_detail})"
        )
        return value, discount, len(comps), detail

    def _comp_adjustment(self, listing: Listing, comps: Sequence[Listing]) -> Tuple[float, str]:
        parts = []
        age_adj = 0.0
        ages = [item.age_years for item in comps if item.age_years is not None]
        if listing.age_years is not None and ages:
            age_adj = max(-0.08, min(0.08, -0.004 * (listing.age_years - median(ages))))
            parts.append(f"edad {age_adj:+.1%}")
        bed_adj = 0.0
        beds = [item.bedrooms for item in comps if item.bedrooms is not None]
        if listing.bedrooms is not None and beds:
            bed_adj = max(-0.045, min(0.045, 0.015 * (listing.bedrooms - median(beds))))
            parts.append(f"recámaras {bed_adj:+.1%}")
        park_adj = 0.0
        parks = [item.parking_spaces for item in comps if item.parking_spaces is not None]
        if listing.parking_spaces is not None and parks:
            park_adj = max(-0.04, min(0.04, 0.02 * (listing.parking_spaces - median(parks))))
            parts.append(f"estacionamiento {park_adj:+.1%}")
        total = max(-0.12, min(0.12, age_adj + bed_adj + park_adj))
        return total, ", ".join(parts) if parts else "sin ajuste"

    def _is_sale_comp(self, subject: Listing, other: Listing) -> bool:
        if other.id == subject.id:
            return False
        if subject.market_key() != other.market_key():
            return False
        if not other.sale_price or not other.construction_m2 or not subject.construction_m2:
            return False
        ratio = other.construction_m2 / subject.construction_m2
        tolerance = self.assumptions.comp_size_tolerance
        return (1 - tolerance) <= ratio <= (1 + tolerance)

    def _estimate_rent(self, listing: Listing) -> Tuple[Optional[float], int, str]:
        if listing.rent_monthly and listing.rent_monthly > 0:
            return listing.rent_monthly, 0, "renta publicada en el mismo inmueble"
        comps = []
        for other in self.listings:
            if other.id == listing.id or not other.rent_monthly or not other.construction_m2:
                continue
            if subject_rent_key(listing) != subject_rent_key(other):
                continue
            if not listing.construction_m2:
                continue
            ratio = other.construction_m2 / listing.construction_m2
            tolerance = self.assumptions.rent_size_tolerance
            if (1 - tolerance) <= ratio <= (1 + tolerance):
                comps.append(other)
        if not comps:
            return None, 0, "sin renta publicada ni comparables de renta"
        rent_ppm2 = median([item.rent_monthly / item.construction_m2 for item in comps])
        return rent_ppm2 * listing.construction_m2, len(comps), f"{len(comps)} comps de renta"

    def _price_cut(self, listing: Listing) -> Tuple[Optional[float], str]:
        if not listing.original_price or listing.original_price <= 0:
            return None, "sin precio de lista original"
        cut = (listing.original_price - listing.sale_price) / listing.original_price
        if cut < 0:
            return 0.0, "el precio pedido subió respecto del original"
        return cut, "reducción contra el precio original"

    def _days_on_market(self, listing: Listing) -> Tuple[Optional[float], str]:
        if listing.published_at is None:
            return None, "sin fecha de publicación"
        days = max(0, (self.as_of - listing.published_at).days)
        return float(days), f"publicado {days} días al {self.as_of.isoformat()}"

    def _age_signal(self, listing: Listing) -> Signal:
        if listing.age_years is None and not listing.renovated:
            return Signal("age_condition", None, False, detail="sin antigüedad")
        if listing.age_years is None:
            return Signal(
                "age_condition",
                62.0,
                True,
                raw=None,
                unit="years",
                detail="renovada, sin antigüedad declarada",
            )
        score = piecewise(listing.age_years, ((0.0, 100.0), (30.0, 40.0), (50.0, 15.0)))
        detail = f"{listing.age_years:g} años"
        if listing.renovated:
            score = min(100.0, score + 12.0)
            detail += ", renovada (+12)"
        return Signal("age_condition", score, True, raw=listing.age_years, unit="years", detail=detail)

    def _spec_signal(self, listing: Listing) -> Signal:
        benchmark = SPEC_BENCHMARKS.get(listing.property_type)
        if benchmark is None:
            return Signal("spec_fit", None, False, detail=f"sin benchmark para {listing.property_type}")
        if any(getattr(listing, name) is None for name in benchmark):
            return Signal("spec_fit", None, False, detail="faltan recámaras, baños o estacionamientos")
        score = 100.0
        notes = []
        for name, penalty in SPEC_PENALTIES.items():
            gap = getattr(listing, name) - benchmark[name]
            if gap < 0:
                score -= penalty * abs(gap)
                notes.append(f"{name} {gap:+g}")
            elif gap > 1:
                score -= 5.0 * (gap - 1)
                notes.append(f"{name} {gap:+g}")
        return Signal(
            "spec_fit",
            max(0.0, min(100.0, score)),
            True,
            raw=score,
            unit="score_before_clamp",
            detail=", ".join(notes) if notes else "en el benchmark del tipo",
        )

    def _feature_signal(self, listing: Listing) -> Signal:
        if not listing.features_provided:
            return Signal("differentiators", None, False, detail="características no informadas")
        catalog = FEATURE_CATALOG.get(listing.property_type, FEATURE_CATALOG["default"])
        hits = [name for name in catalog if name in (listing.features or [])]
        score = min(100.0, 20.0 + 13.0 * len(hits))
        return Signal(
            "differentiators",
            score,
            True,
            raw=float(len(hits)),
            unit="feature_hits",
            detail=", ".join(hits) if hits else "sin características del catálogo",
        )

    def _momentum(self, listing: Listing) -> Tuple[Optional[float], Optional[str]]:
        typed = []
        generic = []
        for point in self.price_index:
            city, zone, ptype = point.key()
            if city and city != fold_text(listing.city):
                continue
            if zone != fold_text(listing.zone):
                continue
            if ptype and ptype != listing.property_type:
                continue
            if ptype:
                typed.append(point)
            else:
                generic.append(point)
        series = typed or generic
        if len(series) >= 2:
            series = sorted(series, key=lambda point: point.as_of)
            first, last = series[0], series[-1]
            span = (last.as_of - first.as_of).days
            if span >= self.assumptions.momentum_min_span_days and first.median_ppm2 > 0:
                annual = (last.median_ppm2 / first.median_ppm2) ** (365.25 / span) - 1
                return annual, "price_index"
        return self._cohort_momentum(listing)

    def _cohort_momentum(self, listing: Listing) -> Tuple[Optional[float], Optional[str]]:
        group = [
            other
            for other in self.listings
            if other.market_key() == listing.market_key()
            and other.sale_price
            and other.construction_m2
            and other.published_at
        ]
        if len(group) < self.assumptions.cohort_min_listings:
            return None, None
        group.sort(key=lambda item: item.published_at)
        midpoint = len(group) // 2
        older, newer = group[:midpoint], group[midpoint:]
        older_day = median([(item.published_at - date.min).days for item in older])
        newer_day = median([(item.published_at - date.min).days for item in newer])
        span = newer_day - older_day
        if span < self.assumptions.momentum_min_span_days:
            return None, None
        older_ppm2 = median([item.sale_price / item.construction_m2 for item in older])
        newer_ppm2 = median([item.sale_price / item.construction_m2 for item in newer])
        if older_ppm2 <= 0:
            return None, None
        annual = (newer_ppm2 / older_ppm2) ** (365.25 / span) - 1
        return annual, "listing_cohort_proxy"

    def _peer_sales(self, listing: Listing, exclude_self: bool) -> List[Listing]:
        peers = []
        for other in self.listings:
            if exclude_self and other.id == listing.id:
                continue
            if other.market_key() != listing.market_key() or not other.sale_price:
                continue
            peers.append(other)
        return peers

    def _absorption_days(self, listing: Listing) -> Optional[float]:
        peers = [
            max(0, (self.as_of - other.published_at).days)
            for other in self._peer_sales(listing, exclude_self=True)
            if other.published_at
        ]
        if len(peers) < self.assumptions.absorption_min_observations:
            return None
        return median(peers)

    def _active_count(self, listing: Listing) -> int:
        return len(self._peer_sales(listing, exclude_self=False))

    def _price_percentile(self, listing: Listing) -> Optional[float]:
        prices = [other.sale_price for other in self._peer_sales(listing, exclude_self=False)]
        if len(prices) < self.assumptions.price_band_min_listings:
            return None
        return percentile_rank(listing.sale_price, prices)

    def _confidence(self, listing: Listing, cma: float, rent: float, momentum: float) -> float:
        parts = {
            "cma": cma,
            "rent": rent,
            "momentum": momentum,
            "published_at": 1.0 if listing.published_at else 0.0,
            "price_history": 1.0 if listing.original_price else 0.0,
            "age": 1.0 if listing.age_years is not None else 0.0,
            "features": 1.0 if listing.features_provided else 0.0,
            "size_and_price": 1.0 if listing.sale_price and listing.construction_m2 else 0.0,
        }
        return sum(CONFIDENCE_WEIGHTS[name] * value for name, value in parts.items())

    def _narrative(self, result: ListingScore, vacancy: float, opex: float) -> str:
        sentences = []
        discount = result.discount_vs_market
        if discount is not None and result.estimated_value is not None:
            if discount >= 0.005:
                sentences.append(
                    f"Esta propiedad aparece {discount:.1%} por debajo del valor estimado "
                    f"de inmuebles comparables ({result.comp_count} comps en {result.microzone or 'la zona'})."
                )
            elif discount <= -0.005:
                sentences.append(
                    f"El precio pedido está {abs(discount):.1%} por encima del valor estimado "
                    f"de comparables ({result.comp_count} comps en {result.microzone or 'la zona'})."
                )
            else:
                sentences.append(
                    f"El precio pedido está alineado con el valor estimado de comparables "
                    f"({result.comp_count} comps)."
                )
        if result.monthly_rent is not None and result.gross_yield is not None and result.cap_rate is not None:
            sentences.append(
                f"Renta estimada {result.monthly_rent:,.0f} {result.currency} al mes. "
                f"Yield bruto {result.gross_yield:.1%}. Cap rate estimado {result.cap_rate:.1%} "
                f"con vacancia {vacancy:.0%} y opex {opex:.0%}."
            )
        if result.illustrative_annual_appreciation is not None:
            sentences.append(
                f"La serie de precios de la microzona marca {result.illustrative_annual_appreciation:.1%} anual. "
                "Es una lectura de precios de oferta, no un pronóstico de plusvalía."
            )
        elif result.appreciation_method == "listing_cohort_proxy":
            sentences.append(
                "Hay un proxy de cohorte en los anuncios, pero no entra al score de plusvalía."
            )
        opportunity = result.opportunity_score
        if opportunity is not None:
            sentences.append(
                f"Opportunity Score {opportunity:.0f}/100. "
                f"Propiedad { _fmt_score(result.property_score) }, "
                f"plusvalía {_fmt_score(result.appreciation_score)}, "
                f"inversión {_fmt_score(result.investment_score)}, "
                f"liquidez {_fmt_score(result.liquidity_score)}. "
                f"Confianza de datos {result.data_confidence:.0%}."
            )
        return " ".join(sentences)


def subject_rent_key(listing: Listing) -> Tuple[str, str, str, str]:
    return listing.market_key()


def _fmt_score(value: Optional[float]) -> str:
    if value is None:
        return "n/d"
    return f"{value:.0f}/100"


def _round(value: Optional[float], digits: int) -> Optional[float]:
    if value is None:
        return None
    return round(value, digits)


def _sort_key(item: ListingScore):
    matched = 0 if item.matches_thesis is not False else 1
    rank = item.thesis_rank_score if item.thesis_rank_score is not None else item.opportunity_score
    rank = -(rank if rank is not None else -1)
    confidence = -(item.data_confidence or 0)
    return (matched, rank, confidence, item.listing_id)


def score_inventory(
    listings: Sequence[Mapping],
    thesis: Optional[Mapping] = None,
    assumptions: Optional[Mapping] = None,
    price_index: Optional[Sequence[Mapping]] = None,
    as_of: Optional[str] = None,
    top_n: Optional[int] = None,
) -> Dict:
    parsed = [listing_from_dict(item) for item in listings]
    assumption_obj = ScoreAssumptions(**assumptions) if assumptions else ScoreAssumptions()
    thesis_obj = InvestmentThesis(**thesis) if thesis else None
    default_city = parsed[0].city if parsed else ""
    index = [index_from_dict(item, default_city=default_city) for item in (price_index or [])]
    engine = OpportunityEngine(
        parsed,
        assumptions=assumption_obj,
        price_index=index,
        as_of=parse_date(as_of) if as_of else date.today(),
    )
    ranked = engine.rank(thesis_obj, top_n=top_n)
    return {
        "formula_version": FORMULA_VERSION,
        "formula": formula_spec(),
        "as_of": engine.as_of.isoformat(),
        "count": len(ranked),
        "results": [item.to_dict() for item in ranked],
    }


def load_book(path: str | Path) -> Dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return score_inventory(
        listings=payload.get("listings") or [],
        assumptions=payload.get("assumptions"),
        price_index=payload.get("price_index"),
        as_of=payload.get("as_of"),
    )


def sample_book_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "palm_diamante_sample.json"
