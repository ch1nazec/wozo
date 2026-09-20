from django.db import transaction
from django.core.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework.request import Request

from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view

from .models import Order, OrderItem
from .serializer import (OrderItemReadSerializer, OrderItemWriteSerializer,
                         OrderReadSerializer, OrderWriteSerializer)
from cart.cart import Cart


from products.models import Product
from pickups.models import PickupPoint, OrderPickup, OrderPickupHistory

from .services import check_order


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

        return Response(data={
                'order': order,
                'order_id': order.pk,
                'pickup_id': pickup_id,}, status=status.HTTP_201_CREATED)


class OrderStatusUpdateView(APIView):
    def post(self, request):

        order_id = request.data.get('order_id')
        action = request.data.get('action')

        allowed_actions = set(choice[0] for choice in Order.STATUS_CHOICES)

        if action not in allowed_actions:
            return Response(data={'error': 'Такой метод не предусмотрен.'},
                            status=status.HTTP_400_BAD_REQUEST)

        order = check_order(order_id)
        if not order:
            return Response({'error': f'Заказа с #{order_id} не существует.'},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                order.change_status(action)
        except ValidationError as error:
            return Response({'error': str(error)}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'status': action},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
def order_items(request: Request, order_id: int):
    order = check_order(order_id)
    if not order:
        return Response({'error': f'Заказа с {order_id}# не существует.'},
                        status=status.HTTP_404_NOT_FOUND)

    order_items = OrderItem.objects.filter(order=order)
    serializer = OrderItemReadSerializer(order_items, many=True).data

    return Response(serializer, status=status.HTTP_200_OK)