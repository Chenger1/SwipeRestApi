import datetime

import pytz
from rest_framework import serializers
from django.utils.translation import gettext as _

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
    building_count = serializers.SerializerMethodField()
    section_count = serializers.SerializerMethodField()
    floor_count = serializers.SerializerMethodField()
    flat_count = serializers.SerializerMethodField()

    class Meta:
        model = House
        fields = '__all__'

    def get_building_count(self, obj):
        return obj.buildings.count()

    def get_section_count(self, obj):
        return Section.objects.filter(building__house=obj).count()

    def get_floor_count(self, obj):
        return Floor.objects.filter(section__building__house=obj).count()

    def get_flat_count(self, obj):
        return Flat.objects.filter(floor__section__building__house=obj).count()


class BuildingSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    has_related = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = '__all__'

    def get_has_related(self, obj):
        return obj.sections.exists()

    def get_full_name(self, obj):
        return f'???????????? ???{obj.number}'

    def create(self, validated_data):
        next_number = Building.get_next(validated_data.get('house'))
        inst = Building.objects.create(number=next_number, house=validated_data.get('house'))
        return inst


class StandpipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Standpipe
        fields = ('id', 'name', )


class SectionSerializer(serializers.ModelSerializer):
    pipes = StandpipeSerializer(many=True, required=False)
    full_name = serializers.SerializerMethodField()
    house = serializers.SerializerMethodField()
    has_related = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ('id', 'number', 'building', 'pipes', 'full_name', 'house', 'has_related')

    def get_has_related(self, obj):
        return obj.floors.exists()

    def get_house(self, obj):
        return obj.building.house.pk

    def get_full_name(self, obj):
        return f'???????????? ???{obj.number}. ???????????? ???{obj.building.number}'

    def create(self, validated_data):
        next_number = Section.get_next(validated_data.get('building'))
        validated_data['number'] = next_number
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
    full_name = serializers.SerializerMethodField()
    house = serializers.SerializerMethodField()
    has_related = serializers.SerializerMethodField()

    class Meta:
        model = Floor
        fields = '__all__'

    def get_has_related(self, obj):
        return obj.flats.exists()

    def get_house(self, obj):
        return obj.section.building.house.pk

    def get_full_name(self, obj):
        building = obj.section.building
        return f'???????? ???{obj.number}. ???????????? ???{obj.section.number}. ???????????? ???{building.number}'

    def create(self, validated_data):
        next_number = Floor.get_next(validated_data.get('building'))
        inst = Floor.objects.create(number=next_number, section=validated_data.get('section'))
        return inst


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
    house_pk = serializers.SerializerMethodField()
    sales_department_pk = serializers.SerializerMethodField()

    class Meta:
        model = Flat
        fields = '__all__'

    def get_sales_department_pk(self, obj):
        return obj.user.pk

    def get_floor_display(self, obj):
        floor = obj.floor
        section = floor.section
        building = section.building
        return f'???????????? {building.number}, ???????????? {section.number}, ???????? {floor.number}'

    def get_house_pk(self, obj):
        return obj.floor.section.building.house.pk


class HouseInRequestSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = House
        fields = ('name', 'address', 'role', 'city', 'role_display')


class FlatInRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = ('pk', 'number', 'floor', 'booked', 'client')


class RequestToChestSerializer(serializers.ModelSerializer):
    flat_display = serializers.SerializerMethodField()

    class Meta:
        model = RequestToChest
        fields = '__all__'

    def create(self, validated_data):
        validated_data['created'] = datetime.datetime.now(tz=pytz.UTC)
        return super().create(validated_data)

    def get_flat_display(self, obj):
        flat = obj.flat
        if flat.client:
            client = obj.flat.client
            return {
                'id': flat.pk,
                'number': flat.number,
                'floor': _('???????????? {building}, ???????????? {section}, ???????? {floor}').format(building=flat.floor.section.building.number,
                                                                                       section=flat.floor.section.number,
                                                                                       floor=flat.floor.number),
                'house': flat.floor.section.building.house.name,
                'house_pk': flat.floor.section.building.house.pk,
                'client_pk': client.pk,
                'client_full_name': client.full_name(),
                'client_phone_number': client.phone_number,
                'client_email': client.email
            }
        return {}

    def update(self, instance, validated_data):
        flat = instance.flat
        flat.owned = validated_data['approved']
        flat.booked = validated_data['approved']
        if not validated_data['approved']:
            flat.client = None
        flat.save()
        return super().update(instance, validated_data)
