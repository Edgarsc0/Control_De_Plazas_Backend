from django.urls import path
from .views import AntigravityChatView, AIUsageStatsView

urlpatterns = [
    path('chat/', AntigravityChatView.as_view(), name='antigravity-chat'),
    path('usage/', AIUsageStatsView.as_view(), name='antigravity-usage'),
]
