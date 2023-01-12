from django_filters import rest_framework as filters
from recipe.models import Recipes, Ingredients, Favorite
from users.models import User


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug', lookup_expr='contains')
    is_favorited = filters.BooleanFilter(method='is_in_favorites_filter')
    is_in_shopping_cart = filters.BooleanFilter(method='is_in_shopping_cart')

    def is_in_favorites_filter(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            queryset = Favorite.objects.filter(user=self.request.user).values_list('recipe', flat=True)
            recipes = Recipes.objects.filter(id__in=queryset)
        return recipes

    def is_in_shopping_cart(self, queryset, name, value):
        pass

    class Meta:
        model = Recipes
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']


class IngredientsFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredients
        fields = ['name', ]
