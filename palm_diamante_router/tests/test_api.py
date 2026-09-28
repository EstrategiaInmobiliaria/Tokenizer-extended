import pytest
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpiar_estado():
    main.cola_revision.limpiar()
    main.politica.precios_confirmados = False
    yield
    main.cola_revision.limpiar()
    main.politica.precios_confirmados = False


@pytest.fixture
def precios_confirmados():
    main.politica.precios_confirmados = True
    yield
    main.politica.precios_confirmados = False


def route(mensaje: str, **extra) -> dict:
    r = client.post("/api/v1/router/route", json={"mensaje": mensaje, **extra})
    assert r.status_code == 200
    return r.json()


def test_health_y_root():
    health = client.get("/health").json()
    assert health["status"] == "healthy"
    assert health["precios_confirmados"] is False
    root = client.get("/").json()
    assert root["proyecto"] == "Palm Diamante"
    assert "route" in root["endpoints"]


def test_toda_respuesta_es_borrador_con_aprobador():
    for mensaje in ("hola", "¿precio de 2 recámaras?", "Soy broker, ¿qué comisión dan?"):
        data = route(mensaje)
        assert data["estado"] == "BORRADOR"
        assert data["requiere_aprobacion"] is True
        assert data["aprobador"] == "Jimmy"
        assert data["alertas_cumplimiento"] == []


def test_precios_bloqueados_por_defecto():
    data = route("¿Cuánto cuesta el de 3 recámaras en la Torre 2?")
    assert data["categoria"] == "COMPRADOR_REAL"
    assert data["precios_incluidos"] is False
    assert "$" not in data["respuesta"]
    assert "PD-T2-204" in data["respuesta"] and "165 m²" in data["respuesta"]
    assert "Estoy confirmando la lista de precios más reciente" in data["respuesta"]
    assert "Jimmy" in data["siguiente_paso"]
    # los datos internos siguen disponibles para el asesor, no para el cliente
    assert data["unidades"][0]["precio_lista_mxn"] == 6_500_000


def test_route_comprador_real_con_precios_confirmados(precios_confirmados):
    data = route("¿Cuánto cuesta el de 3 recámaras en la Torre 2?")
    assert data["accion"] == "RESPONDER_CON_INVENTARIO"
    assert data["bloqueo_datos_confidenciales"] is False
    assert data["precios_incluidos"] is True
    assert [u["id_unidad"] for u in data["unidades"]] == ["PD-T2-204"]
    assert data["asesor_sugerido"] == "CA"
    assert "$6,500,000 MXN" in data["respuesta"]
    assert data["filtros_aplicados"] == {"torre": 2, "recamaras": 3}


def test_ubicacion_usa_plantilla_aprobada():
    data = route("¿Dónde está ubicado el desarrollo?")
    assert data["categoria"] == "COMPRADOR_REAL"
    assert "Costera de las Palmas" in data["respuesta"]
    assert data["unidades"] == []


def test_entrega_no_promete_fechas():
    data = route("¿Cuándo entregan la Torre 1 y qué avance de obra llevan?")
    assert "un asesor te confirma la fecha de entrega" in data["respuesta"]
    assert data["alertas_cumplimiento"] == []


def test_formas_de_pago_usa_plantilla_sin_plazos():
    data = route("¿Manejan enganche y mensualidades?")
    assert "manejamos financiamiento directo, y el plazo depende de la torre" in data["respuesta"]
    for plazo in ("5 meses", "9 meses", "22 meses"):
        assert plazo not in data["respuesta"]


def test_precio_sin_unidades_usa_sinprecio_literal():
    data = route("¿Cuánto cuesta?")
    assert data["categoria"] == "COMPRADOR_REAL"
    assert data["unidades"] == []
    assert data["respuesta"] == (
        "Con gusto. Estoy confirmando la lista de precios más reciente para darte información exacta "
        "y te la comparto en cuanto la tenga. Mientras, ¿qué tamaño de departamento buscas?"
    )


def test_interes_generico_califica_sin_listar_inventario():
    data = route("Me interesa un departamento")
    assert data["categoria"] == "COMPRADOR_REAL"
    assert data["unidades"] == []
    assert data["respuesta"] == (
        "Para mostrarte las opciones que mejor te queden: ¿lo buscas para vivir, vacacionar o invertir? "
        "¿Tienes un rango de presupuesto en mente? ¿Lo pagarías de contado, con plan de pagos o con crédito?"
    )
    assert data["siguiente_paso"].startswith("Calificar al prospecto")


def test_lista_larga_se_recorta_en_el_borrador():
    from router import Inventario, Orquestador
    from router.orchestrator import MAX_UNIDADES_EN_RESPUESTA

    base = {"torre": "Torre 3", "prototipo": "B1", "recamaras": 2, "superficie_m2": 76.04,
            "precio_lista_mxn": 5_040_000, "estatus": "Disponible", "asesor_asignado_defecto": "MT"}
    inv = Inventario.from_dict({
        "proyecto": "P", "desarrolladora": "D", "actualizado": "x",
        "inventario": [{**base, "id_unidad": f"PD-T3-{i:03d}"} for i in range(12)],
    })
    r = Orquestador(inv).rutear("¿Qué tienen disponible en la torre 3?")
    assert len(r.unidades) == 12
    assert r.respuesta.count("PD-T3-") == MAX_UNIDADES_EN_RESPUESTA
    assert f"Hay {12 - MAX_UNIDADES_EN_RESPUESTA} opciones más" in r.respuesta


def test_route_comprador_sin_coincidencias_ofrece_alternativas():
    r = client.post("/api/v1/router/route", json={"mensaje": "Tienen algo de 4 recámaras?"})
    data = r.json()
    assert data["categoria"] == "COMPRADOR_REAL"
    assert len(data["unidades"]) == 2
    assert "no tenemos unidades disponibles con exactamente" in data["respuesta"]


def test_route_comprador_con_cita_usa_plantilla_y_canales_oficiales():
    data = route("Quiero agendar una visita para ver la torre 1")
    assert data["categoria"] == "COMPRADOR_REAL"
    assert "¿Qué día y horario te acomodan?" in data["respuesta"]
    for canal in ("55 4437 8776", "55 6100 0600", "55 2855 7467"):
        assert canal in data["respuesta"]
    assert data["siguiente_paso"].startswith("Agendar cita")
    assert data["pendientes_por_confirmar"] == ["en el desarrollo / en oficina / por videollamada"]


def test_route_lead_frio_usa_primer_contacto_aprobado():
    data = route("hola")
    assert data["categoria"] == "LEAD_FRIO"
    assert data["accion"] == "DESPLEGAR_MENU"
    assert data["respuesta"] == (
        "Hola, gracias por tu interés en Palm Diamante. Te atiende Estrategia Inmobiliaria. "
        "Puedes escribirnos o llamarnos al 55 4437 8776, 55 6100 0600 o 55 2855 7467, y conocer el "
        "proyecto en palm-diamante.com/es. ¿Qué tipo de departamento te interesa?"
    )
    assert data["pendientes_por_confirmar"] == []
    assert [o["etiqueta"] for o in data["menu"]] == [
        "Prototipos y recámaras",
        "Ubicación del desarrollo",
        "Agendar cita o visita",
    ]
    assert data["unidades"] == []
    assert "$" not in data["respuesta"]


def test_route_coyote_escala_y_bloquea_inventario():
    payload = {
        "mensaje": "Soy broker, ¿cuánto cuesta la Torre 2 y qué comisión manejan para terceros?",
        "conversacion_id": "wa-123",
        "canal": "whatsapp",
    }
    r = client.post("/api/v1/router/route", json=payload)
    data = r.json()
    assert data["categoria"] == "COYOTE"
    assert data["accion"] == "ESCALAR_REVISION_MANUAL"
    assert data["bloqueo_datos_confidenciales"] is True
    assert data["unidades"] == []
    for confidencial in ("6,500,000", "4,850,000", "165", "120.5", "PD-T"):
        assert confidencial not in data["respuesta"]
    ticket = data["ticket_revision"]
    assert ticket["alerta"] == "ROJA"
    assert ticket["estado"] == "PENDIENTE"
    assert ticket["conversacion_id"] == "wa-123"
    assert ticket["canal"] == "whatsapp"

    bandeja = client.get("/api/v1/revision-manual").json()
    assert bandeja["total"] == 1
    assert bandeja["tickets"][0]["id_ticket"] == ticket["id_ticket"]

    res = client.post(f"/api/v1/revision-manual/{ticket['id_ticket']}/resolver", json={"resolucion": "Broker confirmado"})
    assert res.status_code == 200
    assert res.json()["estado"] == "RESUELTO"
    assert client.get("/api/v1/revision-manual").json()["total"] == 0
    assert client.get("/api/v1/revision-manual?incluir_resueltos=true").json()["total"] == 1


def test_resolver_ticket_inexistente():
    assert client.post("/api/v1/revision-manual/REV-NOPE/resolver", json={"resolucion": "x y z"}).status_code == 404


def test_classify_no_ejecuta_acciones():
    r = client.post("/api/v1/router/classify", json={"mensaje": "Soy asesor externo, ¿qué comisión dan?"})
    assert r.status_code == 200
    assert r.json()["categoria"] == "COYOTE"
    assert client.get("/api/v1/revision-manual").json()["total"] == 0


def test_inventario_endpoints():
    todo = client.get("/api/v1/inventario").json()
    assert todo["total"] == 2
    filtrado = client.get("/api/v1/inventario", params={"torre": 1}).json()
    assert [u["id_unidad"] for u in filtrado["unidades"]] == ["PD-T1-101"]
    assert client.get("/api/v1/inventario/PD-T2-204").json()["precio_lista_mxn"] == 6_500_000
    assert client.get("/api/v1/inventario/NO-EXISTE").status_code == 404


def test_prompt_endpoint_expone_reglas():
    prompt = client.get("/api/v1/router/prompt").json()["system_prompt"]
    for cat in ("COMPRADOR_REAL", "LEAD_FRIO", "COYOTE"):
        assert cat in prompt


def test_plantillas_endpoint():
    data = client.get("/api/v1/router/plantillas").json()
    assert data["politica"]["aprobador"] == "Jimmy"
    assert data["politica"]["canales_oficiales"] == ["55 4437 8776", "55 6100 0600", "55 2855 7467"]
    por_clave = {p["clave"]: p for p in data["plantillas"]}
    assert {"primer_contacto", "calificar", "sin_precio", "precio", "tamanos", "ubicacion",
            "formas_pago", "entrega", "cita", "seguimiento"} <= set(por_clave)
    assert por_clave["primer_contacto"]["comando"] == "/hola"
    assert por_clave["sin_precio"]["estado"] == "aprobado"
    assert por_clave["precio"]["estado"] == "con_corchetes"
    assert por_clave["precio"]["pendientes"] == ["precio de entrada"]
    assert por_clave["tamanos"]["pendientes"] == [
        ", todos con terraza",
        ", con alberca principal, jardines interiores, palapa social y lounge frente al mar",
    ]
    assert por_clave["coyote_neutral"]["estado"] == "derivado"


def test_validacion_payload():
    assert client.post("/api/v1/router/route", json={}).status_code == 422
