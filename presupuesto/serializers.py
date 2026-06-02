from rest_framework import serializers
from .models import ValuacionPresupuestariaPorNivel, CatalogoPlazas, ConstantesSistema, ConceptosPresupuestal


class ValuacionPresupuestariaPorNivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValuacionPresupuestariaPorNivel
        fields = "__all__"


class CatalogoPlazasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogoPlazas
        fields = "__all__"


class ConstantesSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstantesSistema
        fields = "__all__"


class ConceptosPresupuestalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptosPresupuestal
        fields = "__all__"
