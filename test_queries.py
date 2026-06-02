import os
import django
import sys
from django.db import connection

sys.path.append('/home/edgar/ANAM/EjeCentral/eje_central_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

def main():
    from plantilla.models import MovPos
    table_name = MovPos._meta.db_table

    query_active = f"""
    SELECT COUNT(*) FROM (
        SELECT `Nº Pos Actual`, `Estado Psn`,
               ROW_NUMBER() OVER (
                   PARTITION BY `Nº Pos Actual` 
                   ORDER BY `F Efva` DESC, `Fecha Captura` DESC, `F/H Últ Actz` DESC, id DESC
               ) as rn
        FROM {table_name}
    ) ranked
    WHERE rn = 1 AND `Estado Psn` = 'A';
    """
    
    query_inactive = f"""
    SELECT COUNT(*) FROM (
        SELECT `Nº Pos Actual`, `Estado Psn`,
               ROW_NUMBER() OVER (
                   PARTITION BY `Nº Pos Actual` 
                   ORDER BY `F Efva` DESC, `Fecha Captura` DESC, `F/H Últ Actz` DESC, id DESC
               ) as rn
        FROM {table_name}
    ) ranked
    WHERE rn = 1 AND `Estado Psn` = 'I';
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query_active)
            active_count = cursor.fetchone()[0]
            
            cursor.execute(query_inactive)
            inactive_count = cursor.fetchone()[0]
            
            print(f"Nuevas Activas: {active_count}")
            print(f"Nuevas Inactivas: {inactive_count}")
    except Exception as e:
        print(f"Error con ROW_NUMBER: {e}")

if __name__ == '__main__':
    main()
