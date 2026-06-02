import os
import django
import sys

sys.path.append('/home/edgar/ANAM/EjeCentral/eje_central_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

from plantilla.models import Plantilla1800Plazas

ocupadas_2026 = Plantilla1800Plazas.objects.filter(
    posición__startswith='2026'
).exclude(rfc__isnull=True).exclude(rfc__exact='') \
 .exclude(curp__isnull=True).exclude(curp__exact='') \
 .exclude(num_empleado__isnull=True).exclude(num_empleado__exact='') \
 .exclude(nombres__isnull=True).exclude(nombres__exact='') \
 .count()

print("Ocupadas 2026:", ocupadas_2026)
