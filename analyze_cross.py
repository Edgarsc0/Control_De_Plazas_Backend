import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

from plantilla.models import EmpleadosCompletosSig, MovPos
from django.db.models.expressions import RawSQL

LATEST_MOVPOS_RAW_SQL = """
    SELECT id FROM (
        SELECT id, ROW_NUMBER() OVER (
            PARTITION BY `Nº Pos Actual` 
            ORDER BY `F Efva` DESC, `Fecha Captura` DESC, `F/H Últ Actz` DESC, id DESC
        ) as rn
        FROM MOV_POS
    ) ranked WHERE rn = 1
"""

sub = RawSQL(LATEST_MOVPOS_RAW_SQL, [])

# 1. Obtener los codigos de posiciones activas
active_pos_qs = MovPos.objects.filter(id__in=sub, estado_psn='A').values_list('no_pos_actual', flat=True)
active_pos_set = set(active_pos_qs)

print(f"Total de Posiciones Activas en MOV_POS: {len(active_pos_set)}")

# 2. Obtener los codigos de posiciones en EmpleadosCompletosSig
empleados_pos_qs = EmpleadosCompletosSig.objects.values_list('posicion', flat=True)
empleados_pos_set = set(empleados_pos_qs)

print(f"Total de Posiciones en Empleados Completos SIG: {len(empleados_pos_set)}")

# 3. Cruzar ambos
cruce = active_pos_set.intersection(empleados_pos_set)
print(f"Posiciones Activas que SÍ ESTÁN en Empleados Completos: {len(cruce)}")

# 4. Diferencias
activas_no_empleados = active_pos_set - empleados_pos_set
print(f"Posiciones Activas que NO ESTÁN en Empleados Completos (Fantasmas/Huecos): {len(activas_no_empleados)}")

empleados_no_activas = empleados_pos_set - active_pos_set
print(f"Posiciones en Empleados Completos que NO SON ACTIVAS en MOV_POS (Discrepancia DB): {len(empleados_no_activas)}")

