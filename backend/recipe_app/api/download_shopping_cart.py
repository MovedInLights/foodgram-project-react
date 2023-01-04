from django.http import HttpResponse
from fpdf import FPDF
from recipe.models import Ingredients, RecipeIngredients

ingredients_for_shopping = {}


def download_shopping_cart(shopping_ids):
    for shopping_id in shopping_ids:
        ingredients_obj = RecipeIngredients.objects.filter(
            recipe_id=shopping_id
        )
        for ingredient_obj in ingredients_obj:
            cart_obj_id = ingredient_obj.ingredients_id
            amount = ingredient_obj.amount
            measurement_unit = ingredient_obj.measurement_unit

            if cart_obj_id in ingredients_for_shopping.keys():
                # Add amount for existing key
                ingredients_for_shopping[cart_obj_id][0] += amount

            else:
                # No key in data, add
                ingredients_for_shopping[cart_obj_id] = [amount]
                ingredients_for_shopping[cart_obj_id].append(measurement_unit)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.set_title('Shopping list')
    pdf.text(90, 20, 'Shopping list')
    start_position = 40
    for key in ingredients_for_shopping.keys():
        ingredient_name = Ingredients.objects.get(id=key)
        pdf.text(10, start_position,
                 f'{str(ingredient_name)} ('
                 f'{str(ingredients_for_shopping[key][1])}) '
                 f'— {str(ingredients_for_shopping[key][0])}')

        start_position += 20
    pdf_filename = pdf.output("shopping_cart.pdf")
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(
        pdf_filename
    )
    return response
