import os
import django
import sys
import pandas as pd

# Setup django
sys.path.append('/home/edgar/ANAM/EjeCentral/eje_central_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

from plantilla.models import EmpleadosCompletosSig

def main():
    # File paths
    excel_path = '/home/edgar/Descargas/25 05 Movimientos 0948.xls'
    output_path = '/home/edgar/.gemini/antigravity-cli/brain/6137966f-76f6-4d54-a854-71ca87156e97/scratch/comparacion_plazas.txt'

    # 1. Get positions from Excel
    try:
        # Read the 'Plazas' sheet
        # Notice engine='xlrd' or 'openpyxl' or None. For HTML disguised as XLS, read_html works.
        # Let's try read_excel first.
        try:
            df = pd.read_excel(excel_path, sheet_name='Plazas')
            if 'Nº Pos Actual' not in df.columns:
                # Sometimes headers are in row 1 or 2
                df = pd.read_excel(excel_path, sheet_name='Plazas', header=1)
        except Exception as e:
            # If it's HTML disguised as XLS
            dfs = pd.read_html(excel_path)
            # Find the df that has 'Nº Pos Actual'
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
            if df is None:
                raise Exception("Could not find 'Nº Pos Actual' column in HTML tables")

        # Extract positions, converting to string and stripping whitespace
        excel_pos = set(df['Nº Pos Actual'].dropna().astype(str).str.strip())
    except Exception as e:
        with open(output_path, 'w') as f:
            f.write(f"Error reading Excel file: {str(e)}")
        print(f"Error reading Excel file: {str(e)}")
        return

    # 2. Get positions from Database
    db_pos_list = EmpleadosCompletosSig.objects.values_list('posicion', flat=True)
    # Filter out empty/null and convert to string
    db_pos = set(str(p).strip() for p in db_pos_list if p and str(p).strip())

    # 3. Compare
    in_db_not_excel = db_pos - excel_pos
    in_excel_not_db = excel_pos - db_pos

    # 4. Write results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write("=== Comparación de Posiciones ===\n\n")
        f.write(f"Total en Excel: {len(excel_pos)}\n")
        f.write(f"Total en Base de Datos: {len(db_pos)}\n\n")

        f.write(f"--- Posiciones en Base de Datos pero NO en Excel ({len(in_db_not_excel)}) ---\n")
        if in_db_not_excel:
            for p in sorted(in_db_not_excel):
                f.write(f"{p}\n")
        else:
            f.write("(Ninguna)\n")
        
        f.write("\n")

        f.write(f"--- Posiciones en Excel pero NO en Base de Datos ({len(in_excel_not_db)}) ---\n")
        if in_excel_not_db:
            for p in sorted(in_excel_not_db):
                f.write(f"{p}\n")
        else:
            f.write("(Ninguna)\n")

    print(f"Successfully wrote output to {output_path}")

if __name__ == '__main__':
    main()
