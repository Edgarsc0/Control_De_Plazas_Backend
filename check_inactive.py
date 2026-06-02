import os
import django
import sys
from django.db import connection

# Setup django
sys.path.append('/home/edgar/ANAM/EjeCentral/eje_central_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

def main():
    txt_path = '/home/edgar/.gemini/antigravity-cli/brain/6137966f-76f6-4d54-a854-71ca87156e97/scratch/comparacion_plazas.txt'
    
    # 1. Leer las posiciones que están en BD pero no en Excel desde el archivo txt
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

    print(f"Leídas {len(in_db_not_excel)} posiciones (BD pero no Excel).")

    # 2. Obtener las posiciones inactivas con la nueva query (ROW_NUMBER)
    from plantilla.models import MovPos
    table_name = MovPos._meta.db_table

    query = f"""
    SELECT m.`Nº Pos Actual`
    FROM {table_name} m
    INNER JOIN (
        SELECT id FROM (
            SELECT id, ROW_NUMBER() OVER (
                PARTITION BY `Nº Pos Actual` 
                ORDER BY `F Efva` DESC, `Fecha Captura` DESC, `F/H Últ Actz` DESC, id DESC
            ) as rn
            FROM {table_name}
        ) ranked WHERE rn = 1
    ) latest ON m.id = latest.id
    WHERE m.`Estado Psn` = 'I';
    """

    inactive_positions = set()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            inactive_positions = set(str(row[0]).strip() for row in rows if row[0])
    except Exception as e:
        print(f"Error ejecutando query: {e}")
        return

    print(f"Total posiciones inactivas en BD (Nueva Lógica): {len(inactive_positions)}")

    # 3. Intersecar ambos conjuntos
    intersection = in_db_not_excel.intersection(inactive_positions)
    
    print(f"\nResultado: De las {len(in_db_not_excel)} posiciones que NO están en Excel,")
    print(f"hay EXACTAMENTE {len(intersection)} que son INACTIVAS según la nueva query.")
    
    # Las que sobran (activas)
    activas_faltantes = in_db_not_excel - inactive_positions
    print(f"Esto nos deja con {len(activas_faltantes)} posiciones verdaderamente ACTIVAS que faltan en el Excel.")
    
    # 4. Guardar resultados
    out_file = '/home/edgar/.gemini/antigravity-cli/brain/6137966f-76f6-4d54-a854-71ca87156e97/scratch/inactivas_no_excel_v2.txt'
    with open(out_file, 'w') as f:
        f.write(f"Posiciones Inactivas (NUEVA LOGICA) que NO aparecen en el Excel: {len(intersection)}\n\n")
        for p in sorted(intersection):
            f.write(f"{p}\n")

    out_file_activas = '/home/edgar/.gemini/antigravity-cli/brain/6137966f-76f6-4d54-a854-71ca87156e97/scratch/activas_no_excel_v2.txt'
    with open(out_file_activas, 'w') as f:
        f.write(f"Posiciones ACTIVAS (NUEVA LOGICA) que NO aparecen en el Excel: {len(activas_faltantes)}\n\n")
        for p in sorted(activas_faltantes):
            f.write(f"{p}\n")
            
    print(f"Detalle inactivas guardado en: {out_file}")
    print(f"Detalle activas guardado en: {out_file_activas}")

if __name__ == '__main__':
    main()
