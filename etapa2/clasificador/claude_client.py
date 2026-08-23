from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
CLAUDE_TIMEOUT = int(os.getenv("CLAUDE_TIMEOUT", "20"))
CLAUDE_RETRIES = int(os.getenv("CLAUDE_RETRIES", "3"))


@dataclass
class ResultadoClasificacion:
    categoria: str
    prioridad: str
    confianza: float
    modo: str = "clasificado"


def _prompt_clasificacion(texto: str) -> str:
    return f"""
Eres un clasificador de tickets de soporte interno para LA FORTUNA S.A.
Responde SOLO con JSON válido, sin texto adicional.

Reglas:
- categoria debe ser una de: aplicaciones, hardware, software, red, accesos, reportes, compras, vacaciones, viaticos, nomina, incidentes, otros
- prioridad debe ser una de: baja, media, alta, critica
- confianza debe ser un número entre 0 y 1
- Si el texto no aporta suficiente evidencia, usa "otros" y prioridad "media".

Ticket:
{texto}

JSON esperado:
{{"categoria": "...", "prioridad": "...", "confianza": 0.0}}
"""


def _parse_resultado(raw: str) -> ResultadoClasificacion:
    parsed = json.loads(raw)
    content = parsed["content"][0]["text"] if isinstance(parsed.get("content"), list) else parsed.get("content", "")
    text = content.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    payload = json.loads(text)
    categoria = str(payload.get("categoria", "otros")).lower()
    prioridad = str(payload.get("prioridad", "media")).lower()
    confianza = float(payload.get("confianza", 0.0))
    return ResultadoClasificacion(
        categoria=categoria if categoria else "otros",
        prioridad=prioridad if prioridad else "media",
        confianza=max(0.0, min(confianza, 1.0)),
        modo="clasificado",
    )


def clasificar(texto: str) -> ResultadoClasificacion:
    if not texto or not texto.strip():
        raise ValueError("El texto de la solicitud es obligatorio.")

    if not ANTHROPIC_API_KEY:
        return ResultadoClasificacion(categoria="otros", prioridad="media", confianza=0.0, modo="degradado")

    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 256,
        "system": "Responde solo con JSON válido para clasificar la solicitud de soporte interno.",
        "messages": [{"role": "user", "content": _prompt_clasificacion(texto)}],
    }

    for attempt in range(1, CLAUDE_RETRIES + 1):
        try:
            req = request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                },
                method="POST",
            )
            with request.urlopen(req, timeout=CLAUDE_TIMEOUT) as resp:
                raw = resp.read().decode("utf-8")
                return _parse_resultado(raw)
        except (error.HTTPError, error.URLError, TimeoutError, OSError, ValueError, KeyError):
            if attempt < CLAUDE_RETRIES:
                time.sleep(0.5 * attempt)
                continue
            return ResultadoClasificacion(categoria="otros", prioridad="media", confianza=0.0, modo="degradado")

    return ResultadoClasificacion(categoria="otros", prioridad="media", confianza=0.0, modo="degradado")
