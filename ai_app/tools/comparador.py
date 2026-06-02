from django.forms.models import model_to_dict
from plantilla.models import EmpleadosCompletosSig, MovPos
from ._base import tool_handler, _get_latest_mov_pos_ids

@tool_handler(max_output_chars=6000)
def comparar_plazas(posiciones: list[str]) -> str:
    """
    Compara de 2 a 5 plazas lado a lado generando una tabla comparativa en Markdown.

    Compara campos clave como estado en nómina, ocupante, nivel, unidad administrativa,
    salario bruto y estado en el catálogo de plazas (MOV_POS).

    Args:
        posiciones: Lista de números de plazas a comparar (ej: ["50001234", "50001235"]).
    """
    if not posiciones or not isinstance(posiciones, list):
        return "❌ Error: Debe proporcionar una lista de posiciones en el parámetro 'posiciones'."

    # Limitar de 2 a 5 plazas
    posiciones = [p.strip() for p in posiciones if str(p).strip()]
    if len(posiciones) < 2:
        return "❌ Error: Debe proporcionar al menos 2 plazas para comparar."
    if len(posiciones) > 5:
        posiciones = posiciones[:5]
        # Agregamos aviso al inicio
        aviso = "⚠️ Nota: Se limitó la comparación a las primeras 5 plazas.\n\n"
    else:
        aviso = ""

    # Obtener datos de SIG
    sig_records = {r.posicion: r for r in EmpleadosCompletosSig.objects.filter(posicion__in=posiciones)}

    # Obtener datos de MOV_POS
    latest_ids = _get_latest_mov_pos_ids()
    mov_records = {m.no_pos_actual: m for m in MovPos.objects.filter(id__in=latest_ids, no_pos_actual__in=posiciones)}

    res = aviso + "⚖️  COMPARATIVA DE PLAZAS LADO A LADO\n"
    res += "════════════════════════════════════════════════════════\n\n"
    
    # Encabezados de la tabla Markdown
    res += "| Campo | " + " | ".join([f"Plaza {pos}" for pos in posiciones]) + " |\n"
    res += "| :--- | " + " | ".join([":---" for _ in posiciones]) + " |\n"
    
    # Renglones de comparación
    # Ocupante
    ocupantes = []
    for pos in posiciones:
        sig = sig_records.get(pos)
        if sig and sig.nombres and sig.nombres.strip():
            ocupantes.append(sig.nombres)
        else:
            ocupantes.append("⭕ VACANTE")
    res += "| **Ocupante** | " + " | ".join(ocupantes) + " |\n"

    # Estatus en Nómina
    estatus_sig = []
    nomina_map = {
        "A": "✅ Activo",
        "V": "⭕ Vacante",
        "S": "⚠️ Suspendido",
        "L": "🔵 Licencia",
        "P": "🟡 Lic. Médica"
    }
    for pos in posiciones:
        sig = sig_records.get(pos)
        if sig:
            est_nom = (sig.estado_nomina or "").upper()
            estatus_sig.append(nomina_map.get(est_nom, f"❓ {sig.estado_nomina or 'S/D'}"))
        else:
            estatus_sig.append("❌ No en nómina")
    res += "| **Estatus Nómina (SIG)** | " + " | ".join(estatus_sig) + " |\n"

    # Nivel Tabular
    niveles = []
    for pos in posiciones:
        sig = sig_records.get(pos)
        if sig:
            niveles.append(sig.nivel or "S/D")
        else:
            # Intentar obtener de MOV_POS
            mov = mov_records.get(pos)
            niveles.append(mov.grado or "S/D" if mov else "S/D")
    res += "| **Nivel Tabular** | " + " | ".join(niveles) + " |\n"

    # Unidad Administrativa
    uas = []
    for pos in posiciones:
        sig = sig_records.get(pos)
        if sig:
            uas.append(sig.unidad_administrativa or "S/D")
        else:
            mov = mov_records.get(pos)
            uas.append(mov.unidad_adva or "S/D" if mov else "S/D")
    res += "| **Unidad Admin.** | " + " | ".join(uas) + " |\n"

    # Puesto Funcional
    puestos = []
    for pos in posiciones:
        sig = sig_records.get(pos)
        if sig:
            puestos.append(sig.nombre_puesto_funcional or "S/D")
        else:
            mov = mov_records.get(pos)
            puestos.append(mov.nombre_puesto or "S/D" if mov else "S/D")
    res += "| **Puesto Funcional** | " + " | ".join(puestos) + " |\n"

    # Salario Mensual Bruto (SMB)
    salarios = []
    for pos in posiciones:
        sig = sig_records.get(pos)
        if sig and sig.smb:
            try:
                val = float(sig.smb)
                salarios.append(f"${val:,.2f}")
            except ValueError:
                salarios.append(str(sig.smb))
        else:
            salarios.append("N/A")
    res += "| **Salario Bruto (SMB)** | " + " | ".join(salarios) + " |\n"

    # Estatus Administrativo (MOV_POS)
    estatus_mov = []
    for pos in posiciones:
        mov = mov_records.get(pos)
        if mov:
            estatus_mov.append("✅ ACTIVA" if mov.estado_psn == "A" else "❌ INACTIVA")
        else:
            estatus_mov.append("❓ Sin datos")
    res += "| **Estatus Presupuestal** | " + " | ".join(estatus_mov) + " |\n"

    # Motivo último movimiento
    motivos = []
    for pos in posiciones:
        mov = mov_records.get(pos)
        if mov:
            motivos.append(f"{mov.motivo or 'S/D'} ({mov.f_efva or 'S/D'})")
        else:
            motivos.append("N/A")
    res += "| **Último Movimiento** | " + " | ".join(motivos) + " |\n"

    return res.strip()
