from django.db import connections
from ._base import tool_handler, MAX_RESULTS_DEFAULT, MAX_RESULTS_ABSOLUTE

@tool_handler(max_output_chars=6000)
def buscar_asuntos_scg(
    query: str = None,
    tipo_documento: str = None,
    prioridad: str = None,
    limite: int = 10
) -> str:
    """
    Busca asuntos/oficios en el Sistema de Control de Gestión (SCG) de la ANAM.

    Permite dar seguimiento a correspondencia, solicitudes u oficios oficiales turnados.

    Args:
        query: Término de búsqueda en la descripción del asunto, tema, folio u oficio (ej: "solicitud plaza").
        tipo_documento: Filtrar por tipo de documento (ej: "OFICIO", "VOLANTE").
        prioridad: Filtrar por prioridad (ej: "ALTA", "MEDIA", "BAJA").
        limite: Límite de resultados a retornar (entre 1 y 50).
    """
    limite = min(max(1, limite), MAX_RESULTS_ABSOLUTE)

    sql = """
        SELECT idAsunto, noOficio, folio, remitenteNombre, descripcionAsunto, 
               Tema, prioridad, statusAsunto, unidadAdministrativa, fechaRecepcion, tipoDocumento
        FROM scg_tbl_asunto
        WHERE activo = 1
    """
    params = []

    if query:
        query_clean = f"%{query.strip()}%"
        sql += " AND (descripcionAsunto LIKE %s OR Tema LIKE %s OR noOficio LIKE %s OR folio LIKE %s)"
        params.extend([query_clean, query_clean, query_clean, query_clean])

    if tipo_documento:
        sql += " AND tipoDocumento = %s"
        params.append(tipo_documento.strip())

    if prioridad:
        sql += " AND prioridad = %s"
        params.append(prioridad.strip())

    sql += " ORDER BY idAsunto DESC LIMIT %s"
    params.append(limite)

    # Conectar a la base de datos de control_gestion
    with connections['control_gestion'].cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()

    if not rows:
        return "No se encontraron asuntos en el Sistema de Control de Gestión (SCG) con los criterios especificados."

    res = f"📁 ASUNTOS EN CONTROL DE GESTIÓN (SCG) — Mostrando {len(rows)} registros:\n"
    res += "════════════════════════════════════════════════════════\n\n"

    for r in rows:
        id_asunto, no_oficio, folio, remitente, desc, tema, prio, status, ua, fecha_rec, tipo_doc = r
        
        fecha_str = fecha_rec.strftime("%Y-%m-%d") if fecha_rec else "N/A"
        
        res += f"📄 Asunto ID: {id_asunto} | Folio: {folio or 'N/A'} | Oficio: {no_oficio or 'N/A'}\n"
        res += f"   Tipo: {tipo_doc or 'N/A'} | Recibido: {fecha_str} | Prioridad: {prio or 'N/A'}\n"
        res += f"   Remitente: {remitente or 'N/A'}\n"
        res += f"   Estatus: {status or 'N/A'} | UA: {ua or 'N/A'}\n"
        res += f"   Tema: {tema or 'N/A'}\n"
        res += f"   Descripción: {desc or 'Sin descripción'}\n\n"

    return res.strip()
