from django_filters import rest_framework as filters

from recipe.models import Recipes
from users.models import User


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name="tags__name")
    is_favorited = filters.BooleanFilter(method='is_in_favorites_filter')
    is_in_shopping_cart = filters.BooleanFilter(method='is_in_shopping_cart')

    def is_favorites_filter(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def is_in_shopping_cart(self, queryset, name, value):
        pass

    class Meta:
        model = Recipes
        fields = ['author', 'tags']
