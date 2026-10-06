"""Genera CSV, PNG y un resumen numérico del laboratorio."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from generar_dataset_clase import write_csv
from generar_graficos import generate_all
from packaging_lab import cluster_then_sequence, lfi_daily, sequence_setup_hours
from simpy_linea_empaque import compare_manual_vs_clustered


def main() -> None:
    outdir = ROOT.parent / "output"
    csv_path = write_csv(outdir / "paros_30_dias.csv")
    pngs = generate_all(outdir)
    manual = list("ACBDACBD")
    clustered = cluster_then_sequence(manual)
    summary = {
        "label": "didactic-lab",
        "lfi": {k: v for k, v in lfi_daily().items() if k != "nota"},
        "manual_sequence": "".join(manual),
        "clustered_sequence": "".join(clustered),
        "manual_setup_h": sequence_setup_hours(manual),
        "clustered_setup_h": sequence_setup_hours(clustered),
        "des": {
            k: v
            for k, v in compare_manual_vs_clustered().items()
            if k not in {"manual_log", "clustered_log"}
        },
        "csv": str(csv_path),
        "pngs": [str(p) for p in pngs],
    }
    summary_path = outdir / "lab_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
