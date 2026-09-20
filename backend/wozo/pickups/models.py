from django.db import models

# Create your models here.
class PickupPoint(models.Model):
    latitude = models.DecimalField(verbose_name='Ширина', max_digits=9, decimal_places=6)
    longitude = models.DecimalField(verbose_name='Долгота', max_digits=9, decimal_places=6)

    is_active = models.BooleanField(default=True, verbose_name='Статус')

    class Meta:
        db_table = 'orders_pickuppoint'

        verbose_name = 'Пункт выдачи заказов'
        verbose_name_plural = 'Пункты выдачи заказов'

    def __str__(self):
        status = 'Активен' if self.is_active else 'Закрыт'
        return f'ПВЗ #{self.pk} Коорд: lat: {self.latitude} lon: {self.longitude} Статус: {status}'

    
class OrderPickup(models.Model):
    pickup = models.ForeignKey(PickupPoint, on_delete=models.SET_NULL,
                               null=True, verbose_name='Ид. ПВЗ', related_name='orders')
    order = models.OneToOneField('orders.Order', on_delete=models.SET_NULL, null=True, blank=True,
                              verbose_name='Ид. заказа', related_name='order_pickup')

    class Meta:
        db_table = 'orders_orderpickup'

        verbose_name = 'Заказ в ПВЗ'
        verbose_name_plural = 'Заказы в ПВЗ'

        indexes = [
            models.Index(fields=['pickup', 'order'])]

    def __str__(self):
        return f'ПВЗ: {self.pickup.pk}: {self.order.pk}'


class OrderPickupHistory(models.Model):
    order_pickup = models.ForeignKey('OrderPickup', on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='Ид. заказа ПВЗ', related_name='history_records')
    active = models.CharField(max_length=200, verbose_name='Действие')
    time_active = models.DateTimeField(auto_now_add=True, verbose_name='Время действия')


    class Meta:
        db_table = 'orders_orderpickuphistory'

        verbose_name = 'История заказа'
        verbose_name_plural = 'История заказов'

        indexes = [models.Index(fields=['order_pickup'])]

    def __str__(self):
        if self.order_pickup_id:
            return f'ПВЗ #{self.order_pickup_id} — {self.active}'
        return f'История без ПВЗ (ID записи: {self.pk}) — {self.active}'


