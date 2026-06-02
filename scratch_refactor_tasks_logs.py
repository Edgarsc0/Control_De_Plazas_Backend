import re

with open('plantilla/tasks.py', 'r') as f:
    content = f.read()

# Add _append_log function
append_log_func = """
from django.utils import timezone

def _append_log(bitacora, mensaje, is_error=False):
    if is_error:
        logger.error(mensaje)
    else:
        logger.info(mensaje)
    
    if not bitacora:
        return
        
    timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = "[ERROR]" if is_error else "[INFO]"
    linea = f"{timestamp} {prefix} {mensaje}\\n"
    
    if bitacora.logs_en_vivo is None:
        bitacora.logs_en_vivo = linea
    else:
        bitacora.logs_en_vivo += linea
    bitacora.save(update_fields=['logs_en_vivo'])
"""

content = content.replace("# Helpers\n# ---------------------------------------------------------------------------", "# Helpers\n# ---------------------------------------------------------------------------\n" + append_log_func)

# Replace signatures of helpers
content = content.replace("def _ejecutar_script_node(arg_index: int, download_dir: str, script_path: str) -> str:", "def _ejecutar_script_node(arg_index: int, download_dir: str, script_path: str, bitacora=None) -> str:")
content = content.replace("def _corregir_csv(csv_path: str, script_path: str) -> str:", "def _corregir_csv(csv_path: str, script_path: str, bitacora=None) -> str:")
content = content.replace("def _truncar_tabla(model_class):", "def _truncar_tabla(model_class, bitacora=None):")
content = content.replace("def _importar_csv_empleados_completos(csv_path: str, guardar_historico: bool = False) -> int:", "def _importar_csv_empleados_completos(csv_path: str, guardar_historico: bool = False, bitacora=None) -> int:")
content = content.replace("def _importar_csv_bajas(csv_path: str, guardar_historico: bool = False) -> int:", "def _importar_csv_bajas(csv_path: str, guardar_historico: bool = False, bitacora=None) -> int:")
content = content.replace("def _importar_csv_posiciones(csv_path: str, guardar_historico: bool = False) -> int:", "def _importar_csv_posiciones(csv_path: str, guardar_historico: bool = False, bitacora=None) -> int:")

# Replace loggers inside helpers
content = re.sub(r'logger\.info\("CSV previo eliminado: %s", csv_path\)', r'_append_log(bitacora, f"CSV previo eliminado: {csv_path}")', content)
content = re.sub(r'logger\.info\("Ejecutando script Node\.js: argIndex=%d", arg_index\)', r'_append_log(bitacora, f"Ejecutando script Node.js: argIndex={arg_index}")', content)
content = re.sub(r'logger\.error\("Script Node\.js falló \(argIndex=%d\):\\n%s", arg_index, result\.stderr\)', r'_append_log(bitacora, f"Script Node.js falló (argIndex={arg_index}):\\n{result.stderr}", is_error=True)', content)
content = re.sub(r'logger\.info\("Script Node\.js completado \(argIndex=%d\):\\n%s", arg_index, result\.stdout\)', r'_append_log(bitacora, f"Script Node.js completado (argIndex={arg_index})")', content) # Avoid printing the whole stdout in the UI as it's too big, just the completion

content = re.sub(r'logger\.warning\("Corrector heurístico no encontrado en %s\. Se usará el archivo original\.", corrector_exe\)', r'_append_log(bitacora, f"Corrector heurístico no encontrado en {corrector_exe}. Se usará el archivo original.")', content)
content = re.sub(r'logger\.warning\("No se pudo eliminar el archivo de salida previo %s: %s", output_path, e\)', r'_append_log(bitacora, f"No se pudo eliminar el archivo de salida previo {output_path}: {e}")', content)
content = re.sub(r'logger\.info\("Ejecutando corrector heurístico para: %s", csv_path\)', r'_append_log(bitacora, f"Ejecutando corrector heurístico para: {csv_path}")', content)
content = re.sub(r'logger\.info\("Corrector completado\. Se usará el archivo corregido: %s", output_path\)', r'_append_log(bitacora, f"Corrector completado. Se usará el archivo corregido: {output_path}")', content)
content = re.sub(r'logger\.info\("Corrector completado \(no se encontraron errores, se usará el original\)\."\)', r'_append_log(bitacora, "Corrector completado (no se encontraron errores, se usará el original).")', content)
content = re.sub(r'logger\.error\("Corrector heurístico falló \(código %d\):\\n%s", result\.returncode, result\.stderr\)', r'_append_log(bitacora, f"Corrector heurístico falló (código {result.returncode}):\\n{result.stderr}", is_error=True)', content)
content = re.sub(r'logger\.error\("Error al ejecutar corrector heurístico: %s", e, exc_info=True\)', r'_append_log(bitacora, f"Error al ejecutar corrector heurístico: {e}", is_error=True)', content)

content = re.sub(r'logger\.info\("Tabla truncada: %s", table\)', r'_append_log(bitacora, f"Tabla truncada: {table}")', content)

content = re.sub(r'logger\.info\("EmpleadosCompletosSig: %d registros insertados\.", len\(registros\)\)', r'_append_log(bitacora, f"EmpleadosCompletosSig: {len(registros)} registros insertados.")', content)
content = re.sub(r'logger\.info\("BajasSig: %d registros insertados\.", len\(registros\)\)', r'_append_log(bitacora, f"BajasSig: {len(registros)} registros insertados.")', content)
content = re.sub(r'logger\.info\("MovPos: %d registros insertados\.", len\(registros\)\)', r'_append_log(bitacora, f"MovPos: {len(registros)} registros insertados.")', content)

# Modify importar_zafiro calls to pass bitacora
content = content.replace("csv_posiciones = _ejecutar_script_node(1, download_dir, script_path)", "csv_posiciones = _ejecutar_script_node(1, download_dir, script_path, bitacora)")
content = content.replace("csv_posiciones_corregido = _corregir_csv(csv_posiciones, script_path)", "csv_posiciones_corregido = _corregir_csv(csv_posiciones, script_path, bitacora)")
content = content.replace("total_posiciones = _importar_csv_posiciones(csv_posiciones_corregido, es_historico)", "total_posiciones = _importar_csv_posiciones(csv_posiciones_corregido, es_historico, bitacora)")

content = content.replace("csv_completos = _ejecutar_script_node(6, download_dir, script_path)", "csv_completos = _ejecutar_script_node(6, download_dir, script_path, bitacora)")
content = content.replace("csv_completos_corregido = _corregir_csv(csv_completos, script_path)", "csv_completos_corregido = _corregir_csv(csv_completos, script_path, bitacora)")
content = content.replace("total_completos = _importar_csv_empleados_completos(csv_completos_corregido, es_historico)", "total_completos = _importar_csv_empleados_completos(csv_completos_corregido, es_historico, bitacora)")

content = content.replace("csv_bajas = _ejecutar_script_node(3, download_dir, script_path)", "csv_bajas = _ejecutar_script_node(3, download_dir, script_path, bitacora)")
content = content.replace("csv_bajas_corregido = _corregir_csv(csv_bajas, script_path)", "csv_bajas_corregido = _corregir_csv(csv_bajas, script_path, bitacora)")
content = content.replace("total_bajas = _importar_csv_bajas(csv_bajas_corregido, es_historico)", "total_bajas = _importar_csv_bajas(csv_bajas_corregido, es_historico, bitacora)")

content = content.replace("_truncar_tabla(MovPos)", "_truncar_tabla(MovPos, bitacora)")
content = content.replace("_truncar_tabla(EmpleadosCompletosSig)", "_truncar_tabla(EmpleadosCompletosSig, bitacora)")
content = content.replace("_truncar_tabla(BajasSig)", "_truncar_tabla(BajasSig, bitacora)")

# Refactor the start of importar_zafiro to create the bitacora
importar_zafiro_start = """
    logger.info("=== Iniciando tarea importar_zafiro ===")
    inicio = time.time()

    # Asegurar que el directorio de descarga existe
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    from datetime import datetime
    ahora = datetime.now()
    # Si son las 23:00 o más tarde, consideramos que es el último run del día para el histórico
    es_historico = ahora.hour >= 23

    bitacora = ZafiroBitacora.objects.create(
        status="RUNNING",
        es_historico=es_historico,
        logs_en_vivo=""
    )
    _append_log(bitacora, "=== Iniciando tarea importar_zafiro ===")
    
    try:
        # ── 1. Posiciones (argIndex=1) ─────────────────────────────────────
        _append_log(bitacora, "Descargando Posiciones (argIndex=1)...")
"""

content = re.sub(
    r'    logger\.info\("=== Iniciando tarea importar_zafiro ==="\).*?logger\.info\("Descargando Posiciones \(argIndex=1\)\.\.\."\)',
    importar_zafiro_start,
    content,
    flags=re.DOTALL
)

content = content.replace('logger.info("Descargando Empleados Completos (argIndex=6)...")', '_append_log(bitacora, "Descargando Empleados Completos (argIndex=6)...")')
content = content.replace('logger.info("Descargando Empleados Bajas (argIndex=3)...")', '_append_log(bitacora, "Descargando Empleados Bajas (argIndex=3)...")')

# Refactor the end of importar_zafiro
importar_zafiro_end = """
        duracion = round(time.time() - inicio, 1)
        
        # Guardar éxito en ZafiroBitacora
        bitacora.duracion_segundos = duracion
        bitacora.registros_posiciones = total_posiciones
        bitacora.registros_completos = total_completos
        bitacora.registros_bajas = total_bajas
        bitacora.status = "EXITO"
        bitacora.save()

        _append_log(
            bitacora,
            f"=== Tarea completada en {duracion}s | Posiciones: {total_posiciones} | Completos: {total_completos} | Bajas: {total_bajas} ==="
        )
"""
content = re.sub(
    r'        duracion = round\(time\.time\(\) - inicio, 1\).*?logger\.info\(.*?total_bajas,.*?        \)',
    importar_zafiro_end,
    content,
    flags=re.DOTALL
)

importar_zafiro_except = """
    except Exception as exc:
        duracion = round(time.time() - inicio, 1)
        bitacora.duracion_segundos = duracion
        bitacora.status = "ERROR"
        bitacora.error_message = str(exc)
        bitacora.save()
        _append_log(bitacora, f"Error en importar_zafiro: {exc}", is_error=True)
        raise self.retry(exc=exc)
"""
content = re.sub(
    r'    except Exception as exc:.*?raise self\.retry\(exc=exc\)',
    importar_zafiro_except,
    content,
    flags=re.DOTALL
)

with open('plantilla/tasks.py', 'w') as f:
    f.write(content)
