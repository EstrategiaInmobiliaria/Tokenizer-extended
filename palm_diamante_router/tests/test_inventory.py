import pytest

from router.inventory import DEFAULT_INVENTORY_PATH, Inventario


@pytest.fixture(scope="module")
def inv() -> Inventario:
    return Inventario.from_json(DEFAULT_INVENTORY_PATH)


def test_carga_inventario_maestro(inv):
    assert inv.proyecto == "Palm Diamante"
    assert inv.desarrolladora == "Agartha Bienes Raices"
    assert {u.id_unidad for u in inv.unidades} == {"PD-T1-101", "PD-T2-204"}


def test_buscar_por_torre_y_recamaras(inv):
    assert [u.id_unidad for u in inv.buscar(torre=2)] == ["PD-T2-204"]
    assert [u.id_unidad for u in inv.buscar(recamaras=2)] == ["PD-T1-101"]
    assert inv.buscar(torre=1, recamaras=3) == []


def test_buscar_por_prototipo_insensible_a_mayusculas(inv):
    assert [u.id_unidad for u in inv.buscar(prototipo="b")] == ["PD-T2-204"]


def test_buscar_por_rango_de_precio_ordena_ascendente(inv):
    todos = inv.buscar()
    assert [u.precio_lista_mxn for u in todos] == [4_850_000, 6_500_000]
    assert [u.id_unidad for u in inv.buscar(precio_max_mxn=5_000_000)] == ["PD-T1-101"]
    assert [u.id_unidad for u in inv.buscar(precio_min_mxn=5_000_000)] == ["PD-T2-204"]


def test_solo_disponibles_excluye_vendidas():
    data = {
        "proyecto": "P",
        "desarrolladora": "D",
        "actualizado": "2026-01-01",
        "inventario": [
            {"id_unidad": "X-1", "torre": "Torre 1", "prototipo": "A", "recamaras": 2, "superficie_m2": 100,
             "precio_lista_mxn": 1, "estatus": "Vendido", "asesor_asignado_defecto": "MT"},
            {"id_unidad": "X-2", "torre": "Torre 1", "prototipo": "A", "recamaras": 2, "superficie_m2": 100,
             "precio_lista_mxn": 2, "estatus": "disponible", "asesor_asignado_defecto": "MT"},
        ],
    }
    inv = Inventario.from_dict(data)
    assert [u.id_unidad for u in inv.buscar()] == ["X-2"]
    assert len(inv.buscar(solo_disponibles=False)) == 2


def test_ids_duplicados_son_rechazados():
    unidad = {"id_unidad": "DUP", "torre": "Torre 1", "prototipo": "A", "recamaras": 2, "superficie_m2": 100,
              "precio_lista_mxn": 1, "estatus": "Disponible", "asesor_asignado_defecto": "MT"}
    with pytest.raises(ValueError):
        Inventario.from_dict({"proyecto": "P", "desarrolladora": "D", "actualizado": "x", "inventario": [unidad, unidad]})


def test_por_id_y_resumen_publico(inv):
    assert inv.por_id("pd-t1-101").torre == "Torre 1"
    assert inv.por_id("NO-EXISTE") is None
    resumen = inv.resumen_publico()
    assert resumen["torres"] == ["Torre 1", "Torre 2"]
    assert "precio" not in " ".join(resumen.keys())
