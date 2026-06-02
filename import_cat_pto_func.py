import os
import sys
import csv
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eje_central_back.settings")
django.setup()

from plantilla.models import CatPtoFunc

CSV_PATH = '/home/edgar/CAT_PTO_FUNC.csv'

def clean_val(val):
    if not val:
        return None
    val_stripped = val.strip()
    if val_stripped == '' or val_stripped.lower() == 'null':
        return None
    return val_stripped

def run():
    print("Reading CSV and clearing existing CatPtoFunc records...")
    # Clear existing records
    deleted_count, _ = CatPtoFunc.objects.all().delete()
    print(f"Cleared {deleted_count} existing records.")

    # Map headers to model fields
    mapping = {
        'Cd Pto Funcional': 'cd_pto_funcional',
        'Nombre Puesto Funcional': 'nombre_puesto_funcional',
        'CdNorm': 'cd_norm'
    }

    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        batch = []
        count = 0
        for row in reader:
            # Map columns
            kwargs = {}
            for csv_col, model_field in mapping.items():
                val = row.get(csv_col, None)
                kwargs[model_field] = clean_val(val)
            
            batch.append(CatPtoFunc(**kwargs))
            
            if len(batch) >= 500:
                CatPtoFunc.objects.bulk_create(batch)
                count += len(batch)
                print(f"Imported {count} records...")
                batch = []
        
        if batch:
            CatPtoFunc.objects.bulk_create(batch)
            count += len(batch)
            print(f"Imported {count} records...")

    print("Import finished successfully!")

if __name__ == '__main__':
    run()
