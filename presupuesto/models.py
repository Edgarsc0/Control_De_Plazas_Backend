from django.db import models


class ValuacionPresupuestariaPorNivel(models.Model):
    pk = models.CompositePrimaryKey("nivel", "zona", "codigo")
    nivel = models.CharField(db_column="NIVEL", max_length=255)
    zona = models.CharField(db_column="ZONA", max_length=255)
    codigo = models.CharField(db_column="CODIGO", max_length=255)
    puesto_o_categoria = models.CharField(
        db_column="PUESTO_O_CATEGORIA", max_length=255
    )
    sueldo = models.CharField(db_column="SUELDO", max_length=255)
    compensacion_garantizada = models.CharField(
        db_column="COMPENSACION_GARANTIZADA", max_length=255
    )

    class Meta:
        managed = False
        db_table = "valuacion_presupuestaria_por_nivel"


# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class CatalogoPlazas(models.Model):
    codigo = models.CharField(max_length=20)
    nivel = models.CharField(max_length=20)
    nivel_cruce = models.CharField(max_length=20)
    denominacion = models.CharField(max_length=255)
    zona = models.IntegerField()
    sueldo = models.DecimalField(max_digits=14, decimal_places=4)
    despensa = models.DecimalField(max_digits=14, decimal_places=4)
    prev_social_multiple = models.DecimalField(max_digits=14, decimal_places=4)
    ayuda_servicios = models.DecimalField(max_digits=14, decimal_places=4)
    apoyo_capacitacion = models.DecimalField(max_digits=14, decimal_places=4)
    ayuda_transporte = models.DecimalField(max_digits=14, decimal_places=4)
    compensacion_garantizada = models.DecimalField(max_digits=14, decimal_places=4)
    cuota_issste = models.DecimalField(max_digits=14, decimal_places=4)
    cuota_fovissste = models.DecimalField(max_digits=14, decimal_places=4)
    cuota_cesantia = models.DecimalField(max_digits=14, decimal_places=4)
    ahorro_solidario = models.DecimalField(max_digits=14, decimal_places=4)
    epr_quincenal = models.DecimalField(max_digits=14, decimal_places=4)
    grupo_vacaciones = models.IntegerField()
    grupo_gratificacion = models.IntegerField()
    tiene_epr = models.IntegerField()

    class Meta:
        managed = False
        db_table = "catalogo_plazas"
        unique_together = (("codigo", "nivel_cruce"),)


# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ConstantesSistema(models.Model):
    clave = models.CharField(primary_key=True, max_length=50)
    valor = models.DecimalField(max_digits=18, decimal_places=6)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "constantes_sistema"


# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ConceptosPresupuestal(models.Model):
    concepto = models.CharField(primary_key=True, max_length=10)
    descripcion = models.CharField(max_length=255)
    seccion = models.CharField(max_length=9)
    orden = models.IntegerField()

    class Meta:
        managed = False
        db_table = "conceptos_presupuestal"
