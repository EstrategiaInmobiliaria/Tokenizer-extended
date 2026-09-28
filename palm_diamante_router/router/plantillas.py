"""Plantillas de respuesta tomadas de la Guía de respuestas para WhatsApp (27-sep-2026).

Los textos marcados ``aprobado`` son literales de la guía. Los marcados ``derivado`` se
construyen a partir de sus reglas y deben pasar por la misma aprobación humana.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .policy import CANALES_OFICIALES, SITIO_OFICIAL_CORTO


@dataclass(frozen=True)
class Plantilla:
    clave: str
    seccion: str
    estado: str  # "aprobado" | "derivado" | "pendiente"
    texto: str
    pendiente: str = ""


_canales = ", ".join(CANALES_OFICIALES[:-1]) + f" y {CANALES_OFICIALES[-1]}"
_canales_o = ", ".join(CANALES_OFICIALES[:-1]) + f" o {CANALES_OFICIALES[-1]}"

PLANTILLAS: Dict[str, Plantilla] = {
    p.clave: p
    for p in [
        Plantilla(
            clave="primer_contacto",
            seccion="1. Primer contacto",
            estado="aprobado",
            texto=(
                "Hola, gracias por tu interés en Palm Diamante. Te atiende Estrategia Inmobiliaria. "
                f"Para tu seguridad, nuestros únicos canales son {_canales}, y el sitio oficial es "
                f"{SITIO_OFICIAL_CORTO}. En Acapulco Diamante circulan anuncios con precios, fechas o torres "
                "que no coinciden con la información actual. Si recibes algo distinto, con gusto te lo "
                "confirmamos. Te puedo enviar la lista de precios vigente, el avance de obra más reciente y "
                "los pasos del proceso de compra. ¿Qué tipo de departamento te interesa?"
            ),
        ),
        Plantilla(
            clave="precio_sin_confirmar",
            seccion="2. Precio (lista aún no confirmada)",
            estado="derivado",
            texto=(
                "El precio depende de la torre, el piso y el modelo. En cuanto un asesor confirme la lista "
                "vigente te la comparto completa. ¿Qué tamaño buscas, para tenerte listas las opciones?"
            ),
            pendiente="Jimmy confirma que la lista del 15-sep-2026 sigue vigente y define el precio de entrada.",
        ),
        Plantilla(
            clave="precio_sin_confirmar_con_unidades",
            seccion="2. Precio (lista aún no confirmada, ya se mostraron unidades)",
            estado="derivado",
            texto=(
                "El precio depende de la torre, el piso y el modelo; en cuanto un asesor confirme la lista "
                "vigente te comparto el de estas opciones."
            ),
            pendiente="Jimmy confirma que la lista del 15-sep-2026 sigue vigente y define el precio de entrada.",
        ),
        Plantilla(
            clave="ubicacion",
            seccion="4. Ubicación",
            estado="aprobado",
            texto=(
                "Palm Diamante está en Costera de las Palmas, Granjas del Marqués, C.P. 39890, "
                "Acapulco Diamante, Guerrero, frente al mar."
            ),
        ),
        Plantilla(
            clave="formas_pago",
            seccion="5. Formas de pago",
            estado="aprobado",
            texto=(
                "Manejamos financiamiento directo durante la preventa: 5 meses en Torre I, 9 meses en Torre II "
                "y hasta 22 meses en Torre III. Un asesor te arma el plan de pagos a tu medida. "
                "¿Lo pagarías de contado o con plan de pagos?"
            ),
            pendiente="Enganche, mensualidades, descuento de contado, crédito hipotecario.",
        ),
        Plantilla(
            clave="entrega",
            seccion="6. Entrega y avance de obra",
            estado="aprobado",
            texto=(
                "Con gusto un asesor te confirma la fecha de entrega y el avance de obra más reciente "
                "de la torre que te interesa."
            ),
        ),
        Plantilla(
            clave="cita",
            seccion="7. Cita",
            estado="aprobado",
            texto=(
                "Con gusto te agendo una cita para que conozcas el proyecto. ¿Qué día y horario te acomodan? "
                f"También puedes escribirnos o llamarnos al {_canales_o}."
            ),
            pendiente="Lugar (desarrollo, oficina o videollamada) y horarios.",
        ),
        Plantilla(
            clave="seguimiento",
            seccion="8. Seguimiento a quien dejó de contestar",
            estado="aprobado",
            texto=(
                "¡Hola! Te escribo de Palm Diamante para saber si pudiste revisar la información. Como estamos "
                "en preventa, la disponibilidad cambia seguido. ¿Te gustaría que te aparte un horario esta "
                "semana para platicarlo?"
            ),
        ),
        Plantilla(
            clave="siguiente_paso_generico",
            seccion="Cierre (derivado de 2 y 7)",
            estado="derivado",
            texto="¿Te gustaría agendar una cita para conocer el proyecto o que un asesor te contacte?",
        ),
        Plantilla(
            clave="coyote_neutral",
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
