import os
import django
import sys
import pandas as pd
from django.db import connection

sys.path.append('/home/edgar/ANAM/EjeCentral/eje_central_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

def main():
    positions = [
        '10390001', '10390002', '10390003', '10390004', '10390005',
        '10390007', '10390008', '10390009', '103L0031', '103L0113',
        '103L0115', '103L0116', '103L0117', '103L0118', '103L0119',
        '103L0120', '103L0121', '103L0122', '20190463', '20190563'
    ]
    
    pos_in_clause = ', '.join([f"'{p}'" for p in positions])

    query = f"""
    SELECT * FROM (
        SELECT m.*, 
               ROW_NUMBER() OVER (
                   PARTITION BY `Nº Pos Actual` 
                   ORDER BY `F Efva` DESC, `Fecha Captura` DESC, `F/H Últ Actz` DESC, id DESC
               ) as rn
        FROM MOV_POS m
        WHERE `Nº Pos Actual` IN ({pos_in_clause})
    ) ranked
    WHERE rn = 1;
    """

    try:
        df = pd.read_sql(query, connection)
        
        # Save to CSV for the user
        out_file_csv = '/home/edgar/.gemini/antigravity-cli/brain/6137966f-76f6-4d54-a854-71ca87156e97/scratch/detalle_20_activas.csv'
        out_file_html = '/home/edgar/.gemini/antigravity-cli/brain/6137966f-76f6-4d54-a854-71ca87156e97/scratch/detalle_20_activas.html'
        
        df.to_csv(out_file_csv, index=False)
        df.to_html(out_file_html, index=False, classes='table table-striped')
        
        print(f"Exportados {len(df)} registros.")
        print(f"CSV guardado en: {out_file_csv}")
    except Exception as e:
        print(f"Error ejecutando query: {e}")

if __name__ == '__main__':
    main()
