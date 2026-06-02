import os
import django
import sys

sys.path.append('/home/edgar/ANAM/EjeCentral/eje_central_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

from django.db import connection

def main():
    positions = [
        '10390001', '10390002', '10390003', '10390004', '10390005',
        '10390007', '10390008', '10390009', '103L0031', '103L0113',
        '103L0115', '103L0116', '103L0117', '103L0118', '103L0119',
        '103L0120', '103L0121', '103L0122', '20190463', '20190563'
    ]
    
    pos_str = ",".join([f"'{p}'" for p in positions])
    
    query = f"""
        SELECT `Posición`, `Estado Nómina`, `nombres`
        FROM EMPLEADOS_COMPLETOS_SIG
        WHERE `Posición` IN ({pos_str})
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        
    print(f"Total encontradas en EmpleadosCompletosSig: {len(rows)}")
    
    ocupadas = [r for r in rows if str(r[1]).strip() != '']
    print(f"De esas, tienen Estado de Nomina DISTINTO a vacio (Están ocupadas): {len(ocupadas)}")
    
    if ocupadas:
        print("\nDetalle de las Ocupadas:")
        for r in ocupadas:
            print(f"- {r[0]} | Estado: '{r[1]}' | Empleado: {r[2]}")

if __name__ == '__main__':
    main()
