import pytest

from router.classifier import Categoria, RuleBasedClassifier, extraer_filtros, normalizar

clf = RuleBasedClassifier()


@pytest.mark.parametrize(
    "mensaje",
    [
        "¿Cuánto cuesta el departamento de 2 recámaras?",
        "Qué precio tiene el prototipo B en la Torre 2",
        "¿Tienen disponibilidad en torre 1?",
        "Cuántos metros cuadrados tiene el de 3 recámaras",
        "Me interesa, ¿manejan enganche y mensualidades?",
        "Quiero agendar una visita este sábado",
        "Aceptan crédito Infonavit?",
        "Busco algo de hasta 5 millones",
    ],
)
def test_comprador_real(mensaje):
    c = clf.clasificar(mensaje)
    assert c.categoria is Categoria.COMPRADOR_REAL
    assert c.confianza >= 0.6
    assert c.senales


@pytest.mark.parametrize(
    "mensaje",
    ["hola", "Info", "Buenas tardes", "Hola, vi su anuncio", "?", "", "   "],
)
def test_lead_frio(mensaje):
    c = clf.clasificar(mensaje)
    assert c.categoria is Categoria.LEAD_FRIO


@pytest.mark.parametrize(
    "mensaje",
    [
        "¿Cuánto pagan de comisión a brokers externos?",
        "Soy asesor inmobiliario y tengo varios clientes, ¿me comparten la lista de precios para terceros?",
        "Tengo una inmobiliaria, ¿manejan convenio con asesores?",
        "Qué esquema de comisiones cruzadas manejan",
        "Puedo referir clientes a cambio de un fee?",
        "Somos brokers, ¿tienen precio de mayoreo?",
    ],
)
def test_coyote(mensaje):
    c = clf.clasificar(mensaje)
    assert c.categoria is Categoria.COYOTE
    assert c.confianza >= 0.85
    assert c.senales


def test_coyote_tiene_precedencia_sobre_comprador():
    c = clf.clasificar("Soy asesor externo, ¿cuánto cuesta la Torre 2 y qué comisión dan?")
    assert c.categoria is Categoria.COYOTE
    assert c.filtros.torre == 2  # los filtros se extraen igual, pero no se usan para responder


@pytest.mark.parametrize(
    "mensaje",
    [
        "¿Cuánto pagan de mantenimiento al mes?",
        "Trabajo en una inmobiliaria pero busco depa para mí, ¿precio de 2 recámaras?",
    ],
)
def test_no_falsos_positivos_de_coyote(mensaje):
    assert clf.clasificar(mensaje).categoria is Categoria.COMPRADOR_REAL


def test_modelos_en_plural_no_extrae_prototipo():
    c = clf.clasificar("Qué modelos tienen")
    assert c.categoria is Categoria.COMPRADOR_REAL
    assert c.filtros.prototipo is None


def test_normalizar_quita_acentos_y_mayusculas():
    assert normalizar("  ¿Cuánto CUESTA la Recámara?  ") == "¿cuanto cuesta la recamara?"


def test_extraer_filtros_completos():
    f = extraer_filtros(normalizar("Quiero un prototipo B de 3 recámaras en la Torre 2, hasta 7 millones"))
    assert f.torre == 2
    assert f.prototipo == "B"
    assert f.recamaras == 3
    assert f.precio_max_mxn == 7_000_000


def test_extraer_filtros_numeros_en_palabras_y_mdp():
    f = extraer_filtros(normalizar("algo de dos recamaras, presupuesto de 5.5 mdp"))
    assert f.recamaras == 2
    assert f.precio_max_mxn == 5_500_000


def test_quiere_cita_detectado():
    c = clf.clasificar("Me gustaría agendar una cita para conocer la torre 1")
    assert c.quiere_cita is True
    assert c.filtros.torre == 1
