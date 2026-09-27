import django_filters
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = \
            {
            'category__name': ['icontains', 'exact'],
            'price': ['gte', 'lte'],
            'stocks': ['gte', 'lte'],
            }


class CategoryFilter(django_filters.FilterSet):
    class Meta:
        model = Category
        fields = \
        {
            'name': ['icontains', 'exact'],
            'slug': ['icontains', 'exact']
        }