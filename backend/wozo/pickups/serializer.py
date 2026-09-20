from rest_framework import serializers
from .models import PickupPoint


class PickupPointSerializer(serializers.ModelSerializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        model = PickupPoint
        fields = ('id', 'latitude', 'longitude')