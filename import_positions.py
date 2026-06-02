import os
import sys
import csv
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eje_central_back.settings")
django.setup()

from plantilla.models import MovPos

CSV_PATH = '/home/edgar/Descargas/12_05_26_08_55_AM/posiciones.csv'

def clean_val(val):
    if not val:
        return None
    val_stripped = val.strip()
    if val_stripped == '' or val_stripped.lower() == 'null':
        return None
    return val_stripped

def run():
    print("Reading CSV and clearing existing MovPos records...")
    # Clear existing records
    deleted_count, _ = MovPos.objects.all().delete()
    print(f"Cleared {deleted_count} existing records.")

    # Map headers to model fields
    mapping = {
        'POSICION': 'no_pos_actual',
        'FECHA': 'f_efva',
        'STATUS': 'estado_psn',
        'FECHA_APLICACION': 'fecha_captura',
        'MOTIVO': 'cd_motivo',
        'MOTIVO_DESCR': 'motivo',
        'UNIDAD_GENERAL': 'cd_un',
        'DESCR100': 'unidad_de_negocio',
        'UNIDAD': 'unidad_adva',
        'DEPARTAMENTO': 'cd_departamento',
        'PUESTO': 'cd_puesto',
        'ESTADO_POSICION': 'estado_ptal',
        'FEHCA_ESTADO': 'fecha_est',
        'MAXIMOS_EN_POS': 'maximo',
        'DEPENDENCIA': 'depnd_drt',
        'DEPEN_INDIREC': 'depnd_indrt',
        'UBICACION': 'ubicacion',
        'NIVEL_DE': 'nvl_direc',
        'PLAN_SALARIAS': 'plan_sal',
        'GRADO': 'grado',
        'SCALA': 'esc',
        'PUESTO_ESTRUCTURA': 'puesto_ptal',
        'PARTIDA': 'partida_ptal',
        'GRUPO_PAGO': 'gp_pago',
        'BENEFICIOS': 'prog_beneficios',
        'ULTIMA_ACT': 'fh_ult_actz',
        'ULTIMO_OPERADOR': 'por',
        'HORAS': 'hr_estd_semn',
        'DESCR_1': 'descr',
        'GRUPO_TRABAJO': 'gp_trabajo',
        'CODIGO_ORGANIZACION': 'org_code',
        'CODIGO_GRUPO': 'grupo_cd_sal',
        'DESCRIPCION': 'formal_desc',
        'SHARE': 'pto_compt',
        'LLAVE_POSICION': 'posn_clv',
        'BUDGETED': 'presupuesto'
    }

    with open(CSV_PATH, mode='r', encoding='latin1') as f:
        reader = csv.DictReader(f, delimiter='|')
        batch = []
        count = 0
        for row in reader:
            # Map columns
            kwargs = {}
            for csv_col, model_field in mapping.items():
                val = row.get(csv_col, None)
                kwargs[model_field] = clean_val(val)
            
            # Default for nombre_puesto is None
            kwargs['nombre_puesto'] = None
            
            batch.append(MovPos(**kwargs))
            
            if len(batch) >= 500:
                MovPos.objects.bulk_create(batch)
                count += len(batch)
                print(f"Imported {count} records...")
                batch = []
        
        if batch:
            MovPos.objects.bulk_create(batch)
            count += len(batch)
            print(f"Imported {count} records...")

    print("Import finished successfully!")

if __name__ == '__main__':
    run()
