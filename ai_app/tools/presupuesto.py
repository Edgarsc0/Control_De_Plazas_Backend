from django.db.models import Q, Count
from presupuesto.models import CatalogoPlazas
from plantilla.models import EmpleadosCompletosSig
from ._base import tool_handler

@tool_handler(max_output_chars=6000)
def consultar_presupuesto_plaza(nivel: str, meses: int = 12) -> str:
    """
    Consulta el costo presupuestal de una plaza por su nivel tabular.

    Calcula sueldo base, compensación garantizada, otras prestaciones mensuales
    y el costo total acumulado para un número determinado de meses.

    Args:
        nivel: Nivel tabular de la plaza (ej: "C1", "D2", "LC02").
        meses: Número de meses para calcular (default: 12).
    """
    nivel = nivel.strip()
    plaza = CatalogoPlazas.objects.filter(nivel=nivel).first()

    if not plaza:
        return f"❌ No se encontraron datos presupuestales en CatalogoPlazas para el nivel tabular '{nivel}'."

    sueldo = float(plaza.sueldo or 0)
    comp = float(plaza.compensacion_garantizada or 0)
    
    # Otras prestaciones
    despensa = float(plaza.despensa or 0)
    prev_soc = float(plaza.prev_social_multiple or 0)
    ayuda_serv = float(plaza.ayuda_servicios or 0)
    ayuda_trans = float(plaza.ayuda_transporte or 0)
    apoyo_cap = float(plaza.apoyo_capacitacion or 0)
    
    otros_mensual = despensa + prev_soc + ayuda_serv + ayuda_trans + apoyo_cap
    total_mensual = sueldo + comp + otros_mensual
    
    total_periodo = total_mensual * meses

    res = f"💵 ESTIMACIÓN PRESUPUESTARAL — NIVEL TABULAR: {nivel}\n"
    res += "════════════════════════════════════════════════════════\n"
    res += f"Denominación: {plaza.denominacion or 'N/A'}\n"
    res += f"Código de puesto: {plaza.codigo or 'N/A'}\n"
    res += f"Zona: {plaza.zona or 'N/A'}\n\n"
    
    res += "📊 Desglose Mensual:\n"
    res += f"  - Sueldo Base: ${sueldo:,.2f}\n"
    res += f"  - Compensación Garantizada: ${comp:,.2f}\n"
    res += f"  - Prestaciones Mensuales: ${otros_mensual:,.2f}\n"
    res += f"    (Despensa: ${despensa:,.2f}, Previsión Social: ${prev_soc:,.2f}, Ayuda Servicios: ${ayuda_serv:,.2f}, Transporte: ${ayuda_trans:,.2f}, Capacitación: ${apoyo_cap:,.2f})\n"
    res += f"  - COSTO TOTAL MENSUAL: ${total_mensual:,.2f}\n\n"
    
    res += f"📅 Cálculo para {meses} meses:\n"
    res += f"  - COSTO ESTIMADO DEL PERIODO: ${total_periodo:,.2f}\n"
    res += f"  - COSTO ANUALIZADO (12 meses): ${total_mensual * 12:,.2f}\n"

    return res

@tool_handler(max_output_chars=6000)
def calcular_costo_vacantes(unidad_administrativa: str = None, nivel: str = None) -> str:
    """
    Calcula el costo financiero estimado y el ahorro/impacto presupuestario de las vacantes.

    Filtra vacantes en nómina y suma sus costos correspondientes según el nivel tabular.

    Args:
        unidad_administrativa: UA específica para filtrar las vacantes (parcial).
        nivel: Nivel tabular específico para filtrar las vacantes.
    """
    # Buscar vacantes
    vacantes_qs = EmpleadosCompletosSig.objects.exclude(
        estado_nomina__in=["A", "a", "S", "s", "L", "l", "P", "p"]
    )

    filtros_desc = []
    if unidad_administrativa:
        vacantes_qs = vacantes_qs.filter(unidad_administrativa__icontains=unidad_administrativa.strip())
        filtros_desc.append(f"UA '{unidad_administrativa}'")
    if nivel:
        vacantes_qs = vacantes_qs.filter(nivel__iexact=nivel.strip())
        filtros_desc.append(f"Nivel '{nivel}'")

    total_vacantes = vacantes_qs.count()
    if total_vacantes == 0:
        filtros_str = " y ".join(filtros_desc) if filtros_desc else "globales"
        return f"No se encontraron plazas vacantes para los filtros: {filtros_str}."

    # Agrupar vacantes por nivel
    niveles_vacantes = vacantes_qs.values('nivel').annotate(count=Count('posicion'))
    
    # Obtener el catálogo de plazas indexado por nivel
    catalog = {p.nivel: p for p in CatalogoPlazas.objects.all()}

    costo_mensual_total = 0.0
    costo_anual_total = 0.0
    sin_datos_nivel = []
    
    desglose_niveles = []

    for item in niveles_vacantes:
        nv = item['nivel']
        count = item['count']
        if not nv:
            sin_datos_nivel.append(("Sin nivel", count))
            continue
            
        plaza_ptal = catalog.get(nv)
        if not plaza_ptal:
            sin_datos_nivel.append((nv, count))
            continue
            
        # Calcular costos
        sueldo = float(plaza_ptal.sueldo or 0)
        comp = float(plaza_ptal.compensacion_garantizada or 0)
        despensa = float(plaza_ptal.despensa or 0)
        prev_soc = float(plaza_ptal.prev_social_multiple or 0)
        ayuda_serv = float(plaza_ptal.ayuda_servicios or 0)
        ayuda_trans = float(plaza_ptal.ayuda_transporte or 0)
        apoyo_cap = float(plaza_ptal.apoyo_capacitacion or 0)
        
        costo_unitario = sueldo + comp + despensa + prev_soc + ayuda_serv + ayuda_trans + apoyo_cap
        costo_nivel_mensual = costo_unitario * count
        costo_nivel_anual = costo_nivel_mensual * 12
        
        costo_mensual_total += costo_nivel_mensual
        costo_anual_total += costo_nivel_anual
        
        desglose_niveles.append({
            "nivel": nv,
            "cantidad": count,
            "unitario_mensual": costo_unitario,
            "total_mensual": costo_nivel_mensual
        })

    # Ordenar desglose de niveles por costo total mensual descendente
    desglose_niveles.sort(key=lambda x: x["total_mensual"], reverse=True)

    filtros_str = f" para {', '.join(filtros_desc)}" if filtros_desc else " globales"
    res = f"💰 IMPACTO PRESUPUESTARAL DE VACANTES{filtros_str.upper()}\n"
    res += "════════════════════════════════════════════════════════\n"
    res += f"Total vacantes contabilizadas: {total_vacantes}\n"
    res += f"Costo mensual total vacante: ${costo_mensual_total:,.2f}\n"
    res += f"Costo anualizado total vacante: ${costo_anual_total:,.2f}\n"
    res += "*(Representa el presupuesto no ejercido o 'ahorro' temporal por vacancia)*\n\n"

    res += "📈 Desglose por Nivel Tabular (Top 10):\n"
    for d in desglose_niveles[:10]:
        res += f"  - Nivel {d['nivel']}: {d['cantidad']} vacante(s) | Costo mensual unitario: ${d['unitario_mensual']:,.2f} | Costo total mensual: ${d['total_mensual']:,.2f}\n"

    if len(desglose_niveles) > 10:
        res += f"  ... y {len(desglose_niveles) - 10} niveles más\n"

    if sin_datos_nivel:
        res += "\n⚠️ Vacantes sin correspondencia presupuestal:\n"
        for nv, count in sin_datos_nivel:
            res += f"  - Nivel '{nv}': {count} vacante(s) sin tabulador registrado\n"

    return res
