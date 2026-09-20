from .models import Order


def check_order(order_id: int):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return False
    return order


def check_status(order: Order, status: str) -> bool:
    return order.status == status