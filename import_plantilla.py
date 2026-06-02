import os
import sys
import django
import pandas as pd
import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eje_central_back.settings') 
sys.path.append('/home/edgar/ANAM/EjeCentral/eje_central_back')

try:
    django.setup()
except Exception as e:
    print(f"Error configurando Django: {e}")
    sys.exit(1)

from plantilla.models import Plantilla1800Plazas
from django.db import transaction

def import_data():
    excel_path = '/home/edgar/Descargas/Plantilla_Qna_10_PNC_2026_Formateada.xlsx'
    
    print(f"Leyendo archivo: {excel_path}")
    df = pd.read_excel(excel_path, dtype=str)
    
    # Remplazar valores nulos (NaN) con cadena vacía y quitar el ".0" de los enteros leídos como flotantes por error de formato en Excel
    df = df.fillna("")
    
    # Limpiar nombres de columnas para que coincidan con el mapeo si tenían saltos o espacios raros
    df.columns = df.columns.str.strip().str.replace('\n', ' ')
    
    # Mapeo exacto entre el Excel y el Modelo
    column_mapping = {
        'Posición': 'posición',
        'Estado Nómina': 'estado_nómina',
        'Num Empleado': 'num_empleado',
        'Estado posición': 'estado_posición',
        'RFC': 'rfc',
        'CURP': 'curp',
        'Nombres': 'nombres',
        'Motivo': 'motivo',
        'Fecha efectiva (Personal)': 'fecha_efectiva_personal',
        'Fecha de captura': 'fecha_de_captura',
        'Qna#': 'qna',
        'Fecha prevista de salida': 'fecha_prevista_de_salida',
        'Código Presupuestal': 'código_presupuestal',
        'NJ': 'nj',
        'Nivel': 'nivel',
        'Escala': 'escala',
        'SMB': 'smb',
        'SMN': 'smn',
        'Partida': 'partida',
        'Tipo de Contratación': 'tipo_de_contratación',
        'Cd UN': 'cd_un',
        'Unidad de Negocio': 'unidad_de_negocio',
        'Cd UA': 'cd_ua',
        'Unidad Administrativa': 'unidad_administrativa',
        'Cd Pto Funcional asignado': 'cd_pto_funcional_asignado',
        'Nombre Puesto Funcional Asignado': 'nombre_puesto_funcional_asignado',
        'Id Departamento': 'id_departamento',
        'Departamento': 'departamento',
        'Dependencia Directa': 'dependencia_directa',
        'Of. De Solicitud': 'of_de_solicitud',
        'IPE': 'ipe', 
        'Entidad Federativa': 'entidad_federativa',
        'Tipo de Aduana': 'tipo_de_aduana',
        'Ubicación': 'ubicación',
        'Descripción ubicación': 'descripción_ubicación',
        'Personal Militar o Civil': 'personal_militar_o_civil',
        'Tipo de personal SEDENA / SEMAR': 'tipo_de_personal_sedena_semar',
        'Rango': 'rango',
        'Formato de compatibiliddad': 'formato_de_compatibiliddad',
        'Fecha de ingreso': 'fecha_de_ingreso',
        'F. de Vacancia': 'f_de_vacancia',
        'Of. SHCP': 'of_shcp',
        'Observaciones': 'observaciones',
        'CAP ANUAL': 'cap_anual',
        'CAP MENSUAL': 'cap_mensual',
    }
    
    # Reemplazar valores vacíos con None
    df = df.replace({np.nan: None})
    
    with transaction.atomic():
        print("Truncando tabla Plantilla1800Plazas...")
        # Borrar todo (equivale a truncar para este propósito en Django ORM)
        Plantilla1800Plazas.objects.all().delete()
        print("Tabla vaciada.")
        
        instances = []
        print("Procesando filas...")
        for index, row in df.iterrows():
            model_kwargs = {}
            for excel_col, model_field in column_mapping.items():
                if excel_col in df.columns:
                    val = row[excel_col]
                    if val is not None and val != "":
                        val = str(val).strip()
                        if val.endswith('.0'):
                            val = val[:-2]
                    model_kwargs[model_field] = val if val != "" else None
            
            instance = Plantilla1800Plazas(**model_kwargs)
            instances.append(instance)
        
        print(f"Insertando {len(instances)} registros en la base de datos...")
        Plantilla1800Plazas.objects.bulk_create(instances, batch_size=1000)
        
    print("¡Importación completada exitosamente!")

if __name__ == '__main__':
    import_data()
