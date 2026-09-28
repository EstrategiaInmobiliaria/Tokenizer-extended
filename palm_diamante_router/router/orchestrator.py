"""Orquestador: clasifica el mensaje y ejecuta la acción de negocio correspondiente.

| Categoría        | Acción del sistema                                           |
|------------------|--------------------------------------------------------------|
| COMPRADOR_REAL   | Consultar inventario maestro y responder con datos exactos    |
| LEAD_FRIO        | Desplegar menú rápido de calificación                         |
| COYOTE           | Escalar a revisión manual (alerta roja) y bloquear inventario |

Toda respuesta es un BORRADOR sujeto a aprobación humana y se valida contra la política de
comunicación (canales oficiales, sin dominios/teléfonos de terceros, sin promesas de entrega,
sin precios hasta confirmar la lista vigente).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .classifier import Categoria, Clasificacion, Clasificador, RuleBasedClassifier
from .inventory import Inventario, Unidad, formatear_mxn
from .plantillas import texto as plantilla
from .policy import ESTADO_BORRADOR, PoliticaComunicacion
from .review_queue import ColaRevisionManual


class Accion(str, Enum):
    RESPONDER_CON_INVENTARIO = "RESPONDER_CON_INVENTARIO"
    DESPLEGAR_MENU = "DESPLEGAR_MENU"
    ESCALAR_REVISION_MANUAL = "ESCALAR_REVISION_MANUAL"


MENU_RAPIDO = [
    {"opcion": "1", "etiqueta": "Prototipos y recámaras", "intent": "prototipos"},
    {"opcion": "2", "etiqueta": "Ubicación del desarrollo", "intent": "ubicacion"},
    {"opcion": "3", "etiqueta": "Agendar cita o visita", "intent": "agendar_cita"},
]

SENALES_DE_UNIDADES = {
    "precio", "cuanto_cuesta", "metraje", "disponibilidad", "torre", "prototipo",
    "recamaras", "parametros_explicitos", "interes_de_compra",
}


@dataclass
class ResultadoRuteo:
    categoria: Categoria
    accion: Accion
    confianza: float
    senales: List[str]
    justificacion: str
    respuesta: str
    siguiente_paso: str
    bloqueo_datos_confidenciales: bool
    estado: str = ESTADO_BORRADOR
    requiere_aprobacion: bool = True
    aprobador: str = ""
    precios_incluidos: bool = False
    alertas_cumplimiento: List[str] = field(default_factory=list)
    unidades: List[dict] = field(default_factory=list)
    menu: List[dict] = field(default_factory=list)
    asesor_sugerido: Optional[str] = None
    ticket_revision: Optional[dict] = None
    filtros_aplicados: dict = field(default_factory=dict)


class Orquestador:
    def __init__(
        self,
        inventario: Inventario,
        cola_revision: Optional[ColaRevisionManual] = None,
        clasificador: Optional[Clasificador] = None,
        politica: Optional[PoliticaComunicacion] = None,
    ) -> None:
        self.inventario = inventario
        self.cola_revision = cola_revision or ColaRevisionManual()
        self.clasificador = clasificador or RuleBasedClassifier()
        self.politica = politica or PoliticaComunicacion()

    def rutear(
        self,
        mensaje: str,
        *,
        conversacion_id: Optional[str] = None,
        canal: Optional[str] = None,
    ) -> ResultadoRuteo:
        clasificacion = self.clasificador.clasificar(mensaje)
        if clasificacion.categoria is Categoria.COYOTE:
            resultado = self._escalar(mensaje, clasificacion, conversacion_id, canal)
        elif clasificacion.categoria is Categoria.COMPRADOR_REAL:
            resultado = self._responder_con_inventario(clasificacion)
        else:
            resultado = self._desplegar_menu(clasificacion)
        resultado.aprobador = self.politica.aprobador
        resultado.alertas_cumplimiento = self.politica.validar_borrador(resultado.respuesta)
        return resultado

    # ------------------------------------------------------------------ acciones

    def _responder_con_inventario(self, clasificacion: Clasificacion) -> ResultadoRuteo:
        filtros = clasificacion.filtros
        filtros_dict = {
            k: v
            for k, v in {
                "torre": filtros.torre,
                "prototipo": filtros.prototipo,
                "recamaras": filtros.recamaras,
                "precio_max_mxn": filtros.precio_max_mxn,
            }.items()
            if v is not None
        }
        senales = set(clasificacion.senales)
        pide_unidades = bool(senales & SENALES_DE_UNIDADES)
        pide_precio = bool(senales & {"precio", "cuanto_cuesta"}) or filtros.precio_max_mxn is not None
        mostrar_precios = self.politica.precios_confirmados

        unidades: List[Unidad] = []
        alternativas_usadas = False
        if pide_unidades:
            unidades = self.inventario.buscar(**filtros_dict)
            if not unidades and filtros_dict:
                unidades = self.inventario.buscar()
                alternativas_usadas = True

        bloques: List[str] = []

        if pide_unidades:
            if alternativas_usadas:
                bloques.append(
                    "Por ahora no tenemos unidades disponibles con exactamente esas características, "
                    "pero sí contamos con estas opciones en Palm Diamante:"
                )
            elif unidades:
                bloques.append("Con gusto. Estas son las unidades disponibles en Palm Diamante que coinciden con lo que buscas:")
            else:
                bloques.append("Por el momento no hay unidades disponibles en inventario; un asesor te avisará en cuanto se libere una.")
            bloques.extend(self._describir_unidad(u, con_precio=mostrar_precios) for u in unidades)
            if pide_precio and not mostrar_precios:
                bloques.append(plantilla("precio_sin_confirmar_con_unidades" if unidades else "precio_sin_confirmar"))

        if "ubicacion" in senales:
            bloques.append(plantilla("ubicacion"))
        if "esquema_de_pago" in senales:
            bloques.append(plantilla("formas_pago"))
        if "entrega" in senales:
            bloques.append(plantilla("entrega"))

        if clasificacion.quiere_cita:
            bloques.append(plantilla("cita"))
            siguiente_paso = "Agendar cita: confirmar día, horario y lugar con el prospecto."
        elif not any(b.rstrip().endswith("?") for b in bloques):
            bloques.append(plantilla("siguiente_paso_generico"))
            siguiente_paso = "Ofrecer cita o contacto de asesor."
        else:
            siguiente_paso = "Esperar respuesta del prospecto a la pregunta de calificación."

        if pide_precio and not mostrar_precios:
            siguiente_paso += f" Precios bloqueados hasta que {self.politica.aprobador} confirme la lista vigente."

        asesor = unidades[0].asesor_asignado_defecto if unidades else None
        return ResultadoRuteo(
            categoria=clasificacion.categoria,
            accion=Accion.RESPONDER_CON_INVENTARIO,
            confianza=clasificacion.confianza,
            senales=clasificacion.senales,
            justificacion=clasificacion.justificacion,
            respuesta="\n".join(bloques),
            siguiente_paso=siguiente_paso,
            bloqueo_datos_confidenciales=False,
            precios_incluidos=bool(unidades) and mostrar_precios,
            unidades=[u.to_dict() for u in unidades],
            asesor_sugerido=asesor,
            filtros_aplicados=filtros_dict,
        )

    def _desplegar_menu(self, clasificacion: Clasificacion) -> ResultadoRuteo:
        return ResultadoRuteo(
            categoria=clasificacion.categoria,
            accion=Accion.DESPLEGAR_MENU,
            confianza=clasificacion.confianza,
            senales=clasificacion.senales,
            justificacion=clasificacion.justificacion,
            respuesta=plantilla("primer_contacto"),
            siguiente_paso="Esperar respuesta o selección del menú para calificar interés.",
            bloqueo_datos_confidenciales=False,
            menu=list(MENU_RAPIDO),
        )

    def _escalar(
        self,
        mensaje: str,
        clasificacion: Clasificacion,
        conversacion_id: Optional[str],
        canal: Optional[str],
    ) -> ResultadoRuteo:
        ticket = self.cola_revision.registrar(
            mensaje=mensaje,
            categoria=clasificacion.categoria.value,
            senales=clasificacion.senales,
            justificacion=clasificacion.justificacion,
            conversacion_id=conversacion_id,
            canal=canal,
        )
        return ResultadoRuteo(
            categoria=clasificacion.categoria,
            accion=Accion.ESCALAR_REVISION_MANUAL,
            confianza=clasificacion.confianza,
            senales=clasificacion.senales,
            justificacion=clasificacion.justificacion,
            respuesta=plantilla("coyote_neutral"),
            siguiente_paso=f"Revisión humana del ticket {ticket.id_ticket} (alerta {ticket.alerta}).",
            bloqueo_datos_confidenciales=True,
            ticket_revision=ticket.to_dict(),
        )

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _describir_unidad(u: Unidad, *, con_precio: bool) -> str:
        base = f"- {u.id_unidad} · {u.torre} · Prototipo {u.prototipo} · {u.recamaras} recámaras · {u.superficie_m2:g} m²"
        return f"{base} · {formatear_mxn(u.precio_lista_mxn)}" if con_precio else base
