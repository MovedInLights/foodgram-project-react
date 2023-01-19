from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredients(models.Model):
    name = models.CharField(
        null=True, blank=True, max_length=200, verbose_name='Ingredient_name'
    )
    measurement_unit = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'


class Tags(models.Model):
    name = models.CharField(max_length=200, verbose_name='Tag_name')
    color = ColorField(default='#FF0000', verbose_name='Tag_color')
    slug = models.SlugField(unique=True, verbose_name='Tag_slug')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Recipes(models.Model):
    name = models.CharField(max_length=200, verbose_name='Recipe_name')
    image = models.ImageField(
        upload_to='recipes/images',
        blank=True,
        default=None,
        verbose_name='Ingredient_image',
    )
    text = models.CharField(max_length=500, verbose_name='Recipe_description')
    ingredients = models.ManyToManyField(
        Ingredients, through='RecipeIngredients',
        verbose_name='Related_ingredients'
    )
    tags = models.ManyToManyField(Tags, verbose_name='Recipe_tags')
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='How_long_to_cook')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Name_of_the_chief')
    is_favorited = models.BooleanField(
        default=False,
        verbose_name='Is_in_favorite'
    )
    is_in_shopping_cart = models.BooleanField(
        default=False,
        verbose_name='Is_in_shopping_cart'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication_date'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['-pub_date']


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe_with_ing',

    )
    related_ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredients_for_recipe',
    )

    quantity = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Amount_for_particular_recipe')
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        unique_together = ('recipe', 'related_ingredient')
        verbose_name = 'RecipeIngredient'
        verbose_name_plural = 'RecipeIngredients'

    def __str__(self):
        return f'Recipe {self.recipe}, Ingredient {self.related_ingredient}'


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
