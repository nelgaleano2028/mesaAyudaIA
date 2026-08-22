-- Adaptación del esquema MySQL/MariaDB al motor SQLite de la prueba.
-- Cambios principales: AUTO_INCREMENT -> INTEGER PRIMARY KEY AUTOINCREMENT,
-- DATETIME -> TEXT (guardamos ISO 8601), y se eliminan restricciones de tipo
-- propietario que SQLite valida de forma más flexible que MySQL.

DROP TABLE IF EXISTS historial_estado;
DROP TABLE IF EXISTS adjuntos;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS areas;

CREATE TABLE areas (
  id_area        INTEGER PRIMARY KEY,
  nombre         TEXT NOT NULL,
  sede           TEXT NOT NULL,
  responsable    TEXT
);

CREATE TABLE usuarios (
  id_usuario     INTEGER PRIMARY KEY,
  correo         TEXT NOT NULL UNIQUE,
  nombre         TEXT NOT NULL,
  id_area        INTEGER NOT NULL,
  activo         TEXT NOT NULL DEFAULT 'S',
  FOREIGN KEY (id_area) REFERENCES areas(id_area)
);

CREATE TABLE tickets (
  id_ticket        INTEGER PRIMARY KEY,
  codigo           TEXT NOT NULL UNIQUE,
  id_usuario       INTEGER NOT NULL,
  id_area          INTEGER NOT NULL,
  categoria        TEXT,
  prioridad        TEXT,
  canal            TEXT,
  asunto           TEXT,
  descripcion      TEXT,
  estado           TEXT NOT NULL,
  fecha_creacion   TEXT NOT NULL,
  fecha_cierre     TEXT,
  reaperturas      INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
  FOREIGN KEY (id_area) REFERENCES areas(id_area)
);

CREATE TABLE adjuntos (
  id_adjunto     INTEGER PRIMARY KEY,
  id_ticket      INTEGER NOT NULL,
  nombre_archivo TEXT NOT NULL,
  tamano_kb      INTEGER,
  FOREIGN KEY (id_ticket) REFERENCES tickets(id_ticket)
);

CREATE TABLE historial_estado (
  id_historial   INTEGER PRIMARY KEY,
  id_ticket      INTEGER NOT NULL,
  estado_anterior TEXT,
  estado_nuevo    TEXT NOT NULL,
  fecha_cambio    TEXT NOT NULL,
  usuario_cambio  TEXT,
  FOREIGN KEY (id_ticket) REFERENCES tickets(id_ticket)
);

-- Se mantienen los mismos datos de ejemplo del esquema original, pero el motor
-- acepta TEXT para fechas y no requiere la sintaxis específica de MySQL.
