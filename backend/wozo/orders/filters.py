import django_filters
from .models import Order, OrderItem


GTE_LTE_CONSTANT = ['gte', 'lte']
class OrderFilters(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = \
        {
            'created_at': GTE_LTE_CONSTANT,
            'updated_at': GTE_LTE_CONSTANT,
            'status': ['exact']
        }