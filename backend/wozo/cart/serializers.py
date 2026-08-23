from rest_framework import serializers
from products.models import Product


class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(source='product.id')
    name = serializers.CharField(source='product.name')
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField(min_value=1)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, source='total_price')


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_quantity = serializers.IntegerField()


    def to_representation(self, instance):
        items = list(instance)
        total_price = instance.get_total_price()
        total_quantity = len(instance)


        return {
            'items': items,
            'total_price': total_price,
            'total_quantity': total_quantity
        }


class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError('Id такого продукта нет.')


class CartRemoveSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()