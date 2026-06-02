from rest_framework import serializers
from .models import (
    ScgCatUnidadResponsable,
    ScgCatUnidadAdministrativa,
    ScgCatTipoDocumento,
    ScgCatTema,
    ScgCatStatusTurnado,
    ScgCatStatusResponse,
    ScgCatStatusAsunto,
    ScgCatPrioridad,
    ScgCatMedioRecepcion,
    ScgCatInstruccion,
    ScgCatDeterminantesCopia,
    ScgCatDeterminantes,
)

class ScgCatUnidadResponsableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScgCatUnidadResponsable
        fields = "__all__"

class ScgCatUnidadAdministrativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScgCatUnidadAdministrativa
        fields = "__all__"

class ScgCatTipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScgCatTipoDocumento
        fields = "__all__"

class ScgCatTemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScgCatTema
        fields = "__all__"

class ScgCatStatusTurnadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScgCatStatusTurnado
        fields = "__all__"

class ScgCatStatusResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScgCatStatusResponse
        fields = "__all__"

class ScgCatStatusAsuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScgCatStatusAsunto
        fields = "__all__"

class ScgCatPrioridadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScgCatPrioridad
        fields = "__all__"

class ScgCatMedioRecepcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScgCatMedioRecepcion
        fields = "__all__"

class ScgCatInstruccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScgCatInstruccion
        fields = "__all__"

class ScgCatDeterminantesCopiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScgCatDeterminantesCopia
        fields = "__all__"

class ScgCatDeterminantesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScgCatDeterminantes
        fields = "__all__"
