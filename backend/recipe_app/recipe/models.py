from django.db import models

from users.models import User


class Ingredients(models.Model):
    name = models.CharField(max_length=200)
    amount = models.IntegerField(null=True, blank=True)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'


class Tags(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=200)
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Recipes(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipes/images', blank=True, default=None
    )
    text = models.CharField(max_length=500)
    ingredients = models.ManyToManyField(Ingredients)
    tags = models.ManyToManyField(Tags)
    cooking_time = models.IntegerField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe_with_ing',
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredients_for_recipe',
    )

    amount = models.IntegerField(null=True, blank=True)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        unique_together = ('recipe', 'ingredients')
        verbose_name = 'RecipeIngredient'
        verbose_name_plural = 'RecipeIngredients'

    def __str__(self):
        return f'{self.recipe} {self.ingredients}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user',
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe',
    )

    class Meta:
        unique_together = ('recipe', 'user')
        verbose_name = 'ShoppingCart'
        verbose_name_plural = 'ShoppingCarts'

    def __str__(self):
        return f'{self.recipe} {self.user}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorite',
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe_favorite',
    )

    class Meta:
        unique_together = ('recipe', 'user')
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'

    def __str__(self):
        return f'{self.recipe} {self.user}'
