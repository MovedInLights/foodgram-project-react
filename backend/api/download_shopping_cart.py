from django.http import HttpResponse


def download_shopping_cart(shopping_ids):

    return HttpResponse(shopping_ids, content_type='text/plain')
