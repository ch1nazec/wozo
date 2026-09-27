import django_filters
from .models import PickupPoint


class PickupPointFilters(django_filters.FilterSet):
    class Meta:
        model = PickupPoint
        fields = \
        {
            'latitude': ['exact'],
            'longitude': ['exact'],
        }