from collections import defaultdict
from django.db.models import Count, Q
from plantilla.models import EmpleadosCompletosSig, BajasSig
from ._base import tool_handler

@tool_handler(max_output_chars=6000)
def analizar_unidad_administrativa(
    unidad_administrativa: str,
    incluir_vacantes: bool = True
) -> str:
    """
    Genera un análisis completo de la plantilla de una Unidad Administrativa (UA) específica.

    Incluye conteo de plazas activas, vacantes, licencias, desglose por nivel y por tipo
    de contratación, y tasa de vacancia comparada con el promedio institucional.

    Args:
        unidad_administrativa: Nombre (completo o parcial) de la UA a analizar.
        incluir_vacantes: Si es True, incluye el detalle de hasta 20 plazas vacantes.
    """
    unidad_administrativa = unidad_administrativa.strip()
    
    # Obtener el total global para promedio institucional
    global_total = EmpleadosCompletosSig.objects.count()
    global_vacantes = EmpleadosCompletosSig.objects.filter(
        Q(estado_nomina__isnull=True)
        | Q(estado_nomina="")
        | Q(estado_nomina__iexact="V")
    ).count()
    
    global_vacancy_rate = (global_vacantes / global_total * 100) if global_total else 0.0

    # Query para la UA específica
    qs = EmpleadosCompletosSig.objects.filter(
        unidad_administrativa__icontains=unidad_administrativa
    )
    total = qs.count()

    if total == 0:
        return f"No se encontraron registros para la UA '{unidad_administrativa}'. Verifique el nombre."

    # Estadísticas por estado nómina
    por_estado = defaultdict(int)
    estado_labels = {
        "A": "✅ Activos",
        "V": "⭕ Vacantes",
        "S": "⚠️ Suspendidos",
        "L": "🔵 Licencia",
        "P": "🟡 Lic. Médica",
    }
    
    ua_vacantes = 0
    for item in qs.values("estado_nomina").annotate(c=Count("id")):
        est = (item["estado_nomina"] or "").upper()
        if est in ("V", "", None):
            ua_vacantes += item["c"]
        label = estado_labels.get(est, f"❓ {item['estado_nomina']}")
        por_estado[label] += item["c"]

    ua_vacancy_rate = (ua_vacantes / total * 100) if total else 0.0

    # Por nivel
    por_nivel = list(
        qs.exclude(Q(nivel__isnull=True) | Q(nivel=""))
        .values("nivel")
        .annotate(c=Count("id"))
        .order_by("nivel")
    )

    # Por tipo de contratación
    por_tipo = list(
        qs.exclude(Q(tipo_de_contratacion__isnull=True) | Q(tipo_de_contratacion=""))
        .values("tipo_de_contratacion")
        .annotate(c=Count("id"))
        .order_by("-c")
    )

    res = f"🏢 ANÁLISIS DE UA: {unidad_administrativa.upper()}\n"
    res += "════════════════════════════════════\n"
    res += f"Total de plazas en esta UA: {total}\n"
    res += f"📊 Tasa de vacancia UA: {ua_vacancy_rate:.1f}% vs Institucional: {global_vacancy_rate:.1f}%\n\n"

    res += "📊 Por estado de nómina:\n"
    for label, count in sorted(por_estado.items()):
        res += f"   {label}: {count}\n"

    res += "\n📈 Por nivel tabular:\n"
    for item in por_nivel[:15]:
        res += f"   {item['nivel']}: {item['c']}\n"
    if len(por_nivel) > 15:
        res += f"   ... y {len(por_nivel) - 15} niveles más\n"

    res += "\n💼 Por tipo de contratación:\n"
    for item in por_tipo:
        res += f"   {item['tipo_de_contratacion']}: {item['c']}\n"

    if incluir_vacantes:
        vacantes = list(
            qs.filter(
                Q(estado_nomina__isnull=True)
                | Q(estado_nomina="")
                | Q(estado_nomina__iexact="V")
            ).values("posicion", "nivel", "nombre_puesto_funcional")[:20]
        )
        if vacantes:
            res += f"\n⭕ PLAZAS VACANTES DETECTADAS ({len(vacantes)} mostradas):\n"
            for v in vacantes:
                baja = (
                    BajasSig.objects.filter(posicion=v["posicion"])
                    .order_by("-fecha_efectiva")
                    .values("fecha_efectiva", "nombre_completo", "motivo_descr")
                    .first()
                )
                res += f"   • Plaza {v['posicion']} | Nivel: {v['nivel']} | Puesto: {v['nombre_puesto_funcional']}\n"
                if baja:
                    res += f"     📅 Vacante desde: {baja['fecha_efectiva']} | Ex-ocupante: {baja['nombre_completo']} | Motivo: {baja['motivo_descr']}\n"
                else:
                    res += "     ⚠️ Sin historial de baja registrado en BAJAS_SIG\n"

    return res.strip()
