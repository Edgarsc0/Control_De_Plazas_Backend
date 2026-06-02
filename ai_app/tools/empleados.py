from django.forms.models import model_to_dict
from plantilla.models import EmpleadosCompletosSig, MovPos
from ._base import (
    tool_handler, 
    _aplicar_filtros_avanzados, 
    _build_interop_header, 
    _get_latest_mov_pos_ids,
    MAX_RESULTS_DEFAULT, 
    MAX_RESULTS_ABSOLUTE
)

@tool_handler(max_output_chars=6000)
def buscar_empleados_sig(
    filtros: list[dict], 
    limite: int = MAX_RESULTS_DEFAULT, 
    solo_activos_mov_pos: bool = False
) -> str:
    """
    Busca empleados en la nómina actual (EMPLEADOS_COMPLETOS_SIG).

    Campos principales para filtrar:
      Identificación: posicion, nombres, rfc, curp, id_empleado
      Estado: estado_nomina (A=Activo, V=Vacante, S=Suspendido, L=Licencia, P=Lic.Médica)
      Organización: unidad_administrativa, departamento, cd_ua, unidad_de_negocio
      Puesto: nivel, nombre_puesto_funcional, tipo_de_contratacion (BASE/CONFIANZA/EVENTUAL)
      Ubicación: entidad_federativa, descripcion_ubicacion, aduana, tipo_de_aduana
      Jerarquía: dependencia_directa, nj
      Militar/Civil: personal_militar_o_civil, rango

    Estructura de cada filtro: {"field": "campo", "op": "operador", "value": "valor"}
    Operadores: exact, icontains, startswith, gt, lt, gte, lte, in, isnull

    Ejemplos:
      Buscar por nombre: [{"field": "nombres", "op": "icontains", "value": "García"}]
      Activos nivel C1: [{"field": "estado_nomina", "op": "exact", "value": "A"}, {"field": "nivel", "op": "exact", "value": "C1"}]

    Uso combinado: El campo 'posicion' del resultado sirve como input para
    reporte_integral_plaza(), obtener_cadena_mando() e historial_movimientos_plaza().
    
    Args:
        filtros: Lista de filtros. Cada filtro es un diccionario con field, op (operador) y value.
        limite: Número máximo de registros a retornar (entre 1 y 50).
        solo_activos_mov_pos: Si es True, filtra sólo posiciones marcadas como activas ('A') en MOV_POS.
    """
    qs = EmpleadosCompletosSig.objects.all()

    if solo_activos_mov_pos:
        latest_ids = _get_latest_mov_pos_ids()
        active_positions = MovPos.objects.filter(
            id__in=latest_ids, estado_psn="A"
        ).values_list("no_pos_actual", flat=True)
        qs = qs.filter(posicion__in=active_positions)

    qs = _aplicar_filtros_avanzados(qs, filtros)
    total = qs.count()
    
    # Clamp limit
    limite = min(max(1, limite), MAX_RESULTS_ABSOLUTE)
    results = list(qs[:limite])

    if not results:
        return "No se encontraron empleados con los filtros proporcionados."

    # Extract positions and UAs for CoT/interop
    posiciones = [r.posicion for r in results if r.posicion]
    uas = list(set([r.unidad_administrativa for r in results if r.unidad_administrativa]))
    
    res = _build_interop_header(
        emoji="📋", 
        label="EMPLEADOS_COMPLETOS_SIG", 
        total=total, 
        showing=len(results),
        keys_found={"Posiciones": posiciones, "Unidades Administrativas": uas}
    )

    for r in results:
        d = model_to_dict(r)
        estado_label = {
            "A": "✅ Activo",
            "V": "⭕ Vacante",
            "S": "⚠️ Suspendido",
            "L": "🔵 Licencia",
            "P": "🟡 Licencia Médica",
        }.get((d.get("estado_nomina") or "").upper(), f"❓ {d.get('estado_nomina', 'Sin estado')}")

        res += f"👤 {d.get('nombres', 'SIN NOMBRE')} | Plaza: {d.get('posicion', 'N/A')}\n"
        res += f"   Estado: {estado_label} | Nivel: {d.get('nivel', 'N/A')} | NJ: {d.get('nj', 'N/A')}\n"
        res += f"   RFC: {d.get('rfc', 'N/A')} | CURP: {d.get('curp', 'N/A')}\n"
        res += f"   Puesto: {d.get('nombre_puesto_funcional', 'N/A')}\n"
        res += f"   UA: {d.get('unidad_administrativa', 'N/A')} | Departamento: {d.get('departamento', 'N/A')}\n"
        res += f"   Tipo contratación: {d.get('tipo_de_contratacion', 'N/A')} | SMB: {d.get('smb', 'N/A')}\n"
        res += f"   Jefe directo (posición): {d.get('dependencia_directa', 'N/A')}\n"
        res += f"   Ubicación: {d.get('descripcion_ubicacion', 'N/A')} ({d.get('entidad_federativa', 'N/A')})\n"
        if d.get("latitud") and d.get("longitud"):
            res += f"   Coordenadas: {d.get('latitud')}, {d.get('longitud')}\n"
        if d.get("sindicato"):
            res += f"   Sindicato: {d.get('sindicato')}\n"
        if d.get("personal_militar_o_civil"):
            res += f"   Tipo personal: {d.get('personal_militar_o_civil')} | Rango: {d.get('rango', 'N/A')}\n"
        res += "\n"

    return res.strip()
