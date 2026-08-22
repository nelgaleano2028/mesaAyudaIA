"""
servicio_mock — API REST de terceros simulada.

Simula el comportamiento real de un servicio externo del que usted no
controla la disponibilidad: latencia variable, errores 500 intermitentes
y limitación de tasa 429. No lo modifique: forma parte del enunciado.

Ejecución:
    pip install fastapi uvicorn
    uvicorn app:app --reload --port 8080

Documentación interactiva en http://localhost:8080/docs
Especificación en openapi.yaml
"""

import asyncio
import random
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query, Header
from pydantic import BaseModel, Field

app = FastAPI(
    title="Servicio de Solicitudes Corporativas (simulado)",
    version="1.4.0",
    description="Servicio externo simulado para la Prueba Técnica de Nivelación.",
)

# --- comportamiento simulado ---------------------------------------------
LATENCIA_MIN = 0.10          # segundos
LATENCIA_MAX = 2.50
PROB_ERROR_500 = 0.12        # 12 % de las peticiones fallan con 500
PROB_ERROR_429 = 0.05        # 5 % responden 429
TOKEN_VALIDO = "demo-token-prueba-2026"

ALMACEN: dict[str, dict] = {}


class SolicitudEntrada(BaseModel):
    asunto: str = Field(..., min_length=5, max_length=200)
    descripcion: str = Field("", max_length=4000)
    area: str = Field(..., min_length=2, max_length=80)
    solicitante: str = Field(..., min_length=5, max_length=120)
    canal: str = Field("api", max_length=30)


class SolicitudSalida(BaseModel):
    id: str
    asunto: str
    descripcion: str
    area: str
    solicitante: str
    canal: str
    estado: str
    fecha_creacion: str


async def _simular_red(ruta: str):
    await asyncio.sleep(random.uniform(LATENCIA_MIN, LATENCIA_MAX))
    if ruta != "/health":
        r = random.random()
        if r < PROB_ERROR_500:
            raise HTTPException(status_code=500, detail="Error interno del proveedor. Reintente.")
        if r < PROB_ERROR_500 + PROB_ERROR_429:
            raise HTTPException(
                status_code=429,
                detail="Demasiadas peticiones. Reintente después del tiempo indicado.",
                headers={"Retry-After": "3"},
            )


def _autorizar(authorization: str | None):
    if authorization != f"Bearer {TOKEN_VALIDO}":
        raise HTTPException(status_code=401, detail="Token ausente o inválido.")


@app.get("/health")
async def health():
    await _simular_red("/health")
    return {"estado": "operativo", "hora": datetime.now(timezone.utc).isoformat()}


@app.get("/solicitudes", response_model=list[SolicitudSalida])
async def listar(
    area: str | None = Query(None),
    estado: str | None = Query(None),
    limite: int = Query(50, ge=1, le=200),
    authorization: str | None = Header(None),
):
    _autorizar(authorization)
    await _simular_red("/solicitudes")
    items = list(ALMACEN.values())
    if area:
        items = [i for i in items if i["area"].lower() == area.lower()]
    if estado:
        items = [i for i in items if i["estado"].lower() == estado.lower()]
    return items[:limite]


@app.get("/solicitudes/{id_solicitud}", response_model=SolicitudSalida)
async def obtener(id_solicitud: str, authorization: str | None = Header(None)):
    _autorizar(authorization)
    await _simular_red("/solicitudes")
    if id_solicitud not in ALMACEN:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    return ALMACEN[id_solicitud]


@app.post("/solicitudes", response_model=SolicitudSalida, status_code=201)
async def crear(
    cuerpo: SolicitudEntrada,
    authorization: str | None = Header(None),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
):
    """Crea una solicitud.

    El servicio respeta la cabecera opcional `Idempotency-Key`: dos
    peticiones con la misma clave devuelven la misma solicitud.
    """
    _autorizar(authorization)
    await _simular_red("/solicitudes")
    if idempotency_key:
        for s in ALMACEN.values():
            if s.get("_clave") == idempotency_key:
                return s
    sid = f"EXT-{uuid.uuid4().hex[:10].upper()}"
    reg = {
        "id": sid,
        "asunto": cuerpo.asunto,
        "descripcion": cuerpo.descripcion,
        "area": cuerpo.area,
        "solicitante": cuerpo.solicitante,
        "canal": cuerpo.canal,
        "estado": "Abierto",
        "fecha_creacion": datetime.now(timezone.utc).isoformat(),
        "_clave": idempotency_key,
    }
    ALMACEN[sid] = reg
    return reg


@app.post("/webhook/mensajeria")
async def webhook(evento: dict, authorization: str | None = Header(None)):
    """Punto de entrada del segundo sistema (etapa 4).

    Puede recibir el mismo evento más de una vez y en desorden.
    """
    _autorizar(authorization)
    await _simular_red("/webhook")
    return {"recibido": True, "evento_id": evento.get("evento_id"), "hora": datetime.now(timezone.utc).isoformat()}
