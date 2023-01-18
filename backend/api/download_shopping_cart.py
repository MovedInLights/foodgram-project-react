from django.http import HttpResponse

from recipe.models import Ingredients, RecipeIngredients


def download_shopping_cart(shopping_ids):
    ingredients_for_shopping = {}

    for shopping_id in shopping_ids:
        ingredients_obj = RecipeIngredients.objects.filter(
            recipe_id=shopping_id
        )
        print(ingredients_obj)
        for ingredient_obj in ingredients_obj:
            cart_obj_id = ingredient_obj.related_ingredient_id
            quantity = ingredient_obj.quantity
            measurement_unit = ingredient_obj.measurement_unit

            if cart_obj_id in ingredients_for_shopping.keys():
                # Add amount for existing key
                ingredients_for_shopping[cart_obj_id][0] += quantity

            else:
                # No key in data, add
                ingredients_for_shopping[cart_obj_id] = [quantity]
                ingredients_for_shopping[cart_obj_id].append(measurement_unit)
    content = 'Ingredients for shopping :)\n'
    for key in ingredients_for_shopping.keys():
        ingredient_name = Ingredients.objects.get(id=key)
        print(ingredients_for_shopping)
        content += f'{str(ingredient_name)} {str(ingredients_for_shopping[key][1])} {str(ingredients_for_shopping[key][0])}\n  '

    return HttpResponse(content, content_type='text/plain')
