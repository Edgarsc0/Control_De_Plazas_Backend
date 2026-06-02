from django.db import models

# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.


class ScgCatDeterminantes(models.Model):
    id = models.AutoField(primary_key=True)
    nivel = models.CharField(max_length=255, blank=True, null=True)
    unidaddenegocio = models.CharField(
        db_column="unidadDeNegocio", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    unidadadministrativa = models.CharField(
        db_column="unidadAdministrativa", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    area = models.CharField(max_length=255, blank=True, null=True)
    determinante = models.CharField(max_length=255, blank=True, null=True)
    dependencia = models.CharField(max_length=255, blank=True, null=True)
    fecharegistro = models.DateTimeField(
        db_column="fechaRegistro", blank=True, null=True
    )  # Field name made lowercase.
    fechamodificacion = models.DateTimeField(
        db_column="fechaModificacion", blank=True, null=True
    )  # Field name made lowercase.
    idusuariomodifica = models.IntegerField(
        db_column="idUsuarioModifica", blank=True, null=True
    )  # Field name made lowercase.
    idusuarioregistra = models.IntegerField(
        db_column="idUsuarioRegistra", blank=True, null=True
    )  # Field name made lowercase.
    activo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "scg_cat_determinantes"


class ScgCatDeterminantesCopia(models.Model):
    id = models.AutoField(primary_key=True)
    nivel = models.CharField(max_length=255, blank=True, null=True)
    unidaddenegocio = models.CharField(
        db_column="unidadDeNegocio", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    unidadadministrativa = models.CharField(
        db_column="unidadAdministrativa", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    area = models.CharField(max_length=255, blank=True, null=True)
    determinante = models.CharField(max_length=255, blank=True, null=True)
    dependencia = models.CharField(max_length=255, blank=True, null=True)
    fecharegistro = models.DateTimeField(
        db_column="fechaRegistro", blank=True, null=True
    )  # Field name made lowercase.
    fechamodificacion = models.DateTimeField(
        db_column="fechaModificacion", blank=True, null=True
    )  # Field name made lowercase.
    idusuariomodifica = models.IntegerField(
        db_column="idUsuarioModifica", blank=True, null=True
    )  # Field name made lowercase.
    idusuarioregistra = models.IntegerField(
        db_column="idUsuarioRegistra", blank=True, null=True
    )  # Field name made lowercase.
    activo = models.IntegerField(blank=True, null=True)
    activo_2 = models.IntegerField()

    class Meta:
        managed = False
        db_table = "scg_cat_determinantes_copia"


class ScgCatInstruccion(models.Model):
    idinstruccion = models.AutoField(
        db_column="idInstruccion", primary_key=True
    )  # Field name made lowercase.
    instruccion = models.CharField(max_length=255, blank=True, null=True)
    fecharegistro = models.DateTimeField(
        db_column="fechaRegistro", blank=True, null=True
    )  # Field name made lowercase.
    fechamodificacion = models.DateTimeField(
        db_column="fechaModificacion", blank=True, null=True
    )  # Field name made lowercase.
    idusuarioregistra = models.IntegerField(
        db_column="idUsuarioRegistra", blank=True, null=True
    )  # Field name made lowercase.
    idusuariomodifica = models.IntegerField(
        db_column="idUsuarioModifica", blank=True, null=True
    )  # Field name made lowercase.
    activo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "scg_cat_instruccion"


class ScgCatMedioRecepcion(models.Model):
    idmediorecepcion = models.IntegerField(
        db_column="idMedioRecepcion", primary_key=True
    )  # Field name made lowercase.
    mediorecepcion = models.CharField(
        db_column="medioRecepcion", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    fecharegistro = models.DateTimeField(
        db_column="fechaRegistro", blank=True, null=True
    )  # Field name made lowercase.
    fechamodificacion = models.DateTimeField(
        db_column="fechaModificacion", blank=True, null=True
    )  # Field name made lowercase.
    idusuarioregistra = models.IntegerField(
        db_column="idUsuarioRegistra", blank=True, null=True
    )  # Field name made lowercase.
    idusuariomodifica = models.IntegerField(
        db_column="idUsuarioModifica", blank=True, null=True
    )  # Field name made lowercase.
    activo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "scg_cat_medio_recepcion"


class ScgCatPrioridad(models.Model):
    idprioridad = models.AutoField(
        db_column="idPrioridad", primary_key=True
    )  # Field name made lowercase.
    prioridad = models.CharField(max_length=255, blank=True, null=True)
    fecharegistro = models.DateTimeField(
        db_column="fechaRegistro", blank=True, null=True
    )  # Field name made lowercase.
    fechamodificacion = models.DateTimeField(
        db_column="fechaModificacion", blank=True, null=True
    )  # Field name made lowercase.
    idusuarioregistra = models.IntegerField(
        db_column="idUsuarioRegistra", blank=True, null=True
    )  # Field name made lowercase.
    idusuariomodifica = models.IntegerField(
        db_column="idUsuarioModifica", blank=True, null=True
    )  # Field name made lowercase.
    activo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "scg_cat_prioridad"


class ScgCatStatusAsunto(models.Model):
    idstatusasunto = models.AutoField(
        db_column="idStatusAsunto", primary_key=True
    )  # Field name made lowercase.
    statusasunto = models.CharField(
        db_column="statusAsunto", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    fecharegistro = models.DateTimeField(
        db_column="fechaRegistro", blank=True, null=True
    )  # Field name made lowercase.
    fechamodificacion = models.DateTimeField(
        db_column="fechaModificacion", blank=True, null=True
    )  # Field name made lowercase.
    idusuarioregistra = models.IntegerField(
        db_column="idUsuarioRegistra", blank=True, null=True
    )  # Field name made lowercase.
    idusuariomodifica = models.IntegerField(
        db_column="idUsuarioModifica", blank=True, null=True
    )  # Field name made lowercase.
    activo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "scg_cat_status_asunto"


class ScgCatStatusResponse(models.Model):
    idstatusresponse = models.AutoField(
        db_column="idStatusResponse", primary_key=True
    )  # Field name made lowercase.
    status = models.CharField(max_length=255, blank=True, null=True)
    message = models.CharField(max_length=255, blank=True, null=True)
    fecharegistro = models.DateTimeField(
        db_column="fechaRegistro", blank=True, null=True
    )  # Field name made lowercase.
    activo = models.IntegerField()

    class Meta:
        managed = False
        db_table = "scg_cat_status_response"


class ScgCatStatusTurnado(models.Model):
    idstatusturnado = models.AutoField(
        db_column="idStatusTurnado", primary_key=True
    )  # Field name made lowercase.
    statusturnado = models.CharField(
        db_column="statusTurnado", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    fecharegistro = models.DateTimeField(
        db_column="fechaRegistro", blank=True, null=True
    )  # Field name made lowercase.
    fechamodificacion = models.DateTimeField(
        db_column="fechaModificacion", blank=True, null=True
    )  # Field name made lowercase.
    idusuarioregistra = models.IntegerField(
        db_column="idUsuarioRegistra", blank=True, null=True
    )  # Field name made lowercase.
    idusuariomodifica = models.IntegerField(
        db_column="idUsuarioModifica", blank=True, null=True
    )  # Field name made lowercase.
    activo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "scg_cat_status_turnado"


class ScgCatTema(models.Model):
    idtema = models.AutoField(
        db_column="idTema", primary_key=True
    )  # Field name made lowercase.
    tema = models.CharField(max_length=255, blank=True, null=True)
    fecharegistro = models.DateTimeField(
        db_column="fechaRegistro", blank=True, null=True
    )  # Field name made lowercase.
    fechamodificacion = models.DateTimeField(
        db_column="fechaModificacion", blank=True, null=True
    )  # Field name made lowercase.
    idusuarioregistra = models.IntegerField(
        db_column="idUsuarioRegistra", blank=True, null=True
    )  # Field name made lowercase.
    idusuariomodifica = models.IntegerField(
        db_column="idUsuarioModifica", blank=True, null=True
    )  # Field name made lowercase.
    activo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "scg_cat_tema"


class ScgCatTipoDocumento(models.Model):
    idtipodocumento = models.AutoField(
        db_column="idTipoDocumento", primary_key=True
    )  # Field name made lowercase.
    tipodocumento = models.CharField(
        db_column="tipoDocumento", max_length=255
    )  # Field name made lowercase.
    fecharegistro = models.DateTimeField(
        db_column="fechaRegistro", blank=True, null=True
    )  # Field name made lowercase.
    fechamodificacion = models.DateTimeField(
        db_column="fechaModificacion", blank=True, null=True
    )  # Field name made lowercase.
    idusuarioregistra = models.IntegerField(
        db_column="idUsuarioRegistra", blank=True, null=True
    )  # Field name made lowercase.
    idusuariomodifica = models.IntegerField(
        db_column="idUsuarioModifica", blank=True, null=True
    )  # Field name made lowercase.
    activo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "scg_cat_tipo_documento"


class ScgCatUnidadAdministrativa(models.Model):
    idunidadadministrativa = models.AutoField(
        db_column="idUnidadAdministrativa", primary_key=True
    )  # Field name made lowercase.
    clave = models.CharField(max_length=10, blank=True, null=True)
    unidadadministrativa = models.CharField(
        db_column="unidadAdministrativa", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    esunidadadministrativa = models.IntegerField(
        db_column="esUnidadAdministrativa", blank=True, null=True
    )  # Field name made lowercase.
    esunidaddenegocio = models.IntegerField(
        db_column="esUnidadDeNegocio", blank=True, null=True
    )  # Field name made lowercase.
    fecharegistro = models.DateTimeField(
        db_column="fechaRegistro", blank=True, null=True
    )  # Field name made lowercase.
    fechamodificacion = models.DateTimeField(
        db_column="fechaModificacion", blank=True, null=True
    )  # Field name made lowercase.
    idusuarioregistra = models.IntegerField(
        db_column="idUsuarioRegistra", blank=True, null=True
    )  # Field name made lowercase.
    idusuariomodifica = models.IntegerField(
        db_column="idUsuarioModifica", blank=True, null=True
    )  # Field name made lowercase.
    activo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "scg_cat_unidad_administrativa"


class ScgCatUnidadResponsable(models.Model):
    idunidadresponsable = models.AutoField(
        db_column="idUnidadResponsable", primary_key=True
    )  # Field name made lowercase.
    unidadresponsable = models.CharField(
        db_column="unidadResponsable", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    clave = models.CharField(unique=True, max_length=15, blank=True, null=True)
    idunidadadministrativa = models.CharField(
        db_column="idUnidadAdministrativa", max_length=15, blank=True, null=True
    )  # Field name made lowercase.
    fecharegistro = models.DateTimeField(
        db_column="fechaRegistro", blank=True, null=True
    )  # Field name made lowercase.
    fechamodificacion = models.DateTimeField(
        db_column="fechaModificacion", blank=True, null=True
    )  # Field name made lowercase.
    idusuariomodifica = models.IntegerField(
        db_column="idUsuarioModifica", blank=True, null=True
    )  # Field name made lowercase.
    idusuarioregistra = models.IntegerField(
        db_column="idUsuarioRegistra", blank=True, null=True
    )  # Field name made lowercase.
    activo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "scg_cat_unidad_responsable"
