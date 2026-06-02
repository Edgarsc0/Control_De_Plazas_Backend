import os
import django
import sys
from django.db import connection
from django.db.models.expressions import RawSQL

sys.path.append('/home/edgar/ANAM/EjeCentral/eje_central_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

def main():
    from plantilla.models import MovPos
    
    sub_sql = """
        SELECT id FROM (
            SELECT id, 
                   ROW_NUMBER() OVER (
                       PARTITION BY `Nº Pos Actual` 
                       ORDER BY `F Efva` DESC, `Fecha Captura` DESC, `F/H Últ Actz` DESC, id DESC
                   ) as rn
            FROM plantilla_movpos
        ) ranked
        WHERE rn = 1
    """
    
    active_qs = MovPos.objects.filter(id__in=RawSQL(sub_sql, []), estado_psn='A')
    
    print(f"Total Active via ORM + RawSQL: {active_qs.count()}")
    
if __name__ == '__main__':
    main()
