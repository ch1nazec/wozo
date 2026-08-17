from rest_framework import serializers
from .models import Product, ImageProduct, Category

from users.services import check_seller


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'parent']

    def validate_parent(self, value: dict):
        if value and not Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError('Родительской категории не существует.')
        return value


    def validate(self, attrs: dict):
        if any(sym.isdigit() for sym in attrs.get('name')):
            raise serializers.ValidationError('Категория не может содержать в себе цифры.')
        attrs['name'] = attrs['name'].capitalize()

        return super().validate(attrs)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price',
                  'seller', 'is_active',
                  'category']
        read_only_fields = ['seller']

    def validate(self, attrs: dict):
        seller = attrs.get('seller')
        if not check_seller(seller):
            raise serializers.ValidationError('Такого продавца не существует.')
        return super().validate(attrs)


class ImageProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProduct
        fields = ['url_image', 'product']