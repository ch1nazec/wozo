from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
@receiver(post_delete, sender=CustomUser)
def clear_user_viewset_cache(sender, instance, **kwargs):
    cache.delete_pattern('*UserProfileView*')
    cache.delete_pattern('*UserViewSet*')
    cache.delete_pattern('*SellerViewSet*')
    cache.delete_pattern('*AgentViewSet*')
    cache.delete_pattern('*PersonalDataViewSet*')