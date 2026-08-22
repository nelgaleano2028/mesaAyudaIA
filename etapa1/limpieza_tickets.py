from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


INPUT_COLUMNS = [
    "id",
    "fecha_creacion",
    "fecha_cierre",
    "area",
    "categoria",
    "prioridad",
    "canal",
    "solicitante",
    "asunto",
    "descripcion",
    "estado",
    "reaperturas",
]

MONTH_MAP = {
    "ene": "Jan",
    "feb": "Feb",
    "mar": "Mar",
    "abr": "Apr",
    "may": "May",
    "jun": "Jun",
    "jul": "Jul",
    "ago": "Aug",
    "sep": "Sep",
    "oct": "Oct",
    "nov": "Nov",
    "dic": "Dec",
}

CATEGORY_MAP = {
    "acceso": "accesos",
    "accesos": "accesos",
    "gestion de accesos": "gestion_de_accesos",
    "capacitacion": "capacitacion",
    "capacitación": "capacitacion",
    "compras": "compras",
    "ordenes de compra": "compras",
    "ordenes_de_compra": "compras",
    "órdenes de compra": "compras",
    "red": "red",
    "incidente": "incidente",
    "incidentes": "incidente",
    "reportes": "reportes",
    "informes": "reportes",
    "vacaciones": "vacaciones",
    "viaticos": "viaticos",
    "viáticos": "viaticos",
    "hardware": "hardware",
    "equipos": "hardware",
    "software": "software",
    "nomina": "nomina",
    "nómina": "nomina",
    "conectividad": "conectividad",
    "otros": "otros",
    "aplicaciones": "aplicaciones",
}

PRIORITY_MAP = {
    "1-alta": "alta",
    "alta": "alta",
    "al ta": "alta",
    "2-media": "media",
    "media": "media",
    "3-baja": "baja",
    "baja": "baja",
    "critica": "critica",
    "crítica": "critica",
    "crítico": "critica",
    "1 alta": "alta",
    "2 media": "media",
    "3 baja": "baja",
}

STATUS_MAP = {
    "abierto": "abierto",
    "cerrado": "cerrado",
    "en proceso": "en_proceso",
    "reabierto": "reabierto",
    "escalado": "escalado",
}


def normalize_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return text.strip()


def normalize_area(value: Any) -> str:
    text = normalize_text(value)
    if not text:
        return "sin_area"
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned.title()


def normalize_status(value: Any) -> str:
    text = normalize_text(value).lower().strip()
    normalized = re.sub(r"[^a-z0-9]+", " ", text).strip()
    if not normalized:
        return "sin_estado"
    return STATUS_MAP.get(normalized, normalized.replace(" ", "_"))


def normalize_category(value: Any) -> str:
    text = normalize_text(value).lower().strip()
    if not text:
        return "sin_categoria"
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    canonical = CATEGORY_MAP.get(text, text.replace(" ", "_"))
    if canonical == "sin_categoria":
        return "sin_categoria"
    return canonical


def normalize_priority(value: Any) -> str:
    text = normalize_text(value).lower().strip()
    if not text:
        return "sin_prioridad"
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    text = re.sub(r"\s+", " ", text)
    return PRIORITY_MAP.get(text, text.replace(" ", "_"))


def parse_date(value: Any) -> str | None:
    text = normalize_text(value)
    if not text:
        return None
    stripped = text.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", stripped):
        return stripped
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", stripped):
        return stripped.split(" ")[0]
    for fmt in (
        "%d/%m/%Y",
        "%d/%m/%y",
        "%d-%m-%Y",
        "%d-%m-%y",
        "%d-%b-%Y",
        "%d-%B-%Y",
        "%d %b %Y",
        "%d %B %Y",
        "%Y/%m/%d",
        "%Y.%m.%d",
    ):
        try:
            return datetime.strptime(stripped, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    for fmt in ("%d-%b-%Y", "%d-%B-%Y"):
        month_name = stripped.split("-")[1] if "-" in stripped else ""
        if month_name:
            month_key = month_name.lower()[:3]
            replacement = MONTH_MAP.get(month_key)
            if replacement:
                candidate = re.sub(r"-[A-Za-z]+-", f"-{replacement}-", stripped, count=1)
                try:
                    return datetime.strptime(candidate, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue
    try:
        if "-" in stripped and len(stripped.split("-")) == 3 and stripped.split("-")[1].isalpha():
            day, month, year = stripped.split("-")
            month_key = month.lower()[:3]
            replacement = MONTH_MAP.get(month_key)
            if replacement:
                return datetime.strptime(f"{day}-{replacement}-{year}", "%d-%b-%Y").strftime("%Y-%m-%d")
    except ValueError:
        pass
    return None


def detect_duplicate_keys(first: dict[str, Any], second: dict[str, Any]) -> bool:
    def normalize_duplicate_value(value: Any) -> str:
        text = normalize_text(value).lower()
        text = re.sub(r"[^a-z0-9]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def key_for(ticket: dict[str, Any]) -> tuple[str, str, str, str]:
        solicitante = normalize_duplicate_value(ticket.get("solicitante"))
        asunto = normalize_duplicate_value(ticket.get("asunto"))
        descripcion = normalize_duplicate_value(ticket.get("descripcion"))
        fecha = parse_date(ticket.get("fecha_creacion")) or "sin_fecha"
        return (solicitante, asunto, descripcion, fecha)

    first_key = key_for(first)
    second_key = key_for(second)
    return first_key == second_key


def build_output_paths(base_dir: Path) -> dict[str, Path]:
    results_dir = base_dir if base_dir.name == "salida" else base_dir / "salida"
    results_dir.mkdir(parents=True, exist_ok=True)
    return {
        "clean": results_dir / "tickets_limpios.csv",
        "invalid": results_dir / "tickets_invalidos.csv",
        "summary": results_dir / "resumen_area_prioridad.csv",
        "log": results_dir / "log_limpieza.txt",
    }


def load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def clean_ticket_rows(rows: Iterable[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    cleaned: list[dict[str, Any]] = []
    invalid_rows: list[dict[str, Any]] = []
    log_lines: list[str] = []
    seen_keys: dict[tuple[str, str, str, str], str] = {}

    for row in rows:
        record = {**row}
        record["id"] = normalize_text(record.get("id"))
        record["area"] = normalize_area(record.get("area"))
        record["categoria"] = normalize_category(record.get("categoria"))
        record["prioridad"] = normalize_priority(record.get("prioridad"))
        record["canal"] = normalize_text(record.get("canal")).lower()
        record["solicitante"] = normalize_text(record.get("solicitante")).lower()
        record["asunto"] = normalize_text(record.get("asunto"))
        record["descripcion"] = normalize_text(record.get("descripcion"))
        record["estado"] = normalize_status(record.get("estado"))
        record["reaperturas"] = int(record.get("reaperturas") or 0)

        fecha_creacion = parse_date(record.get("fecha_creacion"))
        fecha_cierre = parse_date(record.get("fecha_cierre"))
        reasons: list[str] = []

        if not record["id"]:
            reasons.append("id vacio")
        if not record["solicitante"]:
            reasons.append("solicitante vacio")
        if not record["asunto"]:
            reasons.append("asunto vacio")
        if not fecha_creacion:
            reasons.append("fecha_creacion invalida")
        if fecha_cierre and fecha_creacion and fecha_cierre < fecha_creacion:
            reasons.append("fecha_cierre anterior a fecha_creacion")
        if record["area"] == "sin_area":
            reasons.append("area vacia")
        if record["categoria"] == "sin_categoria":
            reasons.append("categoria vacia")
        if record["prioridad"] == "sin_prioridad":
            reasons.append("prioridad vacia")
        if record["estado"] == "sin_estado":
            reasons.append("estado vacio")

        duplicate_key = (
            re.sub(r"\s+", " ", record["solicitante"]).strip(),
            re.sub(r"\s+", " ", record["asunto"]).strip().lower(),
            re.sub(r"\s+", " ", record["descripcion"]).strip().lower(),
            fecha_creacion or "sin_fecha",
        )
        if duplicate_key in seen_keys:
            reasons.append("duplicado")
            log_lines.append(f"Duplicado detectado: {record['id']} -> se conserva {seen_keys[duplicate_key]}")
        else:
            seen_keys[duplicate_key] = record["id"]

        if reasons:
            invalid_rows.append({**record, "motivo": "; ".join(reasons)})
            if record["id"]:
                log_lines.append(f"Registro invalido: {record['id']} -> {reasons}")
            continue

        record["fecha_creacion"] = fecha_creacion
        record["fecha_cierre"] = fecha_cierre
        cleaned.append(record)

    return cleaned, invalid_rows, log_lines


def export_clean_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    fieldnames = [
        "id",
        "fecha_creacion",
        "fecha_cierre",
        "area",
        "categoria",
        "prioridad",
        "canal",
        "solicitante",
        "asunto",
        "descripcion",
        "estado",
        "reaperturas",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def export_invalid_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    fieldnames = [
        "id",
        "fecha_creacion",
        "fecha_cierre",
        "area",
        "categoria",
        "prioridad",
        "canal",
        "solicitante",
        "asunto",
        "descripcion",
        "estado",
        "reaperturas",
        "motivo",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def export_summary(rows: list[dict[str, Any]], output_path: Path) -> None:
    counts = Counter((row.get("area"), row.get("prioridad")) for row in rows)
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["area", "prioridad", "cantidad"])
        for (area, prioridad), cantidad in sorted(counts.items()):
            writer.writerow([area, prioridad, cantidad])


def export_log(log_lines: list[str], output_path: Path) -> None:
    output_path.write_text("\n".join(log_lines) + ("\n" if log_lines else ""), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Limpieza y normalización del histórico de tickets.")
    parser.add_argument("--input", type=Path, default=Path("materiales/datos/tickets_historicos.csv"), help="Archivo CSV original")
    parser.add_argument("--output-dir", type=Path, default=Path("etapa1"), help="Directorio base de salida; se crea una subcarpeta 'salida' automáticamente")
    args = parser.parse_args()

    rows = load_rows(args.input)
    cleaned, invalid_rows, log_lines = clean_ticket_rows(rows)
    output_paths = build_output_paths(args.output_dir)
    export_clean_csv(cleaned, output_paths["clean"])
    export_invalid_csv(invalid_rows, output_paths["invalid"])
    export_summary(cleaned, output_paths["summary"])
    export_log(log_lines, output_paths["log"])

    print(f"Tickets limpios: {len(cleaned)}")
    print(f"Tickets invalidos: {len(invalid_rows)}")
    print(f"Archivo generado: {output_paths['clean']}")
    print(f"Resumen generado: {output_paths['summary']}")


if __name__ == "__main__":
    main()
