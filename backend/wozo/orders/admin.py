from django.contrib import admin
from .models import PickupPoint, Order, OrderItem, OrderPickup, OrderPickupHistory


# Register your models here.
@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ('id', 'latitude', 'longitude', 'is_active')
    search_fields = ('latitude', 'longitude',)
    list_filter = ('latitude', 'longitude', 'is_active')

    list_per_page = 30
    ordering = ('latitude', 'longitude',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'status')
    search_fields = ('user', 'created_at', 'updated_at', 'status')

    list_per_page = 50
    ordering = ('created_at', 'updated_at')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'quantity')
    search_fields = ('order', 'product')
    list_filter = ('order', 'product', 'price', 'quantity')

    list_per_page = 30
    ordering = ('order', 'product', 'price', 'quantity')


@admin.register(OrderPickup)
class OrderPickupAdmin(admin.ModelAdmin):
    list_display = ('pickup', 'order')
    search_fields = ('pickup', 'order')

    list_per_page = 30


@admin.register(OrderPickupHistory)
class OrderPickupHistoryAdmin(admin.ModelAdmin):
    list_display = ('order_pickup', 'active', 'time_active')
    search_fields = ('order_pickup', 'time_active')

    list_per_page = 30