from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DB_PATH = Path(os.getenv("DATABASE_PATH", "data/app.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("mesa_ayuda_api")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('{"timestamp":"%(asctime)s","level":"%(levelname)s","message":%(message)s}', datefmt="%Y-%m-%dT%H:%M:%S"))
    logger.addHandler(handler)

app = FastAPI(title="Mesa de Ayuda Inteligente API", version="0.1.0")


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


@app.get("/health")
def health():
    return {"status": "ok"}
