import os
import sys
import django
from django.db.models import Q, Count

sys.path.append("/home/edgar/ANAM/EjeCentral/eje_central_back")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eje_central_back.settings")
django.setup()

from plantilla.models import Plantilla1800Plazas

def main():
    qs = Plantilla1800Plazas.objects.filter(nivel="P33").filter(
        Q(of_de_solicitud__isnull=True) | Q(of_de_solicitud="") | Q(of_de_solicitud="(vacío)")
    )
    
    print(f"Total empty-office P33 plazas: {qs.count()}")
    
    # ¿Cuántas tienen número de empleado asignado?
    con_num = qs.exclude(num_empleado__isnull=True).exclude(num_empleado="").exclude(num_empleado="Sin Número")
    print(f"Plazas con número de empleado no nulo/vacío: {con_num.count()}")
    
    for p in con_num[:10]:
        print(f"  - ID: {p.id}, Pos: {repr(p.posición)}, NumEmp: {repr(p.num_empleado)}, RFC: {repr(p.rfc)}, Nombre: {repr(p.nombres)}")

    # ¿Cuántas tienen nombres asignados?
    con_nombre = qs.exclude(nombres__isnull=True).exclude(nombres="").exclude(nombres="VACANTE").exclude(nombres="Vacante")
    print(f"Plazas con nombre de empleado no nulo/vacante: {con_nombre.count()}")
    for p in con_nombre[:10]:
        print(f"  - ID: {p.id}, Pos: {repr(p.posición)}, NumEmp: {repr(p.num_empleado)}, Nombre: {repr(p.nombres)}")

if __name__ == "__main__":
    main()
