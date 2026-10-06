"""Tests del laboratorio de empaque (cifras didácticas + setup del paper)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "briefings" / "2026-packaging-tsp-lfi"
SIM = ROOT / "simulations"
sys.path.insert(0, str(SIM))

from generar_dataset_clase import generate_rows
from packaging_lab import (
    LfiAssumptions,
    cluster_then_sequence,
    costo_por_paro,
    lfi_daily,
    sequence_setup_hours,
)
from simpy_linea_empaque import compare_manual_vs_clustered


class TestSetupFromPaperAbstract(unittest.TestCase):
    def test_major_vs_minor_hours(self):
        manual = list("ACBDACBD")
        clustered = cluster_then_sequence(manual)
        self.assertEqual("".join(clustered), "ABABCDCD")
        self.assertAlmostEqual(sequence_setup_hours(["A", "C"]), 4.5)
        self.assertAlmostEqual(sequence_setup_hours(["A", "B"]), 1.5)
        self.assertLess(sequence_setup_hours(clustered), sequence_setup_hours(manual))


class TestDidacticLfi(unittest.TestCase):
    def test_unit_cost_and_monthly_before(self):
        a = LfiAssumptions()
        self.assertAlmostEqual(costo_por_paro(a), 4200.0)
        m = lfi_daily(a)
        self.assertEqual(m["paros_antes"], 18)
        self.assertEqual(m["paros_evitados"], 12)
        self.assertAlmostEqual(m["perdida_mensual_antes"], 1_890_000.0)
        self.assertGreater(m["ahorro_diario"], 16_800)  # consistent 12-stop math


class TestClassroomDataset(unittest.TestCase):
    def test_bruno_is_the_hidden_signature(self):
        rows = generate_rows(20261006)
        self.assertEqual(len(rows), 90)  # 30 days × 3 shifts

        def mean_stops(name: str) -> float:
            subset = [r for r in rows if r["operator"] == name]
            return sum(r["unplanned_stops"] for r in subset) / len(subset)

        self.assertGreater(mean_stops("Bruno"), mean_stops("Ana") * 1.5)
        bruno = [r for r in rows if r["operator"] == "Bruno"]
        others = [r for r in rows if r["operator"] != "Bruno"]
        clean_bruno = sum(r["sensor_cleaned"] for r in bruno) / len(bruno)
        clean_others = sum(r["sensor_cleaned"] for r in others) / len(others)
        self.assertLess(clean_bruno, clean_others)
        self.assertLess(clean_bruno, 0.5)


class TestDesAndSources(unittest.TestCase):
    def test_des_cluster_saves_setup(self):
        r = compare_manual_vs_clustered()
        self.assertGreater(r["delta_h"], 0)
        self.assertAlmostEqual(r["manual_setup_h"], sequence_setup_hours(list("ACBDACBD")))
        self.assertAlmostEqual(r["clustered_setup_h"], sequence_setup_hours(list("ABABCDCD")))

    def test_sources_json_has_core_dois(self):
        data = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
        dois = {s.get("doi") for s in data["sources"]}
        self.assertIn("10.1007/978-3-031-67440-2_20", dois)
        self.assertIn("10.2139/ssrn.6416055", dois)

    def test_claim_audit_flags_conflict(self):
        text = (ROOT / "CLAIM_AUDIT.md").read_text(encoding="utf-8")
        self.assertIn("**conflict**", text)
        self.assertIn("not found", text.lower())
        self.assertIn("LFI", text)


if __name__ == "__main__":
    unittest.main()
