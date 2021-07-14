from rest_framework import serializers

from _db.models.models import House, Building, Section, Floor, NewsItem, Standpipe, Document, Flat


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = '__all__'


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = '__all__'


class StandpipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standpipe
        fields = ('id', 'name', )


class SectionSerializer(serializers.ModelSerializer):
    pipes = StandpipeSerializer(many=True, required=False)

    class Meta:
        model = Section
        fields = ('id', 'name', 'building', 'pipes')

    def create(self, validated_data):
        if validated_data.get('pipes'):
            pipes_data = validated_data.pop('pipes')
            section = Section.objects.create(**validated_data)
            for pipe_data in pipes_data:
                Standpipe.objects.create(section=section, **pipe_data)
        else:
            section = Section.objects.create(**validated_data)
        return section


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = '__all__'


class NewsItemSerializer(serializers.ModelSerializer):
    created = serializers.ReadOnlyField()

    class Meta:
        model = NewsItem
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'file', 'house')


class FlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = '__all__'
