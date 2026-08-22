# Etapa 1 — Fundamentos del proyecto

## 1. Instalación

```bash
cd "E:\Proyect\Acertemos\Mesa Ayuda IA"
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Cómo ejecutar cada componente

### 2.1. Limpieza del histórico

```bash
python etapa1/limpieza_tickets.py --input materiales/datos/tickets_historicos.csv --output-dir etapa1/salida
```

Genera:
- `etapa1/salida/tickets_limpios.csv`
- `etapa1/salida/tickets_invalidos.csv`
- `etapa1/salida/resumen_area_prioridad.csv`
- `etapa1/salida/log_limpieza.txt`

### 2.2. Cliente del servicio mock

Primero levanta el servicio mock:

```bash
cd materiales/servicio_mock
uvicorn app:app --port 8080
```

Luego:

```bash
python etapa1/cliente_servicio_mock.py
```

### 2.3. Consultas SQL

Se deja el archivo `etapa1/consultas.sql` con las tres consultas requeridas. Para probarlo en SQLite:

```bash
sqlite3 data/mesa_ayuda.db < etapa1/esquema_sqlite.sql
sqlite3 data/mesa_ayuda.db < etapa1/consultas.sql
```

### 2.4. Pruebas unitarias

```bash
pytest etapa1/tests/test_limpieza.py -q
```

## 3. Qué hace cada componente

- `limpieza_tickets.py`: normaliza fechas, categorías y prioridades; detecta duplicados lógicos y registros inválidos; exporta la versión limpia y el resumen por área/prioridad.
- `cliente_servicio_mock.py`: consume `GET /solicitudes` y `POST /solicitudes`, maneja timeout, 500, 429 con `Retry-After` y 401 con mensajes comprensibles.
- `esquema_sqlite.sql`: adaptación del esquema original para SQLite, preservando la estructura del modelo relacional.
- `consultas.sql`: agregación topológica por área, join de tres tablas y consulta de tickets reabiertos.
- `tests/test_limpieza.py`: valida el parser de fechas, la normalización de categorías y la detección de duplicados.

## 4. Suposiciones y criterios

- Criterio de duplicado: se considera duplicado un ticket cuando coinciden solicitante, asunto, descripción y fecha de creación normalizada, incluso si el `id` cambia. Esto cubre casos repetidos con identificadores distintos.
- Catálogo canónico de categorías: se normaliza a slugs en minúsculas sin espacios ni tildes, por ejemplo `hardware`, `software`, `gestion_de_accesos`, `nomina`, `vacaciones`.
- Reintentos: se reintenta para timeout, 500 y 429, con retroceso simple y límite de tres intentos; se bloquea al agotarse para no repetir indefinidamente.

## 5. Qué dejé fuera

- No se implementó un proceso de ingestión de documentos PDF ni clasificador IA porque este prompt corresponde solamente a la etapa de fundamentos y no al RAG ni a la clasificación automática.
- Las consultas SQL están pensadas como script de análisis y no como servicio web, porque el alcance de la etapa 1 no incluye la API REST propia del proyecto.
- El servicio mock se usa desde un cliente modular, pero no se lo modifica ni se altera su comportamiento, como exige el enunciado.

## 6. Observaciones del dataset real

Se encontraron fechas en estos formatos reales: ISO `YYYY-MM-DD`, `DD/MM/YYYY`, `DD-Mon-YYYY` y `DD-Mon-YYYY` con meses en español (`Ene`, `Abr`, `Ago`, etc.). La lógica de parseo registra en el log cualquier valor que no pueda transformarse a `YYYY-MM-DD` sin ambigüedad.
