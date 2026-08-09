from django.contrib import admin
from .models import CustomUser, Seller


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'third_name',
                    'first_name', 'last_name',
                    'email', 'phone_number',
                    'is_staff', 'date_joined']


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'status']
    list_display_links = ['user']
    list_editable = ['status']

    search_fields = [
        'user__third_name',
        'user__first_name',
        'user__last_name',
        'user__username',
        'status',
        'user__phone_number',
        'user__email']
    list_filter = ['user__third_name',
                   'user__first_name',
                   'user__last_name',
                   'user__username',
                   'status',
                   'user__phone_number',
                   'user__email']

    list_select_related = ['user']
    list_per_page = 50
    ordering = ['user']
