import os
import django
import sys
import pandas as pd
from django.db import connection

sys.path.append('/home/edgar/ANAM/EjeCentral/eje_central_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

def main():
    excel_path = '/home/edgar/Descargas/25 05 Movimientos 0948.xls'

    # 1. Excel pos
    try:
        try:
            df = pd.read_excel(excel_path, sheet_name='Plazas')
            if 'Nº Pos Actual' not in df.columns:
                df = pd.read_excel(excel_path, sheet_name='Plazas', header=1)
        except Exception:
            dfs = pd.read_html(excel_path)
            df = None
            for d in dfs:
                if 'Nº Pos Actual' in d.columns:
                    df = d
                    break
                elif len(d) > 1 and 'Nº Pos Actual' in d.iloc[0].values:
                    d.columns = d.iloc[0]
                    df = d[1:]
                    break
                elif len(d) > 2 and 'Nº Pos Actual' in d.iloc[1].values:
                    d.columns = d.iloc[1]
                    df = d[2:]
                    break

        excel_pos = set(df['Nº Pos Actual'].dropna().astype(str).str.strip())
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        return

    # 2. Inactive positions from DB
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

    # 3. Intersect (Inactive AND In Excel)
    intersection = inactive_positions.intersection(excel_pos)
    
    print(f"Posiciones Inactivas en BD que SI están en Excel: {len(intersection)}")
    for p in intersection:
        print(f"-> {p}")

if __name__ == '__main__':
    main()
