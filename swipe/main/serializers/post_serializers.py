from rest_framework import serializers

from _db.models.models import Post, PostImage, UserFavorites, Complaint

import datetime
import pytz


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('image', 'post')


class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    flat_info = serializers.SerializerMethodField()

    created_display = serializers.DateTimeField(source='created', read_only=True)
    created = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def get_flat_info(self, obj):
        flat = obj.flat
        floor = flat.floor
        section = floor.section
        building = section.building
        house = building.house
        floor = f'Корпус {building.name}, Секция {section.name}, Этаж {floor.name}'
        data = {'square': flat.square, 'kitchen_square': flat.kitchen_square, 'state': flat.get_state_display(),
                'foundation_doc': flat.get_foundation_doc_display(), 'type': flat.get_type_display(),
                'balcony': flat.get_balcony_display(), 'heating': flat.get_heating_display(),
                'floor': floor,
                'plan': flat.get_plan_display(),
                'city': house.city,
                'status': house.get_status_display(),
                'territory': house.get_territory_display(),
                'house_class': house.get_house_class_display()}
        return data

    def update(self, instance, validated_data):
        if validated_data.get('likes'):
            likes = validated_data.pop('likes')
            instance.likes += int(likes)
        if validated_data.get('created'):
            validated_data.pop('created')
            instance.created = datetime.datetime.now(tz=pytz.UTC)
        return super().update(instance, validated_data)


class UserFavoritesWritableSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFavorites
        fields = ('id', 'post', )


class UserFavoritesReadableSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)

    class Meta:
        model = UserFavorites
        fields = ('post', )


class ComplaintSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Complaint
        fields = ('id', 'post', 'type', 'type_display')


class RejectPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'rejected', 'reject_message')
