from rest_framework.pagination import PageNumberPagination

class MyCustomPagination(PageNumberPagination):
    page_size = 20
    
class MyCustomPagination2(PageNumberPagination):
    page_size = 200
