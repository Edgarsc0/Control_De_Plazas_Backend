import re

with open("plantilla/tasks.py", "r") as f:
    content = f.read()

# Replace EmpleadosCompletosSig imports
content = content.replace("from .models import BajasSig, EmpleadosCompletosSig, MovPos", 
    "from .models import BajasSig, EmpleadosCompletosSig, MovPos, ZafiroBitacora, EmpleadosCompletosSigHistorico, BajasSigHistorico, MovPosHistorico")

# For _importar_csv_empleados_completos
content = content.replace("def _importar_csv_empleados_completos(csv_path: str) -> int:", "def _importar_csv_empleados_completos(csv_path: str, guardar_historico: bool = False) -> int:")
content = content.replace("registros = []\n", "    registros = []\n    registros_historico = []\n")

empleados_completos_append = """            registros.append(
                EmpleadosCompletosSig(
                    id_field=row.get("Id", "")[:2] or None,
                    numeral=row.get("numeral", "")[:6] or None,
                    ua=row.get("ua") or None,
                    cent=row.get("cent", "")[:1] or None,
                    dir=row.get("dir", "")[:2] or None,
                    subd=row.get("subd", "")[:1] or None,
                    jd=row.get("jd", "")[:1] or None,
                    depto=row.get("depto", "")[:11] or None,
                    aduana=row.get("Aduana") or None,
                    id_tipo=row.get("id tipo", "")[:1] or None,
                    tipo=row.get("tipo") or None,
                    estado=row.get("estado") or None,
                    municipio=row.get("municipio") or None,
                    latitud=row.get("latitud", "")[:12] or None,
                    longitud=row.get("longitud", "")[:13] or None,
                    ua2=row.get("ua2") or None,
                    posicion=row.get("Posición", "")[:8] or None,
                    estado_nomina=row.get("Estado Nómina", "")[:1] or None,
                    id_empleado=row.get("Id Empleado", "")[:10] or None,
                    rfc=row.get("RFC", "")[:13] or None,
                    curp=row.get("CURP", "")[:18] or None,
                    nombres=row.get("Nombres", "")[:44] or None,
                    motivo=row.get("Motivo", "")[:30] or None,
                    fecha_efectiva_personal=row.get("Fecha efectiva (Personal)") or None,
                    fecha_de_captura=row.get("Fecha de captura") or None,
                    qna=row.get("Qna") or None,
                    fecha_prevista_de_salida=row.get("Fecha prevista de salida", "")[:10] or None,
                    nj=row.get("NJ") or None,
                    codigo_presupuestal=row.get("Código Presupuestal", "")[:10] or None,
                    nivel=row.get("Nivel", "")[:4] or None,
                    escala=row.get("Escala") or None,
                    smb=row.get("SMB", "")[:8] or None,
                    smn=row.get("SMN", "")[:9] or None,
                    partida=row.get("Partida") or None,
                    tipo_de_contratacion=row.get("TIPO DE CONTRATACIÓN", "")[:8] or None,
                    cd_un=row.get("Cd UN") or None,
                    unidad_de_negocio=row.get("Unidad de Negocio", "")[:74] or None,
                    cd_ua=row.get("Cd UA") or None,
                    unidad_administrativa=row.get("Unidad Administrativa") or None,
                    cd_pto_funcional=row.get("Cd Pto Funcional", "")[:6] or None,
                    nombre_puesto_funcional=row.get("Nombre Puesto Funcional", "")[:123] or None,
                    id_departamento=row.get("Id Departamento") or None,
                    departamento=row.get("Departamento") or None,
                    dependencia_directa=row.get("DependenciaDirecta") or None,
                    observaciones=row.get("OBSERVACIONES") or None,
                    ubicacion=row.get("Ubicación") or None,
                    descripcion_ubicacion=row.get("Descripción ubicación", "")[:30] or None,
                    posicion_civil_sedena_semar=row.get("Posición _Civil / SEDENA / SEMAR", "")[:22] or None,
                    personal_militar_o_civil=row.get("Personal Militar o Civil", "")[:12] or None,
                    tipo_de_personal_sedena_semar=row.get("Tipo de personal SEDENA / SEMAR", "")[:11] or None,
                    rango=row.get("Rango", "")[:28] or None,
                    fecha_de_ingreso=row.get("Fecha de ingreso", "")[:10] or None,
                    val_estat=row.get("Val_estat", "")[:7] or None,
                    status_jefe_inm_posicion=row.get("Status Jefe Inm Posición", "")[:9] or None,
                    numempleado=row.get("Numempleado", "")[:10] or None,
                    sindicato=row.get("Sindicato") or None,
                    entidad_federativa=row.get("Entidad Federativa", "")[:19] or None,
                    tipo_de_aduana=row.get("Tipo de Aduana", "")[:10] or None,
                    dg_o_aduana_compactada=row.get("DG o Aduana compactada", "")[:21] or None,
                    proyecto_2024_reduccion_plazas_eventuales=row.get(
                        "Proyecto 2024 Reducción de plazas Eventuales"
                    ) or None,
                    estado_en_nomina=row.get("Estado en nomina") or None,
                    ua_validacion=row.get("UA Validación") or None,
                    validando_posicion_por_documento=row.get(
                        "Validando de posición por documento"
                    ) or None,
                    val_estatx=row.get("Val_estatx", "")[:7] or None,
                    nj_comp=row.get("NJ COMP", "")[:21] or None,
                    nj_ok=row.get("NJ OK") or None,
                    columna=row.get("Columna", "")[:40] or None,
                    nombre_nj=row.get("nombreNJ", "")[:19] or None,
                    nj_operativo_comb=row.get("NJOperativoComb", "")[:13] or None,
                )
            )"""

empleados_completos_historico = empleados_completos_append.replace("registros.append(", "if guardar_historico:\n                registros_historico.append(").replace("EmpleadosCompletosSig(", "EmpleadosCompletosSigHistorico(")

content = content.replace(empleados_completos_append, empleados_completos_append + "\n            " + empleados_completos_historico)

content = content.replace("""    with transaction.atomic():
        _truncar_tabla(EmpleadosCompletosSig)
        # batch_size=1000 para no saturar la memoria en inserciones masivas
        EmpleadosCompletosSig.objects.bulk_create(registros, batch_size=1000)""", """    with transaction.atomic():
        _truncar_tabla(EmpleadosCompletosSig)
        EmpleadosCompletosSig.objects.bulk_create(registros, batch_size=1000)
        if guardar_historico:
            EmpleadosCompletosSigHistorico.objects.bulk_create(registros_historico, batch_size=1000)""")

# BajasSig
content = content.replace("def _importar_csv_bajas(csv_path: str) -> int:", "def _importar_csv_bajas(csv_path: str, guardar_historico: bool = False) -> int:")
content = content.replace("    with open(csv_path, encoding=\"cp1252\", newline=\"\") as f:", "    registros_historico = []\n    with open(csv_path, encoding=\"cp1252\", newline=\"\") as f:")

bajas_append = """            registros.append(
                BajasSig(
                    posicion=row.get("POSICION") or None,
                    no_empleado=row.get("NO_EMPLEADO") or None,
                    nombre_completo=row.get("NOMBRE_COMPLETO") or None,
                    primer_apellido=row.get("PRIMER_APELLIDO") or None,
                    segundo_apellido=row.get("SEGUNDO_APELLIDO") or None,
                    accion=row.get("ACCION") or None,
                    accion_descr=row.get("ACCION_DESCR") or None,
                    motivo=row.get("MOTIVO") or None,
                    motivo_descr=row.get("MOTIVO_DESCR") or None,
                    fecha_efectiva=row.get("FECHA_EFECTIVA") or None,
                    id_puesto_funcional=row.get("ID_PUESTO_FUNCIONAL") or None,
                    puesto_funcional=row.get("PUESTO_FUNCIONAL") or None,
                    denominacion_puesto=row.get("DENOMINACION_PUESTO") or None,
                    inmueble=row.get("INMUEBLE") or None,
                    fecha_prevista=row.get("FECHA_PREVISTA") or None,
                    ultima_actualizacion=row.get("ULTIMA_ACTUALIZACION") or None,
                    ultimo_operador=row.get("ULTIMO_OPERADOR") or None,
                    ultima_fecha_ingreso=row.get("ULTIMA_FECHA_INGRESO") or None,
                    fecha_ingreso=row.get("FECHA_INGRESO") or None,
                    grupo_trabajo=row.get("GRUPO_TRABAJO") or None,
                    codigo_grupo=row.get("CODIGO_GRUPO") or None,
                    fecha_asignacion=row.get("FECHA_ASIGNACION") or None,
                    rfc=row.get("RFC") or None,
                    curp=row.get("CURP") or None,
                    id_persona=row.get("ID_PERSONA") or None,
                    nivel=row.get("NIVEL") or None,
                    nivel1=row.get("NIVEL1") or None,
                    unidad_administrativa=row.get("UNIDAD_ADMINISTRATIVA") or None,
                    genero=row.get("GENERO") or None,
                    fecha_entrada_posicion=row.get("FECHA_ENTRADA_POSICION") or None,
                    fecha_posicion=row.get("FECHA_POSICION") or None,
                )
            )"""

bajas_historico = bajas_append.replace("registros.append(", "if guardar_historico:\n                registros_historico.append(").replace("BajasSig(", "BajasSigHistorico(")
content = content.replace(bajas_append, bajas_append + "\n            " + bajas_historico)

content = content.replace("""    with transaction.atomic():
        _truncar_tabla(BajasSig)
        BajasSig.objects.bulk_create(registros, batch_size=1000)""", """    with transaction.atomic():
        _truncar_tabla(BajasSig)
        BajasSig.objects.bulk_create(registros, batch_size=1000)
        if guardar_historico:
            BajasSigHistorico.objects.bulk_create(registros_historico, batch_size=1000)""")

# Posiciones
content = content.replace("def _importar_csv_posiciones(csv_path: str) -> int:", "def _importar_csv_posiciones(csv_path: str, guardar_historico: bool = False) -> int:")
content = content.replace("    with open(csv_path, encoding=\"cp1252\", newline=\"\") as f:", "    registros_historico = []\n    with open(csv_path, encoding=\"cp1252\", newline=\"\") as f:")

posiciones_append = """            registros.append(
                MovPos(
                    no_pos_actual=row.get("Nº Pos Actual") or None,
                    f_efva=row.get("F Efva") or None,
                    estado_psn=row.get("Estado Psn") or None,
                    fecha_captura=row.get("Fecha Captura") or None,
                    cd_motivo=row.get("Cd Motivo") or None,
                    motivo=row.get("Motivo") or None,
                    cd_un=row.get("Cd UN") or None,
                    unidad_de_negocio=row.get("Unidad de Negocio") or None,
                    unidad_adva=row.get("Unidad Adva#") or None,
                    cd_departamento=row.get("Cd Departamento") or None,
                    cd_puesto=row.get("Cd Puesto") or None,
                    estado_ptal=row.get("Estado Ptal") or None,
                    fecha_est=row.get("Fecha Est") or None,
                    maximo=row.get("Máximo") or None,
                    depnd_drt=row.get("Depnd Drt") or None,
                    depnd_indrt=row.get("Depnd Indrt") or None,
                    ubicacion=row.get("Ubicación") or None,
                    nvl_direc=row.get("Nvl Direc") or None,
                    plan_sal=row.get("Plan Sal") or None,
                    grado=row.get("Grado") or None,
                    esc=row.get("Esc") or None,
                    puesto_ptal=row.get("Puesto Ptal") or None,
                    partida_ptal=row.get("Partida Ptal") or None,
                    gp_pago=row.get("Gp Pago") or None,
                    prog_beneficios=row.get("Prog Beneficios") or None,
                    fh_ult_actz=row.get("F/H Últ Actz") or None,
                    por=row.get("Por") or None,
                    hr_estd_semn=row.get("Hr Estd/Semn") or None,
                    descr=row.get("Descr") or None,
                    gp_trabajo=row.get("Gp Trabajo") or None,
                    org_code=row.get("Org Code") or None,
                    grupo_cd_sal=row.get("Grupo Cd Sal") or None,
                    formal_desc=row.get("FormalDesc") or None,
                    pto_compt=row.get("Pto Compt") or None,
                    posn_clv=row.get("Posn Clv") or None,
                    presupuesto=row.get("Presupuesto") or None,
                    nombre_puesto=row.get("Nombre Puesto") or None,
                )
            )"""

posiciones_historico = posiciones_append.replace("registros.append(", "if guardar_historico:\n                registros_historico.append(").replace("MovPos(", "MovPosHistorico(")
content = content.replace(posiciones_append, posiciones_append + "\n            " + posiciones_historico)

content = content.replace("""    with transaction.atomic():
        _truncar_tabla(MovPos)
        MovPos.objects.bulk_create(registros, batch_size=1000)""", """    with transaction.atomic():
        _truncar_tabla(MovPos)
        MovPos.objects.bulk_create(registros, batch_size=1000)
        if guardar_historico:
            MovPosHistorico.objects.bulk_create(registros_historico, batch_size=1000)""")


# Task Main function
task_func_old = """    try:
        # ── 1. Posiciones (argIndex=1) ─────────────────────────────────────
        logger.info("Descargando Posiciones (argIndex=1)...")
        csv_posiciones = _ejecutar_script_node(1, download_dir, script_path)
        csv_posiciones_corregido = _corregir_csv(csv_posiciones, script_path)
        total_posiciones = _importar_csv_posiciones(csv_posiciones_corregido)
        resultados["posiciones"] = total_posiciones

        # ── 2. Empleados Completos (argIndex=6) ────────────────────────────
        logger.info("Descargando Empleados Completos (argIndex=6)...")
        csv_completos = _ejecutar_script_node(6, download_dir, script_path)
        csv_completos_corregido = _corregir_csv(csv_completos, script_path)
        total_completos = _importar_csv_empleados_completos(csv_completos_corregido)
        resultados["empleados_completos"] = total_completos

        # ── 3. Empleados Bajas (argIndex=3) ────────────────────────────────
        logger.info("Descargando Empleados Bajas (argIndex=3)...")
        csv_bajas = _ejecutar_script_node(3, download_dir, script_path)
        csv_bajas_corregido = _corregir_csv(csv_bajas, script_path)
        total_bajas = _importar_csv_bajas(csv_bajas_corregido)
        resultados["empleados_bajas"] = total_bajas

        duracion = round(time.time() - inicio, 1)
        logger.info(
            "=== Tarea completada en %.1fs | Posiciones: %d | Completos: %d | Bajas: %d ===",
            duracion,
            total_posiciones,
            total_completos,
            total_bajas,
        )
        return {
            "status": "ok",
            "duracion_segundos": duracion,
            **resultados,
        }

    except Exception as exc:
        logger.error("Error en importar_zafiro: %s", exc, exc_info=True)
        raise self.retry(exc=exc)"""

from datetime import datetime
task_func_new = """    from datetime import datetime
    ahora = datetime.now()
    # Si son las 23:00 o más tarde, consideramos que es el último run del día para el histórico
    es_historico = ahora.hour >= 23

    try:
        # ── 1. Posiciones (argIndex=1) ─────────────────────────────────────
        logger.info("Descargando Posiciones (argIndex=1)...")
        csv_posiciones = _ejecutar_script_node(1, download_dir, script_path)
        csv_posiciones_corregido = _corregir_csv(csv_posiciones, script_path)
        total_posiciones = _importar_csv_posiciones(csv_posiciones_corregido, es_historico)
        resultados["posiciones"] = total_posiciones

        # ── 2. Empleados Completos (argIndex=6) ────────────────────────────
        logger.info("Descargando Empleados Completos (argIndex=6)...")
        csv_completos = _ejecutar_script_node(6, download_dir, script_path)
        csv_completos_corregido = _corregir_csv(csv_completos, script_path)
        total_completos = _importar_csv_empleados_completos(csv_completos_corregido, es_historico)
        resultados["empleados_completos"] = total_completos

        # ── 3. Empleados Bajas (argIndex=3) ────────────────────────────────
        logger.info("Descargando Empleados Bajas (argIndex=3)...")
        csv_bajas = _ejecutar_script_node(3, download_dir, script_path)
        csv_bajas_corregido = _corregir_csv(csv_bajas, script_path)
        total_bajas = _importar_csv_bajas(csv_bajas_corregido, es_historico)
        resultados["empleados_bajas"] = total_bajas

        duracion = round(time.time() - inicio, 1)
        
        # Guardar éxito en ZafiroBitacora
        ZafiroBitacora.objects.create(
            duracion_segundos=duracion,
            registros_posiciones=total_posiciones,
            registros_completos=total_completos,
            registros_bajas=total_bajas,
            status="EXITO",
            es_historico=es_historico
        )

        logger.info(
            "=== Tarea completada en %.1fs | Posiciones: %d | Completos: %d | Bajas: %d ===",
            duracion,
            total_posiciones,
            total_completos,
            total_bajas,
        )
        return {
            "status": "ok",
            "duracion_segundos": duracion,
            **resultados,
        }

    except Exception as exc:
        duracion = round(time.time() - inicio, 1)
        ZafiroBitacora.objects.create(
            duracion_segundos=duracion,
            status="ERROR",
            error_message=str(exc),
            es_historico=False
        )
        logger.error("Error en importar_zafiro: %s", exc, exc_info=True)
        raise self.retry(exc=exc)"""

content = content.replace(task_func_old, task_func_new)

with open("plantilla/tasks.py", "w") as f:
    f.write(content)
