from rest_framework import serializers
from .models import CatTipoAsunto, RelacionAsuntoConTipoOficio, AsuntoValuacion

class CatTipoAsuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatTipoAsunto
        fields = '__all__'

class RelacionAsuntoConTipoOficioSerializer(serializers.ModelSerializer):
    # Opcional: mostrar el detalle del tipo de asunto al consultar
    tipo_asunto_detalle = CatTipoAsuntoSerializer(source='idTipoAsunto', read_only=True)

    class Meta:
        model = RelacionAsuntoConTipoOficio
        fields = '__all__'

class AsuntoValuacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsuntoValuacion
        fields = '__all__'
