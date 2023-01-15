import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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

    pdfmetrics.registerFont(TTFont('Verdana', 'Verdana.ttf'))
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer)
    p.setFont("Verdana", 10)

    p.drawString(50, 800, "Ingredients list")
    y = 740
    for key in ingredients_for_shopping.keys():
        ingredient_name = Ingredients.objects.get(id=key)
        print(ingredients_for_shopping)
        p.drawString(50, y, f'{str(ingredient_name)} ('
                            f''f'{str(ingredients_for_shopping[key][1])}'
                            f') 'f'— {str(ingredients_for_shopping[key][0])}')

        y = y + 20

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
