from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import OrderViewSet, order_items, OrderStatusUpdateView


router = DefaultRouter()

router.register(r'', OrderViewSet, basename='order')

urlpatterns = [
    path('detail/<int:order_id>/', order_items, name='order-detail'),
    path('status/', OrderStatusUpdateView.as_view(), name='order-status'),

    path('', include(router.urls)),
]
