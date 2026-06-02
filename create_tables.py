import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("CREATE TABLE IF NOT EXISTS cp_tbl_mov_completo_29_05_26_staging LIKE cp_tbl_mov_completo_29_05_26;")
    cursor.execute("CREATE TABLE IF NOT EXISTS cp_tbl_mov_completo_29_05_26_historico LIKE cp_tbl_mov_completo_29_05_26;")
    
    try:
        cursor.execute("ALTER TABLE cp_tbl_mov_completo_29_05_26_historico ADD COLUMN fecha_descarga DATETIME(6);")
    except Exception as e:
        print(f"Column might already exist: {e}")

print("Tables created successfully.")
