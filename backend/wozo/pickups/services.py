from .models import PickupPoint, OrderPickupHistory, OrderPickup


def check_pickup_point(pickuppoint_id: int):
    try:
        pickup_point = PickupPoint.objects.get(id=pickuppoint_id)
    except PickupPoint.DoesNotExist:
        return False
    return pickup_point


def check_order_pickup(pickuppoint: PickupPoint):
    try:
        order_pickup = OrderPickup.objects.get(pickup=pickuppoint)
    except OrderPickup.DoesNotExist:
        return False
    return order_pickup