from django_filters import rest_framework as filters
from backend.models import Book


class DateFilter(filters.FilterSet):
    date = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Book
        fields = ['author', 'genre', 'date']
