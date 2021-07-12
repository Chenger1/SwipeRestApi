from rest_framework import serializers

from _db.models.models import House


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = '__all__'
