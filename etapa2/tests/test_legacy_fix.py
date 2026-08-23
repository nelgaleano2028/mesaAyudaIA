from etapa2.legacy_fix.legacy_module import (
    contar_reaperturas,
    filtrar_por_periodo,
    resumir_por_area,
)


def test_filtrar_por_periodo_incluye_limites():
    tickets = [
        {"fecha_creacion": "2025-03-01", "area": "Aplicaciones"},
        {"fecha_creacion": "2025-03-15", "area": "Calidad"},
        {"fecha_creacion": "2025-03-31", "area": "Compras"},
        {"fecha_creacion": "2025-04-01", "area": "Operaciones"},
    ]
    result = filtrar_por_periodo(tickets, __import__("datetime").date(2025, 3, 1), __import__("datetime").date(2025, 3, 31))
    assert len(result) == 3
    assert [t["area"] for t in result] == ["Aplicaciones", "Calidad", "Compras"]


def test_resumir_por_area_no_reutiliza_estado_acumulado():
    assert resumir_por_area([
        {"area": "Aplicaciones"},
        {"area": "Calidad"},
    ]) == {"Aplicaciones": 1, "Calidad": 1}
    assert resumir_por_area([{"area": "Aplicaciones"}]) == {"Aplicaciones": 1}


def test_contar_reaperturas_normaliza_estado():
    tickets = [
        {"estado": "reabierto"},
        {"estado": "Reabierto"},
        {"estado": "Cerrado"},
    ]
    assert contar_reaperturas(tickets) == 2


