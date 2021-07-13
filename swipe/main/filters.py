from django_filters import rest_framework as filters

from _db.models.models import Flat


class FlatFilter(filters.FilterSet):
    class Meta:
        model = Flat
        fields = {
            'price': ['gt', 'lt'],
            'price_per_metre': ['gt', 'lt'],
            'square': ['gt', 'lt'],
            'state': ['exact']
        }
