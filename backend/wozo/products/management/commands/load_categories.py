import json
from django.core.management.base import BaseCommand
from ...models import Category

class Command(BaseCommand):
    help = 'Load categories from JSON file (MPTT-safe)'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file with categories')

    def handle(self, *args, **kwargs):
        file_path = kwargs['json_file']
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Очищаем старые категории (если надо)
        Category.objects.all().delete()

        # Создаём категории
        for item in data:
            fields = item['fields']
            category = Category(
                name=fields['name'],
                slug=fields['slug'],
                parent_id=fields['parent']  # MPTT поймёт, что это parent
            )
            category.save()  # Вот тут MPTT сам заполнит lft, rght, tree_id, level

        self.stdout.write(self.style.SUCCESS(f'Загружено {len(data)} категорий'))