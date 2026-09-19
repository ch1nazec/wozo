from django.contrib import admin
from .models import Category, Product, ImageProduct


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'price', 'stocks', 'seller', 'is_active', 'category']
    search_fields = ['name', 'slug', 'price', 'stocks', 'seller__user__first_name', 'is_active']
    list_filter = ['price', 'name', 'stocks',]

    list_per_page = 20
    ordering = ['name', 'price', 'stocks',]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    search_fields = ['name']
    list_filter = ['name', 'slug']

    list_per_page = 20


@admin.register(ImageProduct)
class ImageProductAdmin(admin.ModelAdmin):
    pass