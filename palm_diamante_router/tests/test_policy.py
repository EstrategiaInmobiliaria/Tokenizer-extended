import pytest

from router.plantillas import PLANTILLAS
from router.policy import PoliticaComunicacion


@pytest.fixture
def politica():
    return PoliticaComunicacion()


def test_borrador_limpio_no_tiene_violaciones(politica):
    texto = "Nuestros canales son 55 4437 8776 y 55 6100 0600; sitio oficial palm-diamante.com/es."
    assert politica.validar_borrador(texto) == []


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("Visita el recorrido en palmdiamante.mx/showroom", "dominio_prohibido:palmdiamante.mx"),
        ("Más info en https://palmdiamanteacapulco.com", "dominio_prohibido:palmdiamanteacapulco.com"),
        ("También en ventadeptosacapulco.com", "dominio_prohibido:ventadeptosacapulco.com"),
        ("Llama al 55 4021 2638", "telefono_prohibido:55 4021 2638"),
        ("Llama al 5540212638", "telefono_prohibido:55 4021 2638"),
        ("WhatsApp: 744-271-3055", "telefono_prohibido:744 271 3055"),
        ("Se entrega en diciembre", "promesa_de_entrega_o_avance"),
        ("Llevamos avance de 80%", "promesa_de_entrega_o_avance"),
    ],
)
def test_detecta_violaciones(politica, texto, esperado):
    assert esperado in politica.validar_borrador(texto)


def test_todas_las_plantillas_cumplen_la_politica(politica):
    for p in PLANTILLAS.values():
        assert politica.validar_borrador(p.texto) == [], p.clave


def test_desde_entorno(monkeypatch):
    monkeypatch.delenv("PALM_PRECIOS_CONFIRMADOS", raising=False)
    assert PoliticaComunicacion.desde_entorno().precios_confirmados is False
    monkeypatch.setenv("PALM_PRECIOS_CONFIRMADOS", "1")
    assert PoliticaComunicacion.desde_entorno().precios_confirmados is True
    monkeypatch.setenv("PALM_PRECIOS_CONFIRMADOS", "no")
    assert PoliticaComunicacion.desde_entorno().precios_confirmados is False
    monkeypatch.setenv("PALM_APROBADOR", "Otro")
    assert PoliticaComunicacion.desde_entorno().aprobador == "Otro"
