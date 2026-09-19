from django.db import transaction

from rest_framework.response import Response
from rest_framework.request import Request

from rest_framework import status, viewsets
from rest_framework.decorators import action

from .models import Order, OrderItem, PickupPoint, OrderPickup, OrderPickupHistory
from .serializer import (OrderItemReadSerializer, OrderItemWriteSerializer,
                         OrderReadSerializer, OrderWriteSerializer, PickupPointSerializer)
from cart.cart import Cart

from products.models import Product


# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()


    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_order(self, request: Request, pk=None):
        order = self.get_object()

        if order.status in {'got', 'cancelled'}:
            return Response(
                data={'error': 'Заказ невозможно отменить.'},
                status=status.HTTP_400_BAD_REQUEST)


        order_pickup = OrderPickup.objects.filter(order=order).first()
        OrderPickupHistory.objects.create(
                order_pickup=order_pickup,
                active='Отменён')


        order.status = 'cancelled'
        order.save()

        serializer = OrderReadSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return OrderWriteSerializer
        return OrderReadSerializer


    def create(self, request: Request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(data={'error': 'Пользователь не зарегистрирован.'},
                            status=status.HTTP_404_NOT_FOUND)

        pickup_id = request.data.get('pickup')
        cart = Cart(user.id)

        try:
            pickup_point = PickupPoint.objects.get(id=pickup_id)
        except PickupPoint.DoesNotExist:
            return Response(data={'error': 'Указанный ПВЗ не найден.'}, 
                            status=status.HTTP_404_NOT_FOUND)

        if not list(cart): 
            return Response(data={'error': 'Корзина пуста'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            user = request.user

            order = Order.objects.create(user=user)
            total_amount = 0

            for item in cart:
                product_item = item.get('product')
                quantity_item = item.get('quantity')

                try:
                    product = Product.objects.select_for_update().get(id=product_item.pk)
                except Product.DoesNotExist:
                    return Response(
                        data={'error': f'Товар с id {item.pk} не найден.'},
                        status=status.HTTP_404_NOT_FOUND)

                if product.stocks < quantity_item:
                    return Response(
                        data={'error': f'Недостаточно товара на складе.'},
                        status=status.HTTP_400_BAD_REQUEST)

                
                product.stocks -= quantity_item
                product.save()

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=quantity_item
                )
                total_amount += product.price * quantity_item


            order_pickup_create = OrderPickup.objects.create(
                pickup=pickup_point,
                order=order)
            OrderPickupHistory.objects.create(
                order_pickup=order_pickup_create,
                active='Создан')


            order.total_amount = total_amount
            order.save()
            cart.clear()

        print(order)
        return Response(data={
                'order': order,
                'order_id': order.pk,
                'pickup_id': pickup_id,}, status=status.HTTP_201_CREATED)


class PickupPointViewSet(viewsets.ModelViewSet):
    queryset = PickupPoint.objects.all()
    serializer_class = PickupPointSerializer


    def create(self, request: Request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)