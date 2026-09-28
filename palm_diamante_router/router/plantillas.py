"""Plantillas de respuesta tomadas de la Guía de respuestas para WhatsApp (28-sep-2026).

- ``aprobado``: literal de la guía, listo para borrador.
- ``con_corchetes``: literal de la guía pero contiene [corchetes] que se confirman o se borran
  antes de enviar; el orquestador los expone como ``pendientes_por_confirmar``.
- ``derivado``: construido a partir de las reglas de la guía; requiere la misma aprobación.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from .policy import CANALES_OFICIALES, SITIO_OFICIAL_CORTO

PATRON_CORCHETES = re.compile(r"\[([^\]]+)\]")


def pendientes_en(texto: str) -> List[str]:
    """Contenido de los [corchetes] presentes en un texto (lo que hay que confirmar o borrar)."""
    return [m.strip() for m in PATRON_CORCHETES.findall(texto)]


@dataclass(frozen=True)
class Plantilla:
    clave: str
    comando: str
    seccion: str
    estado: str  # "aprobado" | "con_corchetes" | "derivado"
    texto: str
    pendientes: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(self, "pendientes", pendientes_en(self.texto))


_canales_o = ", ".join(CANALES_OFICIALES[:-1]) + f" o {CANALES_OFICIALES[-1]}"

PLANTILLAS: Dict[str, Plantilla] = {
    p.clave: p
    for p in [
        Plantilla(
            clave="primer_contacto",
            comando="/hola",
            seccion="Primer contacto",
            estado="aprobado",
            texto=(
                "Hola, gracias por tu interés en Palm Diamante. Te atiende Estrategia Inmobiliaria. "
                f"Puedes escribirnos o llamarnos al {_canales_o}, y conocer el proyecto en "
                f"{SITIO_OFICIAL_CORTO}. ¿Qué tipo de departamento te interesa?"
            ),
        ),
        Plantilla(
            clave="calificar",
            comando="/calificar",
            seccion="Conocer al prospecto",
            estado="aprobado",
            texto=(
                "Para mostrarte las opciones que mejor te queden: ¿lo buscas para vivir, vacacionar o invertir? "
                "¿Tienes un rango de presupuesto en mente? ¿Lo pagarías de contado, con plan de pagos o con crédito?"
            ),
        ),
        Plantilla(
            clave="sin_precio",
            comando="/sinprecio",
            seccion="Mientras no esté confirmada la lista",
            estado="aprobado",
            texto=(
                "Con gusto. Estoy confirmando la lista de precios más reciente para darte información exacta "
                "y te la comparto en cuanto la tenga. Mientras, ¿qué tamaño de departamento buscas?"
            ),
        ),
        Plantilla(
            clave="sin_precio_con_unidades",
            comando="/sinprecio",
            seccion="Mientras no esté confirmada la lista (ya se describieron unidades)",
            estado="derivado",
            texto=(
                "Estoy confirmando la lista de precios más reciente para darte información exacta "
                "y te la comparto en cuanto la tenga."
            ),
        ),
        Plantilla(
            clave="precio",
            comando="/precio",
            seccion="Solo con lista confirmada como vigente",
            estado="con_corchetes",
            texto=(
                "Hoy tenemos departamentos desde $[precio de entrada] millones de pesos por un modelo de 76 m², "
                "y hasta Penthouse de 3 recámaras. El precio depende de la torre, el piso y el modelo. "
                "¿Qué tamaño buscas, para compartirte las opciones disponibles?"
            ),
        ),
        Plantilla(
            clave="tamanos",
            comando="/tamanos",
            seccion="Tamaños y recámaras",
            estado="con_corchetes",
            texto=(
                "Tenemos departamentos desde 76 m²[, todos con terraza]. Los Green House y Penthouse tienen "
                "planta alta con más espacio, y los Penthouse son de 3 recámaras. El desarrollo está frente al "
                "mar[, con alberca principal, jardines interiores, palapa social y lounge frente al mar]. "
                "¿Qué tamaño te interesa?"
            ),
        ),
        Plantilla(
            clave="ubicacion",
            comando="/ubicacion",
            seccion="Ubicación",
            estado="aprobado",
            texto=(
                "Palm Diamante está en Costera de las Palmas, Granjas del Marqués, C.P. 39890, "
                "Acapulco Diamante, Guerrero, frente al mar."
            ),
        ),
        Plantilla(
            clave="formas_pago",
            comando="/pago",
            seccion="Formas de pago",
            estado="aprobado",
            texto=(
                "Durante la preventa manejamos financiamiento directo, y el plazo depende de la torre. "
                "Un asesor te arma el plan de pagos a tu medida. ¿Lo pagarías de contado o con plan de pagos?"
            ),
        ),
        Plantilla(
            clave="entrega",
            comando="/entrega",
            seccion="Entrega y avance de obra",
            estado="aprobado",
            texto=(
                "Con gusto un asesor te confirma la fecha de entrega y el avance de obra más reciente "
                "de la torre que te interesa."
            ),
        ),
        Plantilla(
            clave="cita",
            comando="/cita",
            seccion="Agendar",
            estado="con_corchetes",
            texto=(
                "Con gusto te agendo una cita para que conozcas el proyecto[ en el desarrollo / en oficina / "
                "por videollamada]. ¿Qué día y horario te acomodan? También puedes escribirnos o llamarnos al "
                f"{_canales_o}."
            ),
        ),
        Plantilla(
            clave="seguimiento",
            comando="/seguimiento",
            seccion="Quien dejó de contestar",
            estado="aprobado",
            texto=(
                "¡Hola! Te escribo de Palm Diamante. ¿Pudiste revisar la información? Si te quedó alguna duda, "
                "con gusto te la resuelvo, o si prefieres agendamos una llamada esta semana."
            ),
        ),
        Plantilla(
            clave="coyote_neutral",
            comando="",
            seccion="Coyote / broker no autorizado",
            estado="derivado",
            texto=(
                "Gracias por tu mensaje. Un ejecutivo de Estrategia Inmobiliaria revisará tu solicitud "
                "y se pondrá en contacto contigo."
            ),
        ),
    ]
}


def texto(clave: str) -> str:
    return PLANTILLAS[clave].texto
