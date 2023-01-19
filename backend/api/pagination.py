from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'


class CustomSubscriptionsPagination(pagination.PageNumberPagination):
    page_size_query_param = 'recipes_limit'
