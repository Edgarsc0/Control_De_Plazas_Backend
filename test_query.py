import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

from django.db import connection

query = """
    SELECT COUNT(*)                                                                                                                                              
    FROM EMPLEADOS_COMPLETOS_SIG e                                                                                                                          
    WHERE NOT EXISTS (                                                                                                                             
        SELECT 1                                                                                                                            
        FROM MOV_POS m                                                                                                                                      
        INNER JOIN (
            SELECT id, ROW_NUMBER() OVER (
                PARTITION BY `Nº Pos Actual` 
                ORDER BY `F Efva` DESC, `Fecha Captura` DESC, `F/H Últ Actz` DESC, id DESC
            ) as rn
            FROM MOV_POS
        ) latest ON m.id = latest.id AND latest.rn = 1
        WHERE m.`Estado Psn` = 'A' AND m.`Nº Pos Actual` = e.`Posición`
    ) AND e.`Estado Nómina` IN ('P','A','S', 'L');
"""

with connection.cursor() as cursor:
    try:
        cursor.execute(query)
        row = cursor.fetchone()
        print("Count result using NOT EXISTS:", row[0])
    except Exception as e:
        print("Error:", e)
