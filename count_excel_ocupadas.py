import pandas as pd
import sys

excel_path = '/home/edgar/Descargas/25 05 Movimientos 0948.xls'

try:
    # Intenta leerlo como HTML primero (ya que descubrimos que era un HTML disfrazado de XLS)
    dfs = pd.read_html(excel_path)
    # Suponiendo que la pestaña 'Plazas' es la segunda tabla, o la que contenga 'Ocupada / Vacante'
    df = None
    for tbl in dfs:
        if 'Ocupada / Vacante' in tbl.columns:
            df = tbl
            break
        # Sometimes header is in row 0
        elif tbl.iloc[0].isin(['Ocupada / Vacante']).any():
            tbl.columns = tbl.iloc[0]
            tbl = tbl[1:]
            df = tbl
            break
            
    if df is not None:
        print("Columnas encontradas:", df.columns.tolist())
        counts = df['Ocupada / Vacante'].value_counts()
        print("\nConteo de 'Ocupada / Vacante':")
        print(counts)
        print("\nTotal Ocupadas (ignorando mayúsculas/espacios):")
        ocupadas = df['Ocupada / Vacante'].astype(str).str.strip().str.upper()
        print(ocupadas[ocupadas == 'OCUPADA'].count())
    else:
        print("No se encontró la columna 'Ocupada / Vacante' en ninguna tabla HTML.")
except Exception as e:
    print("Error leyendo con read_html:", e)
    # Intentar con read_excel
    try:
        df = pd.read_excel(excel_path, sheet_name='Plazas')
        if 'Ocupada / Vacante' not in df.columns:
            df = pd.read_excel(excel_path, sheet_name='Plazas', header=1)
        
        counts = df['Ocupada / Vacante'].value_counts()
        print("\nConteo de 'Ocupada / Vacante':")
        print(counts)
    except Exception as e2:
        print("Error leyendo con read_excel:", e2)

