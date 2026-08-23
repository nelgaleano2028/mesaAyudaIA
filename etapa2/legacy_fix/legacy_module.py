from datetime import date, datetime

FORMATOS_FECHA = ("%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y")

MESES_ES = {
    "ene": "Jan", "feb": "Feb", "mar": "Mar", "abr": "Apr",
    "may": "May", "jun": "Jun", "jul": "Jul", "ago": "Aug",
    "sep": "Sep", "oct": "Oct", "nov": "Nov", "dic": "Dec",
}


def parsear_fecha(valor):
    """Convierte una fecha en cualquiera de los tres formatos del histórico."""
    if valor is None:
        return None
    valor = str(valor).strip()
    if not valor:
        return None
    partes = valor.split("-")
    if len(partes) == 3 and partes[1].lower() in MESES_ES:
        valor = f"{partes[0]}-{MESES_ES[partes[1].lower()]}-{partes[2]}"
    for f in FORMATOS_FECHA:
        try:
            return datetime.strptime(valor, f).date()
        except ValueError:
            continue
    return None


def filtrar_por_periodo(tickets, inicio, fin):
    """Devuelve los tickets creados dentro del periodo indicado.

    `inicio` y `fin` son objetos date e incluyen ambos extremos del periodo,
    según lo definido por el área de Calidad.
    """
    seleccionados = []
    for t in tickets:
        fc = parsear_fecha(t.get("fecha_creacion"))
        if fc is None:
            continue
        if inicio <= fc <= fin:
            seleccionados.append(t)
    return seleccionados


def resumir_por_area(tickets, acumulador=None):
    """Cuenta tickets por área sin reutilizar estado entre llamadas."""
    if acumulador is None:
        acumulador = {}
    for ticket in tickets:
        area = (ticket.get("area") or "Sin area").strip()
        acumulador[area] = acumulador.get(area, 0) + 1
    return acumulador


def contar_reaperturas(tickets):
    """Cuenta tickets reabiertos ignorando diferencias de mayúsculas."""
    return sum(
        str(ticket.get("estado") or "").strip().lower() == "reabierto"
        for ticket in tickets
    )


def tasa_reapertura(tickets):
    if not tickets:
        return 0.0
    return round(contar_reaperturas(tickets) / len(tickets) * 100, 2)


def dias_atencion(ticket):
    fecha_creacion = parsear_fecha(ticket.get("fecha_creacion"))
    fecha_cierre = parsear_fecha(ticket.get("fecha_cierre"))
    if fecha_creacion is None or fecha_cierre is None:
        return None
    return (fecha_cierre - fecha_creacion).days


def informe_mensual(tickets, anio, mes):
    inicio = date(anio, mes, 1)
    siguiente_mes = date(anio + (mes == 12), 1 if mes == 12 else mes + 1, 1)
    fin = date.fromordinal(siguiente_mes.toordinal() - 1)
    del_mes = filtrar_por_periodo(tickets, inicio, fin)
    return {
        "periodo": f"{anio}-{mes:02d}",
        "total": len(del_mes),
        "por_area": resumir_por_area(del_mes),
        "tasa_reapertura": tasa_reapertura(del_mes),
    }
