from django.contrib import admin
from .models import Category, Product, ImageProduct


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'seller', 'is_active', 'category']
    search_fields = ['name', 'slug', 'price', 'seller__user__first_name', 'is_active']
    list_filter = ['price', 'name']

    list_per_page = 20
    ordering = ['name', 'price']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    search_fields = ['name']
    list_filter = ['name', 'slug']

    list_per_page = 20


@admin.register(ImageProduct)
class ImageProductAdmin(admin.ModelAdmin):
    pass