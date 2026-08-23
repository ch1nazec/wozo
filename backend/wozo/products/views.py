from .models import (Category,
                     Product,
                     ImageProduct)

from .serializers import (CategorySerializer,
                          ImageProductSerializer,
                          ProductReadSerializer, ProductWriteSerializer)

from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from .permissions import IsAdminOrReadUser, IsSellerOrAdmin


# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related('parent').all()
    permission_classes = (IsAdminOrReadUser,)
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('seller', 'category').all()
    permission_classes = (IsSellerOrAdmin,)


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
    def my(self, request):
        products = self.get_queryset().filter(seller__id=request.user)
        serializer = self.get_serializer_class(products, many=True)
        return Response(serializer.data)


class ImageCreateAPI(generics.CreateAPIView):
    permission_classes = (IsSellerOrAdmin,)
    serializer_class = ImageProductSerializer


class ImageListAPI(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ImageProductSerializer

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return ImageProduct.objects.filter(product_id=product_id).select_related('product')
        return ImageProduct.objects.none()