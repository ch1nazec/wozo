from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import (Category,
                     Product,
                     ImageProduct)

from .serializers import (CategorySerializer,
                          ImageProductSerializer,
                          ProductReadSerializer, ProductWriteSerializer)

from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.request import Request

from rest_framework.decorators import action, api_view
from rest_framework_extensions.cache.decorators import cache_response

from .permissions import IsAdminOrReadUser, IsSellerOrAdmin
from .filters import ProductFilter, CategoryFilter
from services.pagination_classes import HunderResultsSetPagination, FiftyResultsSetPagination


# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related('parent').all()
    permission_classes = (IsAdminOrReadUser,)
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter

    pagination_class = HunderResultsSetPagination

    ordering = ('name',)
    ordering_fields = ('name',)

    def list(self, request, *args, **kwargs):
        query_params = request.GET.urlencode()
        cache_key = f'category_list:{query_params}'

        cache_data = cache.get(cache_key)
        if cache_data is not None:
            return Response(cache_data)

        response = super().list(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            cache.set(cache_key, response.data, 60 * 60)
        
        return response

    def retrieve(self, request, *args, **kwargs):
        category_id = kwargs.get('pk')
        cache_key = f'category_detail:{category_id}'

        cache_data = cache.get(cache_key)
        if cache_data is not None:
            return cache_data
        
        response = super().retrieve(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            cache.set(cache_key, cache_data, 60 * 60)
        return response


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('seller', 'category').all()
    permission_classes = (IsSellerOrAdmin,)
    filterset_class = ProductFilter

    pagination_class = FiftyResultsSetPagination

    ordering = ('name',)
    ordering_fields = ('name', 'price', 'stocks',)


    def list(self, request, *args, **kwargs):
        query_params = request.GET.urlencode()
        cache_key = f'product_list:{query_params}'

        cache_data = cache.get(cache_key)
        if cache_data is not None:
            return Response(cache_data)

        response = super().list(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            cache.set(cache_key, response.data, 60 * 60)

        return response


    def retrieve(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        cache_key = f'product_detail:{product_id}'

        cache_data = cache.get(cache_key)
        if cache_data is not None:
            return Response(cache_data)

        response = super().retrieve(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            cache.set(cache_key, response.data, 60 * 60)
        return response


    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return ProductWriteSerializer
        return ProductReadSerializer


    def get_queryset(self):
        queryset = super().get_queryset()
        seller_id = self.request.query_params.get('seller_id')
        if seller_id is not None:
            return queryset.filter(seller_id=seller_id)
        return queryset


    @action(detail=False, methods=['get'])
    def my(self, request: Request):
        cache_key = f'product_my:{request.user.id}'
        
        cache_data = cache.get(cache_key)
        if cache_data is not None:
            return Response(cache_data)

        products = self.get_queryset().filter(seller__id=request.user.id)
        serializer = self.get_serializer(products, many=True)
        data = serializer.data

        cache.set(cache_key, data, 60 * 60)
        return Response(data)


class SellerProductsAPI(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductReadSerializer

    pagination_class = FiftyResultsSetPagination
    
    ordering = ('name',)
    ordering_fields = ('name', 'price', 'stocks')

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def list(self, request: Request, *args, **kwargs):
        seller_id = self.kwargs.get('seller_id')
        query_params = request.GET.urlencode()
        cache_key = f'seller_product_list:{seller_id}:{query_params}'

        cache_data = cache.get(cache_key)
        if cache_data is not None:
            return Response(cache_data)
        products = Product.objects.filter(seller__id=seller_id).select_related('seller')

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            cache.set(cache_key, response.data, 60 * 60)
            return response

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    

class ImageCreateAPI(generics.CreateAPIView):
    permission_classes = (IsSellerOrAdmin,)
    serializer_class = ImageProductSerializer


class ImageListAPI(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ImageProductSerializer

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        # cache_key = f'product_detail:{product_id}'

        # cache_data = cache.get(cache_key)
        # if cache_data is not None:
        #     return Response(cache_data)
        if product_id:
            return ImageProduct.objects.filter(product_id=product_id).select_related('product')
        return ImageProduct.objects.none()

    def list(self, request: Request, *args, **kwargs):
        seller_id = self.kwargs.get('seller_id')
        query_params = request.GET.urlencode()

        cache_key = f'image_list:{seller_id}:{query_params}'
        cache_data = cache.get(cache_key)

        if cache_data is not None:
            return Response(cache_data)
        
        data = super().list(request, *args, **kwargs)
        cache.set(cache_key, data, 60 * 30)
        return data

    def retrieve(self, request: Request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@api_view(['POST'])
def add_stocks_all_products(request: Request):
    stocks = request.data.get('stocks')
    products = Product.objects.all()

    for product in products:
        product.stocks += stocks
        product.save()

    serializer = ProductReadSerializer(products, many=True)
    return Response(serializer.data)