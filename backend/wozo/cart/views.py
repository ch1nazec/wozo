from .cart import Cart

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework import status

from rest_framework.response import Response
from rest_framework.request import Request

from .serializers import (CartSerializer, CartAddSerializer,
                         CartItemSerializer, CartRemoveSerializer)

from products.models import Product


# Create your views here.
class CartViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)


    def list(self, request: Request) -> Response:
        cart = Cart(request.user.id)
        serializer = CartSerializer(cart, many=True)

        data_info = {
            'total_price': cart.get_total_price(),
            'quantity': len(cart)
        }

        selializer_data = serializer.data
        selializer_data.append(data_info)

        return Response(selializer_data)


    def add(self, request: Request) -> Response:
        serializer = CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        product = Product.objects.select_for_update().get(id=product_id)

        if product.stocks < quantity:
            return Response({'error': 'На складе меньше продуктов, чем указано.'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        cart = Cart(request.user.id)
        cart.add(product, quantity)

        return Response({'status': 'added'}, status=status.HTTP_201_CREATED)


    def remove(self, request: Request) -> Response:
        serializer = CartRemoveSerializer(request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        product = Product.objects.get(id=product_id)

        cart = Cart(request.user.id)
        cart.remove(product)

        return Response({'status': 'removed'}, status=status.HTTP_200_OK)


    def clear(self, request: Request) -> Response:
        cart = Cart(request.user.id)
        cart.clear()

        return Response({'status': 'cleared'}, status=status.HTTP_200_OK)