import os
import django
import sys
sys.path.append('/home/edgar/ANAM/EjeCentral/eje_central_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

from plantilla.models import EmpleadosCompletosSig, MovPos
from django.db.models import Max, Subquery, Q

sub = MovPos.objects.values('no_pos_actual').annotate(max_id=Max('id')).values('max_id')
active_position_codes = MovPos.objects.filter(id__in=Subquery(sub), estado_psn='A').values('no_pos_actual')

queryset = EmpleadosCompletosSig.objects.filter(
    posicion__in=Subquery(active_position_codes)
).exclude(
    Q(dependencia_directa__isnull=True) | Q(dependencia_directa='')
)
registros = list(queryset.values())
print(f"Total registros: {len(registros)}")

node_map = {}
for r in registros:
    node_map[r['posicion']] = r

roots = 0
for r in registros:
    dep = r.get('dependencia_directa')
    if dep:
        dep = dep.strip()
    pos = r.get('posicion')
    if not dep or dep == pos or dep not in node_map:
        roots += 1

print(f"Total roots: {roots}")
