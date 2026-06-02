from django.db.models import Count, Q
from plantilla.models import EmpleadosCompletosSig, BajasSig, MovPos
from presupuesto.models import CatalogoPlazas
from ._base import tool_handler, _get_latest_mov_pos_ids

@tool_handler(max_output_chars=6000)
def generar_resumen_ejecutivo(unidad_administrativa: str = None) -> str:
    """
    Genera un resumen ejecutivo y estratégico de la plantilla para reporteo directivo.

    Presenta KPIs clave, indicadores presupuestarios estimados, distribución de personal
    y alertas prioritarias (como alta vacancia o desfasamientos).

    Args:
        unidad_administrativa: Filtrar el análisis para una UA específica (ej: "Aduana de Tijuana").
                               Si es None, se genera el reporte institucional global.
    """
    qs = EmpleadosCompletosSig.objects.all()
    bajas_qs = BajasSig.objects.all()
    
    filtros_desc = "INSTITUCIONAL GLOBAL"
    if unidad_administrativa:
        unidad_administrativa = unidad_administrativa.strip()
        qs = qs.filter(unidad_administrativa__icontains=unidad_administrativa)
        bajas_qs = bajas_qs.filter(unidad_admon__icontains=unidad_administrativa)
        filtros_desc = f"UNIDAD ADMINISTRATIVA: {unidad_administrativa.upper()}"

    total_plazas = qs.count()
    if total_plazas == 0:
        return f"No se encontraron registros para generar el resumen ejecutivo de la UA '{unidad_administrativa}'."

    # KPIs de personal
    activos = qs.filter(estado_nomina="A").count()
    vacantes = qs.exclude(estado_nomina__in=["A", "a", "S", "s", "L", "l", "P", "p"]).count()
    otros_estados = total_plazas - activos - vacantes
    tasa_vacancia = (vacantes / total_plazas * 100) if total_plazas else 0.0

    # Clasificación Militar vs Civil
    militar = qs.filter(personal_militar_o_civil__iexact="MILITAR").count()
    civil = qs.filter(personal_militar_o_civil__iexact="CIVIL").count()

    # Catálogo de presupuestos indexado por nivel
    catalog = {p.nivel: p for p in CatalogoPlazas.objects.all()}

    # Agrupar activos y vacantes por nivel para cálculo de costo
    activos_por_nivel = qs.filter(estado_nomina="A").values('nivel').annotate(count=Count('posicion'))
    vacantes_por_nivel = qs.exclude(estado_nomina__in=["A", "a", "S", "s", "L", "l", "P", "p"]).values('nivel').annotate(count=Count('posicion'))

    costo_mensual_activos = 0.0
    costo_mensual_vacantes = 0.0

    for item in activos_por_nivel:
        nv = item['nivel']
        count = item['count']
        if nv and nv in catalog:
            p = catalog[nv]
            unitario = float(p.sueldo or 0) + float(p.compensacion_garantizada or 0) + float(p.despensa or 0) + float(p.prev_social_multiple or 0) + float(p.ayuda_servicios or 0) + float(p.ayuda_transporte or 0)
            costo_mensual_activos += unitario * count

    for item in vacantes_por_nivel:
        nv = item['nivel']
        count = item['count']
        if nv and nv in catalog:
            p = catalog[nv]
            unitario = float(p.sueldo or 0) + float(p.compensacion_garantizada or 0) + float(p.despensa or 0) + float(p.prev_social_multiple or 0) + float(p.ayuda_servicios or 0) + float(p.ayuda_transporte or 0)
            costo_mensual_vacantes += unitario * count

    # Tendencias de bajas (bajas totales históricas en el filtro)
    total_bajas_hist = bajas_qs.count()

    # Generar el Resumen Ejecutivo
    res = f"📊 RESUMEN EJECUTIVO DIRECTIVO — {filtros_desc}\n"
    res += "════════════════════════════════════════════════════════\n\n"

    res += "📌 INDICADORES CLAVE (KPIs):\n"
    res += f"  - Total de Plazas Registradas: {total_plazas:,}\n"
    res += f"  - Plazas Ocupadas (Activas): {activos:,} ({activos/total_plazas*100:.1f}%)\n"
    res += f"  - Plazas Vacantes: {vacantes:,} ({tasa_vacancia:.1f}%)\n"
    res += f"  - Plazas en Suspensión/Licencia: {otros_estados:,} ({otros_estados/total_plazas*100:.1f}%)\n"
    if militar > 0 or civil > 0:
        tot_mil_civ = militar + civil
        pct_mil = (militar / tot_mil_civ * 100) if tot_mil_civ else 0
        pct_civ = (civil / tot_mil_civ * 100) if tot_mil_civ else 0
        res += f"  - Composición de Fuerza: {militar:,} Militares ({pct_mil:.1f}%) | {civil:,} Civiles ({pct_civ:.1f}%)\n"
    res += "\n"

    res += "💵 FINANZAS Y PRESUPUESTO MENSUAL ESTIMADO:\n"
    res += f"  - Presupuesto mensual ocupado (Activos): ${costo_mensual_activos:,.2f}\n"
    res += f"  - Presupuesto mensual liberado (Vacantes): ${costo_mensual_vacantes:,.2f}\n"
    res += f"  - Gasto Proyectado Total Anual (Activos): ${costo_mensual_activos * 12:,.2f}\n"
    res += "\n"

    res += "🚨 ALERTAS Y DIAGNÓSTICOS PRIORITARIOS:\n"
    alertas = 0
    
    if tasa_vacancia > 15.0:
        res += f"  - ⚠️ TASA DE VACANCIA ELEVADA ({tasa_vacancia:.1f}%). Supera el umbral operativo del 15%.\n"
        alertas += 1

    # Checar si hay discrepancias de plazas inactivas ocupadas
    latest_ids = _get_latest_mov_pos_ids()
    posiciones_inactivas = MovPos.objects.filter(id__in=latest_ids, estado_psn="I").values_list("no_pos_actual", flat=True)
    inactivas_ocupadas = qs.filter(posicion__in=posiciones_inactivas, estado_nomina="A").count()
    if inactivas_ocupadas > 0:
        res += f"  - ❌ DISCREPANCIA PRESUPUESTAL: Hay {inactivas_ocupadas} plazas INACTIVAS administrativamente pero OCUPADAS en nómina SIG.\n"
        alertas += 1

    if total_bajas_hist > 10 and not unidad_administrativa:
        # Analizar principal causa de bajas
        principal_motivo = bajas_qs.values("motivo_descr").annotate(c=Count("id")).order_by("-c").first()
        if principal_motivo:
            res += f"  - 📈 TENDENCIA DE DESINCORPORACIÓN: El principal motivo de baja es '{principal_motivo['motivo_descr']}' con {principal_motivo['c']:,} casos registrados.\n"
            alertas += 1
            
    if alertas == 0:
        res += "  - ✅ Sin alertas críticas detectadas. Estado operativo nominal.\n"

    return res.strip()
