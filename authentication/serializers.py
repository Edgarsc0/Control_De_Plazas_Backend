from rest_framework import serializers
from .models import Whitelist, VerificationCode

class WhitelistSerializer(serializers.ModelSerializer):
    ua_nombre = serializers.ReadOnlyField(source='ua.nombre')
    rol_nombre = serializers.ReadOnlyField(source='rol.name')

    class Meta:
        model = Whitelist
        fields = ['id', 'email', 'rol', 'rol_nombre', 'ua', 'ua_nombre', 'activo']

class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = ['email', 'code']
