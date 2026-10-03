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

        indexes = [
            models.Index(fields=['first_name']),
            models.Index(fields=['date_birth',]),
            models.Index(fields=['phone_number'])]


class PersonalData(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='personal_data')

    inn = models.CharField(max_length=12, blank=True, null=True, unique=True)
    snils = models.CharField(max_length=14, blank=True, null=True, unique=True)

    passport_series = models.CharField(max_length=4, blank=True, null=True)
    passport_number = models.CharField(max_length=6, blank=True, null=True)

    passport_issued_by = models.TextField(blank=True, null=True)
    passport_issued_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.last_name} {self.user.first_name}'

    class Meta:
        ordering = ['-id']
        unique_together = ('passport_series', 'passport_number')
        indexes = \
        [   
            models.Index(fields=['inn']),
            models.Index(fields=['snils']),
            models.Index(fields=['passport_series', 'passport_number']),
        ]

        verbose_name = 'Личные документы'
        verbose_name_plural = 'Личные документы'


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
        ordering = ['-id']
        indexes = [models.Index(fields=['status']),]

        verbose_name = 'Продавец'
        verbose_name_plural = 'Продавцы'


# БУДЕТ РАЗРАБОТАНА ПОЛНОСТЬЮ МОДЕЛЬ С РАБОЧИМИ И СКЛАДАМИ, ОДНАКО СЕЙЧАС ЭТО БОЛЬШЕ ПРО ЗАГЛУШКУ!
# class Worker(models.Model):
#     user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='worker', verbose_name='Пользователь')
#     contract_number = models.CharField(max_length=100, verbose_name='Номер контракта', blank=True, null=True)

#     is_active = models.BooleanField(default=True)


#     class Meta:
#         ordering = ['-id']
#         indexes = \
#         [ 
#             models.Index(fields=['is_active']),
#         ]
#         verbose_name = 'Сотрудник'
#         verbose_name_plural = 'Сотрудники'


class Agent(models.Model):
    personal_data = models.ForeignKey('PersonalData', on_delete=models.CASCADE,
                                      related_name='personaldata_agent', verbose_name='Данные об агенте')
    is_active = models.BooleanField(default=True)


    class Meta:
        ordering = ['-id', 'is_active']
        indexes = \
        [
            models.Index(fields=['personal_data']),
        ]
        verbose_name = 'Агент'
        verbose_name_plural = 'Агенты'

    def __str__(self):
        return f'{self.personal_data.user}'