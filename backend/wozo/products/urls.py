from rest_framework.routers import DefaultRouter

from django.urls import path, include
from .views import (CategoryViewSet, ProductViewSet,
                    ImageCreateAPI)


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'', ProductViewSet, basename='product')

urlpatterns = \
[
    path('image/', ImageCreateAPI.as_view(), name='image-create'),
    path('', include(router.urls)),
]
