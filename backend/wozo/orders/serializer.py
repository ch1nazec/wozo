from rest_framework import serializers
from .models import Order, OrderItem

from users.models import CustomUser

from products.models import Product



class OrderItemWriteSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ('order', 'product', 'price', 'quantity')

    def create(self, validated_data):
        product = self.validated_data['product']
        validated_data['price'] = product.price

        return super().create(validated_data)


    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Цена не должна быть меньше 1')
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Кол-во не должно быть меньше 1')
        return value


class OrderItemReadSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(source='total_price', read_only=True, max_digits=10, decimal_places=2)
    product_name = serializers.CharField(source='product.name')

    class Meta:
        model = OrderItem
        fields = (
            'id', 'order', 'product', 'product_name',
            'price', 'quantity', 'total'
            )


class OrderWriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('user', 'status', 'status_display')

    def get_status_display(self, obj):
        return dict(Order.STATUS_CHOICES).get(obj.status, obj.status)


class OrderReadSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    order_items = OrderItemReadSerializer(many=True, read_only=True, source='items')

    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'status_display', 'order_items', 'created_at', 'updated_at')

    def get_status_display(self, obj):
        return dict(Order.STATUS_CHOICES).get(obj.status, obj.status)