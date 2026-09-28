"""Política de comunicación derivada de la Guía de respuestas para WhatsApp (28-sep-2026).

Reglas duras que el router aplica a todo borrador:
- Nada se envía sin aprobación humana (Jimmy): toda salida es BORRADOR.
- No se dan precios hasta que la lista vigente esté confirmada (``precios_confirmados``).
- No se prometen fechas de entrega ni avance de obra.
- No se presiona con urgencia que los datos no respalden.
- Solo nuestros canales y sitio; nunca dominios ni teléfonos de terceros, y nunca se habla
  de terceros con el cliente.
- Lo que está entre [corchetes] se confirma o se borra antes de enviar.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import List

from .classifier import normalizar

CANALES_OFICIALES: List[str] = ["55 4437 8776", "55 6100 0600", "55 2855 7467"]
WHATSAPP_OFICIAL = "wa.me/525544378776"
SITIO_OFICIAL = "https://palm-diamante.com/es/"
SITIO_OFICIAL_CORTO = "palm-diamante.com/es"

# Uso interno: nunca se mencionan al cliente.
DOMINIOS_PROHIBIDOS: List[str] = [
    "palmdiamante.mx",
    "palmdiamanteacapulco.mx",
    "palmdiamanteacapulco.com",
    "ventadeptosacapulco.com",
]
TELEFONOS_PROHIBIDOS: List[str] = ["55 4021 2638", "744 271 3055"]

APROBADOR_DEFECTO = "Jimmy"
ESTADO_BORRADOR = "BORRADOR"

_ENV_TRUE = {"1", "true", "si", "sí", "yes", "on"}

PATRON_PROMESA_ENTREGA = re.compile(
    r"\b(entregamos|se entrega|la entrega es|fecha de entrega es|entregan en|avance (de obra )?del? \d+ ?%|llevamos \d+ ?%)"
)
PATRON_URGENCIA = re.compile(
    r"\b(ultimas? unidades?|ultimos? departamentos?|se (agotan?|acaban?)|solo (hoy|por hoy|esta semana)|"
    r"apurate|aprovecha|quedan (pocas|pocos|muy pocas)|antes de que (se acabe|suba)|"
    r"el precio sube|ultima oportunidad|disponibilidad cambia seguido|no te quedes sin)\b"
)
PATRON_TERCEROS = re.compile(
    r"\b(terceros|anuncios? (falsos?|no oficiales?|de terceros)|canales? no oficial(es)?|"
    r"otros? vendedores?|paginas? falsas?|no coinciden con la informacion actual)\b"
)


def _solo_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto)


@dataclass
class PoliticaComunicacion:
    precios_confirmados: bool = False
    aprobador: str = APROBADOR_DEFECTO
    canales_oficiales: List[str] = field(default_factory=lambda: list(CANALES_OFICIALES))
    sitio_oficial: str = SITIO_OFICIAL_CORTO

    @classmethod
    def desde_entorno(cls) -> "PoliticaComunicacion":
        flag = os.getenv("PALM_PRECIOS_CONFIRMADOS", "").strip().lower()
        return cls(
            precios_confirmados=flag in _ENV_TRUE,
            aprobador=os.getenv("PALM_APROBADOR", APROBADOR_DEFECTO),
        )

    def validar_borrador(self, texto: str) -> List[str]:
        """Devuelve la lista de violaciones encontradas en un borrador (vacía si cumple)."""
        violaciones: List[str] = []
        texto_norm = normalizar(texto)
        for dominio in DOMINIOS_PROHIBIDOS:
            if dominio in texto_norm:
                violaciones.append(f"dominio_prohibido:{dominio}")
        digitos = _solo_digitos(texto)
        for telefono in TELEFONOS_PROHIBIDOS:
            if _solo_digitos(telefono) in digitos:
                violaciones.append(f"telefono_prohibido:{telefono}")
        if PATRON_PROMESA_ENTREGA.search(texto_norm):
            violaciones.append("promesa_de_entrega_o_avance")
        if PATRON_URGENCIA.search(texto_norm):
            violaciones.append("urgencia_no_respaldada")
        if PATRON_TERCEROS.search(texto_norm):
            violaciones.append("mencion_de_terceros")
        return violaciones
