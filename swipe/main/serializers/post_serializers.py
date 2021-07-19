from rest_framework import serializers

from _db.models.models import Post, PostImage, UserFavorites, Complaint, Promotion, PromotionType

import datetime
import pytz


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('image', 'post')


class PromotionReadableSerializer(serializers.ModelSerializer):
    phrase = serializers.CharField(source='get_phrase_display')

    class Meta:
        model = Promotion
        fields = ('phrase', 'color')


class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    flat_info = serializers.SerializerMethodField()
    promotion = PromotionReadableSerializer(read_only=True)

    created_display = serializers.DateTimeField(source='created', read_only=True)
    created = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'likers': {'read_only': True},
            'dislikers': {'read_only': True}
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


class PromotionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionType
        fields = '__all__'


class PromotionSerializer(serializers.ModelSerializer):
    type_display = PromotionTypeSerializer(read_only=True)
    phrase_display = serializers.CharField(source='get_phrase_display', read_only=True)
    color_display = serializers.CharField(source='get_color_display', read_only=True)

    paid = serializers.BooleanField(default=True)

    class Meta:
        model = Promotion
        exclude = ('price', )

    def create(self, validated_data):
        validated_data['price'] = self.calculate_price(validated_data)
        instance = Promotion.objects.create(**validated_data)
        if validated_data.get('paid'):  # if promotion is not paid - it has no effect on post
            post = instance.post
            post.weight += instance.type.efficiency
            post.save()
        return instance

    def calculate_price(self, validated_data) -> int:
        """
        :param validated_data:
        :return: total price: int
        """
        prices = {
            'phrase': 200,
            'color': 200,
        }
        promotion_type = validated_data.get('type')
        total_price = (prices['phrase'] if validated_data.get('phrase') else 0) + \
                      (prices['color'] if validated_data.get('color') else 0) + promotion_type.price
        return total_price


class PromotionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ('paid',)

    def update(self, instance, validated_data):
        current_paid_status = instance.paid
        instance.paid = validated_data.get('paid')
        instance.save()
        if not current_paid_status and instance.paid:
            post = instance.post
            post.weight += instance.type.efficiency
            post.save()
        return instance
