from rest_framework.routers import DefaultRouter

from django.urls import path, include
from .views import (CategoryViewSet, ProductViewSet,
                    ImageCreateAPI, ImageListAPI, SellerProductsAPI, add_stocks_all_products)


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'', ProductViewSet, basename='product')

urlpatterns = \
[
    path('product-add/', add_stocks_all_products, name='add-stocks'),
    path('product-seller/<seller_id>/', SellerProductsAPI.as_view({'get': 'list'}), name='seller-products'),
    path('images/<int:product_id>/', ImageListAPI.as_view(), name='images-list'),
    path('images/', ImageCreateAPI.as_view(), name='images-create'),
    path('', include(router.urls)),
]
