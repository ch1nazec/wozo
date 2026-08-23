from rest_framework.routers import DefaultRouter

from django.urls import path, include
from .views import (CategoryViewSet, ProductViewSet,
                    ImageCreateAPI, ImageListAPI)


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'', ProductViewSet, basename='product')

urlpatterns = \
[
    path('images/<int:product_id>/', ImageListAPI.as_view(), name='images-list'),
    path('images/', ImageCreateAPI.as_view(), name='images-create'),
    path('', include(router.urls)),
]
