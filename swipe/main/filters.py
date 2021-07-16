from django_filters import rest_framework as filters

from _db.models.models import Flat, House, Post


class FlatFilter(filters.FilterSet):
    class Meta:
        model = Flat
        fields = {
            'price': ['gt', 'lt'],
            'price_per_metre': ['gt', 'lt'],
            'square': ['gt', 'lt'],
            'state': ['exact']
        }


class HouseFilter(filters.FilterSet):
    class Meta:
        model = House
        fields = {
            'city': ['exact'],
            'role': ['exact'],
            'distance_to_sea': ['gt', 'lt'],
            'territory': ['exact'],
            'type': ['exact'],
            'car_park': ['exact'],
            'child_playground': ['exact'],
            'security': ['exact']
        }


class PostFilter(filters.FilterSet):
    class Meta:
        model = Post
        fields = {
            'living_type': ['exact'],
            'payment_options': ['exact'],
            'price': ['gt', 'lt', 'exact'],
            'flat__square': ['gt', 'lt'],
            'flat__price_per_metre': ['gt', 'lt'],
            'flat__number_of_rooms': ['exact', 'gt', 'lt'],
            'flat__state': ['exact'],
            'flat__foundation_doc': ['exact'],
            'flat__type': ['exact'],
            'flat__plan': ['exact'],
            'flat__balcony': ['exact'],
            'flat__heating': ['exact'],
            'house__city': ['exact'],
            'house__status': ['exact'],
            'house__territory': ['exact'],
            'house__house_class': ['exact']
        }
