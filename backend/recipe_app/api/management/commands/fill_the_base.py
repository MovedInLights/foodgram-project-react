import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipe.models import Ingredients

BASE_DIR = settings.BASE_DIR
batch_size = 1000


class Command(BaseCommand):
    help = 'Fill the base'

    def handle(self, *args, **options):
        bulk_list = []

        with open(os.path.join(BASE_DIR, 'data/ingredients.csv')) as f:
            reader = csv.reader(f)
            for row in reader:
                ingredient = Ingredients(name=row[0], measurement_unit=row[1])
                bulk_list.append(ingredient)
                # ingredient.save()
        Ingredients.objects.bulk_create(bulk_list, batch_size)
