from rest_framework import serializers

from _db.models.models import Post, PostImage, UserFavorites, Complaint, Promotion, PromotionType

import datetime
import pytz
from dateutil.relativedelta import relativedelta


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

    living_type_display = serializers.CharField(source='get_living_type_display', read_only=True)
    payment_options_display = serializers.CharField(source='get_payment_options_display', read_only=True)
    agent_coms_display = serializers.CharField(source='get_agent_coms_display', read_only=True)
    communications_display = serializers.CharField(source='get_communications_display', read_only=True)
    reject_message_display = serializers.CharField(source='get_reject_message_display', read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'likers': {'read_only': True},
            'dislikers': {'read_only': True},
            'number': {'read_only': True}
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
                'house_class': house.get_house_class_display(),
                'number': flat.number,
                'id': flat.pk}
        return data

    def validate_created(self, value):
        if self.instance:
            time_range = datetime.datetime.now(tz=pytz.UTC) - self.instance.created
            if time_range.days <= 30:
                raise serializers.ValidationError('You can confirm relevance every 31 days')
            return value
        return value

    def create(self, validated_data):
        validated_data['number'] = Post.get_next_number()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('created'):
            validated_data.pop('created')
            instance.created = datetime.datetime.now(tz=pytz.UTC)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if hasattr(instance, 'promotion') and not instance.promotion.paid:
            #  Promotion is displaying only if it is paid
            rep['promotion'] = None
        return rep


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
        fields = ('id', 'post', 'type', 'type_display', 'description')


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
        extra_kwargs = {
            'end_date': {'read_only': True}
        }

    def create(self, validated_data):
        validated_data['price'] = self.calculate_price(validated_data)
        current_date = datetime.date.today()
        validated_data['end_date'] = current_date + relativedelta(month=current_date.month + 1)
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
        current_date = datetime.date.today()
        instance.end_date = current_date + relativedelta(month=current_date.month + 1)
        instance.save()
        if not current_paid_status and instance.paid:
            post = instance.post
            post.weight += instance.type.efficiency
            post.save()
        return instance
