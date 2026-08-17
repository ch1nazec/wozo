import uuid, os

from django.utils import timezone
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.
class Category(MPTTModel):
    name = models.CharField(max_length=150,
                            blank=False, null=False,
                            unique=True, verbose_name='Категории товаров')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,
                            blank=True, related_name='subcategories')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['parent']),]

    def __str__(self):
        return f'Category: {self.name}'


class Product(models.Model):
    name = models.CharField(max_length=200, blank=False,
                            null=False, verbose_name='Название товара')
    price = models.DecimalField(verbose_name='Цена продукта', decimal_places=2, max_digits=20)
    seller = models.ForeignKey('users.Seller', on_delete=models.CASCADE,
                               related_name='products', verbose_name='Имя продавца')
    is_active = models.BooleanField(default=True, verbose_name='Видимость продукта')

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='products', verbose_name='Категория товара',)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

        ordering = ['name', 'price', 'is_active']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['seller']),
        ]

    def __str__(self):
        return f'{self.name} - {self.price} RUB'


def generate_name_of_image(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    date_image = timezone.now().strftime('image/products/%Y/%m/%d')

    return os.path.join(date_image, new_filename)


class ImageProduct(models.Model):
    url_image = models.ImageField(upload_to=generate_name_of_image,
                                  verbose_name='Путь до изображения')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='images', verbose_name='Фотографии продуктов')

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображение товаров'

        indexes = [models.Index(fields=['product'])]

    def __str__(self):
        return f'Изображение продукта {self.product.name}'