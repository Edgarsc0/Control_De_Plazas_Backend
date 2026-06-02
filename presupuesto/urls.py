from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ValuacionPresupuestariaPorNivelViewSet, 
    CatalogoPlazasViewSet,
    ConstantesSistemaViewSet,
    ConceptosPresupuestalViewSet
)

router = DefaultRouter()
router.register(r'valuacion-presupuestaria', ValuacionPresupuestariaPorNivelViewSet)
router.register(r'catalogo-plazas', CatalogoPlazasViewSet)
router.register(r'constantes-sistema', ConstantesSistemaViewSet)
router.register(r'conceptos-presupuestal', ConceptosPresupuestalViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
