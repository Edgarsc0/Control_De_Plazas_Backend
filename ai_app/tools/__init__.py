# ai_app/tools/__init__.py

from .empleados import buscar_empleados_sig
from .mov_pos import buscar_mov_pos, historial_movimientos_plaza
from .bajas import buscar_bajas_sig
from .estadisticas import get_estadisticas_globales
from .plaza_integral import reporte_integral_plaza
from .unidad_admin import analizar_unidad_administrativa
from .jerarquia import obtener_cadena_mando
from .vacantes import buscar_vacantes
from .presupuesto import consultar_presupuesto_plaza, calcular_costo_vacantes
from .zafiro import estado_sincronizacion_zafiro
from .organigrama import buscar_organigrama
from .comparador import comparar_plazas
from .resumen_ejecutivo import generar_resumen_ejecutivo
from .control_gestion import buscar_asuntos_scg

TOOL_REGISTRY = [
    buscar_empleados_sig,
    buscar_mov_pos,
    historial_movimientos_plaza,
    buscar_bajas_sig,
    get_estadisticas_globales,
    reporte_integral_plaza,
    analizar_unidad_administrativa,
    obtener_cadena_mando,
    buscar_vacantes,
    consultar_presupuesto_plaza,
    calcular_costo_vacantes,
    estado_sincronizacion_zafiro,
    buscar_organigrama,
    comparar_plazas,
    generar_resumen_ejecutivo,
    buscar_asuntos_scg,
]
