from products.serializers import ProductCartSerializer

from rest_framework import serializers
from products.models import Product


class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(source='pk')
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stocks = serializers.IntegerField(min_value=1)
    # total_price = serializers.DecimalField(
    #     max_digits=10, decimal_places=2, source='total_price')

    def to_representation(self, instance):
        print(instance)
        return super().to_representation(instance)



class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True,)
    total_price = serializers.SerializerMethodField()
    total_quantity = serializers.IntegerField()


    def to_representation(self, instance):
        instance['product'] = ProductCartSerializer(instance['product']).data
        return instance


    # def get_total_price(self, obj):
    #     print(obj)
    #     return sum(item['product'].price * item['stocks'] for item in obj['items'])


class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError('Id такого продукта нет.')
        return value


class CartRemoveSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()