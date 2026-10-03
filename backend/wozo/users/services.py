from .models import Seller


def check_seller(seller):
    return Seller.objects.filter(id=seller.id).exists()