from rest_framework.pagination import PageNumberPagination


class TweetPagination(PageNumberPagination):
    """Custom pagination for tweet list API"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
