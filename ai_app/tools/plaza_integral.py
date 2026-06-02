from django.forms.models import model_to_dict
from plantilla.models import EmpleadosCompletosSig, MovPos, BajasSig
from ._base import tool_handler

@tool_handler(max_output_chars=6000)
def reporte_integral_plaza(posicion: str) -> str:
    """
    Genera un reporte completo y cruzado de una plaza combinando las tres fuentes de datos.

    Combina datos administrativos (MOV_POS), de nómina actual (SIG) y de desincorporaciones (BAJAS_SIG)
    para proveer un diagnóstico automático y datos presupuestales estimados.

    Args:
        posicion: Número de plaza/posición (ej: "50001234").
    """
    posicion = posicion.strip()

    if not posicion:
        return (
            "❌ Error: El número de plaza no puede estar vacío. "
            "Si tienes el nombre del empleado, usa buscar_empleados_sig() primero "
            "para obtener su número de plaza."
        )

    # MOV_POS: historial de movimientos (todos)
    movimientos = list(
        MovPos.objects.filter(no_pos_actual=posicion).order_by("-f_efva", "-id")
    )
    ultimo_mov = movimientos[0] if movimientos else None

    # EMPLEADOS_COMPLETOS_SIG
    registro_sig = EmpleadosCompletosSig.objects.filter(posicion=posicion).first()

    # BAJAS_SIG: historial de bajas
    bajas = list(BajasSig.objects.filter(posicion=posicion).order_by("-fecha_efectiva"))
    ultima_baja = bajas[0] if bajas else None

    if not ultimo_mov and not registro_sig:
        return f"❌ Plaza '{posicion}' no encontrada en ninguna fuente de datos (MOV_POS, SIG, BAJAS)."

    res = f"📋 REPORTE INTEGRAL — PLAZA {posicion}\n"
    res += "════════════════════════════════════\n\n"

    # ── Sección 1: Estado administrativo MOV_POS ──
    if ultimo_mov:
        d = model_to_dict(ultimo_mov)
        estado_adm = "✅ ACTIVA" if d.get("estado_psn") == "A" else "❌ INACTIVA"
        res += f"[1] ESTADO ADMINISTRATIVO (MOV_POS) — {estado_adm}\n"
        res += f"    Puesto: {d.get('nombre_puesto', 'N/A')}\n"
        res += f"    Fecha efectiva del último mov: {d.get('f_efva', 'N/A')}\n"
        res += f"    Motivo: {d.get('motivo', 'N/A')} (Cod: {d.get('cd_motivo', 'N/A')})\n"
        res += f"    Unidad de Negocio: [{d.get('cd_un', 'N/A')}] {d.get('unidad_de_negocio', 'N/A')}\n"
        res += f"    Unidad Administrativa: {d.get('unidad_adva', 'N/A')}\n"
        res += f"    Departamento: {d.get('cd_departamento', 'N/A')}\n"
        res += f"    Plan Sal: {d.get('plan_sal', 'N/A')} | Grado: {d.get('grado', 'N/A')} | Escala: {d.get('esc', 'N/A')}\n"
        res += f"    Partida Ptal: {d.get('partida_ptal', 'N/A')} | Gp Pago: {d.get('gp_pago', 'N/A')}\n"
        res += f"    Jefe directo (plaza): {d.get('depnd_drt', 'N/A')}\n"
        res += f"    Total movimientos históricos en esta plaza: {len(movimientos)}\n"
        res += "\n"

    # ── Sección 2: Estado nómina EMPLEADOS_COMPLETOS_SIG ──
    if registro_sig:
        d = model_to_dict(registro_sig)
        estado_nom = (d.get("estado_nomina") or "").upper()
        estado_label = {
            "A": "✅ ACTIVO en nómina",
            "V": "⭕ VACANTE en nómina",
            "S": "⚠️ SUSPENDIDO",
            "L": "🔵 LICENCIA",
            "P": "🟡 LICENCIA MÉDICA",
        }.get(estado_nom, f"❓ {d.get('estado_nomina', 'Sin estado')}")

        res += f"[2] ESTADO NÓMINA (EMPLEADOS_COMPLETOS_SIG) — {estado_label}\n"
        if d.get("nombres") and d.get("nombres").strip():
            res += f"    👤 Ocupante: {d.get('nombres', 'N/A')}\n"
            res += f"    RFC: {d.get('rfc', 'N/A')} | CURP: {d.get('curp', 'N/A')}\n"
            res += f"    ID Empleado: {d.get('id_empleado', 'N/A')}\n"
        else:
            res += f"    👤 Sin ocupante registrado (plaza vacante en SIG)\n"
        res += f"    Nivel: {d.get('nivel', 'N/A')} | NJ: {d.get('nj', 'N/A')}\n"
        res += f"    Puesto funcional: {d.get('nombre_puesto_funcional', 'N/A')}\n"
        res += f"    UA: {d.get('unidad_administrativa', 'N/A')}\n"
        res += f"    Tipo contratación: {d.get('tipo_de_contratacion', 'N/A')}\n"
        res += f"    SMB (Bruto): {d.get('smb', 'N/A')} | SMN (Neto): {d.get('smn', 'N/A')}\n"
        res += f"    Motivo mov: {d.get('motivo', 'N/A')} | Fecha efectiva: {d.get('fecha_efectiva_personal', 'N/A')}\n"
        res += f"    Jefe directo (plaza): {d.get('dependencia_directa', 'N/A')}\n"
        res += f"    Ubicación: {d.get('descripcion_ubicacion', 'N/A')} | {d.get('entidad_federativa', 'N/A')}\n"
        res += "\n"

    # ── Sección 3: Historial de bajas BAJAS_SIG ──
    if bajas:
        res += f"[3] HISTORIAL DE BAJAS (BAJAS_SIG) — {len(bajas)} registro(s)\n"
        for i, baja in enumerate(bajas[:3]):  # Mostrar máximo 3 bajas
            d = model_to_dict(baja)
            res += f"    Baja #{i + 1}:\n"
            res += f"      Empleado: {d.get('nombre_completo', 'N/A')}\n"
            res += f"      📅 Fecha efectiva (vacante desde): {d.get('fecha_efectiva', 'N/A')}\n"
            res += f"      Motivo: {d.get('motivo_descr', 'N/A')}\n"
            res += f"      Acción: {d.get('accion_descr', 'N/A')}\n"
            res += f"      UA: {d.get('unidad_admon', 'N/A')}\n"
            res += f"      Status RRHH: {d.get('humanos_status', 'N/A')} | Nómina: {d.get('nomina_status', 'N/A')}\n"
        if len(bajas) > 3:
            res += f"    ... y {len(bajas) - 3} baja(s) más en el historial\n"
        res += "\n"
    else:
        res += "[3] BAJAS_SIG — Sin historial de bajas para esta plaza.\n\n"

    # ── Sección 4: Presupuesto estimado (CatalogoPlazas) ──
    res += "[4] ESTIMACIÓN PRESUPUESTARIA MENSUAL\n"
    nivel = None
    if registro_sig and registro_sig.nivel:
        nivel = registro_sig.nivel
    elif ultimo_mov and ultimo_mov.grado: # Si no está en sig, checar el grado
        nivel = ultimo_mov.grado
        
    if nivel:
        try:
            from presupuesto.models import CatalogoPlazas
            plaza_ptal = CatalogoPlazas.objects.filter(nivel=nivel).first()
            if plaza_ptal:
                sueldo = float(plaza_ptal.sueldo or 0)
                comp = float(plaza_ptal.compensacion_garantizada or 0)
                # Otras prestaciones/prestaciones mensuales aproximadas
                despensa = float(plaza_ptal.despensa or 0)
                prev_soc = float(plaza_ptal.prev_social_multiple or 0)
                ayuda_serv = float(plaza_ptal.ayuda_servicios or 0)
                ayuda_trans = float(plaza_ptal.ayuda_transporte or 0)
                
                otros = despensa + prev_soc + ayuda_serv + ayuda_trans
                total_estimado = sueldo + comp + otros
                
                res += f"    Nivel Tabular: {nivel}\n"
                res += f"    Denominación: {plaza_ptal.denominacion or 'N/A'}\n"
                res += f"    Sueldo Base: ${sueldo:,.2f}\n"
                res += f"    Compensación Garantizada: ${comp:,.2f}\n"
                res += f"    Otras Prestaciones (Despensa, Transp., etc): ${otros:,.2f}\n"
                res += f"    Costo Mensual Estimado: ${total_estimado:,.2f}\n"
            else:
                res += f"    Sin datos en el Catálogo de Plazas para el nivel tabular '{nivel}'.\n"
        except Exception as e:
            res += f"    Error al consultar datos presupuestarios: {str(e)}\n"
    else:
        res += "    No se pudo determinar el nivel tabular para consultar el presupuesto.\n"
    res += "\n"

    # ── Sección 5: Diagnóstico automático ──
    res += "[5] DIAGNÓSTICO AUTOMÁTICO\n"

    if ultimo_mov and ultimo_mov.estado_psn == "I":
        res += "    ⚠️ Plaza INACTIVA presupuestalmente. No puede ser ocupada.\n"
    elif registro_sig and (registro_sig.estado_nomina or "").upper() == "A":
        res += f"    ✅ Plaza OCUPADA por {registro_sig.nombres or 'empleado sin nombre'}.\n"
        if registro_sig.fecha_efectiva_personal:
            res += f"    Ocupa la plaza desde: {registro_sig.fecha_efectiva_personal}\n"
    elif ultima_baja:
        res += f"    ⭕ Plaza VACANTE desde: {ultima_baja.fecha_efectiva}\n"
        res += f"    Último ocupante: {ultima_baja.nombre_completo}\n"
        res += f"    Motivo de vacancia: {ultima_baja.motivo_descr}\n"
    else:
        res += "    ⭕ Plaza VACANTE (sin registro de ocupante activo en nómina y sin historial de bajas).\n"

    return res.strip()
