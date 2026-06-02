from django.db.models import Q, Max
from plantilla.models import EmpleadosCompletosSig, BajasSig
from ._base import tool_handler, MAX_RESULTS_DEFAULT, MAX_RESULTS_ABSOLUTE

@tool_handler(max_output_chars=6000)
def buscar_vacantes(
    nivel: str = None,
    unidad_administrativa: str = None,
    tipo_de_contratacion: str = None,
    limite: int = 20,
    ordenar_por: str = "antiguedad"
) -> str:
    """
    Busca plazas vacantes en EMPLEADOS_COMPLETOS_SIG con filtros opcionales.

    Identifica plazas vacantes (sin ocupante activo en nómina) y calcula desde
    cuándo están vacantes cruzando datos con la última baja en BAJAS_SIG.

    Args:
        nivel: Nivel tabular exacto (ej: "C1").
        unidad_administrativa: Búsqueda parcial de la Unidad Administrativa (ej: "Veracruz").
        tipo_de_contratacion: Tipo de contratación (ej: "BASE", "CONFIANZA", "EVENTUAL").
        limite: Número máximo de vacantes a retornar (entre 1 y 50).
        ordenar_por: Criterio de ordenamiento:
                     - 'antiguedad' (default): Muestra primero las plazas vacantes hace más tiempo.
                     - 'nivel': Alfabéticamente por nivel tabular.
                     - 'ua': Alfabéticamente por Unidad Administrativa.
    """
    qs = EmpleadosCompletosSig.objects.exclude(
        estado_nomina__in=["A", "a", "S", "s", "L", "l", "P", "p"]
    )

    if nivel:
        qs = qs.filter(nivel__iexact=nivel.strip())
    if unidad_administrativa:
        qs = qs.filter(unidad_administrativa__icontains=unidad_administrativa.strip())
    if tipo_de_contratacion:
        qs = qs.filter(tipo_de_contratacion__icontains=tipo_de_contratacion.strip())

    total = qs.count()
    limite = min(max(1, limite), MAX_RESULTS_ABSOLUTE)

    # Obtenemos los registros
    results = list(qs)

    if not results:
        return "No se encontraron plazas vacantes con los filtros especificados."

    # Obtener últimas bajas para ordenar y mostrar
    positions = [r.posicion for r in results if r.posicion]
    bajas_qs = BajasSig.objects.filter(posicion__in=positions).values('posicion').annotate(latest_fecha=Max('fecha_efectiva'))
    bajas_map = {b['posicion']: b['latest_fecha'] for b in bajas_qs}

    # Ordenamiento
    ordenar_por = ordenar_por.lower().strip()
    if ordenar_por == "antiguedad":
        # Plazas vacantes hace más tiempo (fecha efectiva de baja más antigua/chica primero)
        # Si no tiene fecha de baja, va al final (fecha simulada futura '9999-12-31')
        results.sort(key=lambda r: bajas_map.get(r.posicion) or '9999-12-31')
    elif ordenar_por == "nivel":
        results.sort(key=lambda r: r.nivel or '')
    elif ordenar_por == "ua":
        results.sort(key=lambda r: r.unidad_administrativa or '')

    # Aplicar límite de registros a mostrar
    showing_results = results[:limite]

    res = f"⭕ PLAZAS VACANTES — Total: {total} | Mostrando: {len(showing_results)} ordenado por '{ordenar_por}'\n"
    res += "════════════════════════════════════════════════════════\n\n"

    for r in showing_results:
        res += f"  Plaza: {r.posicion} | Nivel: {r.nivel or 'N/A'} | Tipo: {r.tipo_de_contratacion or 'N/A'}\n"
        res += f"  Puesto: {r.nombre_puesto_funcional or 'N/A'}\n"
        res += f"  UA: {r.unidad_administrativa or 'N/A'}\n"

        # Buscar detalles de la última baja
        ultima_baja = (
            BajasSig.objects.filter(posicion=r.posicion)
            .order_by("-fecha_efectiva")
            .values("fecha_efectiva", "nombre_completo", "motivo_descr")
            .first()
        )
        if ultima_baja:
            res += f"  📅 Vacante desde: {ultima_baja['fecha_efectiva']}\n"
            res += f"  Ex-ocupante: {ultima_baja['nombre_completo']}\n"
            res += f"  Motivo de vacancia: {ultima_baja['motivo_descr']}\n"
        else:
            res += f"  ⚠️ Sin registro de baja asociado en BAJAS_SIG\n"
        res += "\n"

    return res.strip()
