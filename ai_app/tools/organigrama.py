from django.db import connection
from ._base import tool_handler, MAX_RESULTS_DEFAULT, MAX_RESULTS_ABSOLUTE

@tool_handler(max_output_chars=6000)
def buscar_organigrama(query: str = None, limite: int = 15) -> str:
    """
    Busca dependencias, áreas o puestos en la estructura del organigrama institucional (ORGANIGRAMA_ANAM).

    Args:
        query: Término de búsqueda (ej: "dirección", "subdirección", "SOIA"). Si es None, muestra el inicio del catálogo.
        limite: Límite de resultados a retornar (entre 1 y 50).
    """
    limite = min(max(1, limite), MAX_RESULTS_ABSOLUTE)
    
    with connection.cursor() as cursor:
        if not query:
            sql = """
                SELECT departamento, descripcion_larga, unidad_negocio, nivel_direccion 
                FROM ORGANIGRAMA_ANAM
                LIMIT %s
            """
            cursor.execute(sql, [limite])
        else:
            sql = """
                SELECT departamento, descripcion_larga, unidad_negocio, nivel_direccion 
                FROM ORGANIGRAMA_ANAM 
                WHERE descripcion_larga LIKE %s OR departamento LIKE %s
                LIMIT %s
            """
            like_val = f"%{query.strip()}%"
            cursor.execute(sql, [like_val, like_val, limite])
            
        rows = cursor.fetchall()

    if not rows:
        return f"No se encontraron áreas o puestos en el organigrama que coincidan con '{query}'."

    res = f"🗂️  ORGANIGRAMA INSTITUCIONAL ANAM"
    if query:
        res += f" (Búsqueda: '{query}')"
    res += f" — Mostrando {len(rows)} resultados:\n"
    res += "════════════════════════════════════════════════════════\n\n"

    for r in rows:
        depto, desc_larga, un_negocio, nvl_dir = r
        res += f"🏢 Área/Depto: {depto or 'N/A'}\n"
        res += f"   Descripción: {desc_larga or 'N/A'}\n"
        res += f"   Unidad de Negocio: {un_negocio or 'N/A'} | Nivel Dirección: {nvl_dir or 'N/A'}\n\n"

    return res.strip()
