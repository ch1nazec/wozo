from django.urls import path
from .views import CartViewSet

urlpatterns = [
    path('', CartViewSet.as_view({'get': 'list'}), name='cart-list'),
    path('add/', CartViewSet.as_view({'post': 'add'}), name='cart-add'),
    path('remove/', CartViewSet.as_view({'post': 'remove'}), name='cart-remove'),
    path('clear/', CartViewSet.as_view({'post': 'clear'}), name='cart-clear'),
]
