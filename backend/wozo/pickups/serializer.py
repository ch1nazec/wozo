from rest_framework import serializers

from .models import PickupPoint, OrderPickupHistory, OrderPickup, PickupFeedback, PickupImage
from orders.serializer import OrderReadSerializer


class PickupPointSerializer(serializers.ModelSerializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        model = PickupPoint
        fields = ('id', 'agent', 'latitude', 'longitude')


class OrderPickupSerializer(serializers.ModelSerializer):
    total_order = serializers.DecimalField(source='order.total_price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderPickup
        fields = (
            'id', 'pickup',
            'order', 'total_order')



class OrderPickupHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPickupHistory
        fields = (
            'id', 'order_pickup',
            'active', 'time_active')





class PickupImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupImage
        fields = ('image', 'pickup')


class PickupFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupFeedback
        fields = (
            'pickup', 'user',
            'rating', 'text')