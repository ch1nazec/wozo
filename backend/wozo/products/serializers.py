from rest_framework import serializers
from .models import Product, ImageProduct, Category

from users.models import Seller
from users.services import check_seller
from users.serializers import SellerSerializer


class ParentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)

    class Meta:
        model = Category
        fields = ['name', 'parent',]

    def validate(self, attrs: dict):
        name = attrs.get('name')
        if not name:
            return super().validate(attrs)

        if any(sym.isdigit() for sym in attrs.get('name')):
            raise serializers.ValidationError('Категория не может содержать в себе цифры.')
        attrs['name'] = attrs['name'].strip()

        return super().validate(attrs)


class ImageProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = ImageProduct
        fields = ['id', 'url_image', 'product']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.product:
            representation['product'] = {
                'id': instance.product.id,
                'name': instance.product.name
            }


class ProductWriteSerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(queryset=Seller.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = [
            'name', 'price', 'seller',
            'is_active', 'category'
        ]


    def validate(self, attrs: dict):
        seller = attrs.get('seller')
        if not check_seller(seller):
            raise serializers.ValidationError('Такого продавца не существует.')
        return super().validate(attrs)


class ProductReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    seller = SellerSerializer(read_only=True)
    images = ImageProductSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'price',
                  'seller', 'is_active',
                  'category', 'images']
        read_only_fields = ['seller']