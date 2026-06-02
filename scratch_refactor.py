import re

with open("plantilla/models.py", "r") as f:
    content = f.read()

# Refactor EmpleadosCompletosSig
content = content.replace("class EmpleadosCompletosSig(models.Model):", "class EmpleadosCompletosSigBase(models.Model):")
content = re.sub(
    r'(class EmpleadosCompletosSigBase.*?class Meta:\n\s+)managed = True\n\s+db_table = "EMPLEADOS_COMPLETOS_SIG"',
    r'\1abstract = True',
    content,
    flags=re.DOTALL
)

content += """
class EmpleadosCompletosSig(EmpleadosCompletosSigBase):
    class Meta:
        managed = True
        db_table = "EMPLEADOS_COMPLETOS_SIG"

class EmpleadosCompletosSigHistorico(EmpleadosCompletosSigBase):
    fecha_descarga = models.DateTimeField(auto_now_add=True)
    class Meta:
        managed = True
        db_table = "EMPLEADOS_COMPLETOS_SIG_HISTORICO"
"""

# Refactor BajasSig
content = content.replace("class BajasSig(models.Model):", "class BajasSigBase(models.Model):")
content = re.sub(
    r'(class BajasSigBase.*?class Meta:\n\s+)managed = True\n\s+db_table = "BAJAS_SIG"',
    r'\1abstract = True',
    content,
    flags=re.DOTALL
)

content += """
class BajasSig(BajasSigBase):
    class Meta:
        managed = True
        db_table = "BAJAS_SIG"

class BajasSigHistorico(BajasSigBase):
    fecha_descarga = models.DateTimeField(auto_now_add=True)
    class Meta:
        managed = True
        db_table = "BAJAS_SIG_HISTORICO"
"""

# Refactor MovPos
content = content.replace("class MovPos(models.Model):", "class MovPosBase(models.Model):")
content = re.sub(
    r'(class MovPosBase.*?class Meta:\n\s+)managed = True\n\s+db_table = "MOV_POS"',
    r'\1abstract = True',
    content,
    flags=re.DOTALL
)

content += """
class MovPos(MovPosBase):
    class Meta:
        managed = True
        db_table = "MOV_POS"

class MovPosHistorico(MovPosBase):
    fecha_descarga = models.DateTimeField(auto_now_add=True)
    class Meta:
        managed = True
        db_table = "MOV_POS_HISTORICO"
"""

# Add ZafiroBitacora
content += """
class ZafiroBitacora(models.Model):
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)
    duracion_segundos = models.FloatField(null=True, blank=True)
    registros_posiciones = models.IntegerField(default=0)
    registros_completos = models.IntegerField(default=0)
    registros_bajas = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default="OK")
    error_message = models.TextField(null=True, blank=True)
    es_historico = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = "ZAFIRO_BITACORA"
        ordering = ['-fecha_ejecucion']

    def __str__(self):
        return f"{self.fecha_ejecucion} - {self.status}"
"""

with open("plantilla/models.py", "w") as f:
    f.write(content)
