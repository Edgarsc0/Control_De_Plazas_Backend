from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CheckEmailView, VerifyCodeView, WhitelistViewSet

router = DefaultRouter()
router.register(r'whitelist', WhitelistViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('check-email/', CheckEmailView.as_view(), name='check-email'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
]
