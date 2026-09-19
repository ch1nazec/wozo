import json, redis
from django.conf import settings

from decimal import Decimal
from products.models import Product


class Cart:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self.cart_key = f"cart:{self.user_id}"
        self._cart_data = None


    def _load(self):
        if self._cart_data is None:
            data = self.redis_client.get(self.cart_key)
            if data:
                self._cart_data = json.loads(data)
            else:
                self._cart_data = {}
        return self._cart_data


    def _save(self):
        data = json.dumps(self._cart_data, default=str)
        self.redis_client.setex(
            self.cart_key,
            settings.CART_TTL,
            data)


    def add(self, product, quantity: 1, override_quantity=False):
        cart = self._load()
        product_id = product.id

        if product_id not in cart:
            cart[product_id] = {
                'quantity': 0,
                'price': product.price}
            
        if override_quantity:
            cart[product_id]['quantity'] = quantity
        else:
            cart[product_id]['quantity'] += quantity

        self._save()


    def remove(self, product):
        cart = self._load()
        product_id = str(product.id)

        if product_id in cart:
            if cart[product_id]['quantity'] == 1:
                del cart[product_id]
            elif cart[product_id]['quantity'] > 1:
                cart[product_id]['quantity'] -= 1
            self._save()


    def __iter__(self):
        cart = self._load()
        if not cart:
            return

        products_ids = cart.keys()
        products = Product.objects.filter(id__in=products_ids).select_related('category')

        cart_copy = cart.copy()
        for product in products:
            cart_copy[str(product.pk)]['product'] = product
        for item in cart_copy.values():
            price = Decimal(item['price'])
            item['price'] = Decimal(price)
            item['total_price'] = Decimal(price * item['quantity'])
            yield item


    def __len__(self):
        cart = self._load()
        return sum(item['quantity'] for item in cart.values())


    def get_total_price(self):
        cart = self._load()
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in cart.values()
        )

    def clear(self):
        self.redis_client.delete(self.cart_key)
        self._cart_data = None