from django.utils import timezone

from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models


def validate_ages(value):
    if (timezone.now().date() - value).days < 14 * 365.25:
        raise ValidationError('Вход в аккаунт минимум с 14 лет!')

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(verbose_name='Почта пользователя', blank=False, null=False, unique=True)
    third_name = models.CharField(verbose_name='Отчество', max_length=100, blank=True, null=True)

    date_birth = models.DateField(verbose_name='Дата рождения', validators=[validate_ages], blank=True, null=True)
    phone_number = PhoneNumberField(region='RU', blank=True, null=True)

    def __str__(self):
        return f'{self.username} - {self.last_name} {self.first_name} {self.third_name}'


    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        indexes = [models.Index(fields=['first_name', 'date_birth', 'phone_number'])]


class Seller(models.Model):
    class Business(models.TextChoices):
        SELF_EMPLOYED = 'Self-employed', 'Самозанятый'
        INDIVIDUAL_ENTREPRENEUR = 'Individual entrepreneur', 'Индивидуальный предприниматель'
        OOO = 'OOO', 'ООО'

    status = models.CharField(max_length=50, choices=Business.choices)
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='seller')
    is_active = models.BooleanField(verbose_name='Действие продавца', default=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"

    class Meta:
        ordering = ['user__id']
        indexes = [models.Index(fields=['status', 'user'])]

        verbose_name = 'Продавец'
        verbose_name_plural = 'Продавцы'