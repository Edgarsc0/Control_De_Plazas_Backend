from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CatTipoAsuntoViewSet, RelacionAsuntoConTipoOficioViewSet, AsuntoValuacionViewSet

router = DefaultRouter()
router.register(r'tipos-asunto', CatTipoAsuntoViewSet)
router.register(r'relaciones-asunto-oficio', RelacionAsuntoConTipoOficioViewSet)
router.register(r'asuntos-valuacion', AsuntoValuacionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
