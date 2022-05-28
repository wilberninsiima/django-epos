import django_filters
from .models import *

class SalesFilter(django_filters.FilterSet):
    class Meta:
        model=Sale
        fields='__all__'