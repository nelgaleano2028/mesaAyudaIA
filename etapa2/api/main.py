from __future__ import annotations

import os
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from etapa2.clasificador.claude_client import ResultadoClasificacion, clasificar

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DB_PATH = Path(os.getenv("DATABASE_PATH", "data/app.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Mesa de Ayuda Inteligente API", version="0.1.0")

logger = logging.getLogger("mesa_ayuda_api")


class SolicitudInput(BaseModel):
    asunto: str = Field(..., min_length=5, max_length=200)
    descripcion: str = Field(default="", max_length=4000)
    area: str = Field(..., min_length=2, max_length=80)
    canal: str = Field(default="web", max_length=30)
    solicitante: str = Field(..., min_length=5, max_length=120)

    @field_validator("asunto", "descripcion", "area", "canal", "solicitante")
    @classmethod
    def strip_fields(cls, value: str) -> str:
        if value is None:
            return value
        return value.strip()

    @field_validator("asunto", "descripcion", "area", "solicitante")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("No puede quedar vacío.")
        return value


class SolicitudOut(BaseModel):
    id: str
    asunto: str
    descripcion: str
    area: str
    canal: str
    solicitante: str
    estado: str = "pendiente"
    prioridad: str | None = None
    categoria: str | None = None
    fecha_creacion: str


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "La entrada recibida no es válida.",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else {
        "code": "http_error",
        "message": str(exc.detail),
    }
    return JSONResponse(status_code=exc.status_code, content={"error": detail})


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception):
    logger.exception("error_interno_api", extra={"type": type(exc).__name__})
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "Ocurrió un error inesperado en la API.",
            }
        },
    )


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS solicitudes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asunto TEXT NOT NULL,
                descripcion TEXT,
                area TEXT NOT NULL,
                canal TEXT NOT NULL,
                solicitante TEXT NOT NULL,
                estado TEXT NOT NULL,
                prioridad TEXT,
                categoria TEXT,
                fecha_creacion TEXT NOT NULL,
                fecha_clasificacion TEXT
            )
            """
        )
        conn.commit()


def _serialize_row(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


@app.post("/solicitudes", response_model=SolicitudOut, status_code=201)
def crear_solicitud(payload: SolicitudInput):
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    resultado: ResultadoClasificacion = clasificar(f"{payload.asunto} {payload.descripcion}".strip())
    estado = "pendiente_revision" if resultado.modo == "degradado" else "clasificado"
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO solicitudes (asunto, descripcion, area, canal, solicitante, estado, prioridad, categoria, fecha_creacion, fecha_clasificacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.asunto,
                payload.descripcion,
                payload.area,
                payload.canal,
                payload.solicitante,
                estado,
                resultado.prioridad,
                resultado.categoria,
                now,
                now if resultado.modo == "clasificado" else None,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM solicitudes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="No se pudo crear la solicitud.")
    data = _serialize_row(row)
    return {key: data[key] for key in SolicitudOut.model_fields}


@app.get("/solicitudes/{id}")
def obtener_solicitud(id: str):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM solicitudes WHERE id = ?", (id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Solicitud {id} no encontrada.")
    return _serialize_row(row)


@app.get("/solicitudes")
def listar_solicitudes(
    area: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    prioridad: str | None = Query(default=None),
    desde: str | None = Query(default=None),
    hasta: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    query = "SELECT * FROM solicitudes WHERE 1=1"
    params: list[Any] = []
    if area:
        query += " AND area = ?"
        params.append(area)
    if estado:
        query += " AND estado = ?"
        params.append(estado)
    if prioridad:
        query += " AND prioridad = ?"
        params.append(prioridad)
    if desde:
        query += " AND fecha_creacion >= ?"
        params.append(desde)
    if hasta:
        query += " AND fecha_creacion <= ?"
        params.append(hasta)
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_serialize_row(row) for row in rows]


@app.get("/health")
def health():
    return {"status": "ok"}
