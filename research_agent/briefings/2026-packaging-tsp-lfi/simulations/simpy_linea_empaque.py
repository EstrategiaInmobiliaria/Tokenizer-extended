"""DES mínimo de la línea (sin dependencia de SimPy).

Modela contención de una máquina: cada lote espera setup (función del API
previo) y luego un tiempo de proceso. Didáctico.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from packaging_lab import MAJOR_SETUP_H, MINOR_SETUP_H, SKU, setup_hours


@dataclass
class Job:
    sku: SKU
    process_h: float = 2.0


@dataclass
class SimResult:
    makespan_h: float
    setup_h: float
    wait_h: float
    log: List[str] = field(default_factory=list)


def run_line(jobs: List[Job]) -> SimResult:
    t = 0.0
    setup_total = 0.0
    wait_total = 0.0
    prev = None
    log: List[str] = []
    for i, job in enumerate(jobs):
        arrival = t  # single machine, jobs released in order
        if prev is None:
            su = 0.0
        else:
            su = setup_hours(prev, job.sku)
        start = t
        wait = start - arrival
        t = start + su + job.process_h
        setup_total += su
        wait_total += wait
        log.append(
            f"job{i} {job.sku.code} setup={su:.1f}h process={job.process_h:.1f}h done_at={t:.1f}h"
        )
        prev = job.sku
    return SimResult(makespan_h=t, setup_h=setup_total, wait_h=wait_total, log=log)


def compare_manual_vs_clustered() -> dict:
    from packaging_lab import TEACHING_SKUS, cluster_then_sequence

    manual_codes = list("ACBDACBD")
    clustered = cluster_then_sequence(manual_codes)
    manual_jobs = [Job(TEACHING_SKUS[c]) for c in manual_codes]
    clustered_jobs = [Job(TEACHING_SKUS[c]) for c in clustered]
    a, b = run_line(manual_jobs), run_line(clustered_jobs)
    return {
        "manual_setup_h": a.setup_h,
        "clustered_setup_h": b.setup_h,
        "delta_h": a.setup_h - b.setup_h,
        "major": MAJOR_SETUP_H,
        "minor": MINOR_SETUP_H,
        "manual_log": a.log,
        "clustered_log": b.log,
    }


if __name__ == "__main__":
    r = compare_manual_vs_clustered()
    print(f"manual setup={r['manual_setup_h']:.1f}h  clustered={r['clustered_setup_h']:.1f}h  "
          f"delta={r['delta_h']:.1f}h")
    print("note: durations 4.5/1.5 h from SRC-001 abstract; sequence is didactic")
