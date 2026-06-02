from django.db.models import Count, Q
from django.core.cache import cache
from plantilla.models import BajasSig, EmpleadosCompletosSig, MovPos
from ._base import tool_handler, _get_latest_mov_pos_ids

@tool_handler(max_output_chars=6000)
def get_estadisticas_globales() -> str:
    """
    Retorna un panel completo de estadísticas globales de la plantilla de la ANAM.

    Incluye:
    - Estado de plazas en MOV_POS (activas vs inactivas presupuestalmente)
    - Resumen de nómina en EMPLEADOS_COMPLETOS_SIG (activos, vacantes, licencias, etc.)
    - Distribución por tipo de contratación
    - Top 5 Unidades Administrativas con más vacantes y con más personal activo
    - Personal militar vs civil
    - Estadísticas de bajas (desincorporaciones) en BAJAS_SIG

    Usa este tool como PRIMER PASO cuando el usuario pregunta sobre el estado
    general de la plantilla (ej: cuántos empleados, plazas, vacantes).
    """
    cache_key = "estadisticas_globales"
    cached_stats = cache.get(cache_key)
    if cached_stats is not None:
        return cached_stats + "\n\n⚡ (Datos recuperados de la caché - Actualizado hace menos de 5 minutos)"

    latest_ids = _get_latest_mov_pos_ids()

    # Plazas MOV_POS
    total_plazas = len(latest_ids)
    activas = MovPos.objects.filter(id__in=latest_ids, estado_psn="A").count()
    inactivas = MovPos.objects.filter(id__in=latest_ids, estado_psn="I").count()

    # Nómina por estado
    nomina_totals = (
        EmpleadosCompletosSig.objects.values("estado_nomina")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    nomina_map = {
        "A": "✅ Activos",
        "V": "⭕ Vacantes",
        "S": "⚠️ Suspendidos",
        "L": "🔵 Licencia",
        "P": "🟡 Lic. Médica",
    }
    nomina_str = ""
    total_en_nomina = 0
    for item in nomina_totals:
        estado = (item["estado_nomina"] or "").upper()
        label = nomina_map.get(estado, f"❓ '{item['estado_nomina']}'")
        nomina_str += f"   {label}: {item['total']}\n"
        total_en_nomina += item["total"]

    # Por tipo de contratación
    tipo_contrat = (
        EmpleadosCompletosSig.objects.exclude(
            Q(tipo_de_contratacion__isnull=True) | Q(tipo_de_contratacion="")
        )
        .values("tipo_de_contratacion")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )
    tipo_str = "\n".join(
        [f"   {t['tipo_de_contratacion']}: {t['total']}" for t in tipo_contrat]
    )

    # Top 5 UAs con más vacantes
    top_vacantes = (
        EmpleadosCompletosSig.objects.filter(
            Q(estado_nomina__isnull=True)
            | Q(estado_nomina="")
            | Q(estado_nomina__iexact="V")
        )
        .exclude(unidad_administrativa__isnull=True)
        .exclude(unidad_administrativa="")
        .values("unidad_administrativa")
        .annotate(vacantes=Count("id"))
        .order_by("-vacantes")[:5]
    )
    vacantes_str = "\n".join(
        [f"   {v['unidad_administrativa']}: {v['vacantes']}" for v in top_vacantes]
    )

    # Top 5 UAs con más activos
    top_activos = (
        EmpleadosCompletosSig.objects.filter(estado_nomina__iexact="A")
        .exclude(unidad_administrativa__isnull=True)
        .exclude(unidad_administrativa="")
        .values("unidad_administrativa")
        .annotate(activos=Count("id"))
        .order_by("-activos")[:5]
    )
    activos_str = "\n".join(
        [f"   {a['unidad_administrativa']}: {a['activos']}" for a in top_activos]
    )

    # Personal militar vs civil
    mil_civil = (
        EmpleadosCompletosSig.objects.exclude(
            Q(personal_militar_o_civil__isnull=True) | Q(personal_militar_o_civil="")
        )
        .values("personal_militar_o_civil")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    mil_str = "\n".join(
        [f"   {m['personal_militar_o_civil']}: {m['total']}" for m in mil_civil]
    )

    # Bajas recientes
    total_bajas = BajasSig.objects.count()
    top_motivos = (
        BajasSig.objects.exclude(motivo_descr__isnull=True)
        .exclude(motivo_descr="")
        .values("motivo_descr")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )
    motivos_str = "\n".join(
        [f"   {m['motivo_descr']}: {m['total']}" for m in top_motivos]
    )

    stats_str = f"""
🏛️  ESTADÍSTICAS GLOBALES — PLANTILLA ANAM
════════════════════════════════════

📊 MOV_POS (Estado administrativo de plazas):
   Total de plazas únicas: {total_plazas}
   ✅ Plazas ACTIVAS (Estado Psn = A): {activas}
   ❌ Plazas INACTIVAS (Estado Psn = I): {inactivas}

👥 EMPLEADOS_COMPLETOS_SIG (Estado nómina, total registros: {total_en_nomina}):
{nomina_str}
📋 Por tipo de contratación:
{tipo_str}

🏢 Top 5 UAs con más VACANTES:
{vacantes_str}

🏆 Top 5 UAs con más ACTIVOS:
{activos_str}

🎖️  Personal Militar vs Civil:
{mil_str if mil_str else '   Sin datos de clasificación'}

📉 BAJAS_SIG (Historial de desincorporaciones):
   Total registros históricos de bajas: {total_bajas}
   Top 5 motivos de baja:
{motivos_str}
""".strip()

    cache.set(cache_key, stats_str, 300) # 5 minutos
    return stats_str
