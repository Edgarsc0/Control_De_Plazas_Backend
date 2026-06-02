import os
import django
import pandas as pd
import sys

sys.path.append('/home/edgar/ANAM/EjeCentral/eje_central_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

from django.db import connection

def main():
    excel_path = '/home/edgar/Descargas/25 05 Movimientos 0948.xls'

    # 1. Obtener las posiciones ocupadas del EXCEL
    df = pd.read_excel(excel_path, sheet_name='Plazas')
    if 'Ocupada / Vacante' not in df.columns:
        df = pd.read_excel(excel_path, sheet_name='Plazas', header=1)
        
    ocupadas_excel = df[df['Ocupada / Vacante'].astype(str).str.strip().str.upper() == 'OCUPADA']
    # Tomar la columna de la posicion. Es 'Nº Pos Actual'
    posiciones_excel = set(ocupadas_excel['Nº Pos Actual'].astype(str).str.strip())

    # 2. Obtener las posiciones ocupadas de la BD (9,462 registros)
    query = """
        SELECT m.`Nº Pos Actual`
        FROM EMPLEADOS_COMPLETOS_SIG e
        INNER JOIN MOV_POS m ON e.`Posición` = m.`Nº Pos Actual`
        INNER JOIN (
            SELECT id, ROW_NUMBER() OVER (
                PARTITION BY `Nº Pos Actual` 
                ORDER BY `F Efva` DESC, `Fecha Captura` DESC, `F/H Últ Actz` DESC, id DESC
            ) as rn
            FROM MOV_POS
        ) latest ON m.id = latest.id AND latest.rn = 1
        WHERE m.`Estado Psn` = 'A' AND e.`Estado Nómina` IN ('P','A','S','L')
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        posiciones_bd = set(str(row[0]).strip() for row in rows)
        
    print(f"Total en Excel: {len(posiciones_excel)}")
    print(f"Total en BD: {len(posiciones_bd)}")
    
    # 3. Diferencia
    # La que esta en BD pero no en Excel
    bd_no_excel = posiciones_bd - posiciones_excel
    print(f"Posiciones en BD que dicen OCUPADA pero no lo dicen en Excel: {bd_no_excel}")
    
    excel_no_bd = posiciones_excel - posiciones_bd
    print(f"Posiciones en Excel que dicen OCUPADA pero no lo dicen en BD: {excel_no_bd}")

    if bd_no_excel:
        print("\nDetalle en BD para la discrepante:")
        for p in bd_no_excel:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT e.nombres, e.`Estado Nómina`, m.`Estado Psn`, m.motivo FROM EMPLEADOS_COMPLETOS_SIG e INNER JOIN MOV_POS m ON e.`Posición` = m.`Nº Pos Actual` WHERE e.`Posición` = '{p}' LIMIT 1")
                res = cursor.fetchone()
                if res:
                    print(f"Posición: {p} | Empleado: {res[0]} | Est.Nómina: {res[1]} | Est.Psn(MovPos): {res[2]} | Motivo(MovPos): {res[3]}")
                    
            # Let's check what it is in the excel
            ex_row = df[df['Nº Pos Actual'].astype(str).str.strip() == p]
            if not ex_row.empty:
                print(f"En el Excel dice que esta posición tiene Ocupada/Vacante: {ex_row['Ocupada / Vacante'].values[0]}")
            else:
                print("En el Excel no existe esta posicion.")

if __name__ == '__main__':
    main()
