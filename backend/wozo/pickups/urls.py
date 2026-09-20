from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import PickupPointViewSet


router = DefaultRouter()

router.register(r'pickup-points', PickupPointViewSet, basename='pickup-point')

urlpatterns = [
    path('', include(router.urls)),
]
