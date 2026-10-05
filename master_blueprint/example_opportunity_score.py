"""
Corre el Opportunity Score v1 sobre el libro de calibración Palm Diamante.

Uso:
    python example_opportunity_score.py
    python example_opportunity_score.py ruta/al/inventario.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from core.opportunity_score import sample_book_path, score_inventory


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else sample_book_path()
    book = json.loads(path.read_text(encoding="utf-8"))
    thesis = {
        "city": "Acapulco",
        "budget_min": 4_000_000,
        "budget_max": 8_000_000,
        "min_gross_yield": 0.05,
        "objective": "appreciation",
        "horizon_years": 5,
    }
    if book.get("synthetic"):
        print("Libro sintético de calibración. No es inventario real de Palm Diamante.")
    print(f"Fuente: {path}")
    print(
        "Tesis: invertir 4–8 M en Acapulco, yield bruto mínimo 5%, "
        "objetivo plusvalía a 5 años.\n"
    )
    result = score_inventory(
        book["listings"],
        thesis=thesis,
        assumptions=book.get("assumptions"),
        price_index=book.get("price_index"),
        as_of=book.get("as_of"),
        top_n=3,
    )
    medals = ("1", "2", "3")
    for index, item in enumerate(result["results"], start=1):
        if not item["matches_thesis"]:
            continue
        price = item["sale_price"] or 0
        value = item["estimated_value"]
        discount = item["discount_vs_market"]
        appreciation = item["illustrative_annual_appreciation"]
        print(f"Oportunidad #{medals[index - 1] if index <= 3 else index}")
        print(f"{item['title']} — {item['microzone']}")
        print(f"${price:,.0f} {item['currency']}")
        if value is not None:
            print(f"Precio estimado de mercado: ${value:,.0f}")
        if discount is not None:
            print(f"{discount:+.1%} vs. valor estimado de comparables")
        if appreciation is not None:
            print(f"Serie de oferta de la microzona: {appreciation:.1%} anual")
        else:
            print("Serie de oferta de la microzona: no observada")
        if item["cap_rate"] is not None:
            print(f"Cap rate estimado: {item['cap_rate']:.1%}")
        if item["gross_yield"] is not None:
            print(f"Yield bruto: {item['gross_yield']:.1%}")
        print(f"Liquidez: {item['liquidity_score']:.0f}/100")
        print(f"Opportunity Score: {item['opportunity_score']:.0f}/100")
        print(f"Confianza de datos: {item['data_confidence']:.0%}")
        print(item["narrative"])
        print()


if __name__ == "__main__":
    main()
