"""Bandeja de revisión manual para conversaciones escaladas (alerta roja).

Implementación en memoria, suficiente para desarrollo y pruebas. En producción se
sustituye por una tabla/cola persistente (PostgreSQL, Redis, CRM) manteniendo la misma
interfaz ``registrar`` / ``pendientes`` / ``resolver``.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

ALERTA_ROJA = "ROJA"


@dataclass
class TicketRevision:
    id_ticket: str
    conversacion_id: Optional[str]
    canal: Optional[str]
    mensaje: str
    categoria: str
    senales: List[str]
    justificacion: str
    alerta: str = ALERTA_ROJA
    estado: str = "PENDIENTE"
    creado_en: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resuelto_en: Optional[str] = None
    resolucion: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class ColaRevisionManual:
    def __init__(self) -> None:
        self._tickets: Dict[str, TicketRevision] = {}
        self._lock = threading.Lock()

    def registrar(
        self,
        *,
        mensaje: str,
        categoria: str,
        senales: List[str],
        justificacion: str,
        conversacion_id: Optional[str] = None,
        canal: Optional[str] = None,
    ) -> TicketRevision:
        ticket = TicketRevision(
            id_ticket=f"REV-{uuid.uuid4().hex[:8].upper()}",
            conversacion_id=conversacion_id,
            canal=canal,
            mensaje=mensaje,
            categoria=categoria,
            senales=list(senales),
            justificacion=justificacion,
        )
        with self._lock:
            self._tickets[ticket.id_ticket] = ticket
        return ticket

    def pendientes(self) -> List[TicketRevision]:
        with self._lock:
            return [t for t in self._tickets.values() if t.estado == "PENDIENTE"]

    def todos(self) -> List[TicketRevision]:
        with self._lock:
            return list(self._tickets.values())

    def obtener(self, id_ticket: str) -> Optional[TicketRevision]:
        with self._lock:
            return self._tickets.get(id_ticket)

    def resolver(self, id_ticket: str, resolucion: str) -> Optional[TicketRevision]:
        with self._lock:
            ticket = self._tickets.get(id_ticket)
            if ticket is None:
                return None
            ticket.estado = "RESUELTO"
            ticket.resolucion = resolucion
            ticket.resuelto_en = datetime.now(timezone.utc).isoformat()
            return ticket

    def limpiar(self) -> None:
        with self._lock:
            self._tickets.clear()
