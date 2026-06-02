from datetime import datetime, date
from django.forms.models import model_to_dict
from plantilla.models import MovPos
from ._base import (
    tool_handler, 
    _aplicar_filtros_avanzados, 
    _build_interop_header, 
    _get_latest_mov_pos_ids,
    MAX_RESULTS_DEFAULT, 
    MAX_RESULTS_ABSOLUTE
)

def _parse_date(date_val):
    if not date_val:
        return None
    if isinstance(date_val, date):
        return date_val
    if isinstance(date_val, datetime):
        return date_val.date()
    if isinstance(date_val, str):
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y"):
            try:
                return datetime.strptime(date_val, fmt).date()
            except ValueError:
                continue
    return None

@tool_handler(max_output_chars=6000)
def buscar_mov_pos(
    filtros: list[dict],
    limite: int = MAX_RESULTS_DEFAULT,
    solo_ultimo_por_plaza: bool = True
) -> str:
    """
    Busca en MOV_POS (Movimientos de Posición), el registro administrativo de plazas.

    Esta tabla contiene el historial y estado administrativo de cada plaza (A=Activa, I=Inactiva).
    Permite conocer si la plaza existe y en qué UA está asignada presupuestalmente.

    Campos principales para filtrar:
      Identificación: no_pos_actual, nombre_puesto, cd_puesto, formal_desc
      Estado: estado_psn (A=Activa, I=Inactiva), f_efva, fecha_captura, estado_ptal
      Organización: cd_un, unidad_de_negocio, unidad_adva, cd_departamento
      Puesto: nvl_direc, plan_sal, grado, esc
      Jerarquía: depnd_drt, depnd_indrt
      Partida/Pago: partida_ptal, gp_pago, presupuesto

    Estructura de cada filtro: {"field": "campo", "op": "operador", "value": "valor"}
    Operadores: exact, icontains, startswith, gt, lt, gte, lte, in, isnull

    Uso combinado: Con el 'no_pos_actual' obtenido aquí, se puede llamar a
    reporte_integral_plaza() o buscar_empleados_sig(posicion=no_pos_actual).
    
    Args:
        filtros: Lista de filtros (field, op, value).
        limite: Número máximo de registros a retornar (entre 1 y 50).
        solo_ultimo_por_plaza: Si es True, retorna únicamente el estado más reciente de cada plaza.
    """
    qs = MovPos.objects.all()
    qs = _aplicar_filtros_avanzados(qs, filtros)

    if solo_ultimo_por_plaza:
        latest_ids = _get_latest_mov_pos_ids()
        qs = qs.filter(id__in=latest_ids)

    total = qs.count()
    limite = min(max(1, limite), MAX_RESULTS_ABSOLUTE)
    results = list(qs.order_by("-f_efva", "-id")[:limite])

    if not results:
        return "No se encontraron movimientos de posición con los filtros proporcionados."

    posiciones = [r.no_pos_actual for r in results if r.no_pos_actual]
    uas = list(set([r.unidad_adva for r in results if r.unidad_adva]))

    label = "MOV_POS (Último estado)" if solo_ultimo_por_plaza else "MOV_POS (Historial filtrado)"
    res = _build_interop_header(
        emoji="📊",
        label=label,
        total=total,
        showing=len(results),
        keys_found={"Posiciones": posiciones, "Unidades Administrativas": uas}
    )

    for r in results:
        d = model_to_dict(r)
        estado_label = "✅ ACTIVA" if d.get("estado_psn") == "A" else "❌ INACTIVA"

        res += f"🏷️  Plaza: {d.get('no_pos_actual', 'N/A')} — {estado_label}\n"
        res += f"   Puesto: {d.get('nombre_puesto', 'N/A')} (Cod: {d.get('cd_puesto', 'N/A')})\n"
        res += f"   Fecha efectiva: {d.get('f_efva', 'N/A')} | Motivo: {d.get('motivo', 'N/A')} (Cod: {d.get('cd_motivo', 'N/A')})\n"
        res += f"   Unidad de Negocio: [{d.get('cd_un', 'N/A')}] {d.get('unidad_de_negocio', 'N/A')}\n"
        res += f"   Unidad Administrativa: {d.get('unidad_adva', 'N/A')} | Depto: {d.get('cd_departamento', 'N/A')}\n"
        res += f"   Nivel directivo: {d.get('nvl_direc', 'N/A')} | Plan Sal: {d.get('plan_sal', 'N/A')} | Grado: {d.get('grado', 'N/A')} | Escala: {d.get('esc', 'N/A')}\n"
        res += f"   Jefe directo (plaza): {d.get('depnd_drt', 'N/A')} | Jefe indirecto: {d.get('depnd_indrt', 'N/A')}\n"
        res += f"   Partida ptal: {d.get('partida_ptal', 'N/A')} | Gp Pago: {d.get('gp_pago', 'N/A')}\n"
        res += f"   Horas/semana: {d.get('hr_estd_semn', 'N/A')} | Grupo trabajo: {d.get('gp_trabajo', 'N/A')}\n"
        res += f"   Última actualización: {d.get('fh_ult_actz', 'N/A')} | Por: {d.get('por', 'N/A')}\n"
        res += "\n"

    return res.strip()

@tool_handler(max_output_chars=6000)
def historial_movimientos_plaza(posicion: str) -> str:
    """
    Retorna el historial completo de movimientos de una plaza en MOV_POS.

    Útil para rastrear la evolución administrativa de una plaza:
    - ¿Cuándo fue creada o modificada?
    - ¿Ha sido transferida entre unidades administrativas?
    - ¿Cuántos días transcurrieron entre cada movimiento administrativo?

    Args:
        posicion: Número de plaza en SAP (ej: "50001234").
    """
    posicion = posicion.strip()
    if not posicion:
        return "❌ Error: El número de plaza no puede estar vacío."

    movimientos = list(
        MovPos.objects.filter(no_pos_actual=posicion).order_by("-f_efva", "-id")
    )

    if not movimientos:
        return f"No se encontraron movimientos en MOV_POS para la plaza '{posicion}'."

    res = f"📜 HISTORIAL MOV_POS — Plaza {posicion} ({len(movimientos)} movimientos)\n"
    res += "════════════════════════════════════\n\n"

    for i, mov in enumerate(movimientos):
        d = model_to_dict(mov)
        estado = "✅ ACTIVA" if d.get("estado_psn") == "A" else "❌ INACTIVA"
        
        res += f"  [{i + 1}] Estatus: {estado} | Fecha Efectiva: {d.get('f_efva', 'N/A')}\n"
        res += f"      Motivo: {d.get('motivo', 'N/A')} (Cd: {d.get('cd_motivo', 'N/A')})\n"
        res += f"      UN: {d.get('unidad_de_negocio', 'N/A')} | UA: {d.get('unidad_adva', 'N/A')}\n"
        res += f"      Puesto: {d.get('nombre_puesto', 'N/A')} | Grado: {d.get('grado', 'N/A')}\n"
        res += f"      Captura: {d.get('fecha_captura', 'N/A')} | Modificado por: {d.get('por', 'N/A')}\n"

        # Calcular días entre movimientos
        current_date = _parse_date(d.get("f_efva"))
        if i + 1 < len(movimientos):
            prev_mov = movimientos[i + 1]
            prev_date = _parse_date(prev_mov.f_efva)
            if current_date and prev_date:
                diff = (current_date - prev_date).days
                res += f"      ⏱️ Tiempo transcurrido desde movimiento anterior: {diff} días\n"
        
        res += "\n"

    return res.strip()
