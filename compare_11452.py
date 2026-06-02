import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

import pandas as pd
from plantilla.models import MovPos
from django.db.models import Subquery
from django.db.models.expressions import RawSQL

LATEST_MOVPOS_RAW_SQL = """
    SELECT id FROM (
        SELECT id, ROW_NUMBER() OVER (
            PARTITION BY `Nº Pos Actual`
            ORDER BY `F Efva` DESC, `Fecha Captura` DESC, `F/H Últ Actz` DESC, id DESC
        ) as rn
        FROM MOV_POS
    ) ranked WHERE rn = 1
"""

# Get exactly the 11452 active positions according to the UI logic
sub = RawSQL(LATEST_MOVPOS_RAW_SQL, [])
active_positions_qs = MovPos.objects.filter(id__in=sub, estado_psn='A')
print(f"Total registros activos en DB (LATEST_MOVPOS_RAW_SQL): {active_positions_qs.count()}")

db_pos = set(active_positions_qs.values_list('no_pos_actual', flat=True))

# Load Excel
excel_path = '/home/edgar/Descargas/25 05 Movimientos 0948.xls'
df = pd.read_excel(excel_path, sheet_name='Plazas')
if 'Nº Pos Actual' not in df.columns:
    df = pd.read_excel(excel_path, sheet_name='Plazas', header=1)
excel_pos = set(df['Nº Pos Actual'].dropna().astype(str).str.strip())
print(f"Total posiciones en Excel: {len(excel_pos)}")

# Find missing
missing = db_pos - excel_pos
print(f"Posiciones activas en DB pero NO en Excel: {len(missing)}")

missing_list = sorted(list(missing))
print("Ejemplos:", missing_list)

with open('/home/edgar/.gemini/antigravity-cli/brain/6137966f-76f6-4d54-a854-71ca87156e97/scratch/activas_no_excel_final.txt', 'w') as f:
    for m in missing_list:
        f.write(m + '\n')
print(f"Guardadas en activas_no_excel_final.txt")

