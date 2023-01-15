from django_filters import rest_framework as filters
from recipe.models import Ingredients


class IngredientsFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredients
        fields = ['name', ]
