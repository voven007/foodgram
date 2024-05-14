from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """Пагинатор для вывода определенного количества объектов на страниц"""

    page_size_query_param = 'limit'
    page_size = 6
