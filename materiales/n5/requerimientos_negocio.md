# Etapa 5 — Requerimientos del negocio para el documento de decisión

Para cada uno de los tres requerimientos siguientes decida si la solución
óptima es **inteligencia artificial**, **automatización tradicional** o una
**secuencia combinada**. Sustente con criterios de volumen, estabilidad del
problema, costo, latencia, tolerancia al error y esfuerzo de mantenimiento.
Indique además bajo qué condición cambiaría su decisión.

No se evalúa que coincida con una respuesta esperada. Se evalúa el criterio
con que sustenta la decisión y si reconoce cuándo la IA es la peor opción.

---

## R-01 · Clasificación de solicitudes entrantes

El área recibe en promedio **3.000 solicitudes diarias** que deben quedar
clasificadas en **12 categorías** definidas en el catálogo de servicios. Las
categorías no han cambiado en los últimos tres años. Existe el histórico de
tickets ya clasificados a mano. La clasificación errada se corrige en menos
de un minuto y no genera efecto sobre el usuario final, solo sobre el
indicador de asignación.

Restricción: el proceso corre en lote cada hora. No requiere respuesta
inmediata.

---

## R-02 · Consulta de políticas internas en lenguaje natural

Los colaboradores preguntan cosas como *"¿con cuánta anticipación debo pedir
vacaciones?"* o *"¿cuánto me reconocen de hospedaje en Cartagena?"*. Hoy la
mesa de ayuda responde manualmente y consume cerca del **18 % del tiempo del
equipo**. Las políticas cambian una o dos veces al año y están en cinco
documentos PDF.

Restricción: una respuesta equivocada sobre montos o plazos genera reclamación
formal ante Talento Humano. El volumen es de unas 80 consultas diarias.

---

## R-03 · Recordatorio de tickets sin gestión

Cuando un ticket lleva **tres días hábiles sin ningún cambio de estado**, debe
enviarse un recordatorio al responsable asignado y, al quinto día, un
escalamiento al coordinador del área. El texto del mensaje es siempre el
mismo, con el código del ticket y el nombre del responsable.

Restricción: debe ejecutarse todos los días a las 8:00 a. m. y no puede
duplicar recordatorios si el proceso se ejecuta dos veces.
