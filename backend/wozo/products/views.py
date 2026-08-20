from .models import (Category,
                     Product,
                     ImageProduct)

from .serializers import (CategorySerializer,
                          ProductSerializer,
                          ImageProductSerializer)

from rest_framework import viewsets, views, generics
from .permissions import IsAdminOrReadUser, IsSellerOrAdmin


# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related('parent').all()
    permission_classes = (IsAdminOrReadUser,)
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('seller', 'category').all()
    permission_classes = (IsSellerOrAdmin,)
    serializer_class = ProductSerializer


    def get_queryset(self):
        queryset = super().get_queryset()
        seller_id = self.request.query_params.get('seller_id')
        if seller_id is not None:
            return queryset.filter(seller_id=seller_id)
        return queryset


class ImageCreateAPI(generics.CreateAPIView):
    queryset = ImageProduct.objects.select_related('product').all()
    permission_classes = (IsSellerOrAdmin,)
    serializer_class = ImageProductSerializer