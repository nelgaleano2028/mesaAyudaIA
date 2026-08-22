# Servicio mock

```bash
pip install -r requirements.txt
uvicorn app:app --port 8080
```

Token de prueba: `demo-token-prueba-2026`
Cabecera: `Authorization: Bearer demo-token-prueba-2026`

Documentación interactiva: http://localhost:8080/docs

**El servicio falla a propósito.** Latencia de 0,1 a 2,5 s, 12 % de errores 500
y 5 % de respuestas 429 con cabecera `Retry-After`. No lo modifique.
