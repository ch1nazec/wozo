from models import Seller


def check_seller(seller: dict):
    return Seller.objects.filter(id=seller.get('id')).exists()