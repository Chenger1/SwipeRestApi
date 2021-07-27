from rest_framework import serializers

from django.shortcuts import get_object_or_404

from _db.models.models import House, Building, Section, Floor, NewsItem, Standpipe, Document, Flat, RequestToChest


class HouseDetailFlatSerializer(serializers.ModelSerializer):
    floor = serializers.SerializerMethodField()

    class Meta:
        model = Flat
        fields = ('number', 'square', 'floor', 'client', 'booked')

    def get_floor(self, obj):
        return obj.floor.name


class HouseSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    house_class_display = serializers.CharField(source='get_house_class_display', read_only=True)
    tech_display = serializers.CharField(source='get_tech_display', label='tech', read_only=True)
    territory_display = serializers.CharField(source='get_territory_display', read_only=True)
    gas_display = serializers.CharField(source='get_gas_display', read_only=True)
    heating_display = serializers.CharField(source='get_heating_display', read_only=True)
    electricity_display = serializers.CharField(source='get_electricity_display', read_only=True)
    sewerage_display = serializers.CharField(source='get_sewerage_display', read_only=True)
    water_supply_display = serializers.CharField(source='get_water_supply_display', read_only=True)
    communal_payments_display = serializers.CharField(source='get_communal_payments_display', read_only=True)
    completion_display = serializers.CharField(source='get_completion_display', read_only=True)
    payment_options_display = serializers.CharField(source='get_payment_options_display', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    sum_in_contract_display = serializers.CharField(source='get_sum_in_contract_display', read_only=True)

    flats = HouseDetailFlatSerializer(read_only=True, many=True)

    class Meta:
        model = House
        fields = '__all__'
        extra_kwargs = {
            'status': {'write_only': True},
            'type': {'write_only': True},
            'house_class': {'write_only': True},
            'tech': {'write_only': True},
            'territory': {'write_only': True},
            'gas': {'write_only': True},
            'heating': {'write_only': True},
            'electricity': {'write_only': True},
            'sewerage': {'write_only': True},
            'water_supply': {'write_only': True},
            'communal_payments': {'write_only': True},
            'completion': {'write_only': True},
            'payment_options': {'write_only': True},
            'role': {'write_only': True},
            'sum_in_contract': {'write_only': True}
        }


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = '__all__'


class StandpipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

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

    def update(self, instance, validated_data):
        pipes_data = None
        if validated_data.get('pipes'):
            pipes_data = validated_data.pop('pipes')
        instance = super().update(instance, validated_data)
        if pipes_data:
            for pipe_data in pipes_data:
                pipe = get_object_or_404(Standpipe, pk=pipe_data.get('id'))
                pipe.name = pipe_data.get('name')
                pipe.save()
        return instance


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = '__all__'


class NewsItemSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()

    class Meta:
        model = NewsItem
        fields = '__all__'

    def get_created(self, obj):
        return f'{obj.created.year}-{obj.created.month}-{obj.created.day}'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'file', 'house')


class FlatSerializer(serializers.ModelSerializer):
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    foundation_doc_display = serializers.CharField(source='get_foundation_doc_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    plan_display = serializers.CharField(source='get_plan_display', read_only=True)
    balcony_display = serializers.CharField(source='get_balcony_display', read_only=True)

    floor_display = serializers.SerializerMethodField()

    class Meta:
        model = Flat
        fields = '__all__'
        extra_kwargs = {
            'state': {'write_only': True},
            'foundation_doc': {'write_only': True},
            'type': {'write_only': True},
            'plan': {'write_only': True},
            'balcony': {'write_only': True}
        }

    def get_floor_display(self, obj):
        floor = obj.floor
        section = floor.section
        building = section.building
        return f'Корпус {building.name}, Секция {section.name}, Этаж {floor.name}'


class HouseInRequestSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = House
        fields = ('name', 'address', 'role', 'city', 'role_display')


class FlatInRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = ('number', 'floor', 'booked', 'client')


class RequestToChestSerializer(serializers.ModelSerializer):
    house_display = HouseInRequestSerializer(read_only=True)
    flat_display = FlatInRequestSerializer(read_only=True)

    class Meta:
        model = RequestToChest
        fields = '__all__'

    def update(self, instance, validated_data):
        flat = instance.flat
        flat.owned = validated_data['approved']
        flat.booked = validated_data['approved']
        if not validated_data['approved']:
            flat.client = None
        flat.save()
        return super().update(instance, validated_data)
