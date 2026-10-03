from rest_framework.pagination import PageNumberPagination


class HunderResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page'


class FiftyResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page'