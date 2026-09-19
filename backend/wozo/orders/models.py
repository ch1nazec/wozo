from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

# Create your models here.
class PickupPoint(models.Model):
    latitude = models.DecimalField(verbose_name='Ширина', max_digits=9, decimal_places=6)
    longitude = models.DecimalField(verbose_name='Долгота', max_digits=9, decimal_places=6)

    is_active = models.BooleanField(default=True, verbose_name='Статус')

    class Meta:
        verbose_name = 'Пункт выдачи заказов'
        verbose_name_plural = 'Пункты выдачи заказов'

    def __str__(self):
        status = 'Активен' if self.is_active else 'Закрыт'
        return f'ПВЗ #{self.pk} Коорд: lat: {self.latitude} lon: {self.longitude} Статус: {status}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('shipped', 'Отправлен'),
        ('success', 'На ПВЗ'),
        ('cancelled', 'Отменён'),
        ('got', 'Получен')
    ]
    user = models.ForeignKey(User, verbose_name='Заказ пользователя', on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время изменения')
    status = models.CharField(choices=STATUS_CHOICES, max_length=15, default='pending')


    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at', '-updated_at']

        indexes = [models.Index(fields=['user'])]

    def __str__(self):
        return f'{self.user} - {self.created_at} {self.status}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Предмет товара', related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, verbose_name='Товар', related_name='order_items')
    price = models.DecimalField(verbose_name='Цена продукта', decimal_places=2, max_digits=10)
    quantity = models.PositiveIntegerField(verbose_name='Кол-во товара')


    class Meta:
        verbose_name = 'Продукт заказа'
        verbose_name_plural = 'Продукты заказа'
        ordering = ['-order', '-product']

        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product'])]

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        product_name = self.product.name if self.product.name else 'Удалённый товар'
        return f'Item {self.id} ({product_name}) x {self.quantity}'


class OrderPickup(models.Model):
    pickup = models.ForeignKey(PickupPoint, on_delete=models.SET_NULL,
                               null=True, verbose_name='Ид. ПВЗ', related_name='orders')
    order = models.OneToOneField('Order', on_delete=models.SET_NULL, null=True, blank=True,
                              verbose_name='Ид. заказа', related_name='order_pickup')

    class Meta:
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
        verbose_name = 'История заказа'
        verbose_name_plural = 'История заказов'

        indexes = [models.Index(fields=['order_pickup'])]

    def __str__(self):
        if self.order_pickup_id:
            return f'ПВЗ #{self.order_pickup_id} — {self.active}'
        return f'История без ПВЗ (ID записи: {self.pk}) — {self.active}'