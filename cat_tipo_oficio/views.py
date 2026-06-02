from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import CatTipoAsunto, RelacionAsuntoConTipoOficio, AsuntoValuacion
from .serializers import CatTipoAsuntoSerializer, RelacionAsuntoConTipoOficioSerializer, AsuntoValuacionSerializer

class CatTipoAsuntoViewSet(viewsets.ModelViewSet):
    queryset = CatTipoAsunto.objects.all()
    serializer_class = CatTipoAsuntoSerializer

class RelacionAsuntoConTipoOficioViewSet(viewsets.ModelViewSet):
    queryset = RelacionAsuntoConTipoOficio.objects.all()
    serializer_class = RelacionAsuntoConTipoOficioSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        idAsuntoSCG = self.request.query_params.get('idAsuntoSCG')
        if idAsuntoSCG:
            queryset = queryset.filter(idAsuntoSCG=idAsuntoSCG)
        return queryset

    def create(self, request, *args, **kwargs):
        idAsuntoSCG = request.data.get('idAsuntoSCG')
        idTipoAsunto = request.data.get('idTipoAsunto')
        
        if not idAsuntoSCG or not idTipoAsunto:
            return Response(
                {"error": "idAsuntoSCG and idTipoAsunto are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Lógica de "upsert": Si ya existe una relación para este asunto, la actualizamos
        relacion, created = RelacionAsuntoConTipoOficio.objects.update_or_create(
            idAsuntoSCG=idAsuntoSCG,
            defaults={'idTipoAsunto_id': idTipoAsunto}
        )
        
        serializer = self.get_serializer(relacion)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class AsuntoValuacionViewSet(viewsets.ModelViewSet):
    queryset = AsuntoValuacion.objects.all()
    serializer_class = AsuntoValuacionSerializer
