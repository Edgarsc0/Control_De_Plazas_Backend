import os
import django
import sys
from django.db import connection

sys.path.append('/home/edgar/ANAM/EjeCentral/eje_central_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

def main():
    txt_path = '/home/edgar/.gemini/antigravity-cli/brain/6137966f-76f6-4d54-a854-71ca87156e97/scratch/comparacion_plazas.txt'
    
    # 1. Posiciones en BD pero no en Excel
    in_db_not_excel = set()
    reading = False
    try:
        with open(txt_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("--- Posiciones en Base de Datos pero NO en Excel"):
                    reading = True
                    continue
                elif line.startswith("--- Posiciones en Excel pero NO en Base de Datos"):
                    reading = False
                    continue
                
                if reading and line and line != "(Ninguna)":
                    in_db_not_excel.add(line)
    except Exception as e:
        print(f"Error reading txt file: {e}")
        return

    # 2. Inactivas de la BD según la query del usuario
    from plantilla.models import MovPos
    table_name = MovPos._meta.db_table
    query = f"""
    SELECT m.`Nº Pos Actual`
    FROM {table_name} m
    INNER JOIN (
        SELECT `Nº Pos Actual`, MAX(id) AS max_id
        FROM {table_name}
        GROUP BY `Nº Pos Actual`
    ) latest ON m.id = latest.max_id
    WHERE m.`Estado Psn` = 'I';
    """

    inactive_positions = set()
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        inactive_positions = set(str(row[0]).strip() for row in rows if row[0])

    # 3. La diferencia: in_db_not_excel MENOS inactive_positions
    missing_active = in_db_not_excel - inactive_positions
    
    print(f"Total en BD pero no en Excel: {len(in_db_not_excel)}")
    print(f"Total de esas que SÍ son Inactivas: {len(in_db_not_excel.intersection(inactive_positions))}")
    print(f"Total restantes (Tus activas faltantes): {len(missing_active)}")

    out_file = '/home/edgar/.gemini/antigravity-cli/brain/6137966f-76f6-4d54-a854-71ca87156e97/scratch/activas_no_excel.txt'
    with open(out_file, 'w') as f:
        f.write(f"Posiciones que ESTÁN en BD, NO están en Excel y NO están inactivas ({len(missing_active)}):\n\n")
        for p in sorted(missing_active):
            f.write(f"{p}\n")
            
    print(f"El detalle ha sido guardado en: {out_file}")

if __name__ == '__main__':
    main()
