"""Acceso al inventario maestro (JSON) de Palm Diamante.

El inventario es la única fuente de verdad para precios, metrajes y disponibilidad.
Ningún agente debe inventar datos: todo pasa por este módulo.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

DEFAULT_INVENTORY_PATH = Path(__file__).resolve().parent.parent / "data" / "inventario_maestro.json"

ESTATUS_DISPONIBLE = "Disponible"


@dataclass(frozen=True)
class Unidad:
    id_unidad: str
    torre: str
    prototipo: str
    recamaras: int
    superficie_m2: float
    precio_lista_mxn: int
    estatus: str
    asesor_asignado_defecto: str

    @property
    def disponible(self) -> bool:
        return self.estatus.strip().lower() == ESTATUS_DISPONIBLE.lower()

    @property
    def numero_torre(self) -> Optional[int]:
        digits = "".join(ch for ch in self.torre if ch.isdigit())
        return int(digits) if digits else None

    def to_dict(self) -> dict:
        return {
            "id_unidad": self.id_unidad,
            "torre": self.torre,
            "prototipo": self.prototipo,
            "recamaras": self.recamaras,
            "superficie_m2": self.superficie_m2,
            "precio_lista_mxn": self.precio_lista_mxn,
            "estatus": self.estatus,
            "asesor_asignado_defecto": self.asesor_asignado_defecto,
        }


@dataclass
class Inventario:
    proyecto: str
    desarrolladora: str
    actualizado: str
    unidades: List[Unidad] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Inventario":
        unidades = [Unidad(**u) for u in data.get("inventario", [])]
        ids = [u.id_unidad for u in unidades]
        if len(ids) != len(set(ids)):
            raise ValueError("El inventario contiene id_unidad duplicados")
        return cls(
            proyecto=data["proyecto"],
            desarrolladora=data["desarrolladora"],
            actualizado=data["actualizado"],
            unidades=unidades,
        )

    @classmethod
    def from_json(cls, path: Path | str = DEFAULT_INVENTORY_PATH) -> "Inventario":
        with open(path, encoding="utf-8") as fh:
            return cls.from_dict(json.load(fh))

    def buscar(
        self,
        *,
        torre: Optional[int] = None,
        prototipo: Optional[str] = None,
        recamaras: Optional[int] = None,
        precio_max_mxn: Optional[int] = None,
        precio_min_mxn: Optional[int] = None,
        solo_disponibles: bool = True,
    ) -> List[Unidad]:
        resultado: Iterable[Unidad] = self.unidades
        if solo_disponibles:
            resultado = (u for u in resultado if u.disponible)
        if torre is not None:
            resultado = (u for u in resultado if u.numero_torre == torre)
        if prototipo is not None:
            resultado = (u for u in resultado if u.prototipo.upper() == prototipo.upper())
        if recamaras is not None:
            resultado = (u for u in resultado if u.recamaras == recamaras)
        if precio_min_mxn is not None:
            resultado = (u for u in resultado if u.precio_lista_mxn >= precio_min_mxn)
        if precio_max_mxn is not None:
            resultado = (u for u in resultado if u.precio_lista_mxn <= precio_max_mxn)
        return sorted(resultado, key=lambda u: u.precio_lista_mxn)

    def por_id(self, id_unidad: str) -> Optional[Unidad]:
        objetivo = id_unidad.strip().upper()
        return next((u for u in self.unidades if u.id_unidad.upper() == objetivo), None)

    def resumen_publico(self) -> dict:
        """Datos que sí pueden compartirse con cualquier prospecto (sin precios)."""
        return {
            "proyecto": self.proyecto,
            "desarrolladora": self.desarrolladora,
            "torres": sorted({u.torre for u in self.unidades}),
            "prototipos": sorted({u.prototipo for u in self.unidades}),
            "recamaras": sorted({u.recamaras for u in self.unidades}),
        }


def formatear_mxn(monto: float) -> str:
    return f"${monto:,.0f} MXN"
