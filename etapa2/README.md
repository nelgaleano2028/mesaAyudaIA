# Etapa 2 - Autonomía e integración

## Componentes

- `api/main.py`: API FastAPI con SQLite, validación, errores uniformes y filtros.
- `clasificador/claude_client.py`: cliente HTTP desacoplado para Anthropic con timeout, reintentos y fallback.
- `legacy_fix/legacy_module.py`: correcciones S1, S2 y S3 del módulo heredado.

## Configuración

Copia `.env.example` a `.env` y configura `ANTHROPIC_API_KEY` si deseas usar Claude.
Sin clave, la API funciona en modo degradado y guarda `estado="pendiente_revision"`, `categoria="otros"` y `prioridad="media"`.

## Ejecución

```powershell
Set-Location "E:\Proyect\Acertemos\Mesa Ayuda IA"
.\.venv\Scripts\Activate.ps1
uvicorn etapa2.api.main:app --reload --port 8000
```

## Endpoints

```powershell
$body = @{ asunto = "No puedo ingresar al sistema"; descripcion = "Necesito ayuda con acceso"; area = "Tecnologia"; canal = "web"; solicitante = "usuario@lafortuna.com.co" } | ConvertTo-Json -Compress
Invoke-RestMethod http://localhost:8000/solicitudes -Method Post -ContentType "application/json" -Body $body
Invoke-RestMethod http://localhost:8000/solicitudes
Invoke-RestMethod http://localhost:8000/solicitudes/1
Invoke-RestMethod "http://localhost:8000/solicitudes?area=Tecnologia&limit=20"
```

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest etapa1/tests etapa2/tests -q
```

Las pruebas cubren los tres defectos legacy y el comportamiento degradado del clasificador.
