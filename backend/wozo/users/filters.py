import django_filters
from .models import Seller, PersonalData


FILTER_CONSTANT = ['exact', 'icontains']

class SellerFilters(django_filters.FilterSet):
    class Meta:
        model = Seller
        fields = {
            'status': FILTER_CONSTANT
        }


class PersonalDataFilters(django_filters.FilterSet):
    class Meta:
        model = PersonalData
        fields = \
        {
            'inn': FILTER_CONSTANT,
            'snils': FILTER_CONSTANT,
            'passport_series': FILTER_CONSTANT,
            'passport_number': FILTER_CONSTANT,
        }