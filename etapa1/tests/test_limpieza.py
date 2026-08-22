import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from limpieza_tickets import detect_duplicate_keys, normalize_category, parse_date


def test_parse_date_supports_multiple_formats():
    assert parse_date("2025-03-08") == "2025-03-08"
    assert parse_date("20-Jul-2025") == "2025-07-20"
    assert parse_date("31/05/2026") == "2026-05-31"
    assert parse_date("not-a-date") is None


def test_normalize_category_reduces_variants():
    assert normalize_category("  HARDWARE  ") == "hardware"
    assert normalize_category("Gestión de accesos") == "gestion_de_accesos"
    assert normalize_category("") == "sin_categoria"


def test_detect_duplicate_keys_marks_logically_equal_tickets():
    first = {
        "solicitante": "usuario001@lafortuna.com.co",
        "asunto": "Solicitud de acceso",
        "descripcion": "El usuario reporta la novedad.",
        "fecha_creacion": "2025-01-10",
    }
    second = {
        "solicitante": "usuario001@lafortuna.com.co",
        "asunto": "solicitud de acceso",
        "descripcion": "el usuario reporta la novedad",
        "fecha_creacion": "2025-01-10",
    }
    assert detect_duplicate_keys(first, second) is True
    assert detect_duplicate_keys(first, {**first, "asunto": "distinto"}) is False
