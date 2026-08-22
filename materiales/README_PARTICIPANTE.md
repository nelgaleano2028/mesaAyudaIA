# Materiales de la Prueba Técnica de Nivelación — Perfiles IA
LA FORTUNA S.A. · Coordinación de Aplicaciones

Todos los datos de esta carpeta son **sintéticos**. No corresponden a
información real de la compañía ni de sus colaboradores. Aun así, está
prohibido usar datos reales de la compañía en herramientas externas durante
la prueba.

## Contenido

| Ruta | Qué es | Se usa en |
|---|---|---|
| `datos/tickets_historicos.csv` | 2.000 registros con ruido real: tres formatos de fecha, categorías inconsistentes, campos vacíos y duplicados. | Etapas 1 y 5 |
| `datos/esquema.sql` | Modelo relacional con datos de prueba (áreas, usuarios, tickets, adjuntos, historial). | Etapa 1 |
| `politicas/` | Cinco políticas internas en PDF con secciones numeradas. | Etapa 3 |
| `legacy/legacy_module.py` | Módulo heredado con defectos de lógica. Los tres síntomas están descritos al inicio del archivo. | Etapa 2 |
| `servicio_mock/` | API REST externa simulada, con su especificación OpenAPI. Falla a propósito. | Etapas 1, 2 y 4 |
| `revision/pr_para_revision.diff` | Cambio de código para revisar. | Etapa 5 y sustentación |
| `n5/requerimientos_negocio.md` | Los tres requerimientos del documento de decisión. | Etapa 5 |
| `n5/plantilla_conjunto_referencia.csv` | Plantilla del conjunto de referencia etiquetado. | Etapa 5 |

## Antes de empezar

1. Lea el **Anexo A — Enunciado de la prueba técnica**. Ahí están las etapas,
   los entregables y las reglas.
2. Declare su nivel objetivo en el formulario de inicio.
3. Cree su repositorio y haga commits a lo largo de los cinco días. El
   historial es parte de lo que se evalúa.
4. Cuando entregue, incluya la **declaración de uso de asistentes de IA**.

## Advertencia sobre las políticas

El corpus de políticas **no cubre todos los temas** que pueden preguntarse.
Eso es intencional: su solución debe reconocer cuándo no tiene evidencia y
decirlo, en lugar de responder de todos modos.
