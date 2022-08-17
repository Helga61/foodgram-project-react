import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Наполнение базы тестовыми данными из таблицы ингредиентов'

    def handle(self, *args, **options):
        with open("data/ingredients.csv", encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measure_unit=row[1],
                )
