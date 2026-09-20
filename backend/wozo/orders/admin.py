from django.contrib import admin
from .models import Order, OrderItem


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at', 'status')
    search_fields = ('user', 'created_at', 'updated_at', 'status')

    list_per_page = 50
    ordering = ('created_at', 'updated_at')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'price', 'quantity')
    search_fields = ('order', 'product')
    list_filter = ('order', 'product', 'price', 'quantity')

    list_per_page = 30
    ordering = ('order', 'product', 'price', 'quantity')
