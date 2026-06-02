import re

with open("plantilla/tasks.py", "r") as f:
    content = f.read()

# Fix duplicates of registros_historico
content = re.sub(r'        registros = \[\]\n    registros_historico = \[\]\n\n    registros_historico = \[\]\n    registros_historico = \[\]\n', '    registros = []\n    registros_historico = []\n', content)
content = re.sub(r'    registros_historico = \[\]\n    with open\(csv_path, encoding="cp1252", newline=""\) as f:', '    registros = []\n    registros_historico = []\n    with open(csv_path, encoding="cp1252", newline="") as f:', content)

# It seems `registros = []` is missing from `_importar_csv_bajas`. Let's just make sure we replace the initialization blocks correctly.
content = content.replace('    registros_historico = []\n\n    registros_historico = []\n    registros_historico = []\n', '    registros_historico = []\n')

# Fix indentation of if guardar_historico:
content = content.replace('                        if guardar_historico:\n                registros_historico.append(\n                EmpleadosCompletosSigHistorico(', '            if guardar_historico:\n                registros_historico.append(\n                    EmpleadosCompletosSigHistorico(')

content = content.replace('                        if guardar_historico:\n                registros_historico.append(\n                MovPosHistorico(', '            if guardar_historico:\n                registros_historico.append(\n                    MovPosHistorico(')

content = content.replace('                        if guardar_historico:\n                registros_historico.append(\n                BajasSigHistorico(', '            if guardar_historico:\n                registros_historico.append(\n                    BajasSigHistorico(')


with open("plantilla/tasks.py", "w") as f:
    f.write(content)
