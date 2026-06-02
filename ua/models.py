from django.db import models

class UnidadAdministrativa(models.Model):
    nombre = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre
