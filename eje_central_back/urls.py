from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/ua/", include("ua.urls")),
    path("api/plantilla/", include("plantilla.urls")),
    path("api/presupuesto/", include("presupuesto.urls")),
    path("api/control-gestion/", include("control_gestion.urls")),
    path("api/cat-tipo-oficio/", include("cat_tipo_oficio.urls")),
    path("api/ai/", include("ai_app.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
