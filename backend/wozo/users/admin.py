from django.contrib import admin
from .models import CustomUser, Seller


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'third_name', 'first_name', 'last_name', 'email', 'phone_number', 'phone_number', 'is_staff', 'date_joined']