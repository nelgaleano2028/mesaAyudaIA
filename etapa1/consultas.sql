-- 1) Agregación por área: cuenta tickets por área para identificar puntos críticos.
SELECT a.nombre AS area, COUNT(t.id_ticket) AS cantidad_tickets
FROM tickets t
JOIN areas a ON a.id_area = t.id_area
GROUP BY a.nombre
ORDER BY cantidad_tickets DESC;

-- 2) Join de tres tablas: muestra el historial más reciente de cada ticket con usuario y área.
SELECT t.codigo,
       u.nombre AS usuario,
       a.nombre AS area,
       h.estado_nuevo,
       h.fecha_cambio
FROM tickets t
JOIN usuarios u ON u.id_usuario = t.id_usuario
JOIN areas a ON a.id_area = t.id_area
LEFT JOIN historial_estado h ON h.id_ticket = t.id_ticket
ORDER BY t.codigo, h.fecha_cambio DESC;

-- 3) Tickets reabiertos: identifica tickets que han vuelto a abrirse según el historial.
SELECT t.codigo,
       t.asunto,
       t.reaperturas,
       MAX(h.fecha_cambio) AS ultima_reapertura
FROM tickets t
JOIN historial_estado h ON h.id_ticket = t.id_ticket
WHERE h.estado_nuevo = 'Reabierto'
   OR h.estado_anterior = 'Cerrado'
GROUP BY t.codigo, t.asunto, t.reaperturas
HAVING t.reaperturas > 0
ORDER BY t.reaperturas DESC, ultima_reapertura DESC;
