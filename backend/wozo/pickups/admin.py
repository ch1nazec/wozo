from django.contrib import admin
from .models import PickupPoint, OrderPickup, OrderPickupHistory


# Register your models here.
@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ('id', 'latitude', 'longitude', 'is_active')
    search_fields = ('latitude', 'longitude',)
    list_filter = ('latitude', 'longitude', 'is_active')

    list_per_page = 30
    ordering = ('latitude', 'longitude',)


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