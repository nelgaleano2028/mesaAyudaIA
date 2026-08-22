from __future__ import annotations

import json
import os
import socket
import time
from pathlib import Path
from typing import Any
from urllib import error, request

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

SERVICE_URL = os.getenv("SERVICIO_MOCK_URL", "http://localhost:8080")
SERVICE_TOKEN = os.getenv("SERVICIO_MOCK_TOKEN", "demo-token-prueba-2026")


class ServicioMockError(RuntimeError):
    """Error de negocio del servicio mock con mensaje amigable."""


class ServicioMockClient:
    def __init__(self, base_url: str | None = None, token: str | None = None, timeout: float = 5.0):
        self.base_url = (base_url or SERVICE_URL).rstrip("/")
        self.token = token or SERVICE_TOKEN
        self.timeout = timeout

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {"Accept": "application/json", "Authorization": f"Bearer {self.token}"}
        if extra:
            headers.update(extra)
        return headers

    def _request_json(self, method: str, path: str, payload: dict[str, Any] | None = None, extra_headers: dict[str, str] | None = None, retries: int = 3) -> Any:
        url = f"{self.base_url}{path}"
        body = None
        headers = self._headers(extra_headers)
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        attempt = 0
        while True:
            try:
                req = request.Request(url, data=body, headers=headers, method=method)
                with request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8")
                    if not raw:
                        return None
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError:
                        return raw
            except error.HTTPError as exc:
                if exc.code == 401:
                    raise ServicioMockError("Token ausente o inválido. Verifica el valor del token en .env.") from exc
                if exc.code == 429:
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    delay = float(retry_after) if retry_after and retry_after.isdigit() else 1.0
                    if attempt < retries:
                        print(f"Rate limit: esperando {delay}s antes de reintentar ({attempt + 1}/{retries})")
                        time.sleep(delay)
                        attempt += 1
                        continue
                    raise ServicioMockError("El servicio mock respondió 429 por exceso de solicitudes. Reintento agotado.") from exc
                if exc.code == 500:
                    if attempt < retries:
                        delay = 0.5 * (attempt + 1)
                        print(f"500 del proveedor: reintento en {delay}s ({attempt + 1}/{retries})")
                        time.sleep(delay)
                        attempt += 1
                        continue
                    raise ServicioMockError("El servicio mock falló con error 500 y no pudo completarse la operación.") from exc
                raise ServicioMockError(f"Respuesta HTTP inesperada: {exc.code} - {exc.reason}") from exc
            except (TimeoutError, socket.timeout, OSError, error.URLError) as exc:
                if attempt < retries:
                    delay = 0.5 * (attempt + 1)
                    print(f"Timeout/infraestructura: reintento en {delay}s ({attempt + 1}/{retries})")
                    time.sleep(delay)
                    attempt += 1
                    continue
                raise ServicioMockError("No se pudo contactar al servicio mock dentro del tiempo máximo permitido.") from exc

    def listar_solicitudes(self, area: str | None = None, estado: str | None = None, limite: int = 50) -> list[dict[str, Any]]:
        params = []
        if area:
            params.append(f"area={area}")
        if estado:
            params.append(f"estado={estado}")
        params.append(f"limite={limite}")
        query = "&".join(params)
        return self._request_json("GET", f"/solicitudes?{query}")

    def crear_solicitud(self, payload: dict[str, Any], idempotency_key: str | None = None) -> dict[str, Any]:
        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return self._request_json("POST", "/solicitudes", payload=payload, extra_headers=headers)


if __name__ == "__main__":
    client = ServicioMockClient()
    try:
        print("Listado de solicitudes:")
        print(json.dumps(client.listar_solicitudes(limite=5), indent=2, ensure_ascii=False))
        payload = {
            "asunto": "Solicitud de acceso a nuevas credenciales",
            "descripcion": "Necesito acceso temporal al sistema de inventario para pruebas.",
            "area": "Aplicaciones",
            "solicitante": "usuario.demo@lafortuna.com.co",
            "canal": "api",
        }
        print("\nCreación de solicitud:")
        print(json.dumps(client.crear_solicitud(payload, idempotency_key="demo-key-001"), indent=2, ensure_ascii=False))
    except ServicioMockError as exc:
        print(f"ERROR: {exc}")
