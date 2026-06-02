from rest_framework import viewsets
from .models import UnidadAdministrativa
from .serializers import UnidadAdministrativaSerializer

class UnidadAdministrativaViewSet(viewsets.ModelViewSet):
    queryset = UnidadAdministrativa.objects.all()
    serializer_class = UnidadAdministrativaSerializer
