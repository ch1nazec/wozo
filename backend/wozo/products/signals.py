from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, Category, ImageProduct


@receiver([post_delete, post_save], sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    cache.delete(f'product_detail:{instance.id}')

    cache.delete_pattern('product_list:*')
    if instance.seller_id:
        cache.delete(f'product_my:{instance.seller_id}')
        cache.delete_pattern(f'seller_products_list:{instance.seller_id}:*')


@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    cache.delete(f'category_detail:{instance.id}')
    cache.delete_pattern('category_list:*')


@receiver([post_save, post_delete], sender=ImageProduct)
def clear_image_cache(sender, instance, **kwargs):
    if instance.product_id:
        cache.delete(f'image_list:{instance.product_id}')