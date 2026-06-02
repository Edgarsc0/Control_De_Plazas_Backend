from django.forms.models import model_to_dict
from plantilla.models import BajasSig
from ._base import (
    tool_handler, 
    _aplicar_filtros_avanzados, 
    _build_interop_header, 
    MAX_RESULTS_DEFAULT, 
    MAX_RESULTS_ABSOLUTE
)

@tool_handler(max_output_chars=6000)
def buscar_bajas_sig(
    filtros: list[dict],
    limite: int = MAX_RESULTS_DEFAULT,
    desde_fecha: str = None,
    hasta_fecha: str = None
) -> str:
    """
    Busca registros de desincorporación de personal (bajas) en la tabla BAJAS_SIG.

    Es la fuente principal para conocer cuándo quedó vacante una plaza y por qué motivo.

    Campos principales para filtrar:
      Identificación: posicion (plaza vacante), nombre_completo, rfc, curp, no_empleado
      Motivo: motivo_descr, accion_descr, motivo, accion
      Fecha: fecha_efectiva (fecha de baja = inicio de vacancia), fecha_aplicacion, fecha_ingreso
      Estatus trámite: humanos_status (APROBADO/PENDIENTE), nomina_status
      Organización: unidad_admon (UA al momento de baja), departamento
      Puesto: nivel_tabular, plan_salarial, grado, smb

    Estructura de cada filtro: {"field": "campo", "op": "operador", "value": "valor"}
    Operadores: exact, icontains, startswith, gt, lt, gte, lte, in, isnull

    Uso combinado: El campo 'posicion' sirve para buscar la plaza en
    reporte_integral_plaza() o buscar_mov_pos(no_pos_actual=posicion).
    
    Args:
        filtros: Lista de filtros (field, op, value).
        limite: Número máximo de registros a retornar (entre 1 y 50).
        desde_fecha: Filtro rápido de fecha_efectiva mayor o igual a (formato: YYYY-MM-DD).
        hasta_fecha: Filtro rápido de fecha_efectiva menor o igual a (formato: YYYY-MM-DD).
    """
    qs = BajasSig.objects.all()

    if desde_fecha:
        qs = qs.filter(fecha_efectiva__gte=desde_fecha.strip())
    if hasta_fecha:
        qs = qs.filter(fecha_efectiva__lte=hasta_fecha.strip())

    qs = _aplicar_filtros_avanzados(qs, filtros)
    total = qs.count()
    limite = min(max(1, limite), MAX_RESULTS_ABSOLUTE)
    results = list(qs.order_by("-fecha_efectiva")[:limite])

    if not results:
        return "No se encontraron registros de bajas con los filtros proporcionados."

    posiciones = [r.posicion for r in results if r.posicion]
    uas = list(set([r.unidad_admon for r in results if r.unidad_admon]))

    res = _build_interop_header(
        emoji="📉",
        label="BAJAS_SIG",
        total=total,
        showing=len(results),
        keys_found={"Posiciones": posiciones, "Unidades Administrativas": uas}
    )

    for r in results:
        d = model_to_dict(r)
        res += f"🔻 {d.get('nombre_completo', 'SIN NOMBRE')} | Plaza: {d.get('posicion', 'N/A')}\n"
        res += f"   RFC: {d.get('rfc', 'N/A')} | CURP: {d.get('curp', 'N/A')}\n"
        res += f"   No. Empleado: {d.get('no_empleado', 'N/A')}\n"
        res += f"   📅 Fecha efectiva de baja (vacante desde): {d.get('fecha_efectiva', 'N/A')}\n"
        res += f"   Fecha aplicación nómina: {d.get('fecha_aplicacion', 'N/A')}\n"
        res += f"   Acción: {d.get('accion_descr', 'N/A')} (Cod: {d.get('accion', 'N/A')})\n"
        res += f"   Motivo: {d.get('motivo_descr', 'N/A')} (Cod: {d.get('motivo', 'N/A')})\n"
        res += f"   Status RRHH: {d.get('humanos_status', 'N/A')} | Status Nómina: {d.get('nomina_status', 'N/A')}\n"
        res += f"   UA al momento de baja: {d.get('unidad_admon', 'N/A')}\n"
        res += f"   Departamento: {d.get('departamento', 'N/A')}\n"
        res += f"   Plan Sal: {d.get('plan_salarial', 'N/A')} | Grado: {d.get('grado', 'N/A')} | Nivel: {d.get('nivel_tabular', 'N/A')}\n"
        res += f"   SMB: {d.get('smb', 'N/A')}\n"
        res += f"   Fecha ingreso: {d.get('fecha_ingreso', 'N/A')} | Género: {d.get('genero', 'N/A')}\n"
        res += "\n"

    return res.strip()
