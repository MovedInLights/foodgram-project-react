from django.contrib import admin

from recipe.models import (Favorite, Ingredients, RecipeIngredients, Recipes,
                           ShoppingCart, Tags)

from .models import User


class TagsAdm(admin.ModelAdmin):
    model = Tags
    list_display = ('name', 'color', 'slug')
    list_display_links = ('name',)


class IngredientsAdm(admin.ModelAdmin):
    model = Ingredients
    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('name',)
    list_filter = ['name']


class RecipesAdm(admin.ModelAdmin):

    model = Recipes
    list_display = (
        'name',
        'image',
        'text',
        'tag',
        'cooking_time',
        'author',
        'ingredient',
        'favorite_count'
    )
    list_display_links = ('name',)
    list_filter = ['author', 'name', 'tags']

    def ingredient(self, obj):
        return ", ".join([ing.name for ing in obj.ingredients.all()])

    def tag(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    def favorite_count(self, obj):
        print(obj)
        return Favorite.objects.filter(recipe=obj).count()


class UserAdm(admin.ModelAdmin):
    model = User
    list_display = ('username', 'first_name', 'last_name', 'email',)
    list_display_links = ('username',)
    list_filter = ['username', 'email']


class RecipeIngredientsAdm(admin.ModelAdmin):
    model = RecipeIngredients
    list_display = ('recipe', 'ingredients', 'amount')
    list_display_links = ('recipe',)


class ShoppingCartAdm(admin.ModelAdmin):
    model = ShoppingCart
    list_display = ('user', 'recipe',)
    list_display_links = ('user',)


class FavoriteAdm(admin.ModelAdmin):
    model = Favorite
    list_display = ('user', 'recipe',)
    list_display_links = ('user',)


admin.site.register(User, UserAdm)
admin.site.register(Tags, TagsAdm)
admin.site.register(Recipes, RecipesAdm)
admin.site.register(Ingredients, IngredientsAdm)
admin.site.register(RecipeIngredients, RecipeIngredientsAdm)
admin.site.register(ShoppingCart, ShoppingCartAdm)
admin.site.register(Favorite, FavoriteAdm)
