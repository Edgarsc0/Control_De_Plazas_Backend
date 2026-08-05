"""
Edición manual de celdas de EMPLEADOS_COMPLETOS_SIG vía CeldaOverride.

EMPLEADOS_COMPLETOS_SIG se trunca y recarga completa en cada `importar_zafiro`
(cada 30 min, ver tasks.py), así que cualquier UPDATE manual se perdería en la
siguiente corrida si no se registrara aparte. `registrar_y_aplicar_override_empleado`
guarda el cambio en CeldaOverride y lo aplica de inmediato sobre la tabla viva;
`aplicar_overrides_empleados_completos` lo reaplica tras cada import (mismo
patrón que `tasks._reaplicar_prioridad_nivel_jerarquico`).
"""

import hashlib
import json

from django.db import connection, transaction

from .models import CeldaOverride, DatosPersonales, EmpleadosCompletosSig, EmpleadosCompletosSigBase

TABLA_EMPLEADOS = "EMPLEADOS_COMPLETOS_SIG"

EDITABLE_COLUMNS_EMPLEADOS = {
    f.name
    for f in EmpleadosCompletosSigBase._meta.get_fields()
    if f.name not in ("id", "posicion")
}

TABLA_DATOS_PERSONALES = "DATOS_PERSONALES"

# Sólo Escolaridad/Contacto/Domicilio (ver EmployeeRecordModal.jsx,
# DATOS_PERSONALES_GROUPS) — el resto de DATOS_PERSONALES (identificación,
# puesto/adscripción) no es editable desde este permiso.
EDITABLE_COLUMNS_DATOS_PERSONALES = {
    "escolaridad_tipo", "escolaridad_nivrl", "escolaridad_area", "carrera", "centro_escolar",
    "phone", "phone1", "extension", "email_addr", "email_addr2",
    "calle", "hr_numero_exterior", "hr_numero_interior", "colonia", "postal", "hr_municipio", "estado",
}


def compute_clave_hash(clave_negocio: dict) -> str:
    return hashlib.sha256(
        json.dumps(clave_negocio, sort_keys=True).encode()
    ).hexdigest()


def registrar_y_aplicar_override_empleado(posicion, columna, valor_nuevo, usuario):
    """
    Registra la edición en CeldaOverride y la aplica de inmediato sobre
    EMPLEADOS_COMPLETOS_SIG, todo en una transacción:
      1. Valida que `columna` sea editable.
      2. Bloquea (select_for_update) y lee la fila viva para capturar
         `valor_original` (lo que se está a punto de sobreescribir, sea el
         dato original de ZAFIRO o un override previo ya aplicado).
      3. Desactiva el override activo previo de esa (tabla, clave, columna),
         si existe — se conserva, no se borra.
      4. Crea el nuevo CeldaOverride (activo=True).
      5. Ejecuta el UPDATE sobre EMPLEADOS_COMPLETOS_SIG.

    Lanza ValueError si la columna no es editable o la posición no existe.

    Nota: MySQL no soporta el UniqueConstraint condicional de CeldaOverride.Meta
    (Django emite W036 y no lo crea a nivel BD) — la unicidad de "un override
    activo por celda" se garantiza aquí por transacción + select_for_update
    sobre la fila de EMPLEADOS_COMPLETOS_SIG, que serializa ediciones
    concurrentes sobre la misma posición.
    """
    if columna not in EDITABLE_COLUMNS_EMPLEADOS:
        raise ValueError(f"Columna '{columna}' no es editable.")

    clave_negocio = {"posicion": posicion}
    clave_hash = compute_clave_hash(clave_negocio)

    with transaction.atomic():
        fila = (
            EmpleadosCompletosSig.objects.select_for_update()
            .filter(posicion=posicion)
            .first()
        )
        if fila is None:
            raise ValueError(
                f"Posición '{posicion}' no existe en EMPLEADOS_COMPLETOS_SIG."
            )

        valor_original = getattr(fila, columna)
        valor_original = None if valor_original is None else str(valor_original)
        valor_nuevo_str = None if valor_nuevo is None else str(valor_nuevo)

        CeldaOverride.objects.filter(
            tabla=TABLA_EMPLEADOS,
            clave_negocio_hash=clave_hash,
            columna=columna,
            activo=True,
        ).update(activo=False)

        override = CeldaOverride.objects.create(
            tabla=TABLA_EMPLEADOS,
            clave_negocio=clave_negocio,
            clave_negocio_hash=clave_hash,
            columna=columna,
            valor_original=valor_original,
            valor_nuevo=valor_nuevo_str,
            usuario=usuario,
            activo=True,
        )

        EmpleadosCompletosSig.objects.filter(posicion=posicion).update(
            **{columna: valor_nuevo_str}
        )

    return override


def aplicar_overrides_empleados_completos(bitacora=None):
    """
    Reaplica todos los overrides activos de EMPLEADOS_COMPLETOS_SIG sobre la
    tabla recién importada. No falla si una `posicion` ya no existe (baja,
    posición eliminada del CSV de ZAFIRO) — solo la cuenta como huérfana.
    """
    overrides = CeldaOverride.objects.filter(tabla=TABLA_EMPLEADOS, activo=True)
    aplicados, huerfanos = 0, 0
    with transaction.atomic():
        for ov in overrides:
            posicion = ov.clave_negocio.get("posicion")
            updated = EmpleadosCompletosSig.objects.filter(posicion=posicion).update(
                **{ov.columna: ov.valor_nuevo}
            )
            if updated:
                aplicados += 1
            else:
                huerfanos += 1
    return {"aplicados": aplicados, "huerfanos": huerfanos}


def registrar_y_aplicar_override_datos_personales(no_empleado, columna, valor_nuevo, usuario):
    """
    Mismo patrón que `registrar_y_aplicar_override_empleado`, pero sobre
    DATOS_PERSONALES (tab "Datos personales" del expediente, permiso
    authentication.edit_datos_personales) y con clave de negocio
    `no_empleado` en vez de `posicion`. Sólo columnas de Escolaridad/
    Contacto/Domicilio son editables (ver EDITABLE_COLUMNS_DATOS_PERSONALES).

    Lanza ValueError si la columna no es editable o el empleado no existe.
    """
    if columna not in EDITABLE_COLUMNS_DATOS_PERSONALES:
        raise ValueError(f"Columna '{columna}' no es editable.")

    clave_negocio = {"no_empleado": no_empleado}
    clave_hash = compute_clave_hash(clave_negocio)

    with transaction.atomic():
        fila = (
            DatosPersonales.objects.select_for_update()
            .filter(no_empleado=no_empleado)
            .first()
        )
        if fila is None:
            raise ValueError(
                f"Empleado '{no_empleado}' no existe en DATOS_PERSONALES."
            )

        valor_original = getattr(fila, columna)
        valor_original = None if valor_original is None else str(valor_original)
        valor_nuevo_str = None if valor_nuevo is None else str(valor_nuevo)

        if (valor_original or "").strip() == (valor_nuevo_str or "").strip():
            return None

        CeldaOverride.objects.filter(
            tabla=TABLA_DATOS_PERSONALES,
            clave_negocio_hash=clave_hash,
            columna=columna,
            activo=True,
        ).update(activo=False)

        override = CeldaOverride.objects.create(
            tabla=TABLA_DATOS_PERSONALES,
            clave_negocio=clave_negocio,
            clave_negocio_hash=clave_hash,
            columna=columna,
            valor_original=valor_original,
            valor_nuevo=valor_nuevo_str,
            usuario=usuario,
            activo=True,
        )

        DatosPersonales.objects.filter(no_empleado=no_empleado).update(
            **{columna: valor_nuevo_str}
        )

    return override


def aplicar_overrides_datos_personales(bitacora=None):
    """
    Reaplica todos los overrides activos de DATOS_PERSONALES sobre la tabla
    recién importada (blue-green swap, ver tasks._swap_blue_green_tables).
    No falla si un `no_empleado` ya no existe — solo lo cuenta como huérfano.

    Delega en el SP `sp_aplicar_overrides_datos_personales` (ya vive en la
    BD, ver eje_central_back/plantilla/sql/sp_aplicar_overrides_datos_personales.sql):
    1 UPDATE...JOIN por columna distinta corrido dentro de MySQL, en vez del
    loop en Python de antes (un UPDATE por override, uno por uno) — contra la
    BD remota eso tardaba minutos con miles de overrides activos.
    """
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                "CALL sp_aplicar_overrides_datos_personales(@aplicados, @huerfanos)"
            )
            cursor.execute("SELECT @aplicados, @huerfanos")
            aplicados, huerfanos = cursor.fetchone()

    return {"aplicados": aplicados or 0, "huerfanos": huerfanos or 0}
