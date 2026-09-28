"""
Palm Diamante - Router Comercial de Primer Contacto (FastAPI)

Conecta el inventario maestro JSON con el clasificador de intención para que la
automatización (WhatsApp, web chat, CRM) filtre el tráfico antes de comprometer
tiempo humano o comercial.

Endpoints:
- POST /api/v1/router/route            - Clasifica y ejecuta la acción de negocio
- POST /api/v1/router/classify         - Solo clasifica (sin acción)
- GET  /api/v1/inventario              - Consulta inventario con filtros
- GET  /api/v1/inventario/{id_unidad}  - Detalle de una unidad
- GET  /api/v1/revision-manual         - Bandeja de tickets escalados (alerta roja)
- POST /api/v1/revision-manual/{id}/resolver - Cierra un ticket
- GET  /health                         - Health check

Ejecutar:  uvicorn main:app --reload   (desde palm_diamante_router/)
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from router import (
    PLANTILLAS,
    Categoria,
    ColaRevisionManual,
    Inventario,
    Orquestador,
    PoliticaComunicacion,
    RuleBasedClassifier,
    SYSTEM_PROMPT,
)
from router.orchestrator import Accion

INVENTORY_PATH = Path(os.getenv("PALM_INVENTORY_PATH", Path(__file__).parent / "data" / "inventario_maestro.json"))

app = FastAPI(
    title="Palm Diamante - Router Comercial",
    description="Filtro de primer contacto: Comprador Real / Lead Frío / Coyote, conectado al inventario maestro.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir a los dominios del CRM / chatbot
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

inventario = Inventario.from_json(INVENTORY_PATH)
cola_revision = ColaRevisionManual()
clasificador = RuleBasedClassifier()
# PALM_PRECIOS_CONFIRMADOS=1 solo cuando Jimmy confirme que la lista vigente sigue válida.
politica = PoliticaComunicacion.desde_entorno()
orquestador = Orquestador(inventario, cola_revision, clasificador, politica)


# ============================================================================ modelos

class MensajeEntrante(BaseModel):
    mensaje: str = Field(..., min_length=0, max_length=4000, description="Texto enviado por el prospecto")
    conversacion_id: Optional[str] = Field(None, description="Id de la conversación en el canal de origen")
    canal: Optional[str] = Field(None, description="whatsapp | web | instagram | facebook | ...")

    model_config = {
        "json_schema_extra": {
            "example": {
                "mensaje": "Hola, ¿cuánto cuesta un departamento de 3 recámaras en la Torre 2?",
                "conversacion_id": "wa-5215512345678",
                "canal": "whatsapp",
            }
        }
    }


class ClasificacionResponse(BaseModel):
    categoria: Categoria
    confianza: float
    senales: List[str]
    justificacion: str
    filtros: dict
    quiere_cita: bool


class RuteoResponse(BaseModel):
    categoria: Categoria
    accion: Accion
    confianza: float
    senales: List[str]
    justificacion: str
    respuesta: str
    siguiente_paso: str
    bloqueo_datos_confidenciales: bool
    estado: str
    requiere_aprobacion: bool
    aprobador: str
    precios_incluidos: bool
    alertas_cumplimiento: List[str] = []
    pendientes_por_confirmar: List[str] = []
    unidades: List[dict] = []
    menu: List[dict] = []
    asesor_sugerido: Optional[str] = None
    ticket_revision: Optional[dict] = None
    filtros_aplicados: dict = {}


class ResolucionTicket(BaseModel):
    resolucion: str = Field(..., min_length=3, description="Ej. 'Broker confirmado, bloqueado' o 'Falso positivo, liberar'")


# ========================================================================== endpoints

@app.get("/")
async def root():
    return {
        "service": "Palm Diamante - Router Comercial",
        "version": "1.0.0",
        "proyecto": inventario.proyecto,
        "desarrolladora": inventario.desarrolladora,
        "inventario_actualizado": inventario.actualizado,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "route": "/api/v1/router/route",
            "classify": "/api/v1/router/classify",
            "inventario": "/api/v1/inventario",
            "revision_manual": "/api/v1/revision-manual",
        },
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "unidades_en_inventario": len(inventario.unidades),
        "tickets_pendientes": len(cola_revision.pendientes()),
        "precios_confirmados": politica.precios_confirmados,
        "aprobador": politica.aprobador,
    }


@app.post("/api/v1/router/classify", response_model=ClasificacionResponse, tags=["Router"])
async def classify(payload: MensajeEntrante):
    """Clasifica el mensaje sin ejecutar ninguna acción (útil para auditoría y pruebas A/B)."""
    c = clasificador.clasificar(payload.mensaje)
    return ClasificacionResponse(
        categoria=c.categoria,
        confianza=c.confianza,
        senales=c.senales,
        justificacion=c.justificacion,
        filtros={k: v for k, v in vars(c.filtros).items() if v is not None},
        quiere_cita=c.quiere_cita,
    )


@app.post("/api/v1/router/route", response_model=RuteoResponse, tags=["Router"])
async def route(payload: MensajeEntrante):
    """Clasifica el mensaje y ejecuta la acción de negocio correspondiente.

    - **COMPRADOR_REAL** → consulta inventario y devuelve `respuesta` + `unidades`.
    - **LEAD_FRIO** → devuelve `respuesta` con `menu` de calificación.
    - **COYOTE** → crea `ticket_revision` con alerta roja; `bloqueo_datos_confidenciales=true`.

    Toda `respuesta` es un **BORRADOR** (`requiere_aprobacion=true`): nada se envía al cliente sin
    aprobación humana. `alertas_cumplimiento` debe venir vacío; si no, el borrador viola la guía.
    `pendientes_por_confirmar` lista los [corchetes] que hay que confirmar o borrar antes de enviar.
    """
    resultado = orquestador.rutear(
        payload.mensaje,
        conversacion_id=payload.conversacion_id,
        canal=payload.canal,
    )
    return RuteoResponse(**vars(resultado))


@app.get("/api/v1/inventario", tags=["Inventario"])
async def listar_inventario(
    torre: Optional[int] = Query(None, ge=1),
    prototipo: Optional[str] = Query(None, min_length=1, max_length=2),
    recamaras: Optional[int] = Query(None, ge=1),
    precio_min_mxn: Optional[int] = Query(None, ge=0),
    precio_max_mxn: Optional[int] = Query(None, ge=0),
    solo_disponibles: bool = True,
):
    unidades = inventario.buscar(
        torre=torre,
        prototipo=prototipo,
        recamaras=recamaras,
        precio_min_mxn=precio_min_mxn,
        precio_max_mxn=precio_max_mxn,
        solo_disponibles=solo_disponibles,
    )
    return {
        "proyecto": inventario.proyecto,
        "actualizado": inventario.actualizado,
        "total": len(unidades),
        "unidades": [u.to_dict() for u in unidades],
    }


@app.get("/api/v1/inventario/{id_unidad}", tags=["Inventario"])
async def detalle_unidad(id_unidad: str):
    unidad = inventario.por_id(id_unidad)
    if unidad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unidad {id_unidad} no existe")
    return unidad.to_dict()


@app.get("/api/v1/revision-manual", tags=["Revisión manual"])
async def bandeja_revision(incluir_resueltos: bool = False):
    tickets = cola_revision.todos() if incluir_resueltos else cola_revision.pendientes()
    return {"total": len(tickets), "tickets": [t.to_dict() for t in tickets]}


@app.post("/api/v1/revision-manual/{id_ticket}/resolver", tags=["Revisión manual"])
async def resolver_ticket(id_ticket: str, payload: ResolucionTicket):
    ticket = cola_revision.resolver(id_ticket, payload.resolucion)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket {id_ticket} no existe")
    return ticket.to_dict()


@app.get("/api/v1/router/prompt", tags=["Router"])
async def prompt_del_router():
    """Devuelve las reglas de negocio en prosa para inyectarlas a un clasificador LLM externo."""
    return {"system_prompt": SYSTEM_PROMPT}


@app.get("/api/v1/router/plantillas", tags=["Router"])
async def plantillas_de_respuesta():
    """Plantillas de la Guía de respuestas para WhatsApp (aprobadas, derivadas y sus pendientes)."""
    return {
        "politica": {
            "estado_por_defecto": "BORRADOR",
            "aprobador": politica.aprobador,
            "precios_confirmados": politica.precios_confirmados,
            "canales_oficiales": politica.canales_oficiales,
            "sitio_oficial": politica.sitio_oficial,
        },
        "plantillas": [vars(p) for p in PLANTILLAS.values()],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8010, reload=True, log_level="info")
