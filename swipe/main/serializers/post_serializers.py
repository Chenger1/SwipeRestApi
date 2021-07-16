from rest_framework import serializers

from _db.models.models import Post, PostImage


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('image', 'post')


class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    flat_info = serializers.SerializerMethodField()

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
        floor = f'Корпус {building.name}, Секция {section.name}, Этаж {floor.name}'
        data = {'square': flat.square, 'kitchen_square': flat.kitchen_square, 'state': flat.get_state_display(),
                'foundation_doc': flat.get_foundation_doc_display(), 'type': flat.get_type_display(),
                'balcony': flat.get_balcony_display(), 'heating': flat.get_heating_display(),
                'floor': floor}
        return data
