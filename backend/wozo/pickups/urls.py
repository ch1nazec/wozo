from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import PickupPointViewSet, OrdersPickupPointAPIView, PickupImageViewSet, PickupFeedbackViewSet


router = DefaultRouter()

router.register(r'pickup-points', PickupPointViewSet, basename='pickup-point')
router.register(r'pickup-image', PickupImageViewSet, basename='pickup-image')
router.register(r'pickup-feedback', PickupFeedbackViewSet, basename='pickup-feedback')

urlpatterns = [
    path('pickup-orders/<int:pickup_id>/', OrdersPickupPointAPIView.as_view(), name='orders-pickup'),
    path('', include(router.urls)),
]
