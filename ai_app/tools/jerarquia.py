from django.db import connection
from django.db.models import Q
from plantilla.models import EmpleadosCompletosSig
from ._base import tool_handler

@tool_handler(max_output_chars=6000)
def obtener_cadena_mando(query: str, direccion: str = "arriba") -> str:
    """
    Obtiene la jerarquía organizacional (cadena de mando) para un empleado o plaza.

    Permite consultar hacia arriba (jefes) o hacia abajo (subordinados).

    Args:
        query: Criterio de búsqueda (número de plaza '50001234', nombre del empleado, o ID SAP).
        direccion: Dirección de la jerarquía:
                   - 'arriba' (default): Sube por la cadena de mando hasta el puesto directivo más alto.
                   - 'abajo': Baja por la cadena de mando mostrando subordinados (hasta 5 niveles, max 50 registros).
    """
    query = query.strip()
    direccion = direccion.lower().strip()

    base = EmpleadosCompletosSig.objects.filter(
        Q(posicion=query) | Q(nombres__icontains=query) | Q(id_empleado=query)
    ).first()

    if not base:
        return f"No se encontró ningún empleado o plaza con el criterio '{query}'."

    if direccion == "abajo":
        sql = """
            WITH RECURSIVE Subordinados AS (
                SELECT
                    `Posición` AS Posicion,
                    `Nombres` AS Empleado,
                    `Nombre Puesto Funcional` AS Puesto_Funcional,
                    `Nivel` AS Nivel,
                    `DependenciaDirecta` AS Jefe_Directo,
                    1 AS Nivel_Jerarquia
                FROM EMPLEADOS_COMPLETOS_SIG
                WHERE `Posición` = %s

                UNION ALL

                SELECT
                    emp.`Posición`,
                    emp.`Nombres`,
                    emp.`Nombre Puesto Funcional`,
                    emp.`Nivel`,
                    emp.`DependenciaDirecta`,
                    sub.Nivel_Jerarquia + 1
                FROM EMPLEADOS_COMPLETOS_SIG emp
                INNER JOIN Subordinados sub ON emp.`DependenciaDirecta` = sub.Posicion
                WHERE sub.Nivel_Jerarquia < 5 -- Limitar profundidad a 5 niveles
                  AND emp.`Posición` != sub.Posicion
            )
            SELECT Posicion, Empleado, Puesto_Funcional, Nivel, Jefe_Directo, Nivel_Jerarquia
            FROM Subordinados
            ORDER BY Nivel_Jerarquia ASC, Posicion ASC
            LIMIT 50;
        """
    else:
        # Dirección arriba
        sql = """
            WITH RECURSIVE CadenaHaciaArriba AS (
                SELECT
                    `Posición` AS Posicion,
                    `Nombres` AS Empleado,
                    `Nombre Puesto Funcional` AS Puesto_Funcional,
                    `Nivel` AS Nivel,
                    `DependenciaDirecta` AS Jefe_Directo,
                    1 AS Nivel_Jerarquia
                FROM EMPLEADOS_COMPLETOS_SIG
                WHERE `Posición` = %s

                UNION ALL

                SELECT
                    jefe.`Posición`,
                    jefe.`Nombres`,
                    jefe.`Nombre Puesto Funcional`,
                    jefe.`Nivel`,
                    jefe.`DependenciaDirecta`,
                    empleado.Nivel_Jerarquia + 1
                FROM EMPLEADOS_COMPLETOS_SIG jefe
                INNER JOIN CadenaHaciaArriba empleado ON jefe.`Posición` = empleado.Jefe_Directo
                WHERE empleado.Jefe_Directo IS NOT NULL
                  AND empleado.Jefe_Directo != ''
                  AND empleado.Jefe_Directo != '0'
                  AND jefe.`Posición` != empleado.Posicion
            )
            SELECT Posicion, Empleado, Puesto_Funcional, Nivel, Jefe_Directo, Nivel_Jerarquia
            FROM CadenaHaciaArriba
            ORDER BY Nivel_Jerarquia ASC;
        """

    with connection.cursor() as cursor:
        cursor.execute(sql, [base.posicion])
        cols = [col[0] for col in cursor.description]
        rows = [dict(zip(cols, row)) for row in cursor.fetchall()]

    if not rows:
        return f"Sin información jerárquica para plaza {base.posicion}."

    if direccion == "abajo":
        res = f"🏛️  ORGANIGRAMA SUBORDINADO (Dirección Abajo) — {base.nombres} (Plaza: {base.posicion})\n"
        res += "════════════════════════════════════════════════════════\n"
        for r in rows:
            # indentamos de acuerdo al nivel de jerarquía
            indent = "  " * (r["Nivel_Jerarquia"] - 1)
            arrow = "└─ " if r["Nivel_Jerarquia"] > 1 else "👤 "
            res += f"{indent}{arrow}{r['Empleado'] or 'VACANTE'} [{r['Posicion']}]\n"
            res += f"{indent}   Puesto: {r['Puesto_Funcional'] or 'N/A'} | Nivel: {r['Nivel'] or 'N/A'}\n"
    else:
        res = f"🏛️  CADENA DE MANDO (Dirección Arriba) — {base.nombres} (Plaza: {base.posicion})\n"
        res += "════════════════════════════════════════════════════════\n"
        for r in rows:
            indent = "  " * (r["Nivel_Jerarquia"] - 1)
            arrow = "└─ " if r["Nivel_Jerarquia"] > 1 else "👤 "
            res += f"{indent}{arrow}{r['Empleado'] or 'VACANTE'} [{r['Posicion']}]\n"
            res += f"{indent}   Puesto: {r['Puesto_Funcional'] or 'N/A'} | Nivel: {r['Nivel'] or 'N/A'}\n"

    return res.strip()
