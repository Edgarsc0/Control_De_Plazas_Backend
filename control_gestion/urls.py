from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ScgCatUnidadResponsableViewSet,
    ScgCatUnidadAdministrativaViewSet,
    ScgCatTipoDocumentoViewSet,
    ScgCatTemaViewSet,
    ScgCatStatusTurnadoViewSet,
    ScgCatStatusResponseViewSet,
    ScgCatStatusAsuntoViewSet,
    ScgCatPrioridadViewSet,
    ScgCatMedioRecepcionViewSet,
    ScgCatInstruccionViewSet,
    ScgCatDeterminantesCopiaViewSet,
    ScgCatDeterminantesViewSet,
)

router = DefaultRouter()
router.register(r"unidad-responsable", ScgCatUnidadResponsableViewSet)
router.register(r"unidad-administrativa", ScgCatUnidadAdministrativaViewSet)
router.register(r"tipo-documento", ScgCatTipoDocumentoViewSet)
router.register(r"tema", ScgCatTemaViewSet)
router.register(r"status-turnado", ScgCatStatusTurnadoViewSet)
router.register(r"status-response", ScgCatStatusResponseViewSet)
router.register(r"status-asunto", ScgCatStatusAsuntoViewSet)
router.register(r"prioridad", ScgCatPrioridadViewSet)
router.register(r"medio-recepcion", ScgCatMedioRecepcionViewSet)
router.register(r"instruccion", ScgCatInstruccionViewSet)
router.register(r"determinantes-copia", ScgCatDeterminantesCopiaViewSet)
router.register(r"determinantes", ScgCatDeterminantesViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
