import csv

from django.core.management.base import BaseCommand

from recipe.models import Ingredients


class Command(BaseCommand):
    help = 'Fill the base'

    def handle(self, *args, **options):

        with open(
                '/home/aladinsane/Development/'
                'foodgram-project-react-master/data/ingredients.csv', 'r'
        ) as f:
            reader = csv.reader(f)
            for row in reader:
                ingredient = Ingredients(name=row[0], measurement_unit=row[1])
                print(ingredient)
                ingredient.save()
