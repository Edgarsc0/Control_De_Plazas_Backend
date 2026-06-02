from rest_framework import viewsets
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
from .serializers import (
    ScgCatUnidadResponsableSerializer,
    ScgCatUnidadAdministrativaSerializer,
    ScgCatTipoDocumentoSerializer,
    ScgCatTemaSerializer,
    ScgCatStatusTurnadoSerializer,
    ScgCatStatusResponseSerializer,
    ScgCatStatusAsuntoSerializer,
    ScgCatPrioridadSerializer,
    ScgCatMedioRecepcionSerializer,
    ScgCatInstruccionSerializer,
    ScgCatDeterminantesCopiaSerializer,
    ScgCatDeterminantesSerializer,
)

class ScgCatUnidadResponsableViewSet(viewsets.ModelViewSet):
    queryset = ScgCatUnidadResponsable.objects.all()
    serializer_class = ScgCatUnidadResponsableSerializer

class ScgCatUnidadAdministrativaViewSet(viewsets.ModelViewSet):
    queryset = ScgCatUnidadAdministrativa.objects.all()
    serializer_class = ScgCatUnidadAdministrativaSerializer

class ScgCatTipoDocumentoViewSet(viewsets.ModelViewSet):
    queryset = ScgCatTipoDocumento.objects.all()
    serializer_class = ScgCatTipoDocumentoSerializer

class ScgCatTemaViewSet(viewsets.ModelViewSet):
    queryset = ScgCatTema.objects.all()
    serializer_class = ScgCatTemaSerializer

class ScgCatStatusTurnadoViewSet(viewsets.ModelViewSet):
    queryset = ScgCatStatusTurnado.objects.all()
    serializer_class = ScgCatStatusTurnadoSerializer

class ScgCatStatusResponseViewSet(viewsets.ModelViewSet):
    queryset = ScgCatStatusResponse.objects.all()
    serializer_class = ScgCatStatusResponseSerializer

class ScgCatStatusAsuntoViewSet(viewsets.ModelViewSet):
    queryset = ScgCatStatusAsunto.objects.all()
    serializer_class = ScgCatStatusAsuntoSerializer

class ScgCatPrioridadViewSet(viewsets.ModelViewSet):
    queryset = ScgCatPrioridad.objects.all()
    serializer_class = ScgCatPrioridadSerializer

class ScgCatMedioRecepcionViewSet(viewsets.ModelViewSet):
    queryset = ScgCatMedioRecepcion.objects.all()
    serializer_class = ScgCatMedioRecepcionSerializer

class ScgCatInstruccionViewSet(viewsets.ModelViewSet):
    queryset = ScgCatInstruccion.objects.all()
    serializer_class = ScgCatInstruccionSerializer

class ScgCatDeterminantesCopiaViewSet(viewsets.ModelViewSet):
    queryset = ScgCatDeterminantesCopia.objects.all()
    serializer_class = ScgCatDeterminantesCopiaSerializer

class ScgCatDeterminantesViewSet(viewsets.ModelViewSet):
    queryset = ScgCatDeterminantes.objects.all()
    serializer_class = ScgCatDeterminantesSerializer
