"""Clasificador de intención: Comprador Real vs. Lead Frío vs. Coyote.

Implementación determinista basada en reglas (regex sobre texto normalizado) para que
el filtrado sea auditable y no dependa de un LLM. Cualquier clasificador alternativo
(por ejemplo, uno respaldado por LLM usando ``SYSTEM_PROMPT``) puede sustituirlo
implementando el protocolo ``Clasificador``.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Pattern, Protocol, Sequence, Tuple

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "reglas_clasificacion.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")


class Categoria(str, Enum):
    COMPRADOR_REAL = "COMPRADOR_REAL"
    LEAD_FRIO = "LEAD_FRIO"
    COYOTE = "COYOTE"


@dataclass
class FiltrosExtraidos:
    """Parámetros de búsqueda que el prospecto menciona explícitamente."""

    torre: Optional[int] = None
    prototipo: Optional[str] = None
    recamaras: Optional[int] = None
    precio_max_mxn: Optional[int] = None

    def vacio(self) -> bool:
        return all(v is None for v in (self.torre, self.prototipo, self.recamaras, self.precio_max_mxn))


@dataclass
class Clasificacion:
    categoria: Categoria
    confianza: float
    senales: List[str] = field(default_factory=list)
    justificacion: str = ""
    filtros: FiltrosExtraidos = field(default_factory=FiltrosExtraidos)
    quiere_cita: bool = False


class Clasificador(Protocol):
    def clasificar(self, mensaje: str) -> Clasificacion: ...


def normalizar(texto: str) -> str:
    """Minúsculas, sin acentos y con espacios colapsados para que las reglas sean estables."""
    sin_acentos = "".join(
        ch for ch in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(ch)
    )
    return re.sub(r"\s+", " ", sin_acentos.lower()).strip()


def _compilar(reglas: Sequence[Tuple[str, str]]) -> List[Tuple[str, Pattern[str]]]:
    return [(etiqueta, re.compile(patron)) for etiqueta, patron in reglas]


# Etiqueta legible -> patrón sobre texto normalizado (sin acentos, minúsculas).
REGLAS_COYOTE = _compilar(
    [
        ("comision", r"\bcomision(es|ista|istas)?\b"),
        ("broker", r"\bbroker(s|es)?\b"),
        ("se_identifica_como_asesor", r"\bsoy (asesor|asesora|agente|corredor|corredora|promotor|promotora)\b"),
        ("asesor_externo", r"\b(asesor|asesora|asesores|agente|agentes) (externo|externa|externos|independiente|independientes|inmobiliario|inmobiliaria|inmobiliarios)\b"),
        ("inmobiliaria_propia", r"\b(tengo|somos|represento|manejo) (una |la )?(inmobiliaria|agencia|despacho)\b"),
        ("intermediacion", r"\bintermedia(r|cion|rio|rios)\b"),
        ("cartera_de_clientes", r"\b(tengo|traigo|manejo|cuento con) (varios |muchos |algunos |una cartera de |cartera de )?(clientes|prospectos|inversionistas)\b"),
        ("referir_clientes", r"\b(referir|canalizar|pasar|mandar)(les|te)? (clientes|prospectos|compradores)\b"),
        ("precios_para_terceros", r"\b(lista|listas|precio|precios|tabla) (de precios )?(para|de|a) (terceros|asesores|brokers|externos|intermediarios|revendedores)\b"),
        ("terceros", r"\bterceros\b"),
        ("mayoreo", r"\b(mayoreo|precio de mayoreo|precio especial para asesores)\b"),
        ("fee_pago_por_referido", r"\b(fee|referral|pago por referido|bono por referido|cuanto (me )?(pagan|dan|ofrecen) (por|de) (comision|referido|referidos|cliente|venta|cierre))\b"),
        ("convenio_con_asesores", r"\b(convenio|alianza|esquema de colaboracion|colaboracion comercial|contrato de exclusividad)\b"),
        ("revender", r"\b(revender|reventa|revendo)\b"),
    ]
)

REGLAS_COMPRADOR = _compilar(
    [
        ("precio", r"\b(precio|precios|costo|costos|cotizacion|cotizar|cotizame|presupuesto)\b"),
        ("cuanto_cuesta", r"\bcuanto (cuesta|cuestan|vale|valen|sale|salen|es|seria|estan?)\b"),
        ("metraje", r"\b(m2|mts|mts2|metros|metraje|superficie|m²)\b"),
        ("disponibilidad", r"\bdisponib\w*"),
        ("torre", r"\btorre(s)?\b"),
        ("prototipo", r"\bprototipo(s)?\b|\bmodelo(s)?\b"),
        ("recamaras", r"\b(recamara|recamaras|habitacion|habitaciones|cuarto|cuartos|dormitorio|dormitorios)\b|\b\d\s*rec\b"),
        ("esquema_de_pago", r"\b(enganche|mensualidad|mensualidades|esquema(s)? de pago|plan(es)? de pago|forma(s)? de pago|financiamiento|credito|hipoteca|hipotecario|infonavit|fovissste|apartado|apartar|contado)\b"),
        ("cita_o_visita", r"\b(cita|visita|visitar|agendar|agenda|recorrido|conocerlo|conocerlos|conocer el|ir a ver|pasar a ver|showroom|departamento muestra)\b"),
        ("entrega", r"\b(fecha de entrega|entregan|cuando entregan|preventa)\b"),
        ("interes_de_compra", r"\b(comprar|compra|adquirir|invertir|inversion|rendimiento|plusvalia|me interesa)\b"),
        ("costos_asociados", r"\b(mantenimiento|cuota|cuotas|escrituras|escrituracion|notario|predial|gastos notariales)\b"),
    ]
)

PATRON_CITA = re.compile(r"\b(cita|visita|visitar|agendar|agenda|recorrido|conocerlo|conocerlos|ir a ver|pasar a ver)\b")
PATRON_TORRE = re.compile(r"\btorre\s*(\d+)\b")
PATRON_PROTOTIPO = re.compile(r"\b(?:prototipo|modelo|tipo)\s+([a-z])\b")
PATRON_RECAMARAS = re.compile(r"\b(\d+|una|uno|dos|tres|cuatro)\s*(?:rec\b|recamaras?\b|habitacion(?:es)?\b|cuartos?\b|dormitorios?\b)")
PATRON_PRESUPUESTO = re.compile(
    r"\b(?:hasta|maximo|max|menos de|no mas de|presupuesto (?:de|es de)?|alrededor de|cerca de|unos)\s*\$?\s*([\d][\d.,]*)\s*(millones|millon|mdp|mill|mil|k)?\b"
)
NUMEROS_PALABRA = {"una": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4}


def _a_entero(valor: str, unidad: Optional[str]) -> Optional[int]:
    limpio = valor.replace(",", "")
    try:
        numero = float(limpio)
    except ValueError:
        return None
    unidad = (unidad or "").lower()
    if unidad in {"millones", "millon", "mdp", "mill"}:
        numero *= 1_000_000
    elif unidad in {"mil", "k"}:
        numero *= 1_000
    elif numero < 100:  # "hasta 5" en contexto inmobiliario casi siempre son millones
        numero *= 1_000_000
    return int(numero) if numero >= 100_000 else None


def extraer_filtros(texto_normalizado: str) -> FiltrosExtraidos:
    filtros = FiltrosExtraidos()
    if m := PATRON_TORRE.search(texto_normalizado):
        filtros.torre = int(m.group(1))
    if m := PATRON_PROTOTIPO.search(texto_normalizado):
        filtros.prototipo = m.group(1).upper()
    if m := PATRON_RECAMARAS.search(texto_normalizado):
        token = m.group(1)
        filtros.recamaras = NUMEROS_PALABRA.get(token) or int(token)
    if m := PATRON_PRESUPUESTO.search(texto_normalizado):
        filtros.precio_max_mxn = _a_entero(m.group(1), m.group(2))
    return filtros


class RuleBasedClassifier:
    """Clasificador determinista. Precedencia: COYOTE > COMPRADOR_REAL > LEAD_FRIO."""

    def clasificar(self, mensaje: str) -> Clasificacion:
        texto = normalizar(mensaje or "")
        if not texto:
            return Clasificacion(
                categoria=Categoria.LEAD_FRIO,
                confianza=1.0,
                justificacion="Mensaje vacío: se despliega menú de calificación.",
            )

        senales_coyote = [etiqueta for etiqueta, patron in REGLAS_COYOTE if patron.search(texto)]
        senales_comprador = [etiqueta for etiqueta, patron in REGLAS_COMPRADOR if patron.search(texto)]
        filtros = extraer_filtros(texto)
        quiere_cita = bool(PATRON_CITA.search(texto))

        if senales_coyote:
            confianza = min(0.99, 0.85 + 0.05 * len(senales_coyote))
            return Clasificacion(
                categoria=Categoria.COYOTE,
                confianza=round(confianza, 2),
                senales=senales_coyote,
                justificacion=(
                    "Se detectaron señales de intermediación no autorizada "
                    f"({', '.join(senales_coyote)}); se bloquea inventario y se escala a revisión manual."
                ),
                filtros=filtros,
                quiere_cita=quiere_cita,
            )

        if senales_comprador or not filtros.vacio():
            senales = senales_comprador + ([] if filtros.vacio() else ["parametros_explicitos"])
            confianza = min(0.95, 0.6 + 0.1 * len(senales))
            return Clasificacion(
                categoria=Categoria.COMPRADOR_REAL,
                confianza=round(confianza, 2),
                senales=senales,
                justificacion=(
                    "El prospecto pregunta por datos concretos de compra "
                    f"({', '.join(senales)}); se consulta el inventario maestro."
                ),
                filtros=filtros,
                quiere_cita=quiere_cita,
            )

        palabras = len(texto.split())
        return Clasificacion(
            categoria=Categoria.LEAD_FRIO,
            confianza=0.75 if palabras <= 6 else 0.55,
            senales=["saludo_o_mensaje_generico"],
            justificacion="Mensaje genérico sin contexto de compra; se despliega menú de calificación.",
            filtros=filtros,
            quiere_cita=quiere_cita,
        )
