from django.contrib import admin
from recipe.models import (Favorite, Ingredients, RecipeIngredients, Recipes,
                           ShoppingCart, Tags)
from django.core.management import call_command


class RecipeIngredientsAdm(admin.ModelAdmin):
    model = RecipeIngredients
    list_display = ('recipe', 'related_ingredient', 'amount')
    list_display_links = ('recipe',)


class ShoppingCartAdm(admin.ModelAdmin):
    model = ShoppingCart
    list_display = ('user', 'recipe',)
    list_display_links = ('user',)


class FavoriteAdm(admin.ModelAdmin):
    model = Favorite
    list_display = ('user', 'recipe',)
    list_display_links = ('user',)


class TagsAdm(admin.ModelAdmin):
    model = Tags
    list_display = ('name', 'color', 'slug')
    list_display_links = ('name',)


class IngredientsAdm(admin.ModelAdmin):
    actions = ['fill_the_base', ]
    model = Ingredients
    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('name',)
    list_filter = ['name']

    def fill_the_base(self, request, queryset):
        for qs in queryset:
            call_command('fill_the_base')


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
        return Favorite.objects.filter(recipe=obj).count()


admin.site.register(Tags, TagsAdm)
admin.site.register(Recipes, RecipesAdm)
admin.site.register(Ingredients, IngredientsAdm)
admin.site.register(RecipeIngredients, RecipeIngredientsAdm)
admin.site.register(ShoppingCart, ShoppingCartAdm)
admin.site.register(Favorite, FavoriteAdm)
