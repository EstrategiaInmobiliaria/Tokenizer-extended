#!/usr/bin/env python3
"""
Orquestador: TensorFlow predictions → Power BI (SQL + Push Dataset)

Uso:
  # Exportar batch desde impact tracker
  python scripts/export_to_powerbi.py --source tracker

  # Generar predicciones frescas y exportar
  python scripts/export_to_powerbi.py --source live --category real_estate

  # Solo push streaming
  python scripts/export_to_powerbi.py --mode streaming --source tracker

  # Snapshot diario (replace)
  python scripts/export_to_powerbi.py --source tracker --write-mode replace

Variables de entorno:
  DATABASE_URL           sqlite:///... | postgresql://user:pass@host/db
  POWERBI_PUSH_URL       URL del Push/Streaming Dataset
  POWERBI_EXPORT_MODE    repository | streaming | hybrid
  POWERBI_SQL_TABLE      predicciones_tensorflow
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

# Paths
BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from dotenv import load_dotenv

load_dotenv(BACKEND.parent / ".env")
load_dotenv(BACKEND / ".env")

from integrations.powerbi_exporter import (
    PowerBIExportPipeline,
    PredictionRowBuilder,
)


def export_from_tracker(pipeline: PowerBIExportPipeline, write_mode: str, limit: Optional[int]):
    metrics_file = BACKEND / "data" / "metrics" / "predictions.jsonl"
    if not metrics_file.exists():
        print(f"⚠️  No hay predicciones en {metrics_file}")
        print("   Generando batch demo para bootstrap...")
        return export_live_batch(pipeline, write_mode, categories=["real_estate", "social_media"])

    result = pipeline.export_batch_file(metrics_file, write_mode=write_mode, limit=limit)
    return result


def export_live_batch(
    pipeline: PowerBIExportPipeline,
    write_mode: str,
    categories: Optional[List[str]] = None,
):
    """Corre modelos y exporta predicciones frescas (lote diario)."""
    categories = categories or ["real_estate", "social_media", "personal_tco"]
    batch_id = f"live_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    rows = []

    if "real_estate" in categories:
        try:
            from models.real_estate_opportunity import RealEstateOpportunityDetector

            detector = RealEstateOpportunityDetector()
            samples = [
                {
                    "precio_m2": 45000,
                    "ubicacion": "Querétaro",
                    "amenidades": 12,
                    "velocidad_ventas": 0.85,
                    "cap_rate": 7.2,
                    "id_negocio": "DEV-QRO-001",
                },
                {
                    "precio_m2": 52000,
                    "ubicacion": "CDMX",
                    "amenidades": 15,
                    "velocidad_ventas": 0.72,
                    "cap_rate": 6.8,
                    "id_negocio": "DEV-CDMX-014",
                },
                {
                    "precio_m2": 38000,
                    "ubicacion": "Monterrey",
                    "amenidades": 10,
                    "velocidad_ventas": 0.90,
                    "cap_rate": 7.5,
                    "id_negocio": "DEV-MTY-007",
                },
            ]
            for sample in samples:
                id_negocio = sample.pop("id_negocio")
                pred = detector.predict(sample)
                rows.append(
                    PredictionRowBuilder.build_row(
                        category="real_estate",
                        model="real_estate_opportunity",
                        prediction=pred,
                        input_data=sample,
                        id_negocio=id_negocio,
                        confidence_score=pred.get("probabilidad_venta_12m"),
                        batch_id=batch_id,
                    )
                )
        except Exception as e:
            print(f"⚠️  Real estate skip: {e}")

    if "social_media" in categories:
        try:
            from models.social_media_optimizer import SocialMediaContentOptimizer

            optimizer = SocialMediaContentOptimizer()
            sample = {
                "tipo_contenido": "Reel",
                "hora": 9,
                "dia_semana": 1,
                "num_hashtags": 5,
                "tema_categoria": "Cap Rate",
                "longitud_caption": 150,
            }
            pred = optimizer.predict(sample)
            rows.append(
                PredictionRowBuilder.build_row(
                    category="social_media",
                    model="social_content_optimizer",
                    prediction=pred,
                    input_data=sample,
                    id_negocio="POST-LIVE-001",
                    confidence_score=pred.get("probabilidad_viral"),
                    batch_id=batch_id,
                )
            )
        except Exception as e:
            print(f"⚠️  Social media skip: {e}")

    if "personal_tco" in categories:
        try:
            from models.personal_decision_models import TCOCalculator

            tco = TCOCalculator()
            geely = {
                "precio_inicial": 650000,
                "gasolina_mensual": 800,
                "seguro_anual": 12000,
                "mantenimiento_anual": 8000,
                "depreciacion_anual": 65000,
                "km_anuales": 20000,
                "rendimiento_km_l": 25,
                "es_electrico": 1,
            }
            pred = tco.calculate_tco(geely)
            rows.append(
                PredictionRowBuilder.build_row(
                    category="personal_tco",
                    model="tco_calculator",
                    prediction=pred,
                    input_data=geely,
                    id_negocio="AUTO-GEELY-EX5",
                    confidence_score=0.95,
                    batch_id=batch_id,
                )
            )
        except Exception as e:
            print(f"⚠️  TCO skip: {e}")

    if not rows:
        return {"status": "error", "reason": "No se generaron predicciones (¿modelos entrenados?)"}

    return pipeline.export_predictions(rows, write_mode=write_mode)


def main():
    parser = argparse.ArgumentParser(description="Export TensorFlow predictions → Power BI")
    parser.add_argument(
        "--source",
        choices=["tracker", "live"],
        default="tracker",
        help="tracker=predictions.jsonl | live=correr modelos ahora",
    )
    parser.add_argument(
        "--mode",
        choices=["repository", "streaming", "hybrid"],
        default=None,
        help="Override POWERBI_EXPORT_MODE",
    )
    parser.add_argument(
        "--write-mode",
        choices=["append", "replace", "upsert"],
        default="append",
        help="Estrategia SQL",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limitar filas desde tracker")
    parser.add_argument(
        "--category",
        action="append",
        dest="categories",
        help="Categorías para --source live (repetible)",
    )
    parser.add_argument("--json", action="store_true", help="Salida JSON pura")
    args = parser.parse_args()

    pipeline = PowerBIExportPipeline(mode=args.mode)

    print("=" * 60)
    print("📊 EXPORT TensorFlow → Power BI")
    print("=" * 60)
    print(f"Mode:       {pipeline.mode}")
    print(f"Source:     {args.source}")
    print(f"Write mode: {args.write_mode}")
    print(f"DB scheme:  {pipeline.db.database_url.split('://', 1)[0]}")
    print(f"Push URL:   {'configurada' if pipeline.push.enabled else 'no configurada'}")
    print()

    if args.source == "tracker":
        result = export_from_tracker(pipeline, args.write_mode, args.limit)
    else:
        result = export_live_batch(pipeline, args.write_mode, args.categories)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        if result.get("database", {}).get("status") == "ok":
            print(f"\n✅ SQL: {result['database']['rows_written']} filas → {result['database']['table']}")
            print(f"   Total en tabla: {result['database'].get('total_rows')}")
        if result.get("push"):
            print(f"📡 Push: {result['push']}")
        print("\n📌 Power BI Desktop:")
        print("   Obtener datos → SQLite/PostgreSQL → tabla predicciones_tensorflow")
        print("   DirectQuery = tiempo casi real | Import = refresh programado")

    # Exit code para CI
    db_ok = result.get("database") is None or result.get("database", {}).get("status") == "ok"
    push = result.get("push")
    push_ok = push is None or push.get("status") in ("ok", "skipped")
    sys.exit(0 if db_ok and push_ok else 1)


if __name__ == "__main__":
    main()
