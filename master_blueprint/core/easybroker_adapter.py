"""
Adaptador de lectura del payload de propiedad de EasyBroker.

No llama a la API. La cuenta normal de EasyBroker solo ve el inventario
de esa cuenta; un portal multiagencia usa Integration Partners y recibe
el mismo objeto de propiedad. Este módulo lo deja en el esquema que
consume el Opportunity Score.

La microzona no existe en EasyBroker. v1 usa la colonia como microzona
hasta que haya una capa geográfica propia.
"""

from __future__ import annotations

from typing import Mapping, Optional

from .opportunity_score import Listing, as_float, listing_from_dict, normalize_property_type


def from_easybroker_property(payload: Mapping) -> Listing:
    if not isinstance(payload, Mapping):
        raise ValueError("El payload de EasyBroker tiene que ser un objeto")
    location = payload.get("location") or {}
    if not isinstance(location, Mapping):
        location = {}
    city = str(location.get("city") or payload.get("city") or "")
    neighborhood = str(location.get("neighborhood") or payload.get("neighborhood") or "")
    name = str(location.get("name") or "")
    if not neighborhood and name:
        neighborhood = name.split(",")[0].strip()
    if not city and "," in name:
        city = name.split(",")[-1].strip()
    microzone = str(payload.get("microzone") or neighborhood)

    sale_price = None
    rent_monthly = None
    currency = str(payload.get("currency") or "MXN")
    original_price = as_float(payload.get("original_price"))
    construction_m2 = as_float(payload.get("construction_size", payload.get("construction_m2")))
    for operation in payload.get("operations") or []:
        if not isinstance(operation, Mapping):
            continue
        kind = str(operation.get("type") or "").strip().lower()
        amount = as_float(operation.get("amount"))
        currency = str(operation.get("currency") or currency)
        unit = str(operation.get("unit") or "total").strip().lower()
        if original_price is None:
            original_price = as_float(operation.get("original_amount") or operation.get("previous_amount"))
        if kind == "sale":
            sale_price = _apply_unit(amount, unit, construction_m2)
        elif kind in {"rental", "rent"}:
            rent_monthly = _apply_unit(amount, unit, construction_m2)

    bathrooms = as_float(payload.get("bathrooms"))
    half = as_float(payload.get("half_bathrooms")) or 0.0
    if bathrooms is not None:
        bathrooms += 0.5 * half
    elif half:
        bathrooms = 0.5 * half

    age = payload.get("age", payload.get("age_years"))
    if isinstance(age, str) and age.strip().lower() in {"new", "nuevo", "a estrenar"}:
        age = 0

    return listing_from_dict(
        {
            "id": payload.get("public_id") or payload.get("id"),
            "title": payload.get("title") or "",
            "property_type": normalize_property_type(payload.get("property_type")),
            "currency": currency,
            "sale_price": sale_price,
            "original_price": original_price,
            "rent_monthly": rent_monthly,
            "construction_m2": construction_m2,
            "bedrooms": payload.get("bedrooms"),
            "bathrooms": bathrooms,
            "parking_spaces": payload.get("parking_spaces"),
            "age_years": age,
            "features": _feature_names(payload),
            "city": city,
            "municipality": str(location.get("region") or payload.get("municipality") or ""),
            "neighborhood": neighborhood,
            "microzone": microzone,
            "published_at": payload.get("published_at") or payload.get("created_at"),
            "updated_at": payload.get("updated_at"),
            "agency": _agency_name(payload),
            "source": "easybroker",
        }
    )


def _apply_unit(amount: Optional[float], unit: str, construction_m2: Optional[float]) -> Optional[float]:
    if amount is None:
        return None
    if unit in {"square_meter", "m2", "square_meters"}:
        if not construction_m2:
            return None
        return amount * construction_m2
    return amount


def _feature_names(payload: Mapping):
    raw = payload.get("features")
    if raw is None:
        raw = payload.get("property_features")
    if raw is None:
        return None
    names = []
    for item in raw:
        if isinstance(item, Mapping):
            names.append(str(item.get("name") or item.get("label") or ""))
        else:
            names.append(str(item))
    return names


def _agency_name(payload: Mapping) -> str:
    agency = payload.get("agency")
    if isinstance(agency, Mapping):
        return str(agency.get("name") or "")
    agent = payload.get("agent")
    if isinstance(agent, Mapping):
        return str(agent.get("full_name") or agent.get("name") or "")
    return ""
