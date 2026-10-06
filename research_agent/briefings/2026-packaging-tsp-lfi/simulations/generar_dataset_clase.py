"""CSV de 30 días con firma de operador oculta. Didáctico (SRC-D01)."""

from __future__ import annotations

import csv
import random
from pathlib import Path

SEED = 20261006
OPERATORS = ("Ana", "Bruno", "Carla")
FAMILIES = ("X", "Y")


def generate_rows(seed: int = SEED) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    day_id = 0
    for day in range(1, 31):
        weekday = (day - 1) % 7  # 0 = lunes
        for shift in (1, 2, 3):
            day_id += 1
            operator = OPERATORS[(day + shift) % 3]
            # Most days stay inside a family; ~1/3 cross APIs (major setup).
            family = FAMILIES[0 if rng.random() > 0.33 else 1]
            crossed = rng.random() < 0.33
            setup_h = 4.5 if crossed else 1.5
            roll_changes = rng.choice([2, 3, 3, 4])
            # Bruno rarely cleans the sensor after a roll change.
            if operator == "Bruno":
                cleaned = rng.random() < 0.22
            else:
                cleaned = rng.random() < 0.85
            base_stops = rng.randint(1, 3)
            if operator == "Bruno" and not cleaned:
                extra = rng.randint(4, 7)
            else:
                extra = rng.randint(0, 1)
            if weekday == 4 and shift == 3:
                extra += rng.randint(0, 2)
            stops = base_stops + extra
            minutes = round(sum(rng.gauss(18, 3) for _ in range(stops)), 1)
            rows.append(
                {
                    "day": day,
                    "weekday": weekday,
                    "shift": shift,
                    "operator": operator,
                    "family_run": family,
                    "crossed_family": int(crossed),
                    "setup_hours": setup_h,
                    "roll_changes": roll_changes,
                    "sensor_cleaned": int(cleaned),
                    "unplanned_stops": stops,
                    "stop_minutes": minutes,
                }
            )
    return rows


def write_csv(path: Path, seed: int = SEED) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = generate_rows(seed)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "output" / "paros_30_dias.csv"
    write_csv(out)
    print(f"wrote {out}")
