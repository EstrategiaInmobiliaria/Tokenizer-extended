"""Orquestador: clasifica el mensaje y ejecuta la acción de negocio correspondiente.

| Categoría        | Acción del sistema                                           |
|------------------|--------------------------------------------------------------|
| COMPRADOR_REAL   | Consultar inventario maestro y responder con datos exactos    |
| LEAD_FRIO        | Desplegar menú rápido de calificación                         |
| COYOTE           | Escalar a revisión manual (alerta roja) y bloquear inventario |
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .classifier import Categoria, Clasificacion, Clasificador, RuleBasedClassifier
from .inventory import Inventario, Unidad, formatear_mxn
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
    ) -> None:
        self.inventario = inventario
        self.cola_revision = cola_revision or ColaRevisionManual()
        self.clasificador = clasificador or RuleBasedClassifier()

    def rutear(
        self,
        mensaje: str,
        *,
        conversacion_id: Optional[str] = None,
        canal: Optional[str] = None,
    ) -> ResultadoRuteo:
        clasificacion = self.clasificador.clasificar(mensaje)
        if clasificacion.categoria is Categoria.COYOTE:
            return self._escalar(mensaje, clasificacion, conversacion_id, canal)
        if clasificacion.categoria is Categoria.COMPRADOR_REAL:
            return self._responder_con_inventario(clasificacion)
        return self._desplegar_menu(clasificacion)

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
        unidades = self.inventario.buscar(**filtros_dict)
        alternativas_usadas = False
        if not unidades and filtros_dict:
            unidades = self.inventario.buscar()
            alternativas_usadas = True

        lineas: List[str] = []
        if alternativas_usadas:
            lineas.append(
                "Por ahora no tenemos unidades disponibles con exactamente esas características, "
                "pero sí contamos con estas opciones en Palm Diamante:"
            )
        elif unidades:
            lineas.append("Con gusto. Estas son las unidades disponibles en Palm Diamante que coinciden con lo que buscas:")
        else:
            lineas.append("Por el momento no hay unidades disponibles en inventario; un asesor te avisará en cuanto se libere una.")

        for u in unidades:
            lineas.append(self._describir_unidad(u))

        siguiente_paso = (
            "Agendar visita: pedir día y horario preferido al prospecto."
            if clasificacion.quiere_cita
            else "Ofrecer visita al desarrollo o revisar esquema de pago."
        )
        cierre = (
            "¿Qué día y horario te acomoda para la visita al desarrollo?"
            if clasificacion.quiere_cita
            else "¿Te gustaría agendar una visita o que te comparta el esquema de pago de alguna unidad?"
        )
        lineas.append(cierre)

        asesor = unidades[0].asesor_asignado_defecto if unidades else None
        return ResultadoRuteo(
            categoria=clasificacion.categoria,
            accion=Accion.RESPONDER_CON_INVENTARIO,
            confianza=clasificacion.confianza,
            senales=clasificacion.senales,
            justificacion=clasificacion.justificacion,
            respuesta="\n".join(lineas),
            siguiente_paso=siguiente_paso,
            bloqueo_datos_confidenciales=False,
            unidades=[u.to_dict() for u in unidades],
            asesor_sugerido=asesor,
            filtros_aplicados=filtros_dict,
        )

    def _desplegar_menu(self, clasificacion: Clasificacion) -> ResultadoRuteo:
        resumen = self.inventario.resumen_publico()
        saludo = (
            f"¡Hola! Bienvenido a {resumen['proyecto']} de {resumen['desarrolladora']}. "
            "¿Sobre qué te gustaría saber más?"
        )
        opciones = "\n".join(f"{o['opcion']}) {o['etiqueta']}" for o in MENU_RAPIDO)
        return ResultadoRuteo(
            categoria=clasificacion.categoria,
            accion=Accion.DESPLEGAR_MENU,
            confianza=clasificacion.confianza,
            senales=clasificacion.senales,
            justificacion=clasificacion.justificacion,
            respuesta=f"{saludo}\n{opciones}",
            siguiente_paso="Esperar selección del menú para calificar interés.",
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
            respuesta=(
                "Gracias por tu mensaje. Un ejecutivo de Agartha Bienes Raices revisará tu "
                "solicitud y se pondrá en contacto contigo."
            ),
            siguiente_paso=f"Revisión humana del ticket {ticket.id_ticket} (alerta {ticket.alerta}).",
            bloqueo_datos_confidenciales=True,
            ticket_revision=ticket.to_dict(),
        )

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _describir_unidad(u: Unidad) -> str:
        return (
            f"- {u.id_unidad} · {u.torre} · Prototipo {u.prototipo} · {u.recamaras} recámaras · "
            f"{u.superficie_m2:g} m² · {formatear_mxn(u.precio_lista_mxn)}"
        )
