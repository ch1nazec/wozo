import os
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator



# Create your models here.
class PickupPoint(models.Model):
    agent = models.ForeignKey('users.Agent', verbose_name='Агент',
                              related_name='pickup_points', blank=True,
                              null=True, on_delete=models.SET_NULL)

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
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True,
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


class PickupImage(models.Model):
    image = models.ImageField(upload_to='pickups/%Y/%m/%d/', verbose_name='Путь до изображения ПВЗ')
    pickup = models.ForeignKey('PickupPoint', on_delete=models.CASCADE,
                               related_name='images', verbose_name='Фотографии ПВЗ')

    class Meta:
        verbose_name = 'Изображение ПВЗ'
        verbose_name_plural = 'Изображения ПВЗ'

        indexes = [models.Index(fields=['pickup'])]

    def __str__(self):
        pickup_id = self.pickup_id if self.pickup_id else "Удален"
        filename = os.path.basename(self.image.name) if self.image else "Нет файла"

        return f'Изображение ПВЗ #{pickup_id} ({filename})'


class PickupFeedback(models.Model):
    pickup = models.ForeignKey('PickupPoint', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='feedbacks_pickup', verbose_name='ПВЗ для отзывов')
    user = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='feedbacks_user', verbose_name='Отзыв от пользователя')
    text = models.CharField(max_length=150, verbose_name='Текст отзыва',
                            blank=True, null=True)
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка'
    )
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв к ПВЗ'
        verbose_name_plural = 'Отзывы к ПВЗ'
        indexes = [models.Index(fields=['user'])]

        constraints = [
            models.UniqueConstraint(fields=['pickup', 'user'],
                                    name='unique_pickup_user_feedback')]

    def __str__(self):
        pickup_name = f"#{self.pickup.pk}" if self.pickup else "Удаленный ПВЗ"
        username = self.user.username if self.user else "Удаленный пользователь"
        short_text = f": {self.text[:30]}..." if self.text else ""
        
        return f'Отзыв от {username} на ПВЗ {pickup_name}{short_text} (Рейтинг: {self.rating})'