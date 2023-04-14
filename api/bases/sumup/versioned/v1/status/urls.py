from django.urls import path, re_path
from .views import HealthCheckViewSet

urlpatterns = [
    re_path(r'^ping$', HealthCheckViewSet.as_view({'get': 'ping'}))
]