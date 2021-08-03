from rest_framework import serializers

from _db.models.user import User, Contact, Message, Attachment, UserFilter
from _db.models import choices


class UserSerializer(serializers.ModelSerializer):
    notifications_display = serializers.CharField(source='get_notifications_display', read_only=True)  # to display beauty name instead of const
    role_display = serializers.CharField(source='get_role_display', read_only=True)  # to display beauty name instead of const

    class Meta:
        model = User
        fields = ['pk', 'first_name', 'last_name', 'email',
                  'phone_number', 'notifications', 'subscribed', 'end_date', 'role', 'photo', 'is_staff',
                  'is_superuser', 'notifications_display', 'role_display']
        read_only = ('email', )
        write_only = ('notifications', 'role')

    def update(self, instance, validated_data):
        if validated_data.get('get_notifications_display'):
            instance.notifications = validated_data.get('get_notifications_display')
        return super().update(instance, validated_data)

    def validated_role(self, value):
        """ SYSTEM user is a user for sending notifications """
        if value == 'SYSTEM':
            raise serializers.ValidationError('In system in be only one user with role "SYSTEM"')
        return value


class UserContactSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['pk', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'photo', 'role_display']
        write_only = ('role', )


class ContactSerializer(serializers.ModelSerializer):
    contact = UserContactSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = ['pk', 'contact']


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('pk', 'message', 'file')


class WritableMessageSerializer(serializers.ModelSerializer):
    """
    This serializer for writing purposes.
    'sender' and 'receiver' look like integer - 'pk'
    """
    class Meta:
        model = Message
        fields = ('pk', 'sender', 'receiver', 'text', 'created')


class ReadableMessageSerializer(serializers.ModelSerializer):
    """
    This serializer only to for reading purposes.
    'sender' and 'receiver' look like nested dictionary.
    """

    sender = UserContactSerializer(read_only=True)
    receiver = UserContactSerializer(read_only=True)
    attach = AttachmentSerializer(read_only=True, many=True)

    class Meta:
        model = Message
        fields = ('pk', 'sender', 'receiver', 'text', 'created', 'attach')


class UserFilterSerializer(serializers.Serializer):
    living_type = serializers.ChoiceField(choices=choices.type_choices, required=False)
    payment_options = serializers.ChoiceField(choices=choices.payment_options_choices, required=False)
    price__gte = serializers.IntegerField(required=False)
    price__lte = serializers.IntegerField(required=False)
    flat__square__gte = serializers.IntegerField(required=False)
    flat__square__lte = serializers.IntegerField(required=False)
    flat__state = serializers.ChoiceField(choices=choices.state_choices, required=False)
    house__status = serializers.ChoiceField(choices=choices.status_choices, required=False)
    house__city = serializers.CharField(required=False)
    house__address = serializers.CharField(required=False)

    def create(self, validated_data):
        user_filter = UserFilter.objects.create(market=validated_data.get('living_type'),
                                                payment_cond=validated_data.get('payment_options'),
                                                min_price=validated_data.get('price__gte'),
                                                max_price=validated_data.get('price__lte'),
                                                min_square=validated_data.get('flat__square__gte'),
                                                max_square=validated_data.get('flat__square__lte'),
                                                status=validated_data.get('house__status'),
                                                city=validated_data.get('house__city'),
                                                address=validated_data.get('house__address'),
                                                number_of_rooms=validated_data.get('flat__number_of_rooms'),
                                                state=validated_data.get('flat__state'),
                                                user=validated_data.get('user'))
        return user_filter

    def update(self, instance, validated_data):
        instance.market = validated_data.get('living_type', instance.market)
        instance.payment_cond = validated_data.get('payment_options', instance.payment_cond)
        instance.min_price = validated_data.get('price__gte', instance.min_price)
        instance.max_price = validated_data.get('price__lte', instance.max_price)
        instance.min_square = validated_data.get('flat__square__gte', instance.min_square)
        instance.max_square = validated_data.get('flat__square__lte', instance.max_square)
        instance.status = validated_data.get('house__status', instance.status)
        instance.city = validated_data.get('house__city', instance.city)
        instance.address = validated_data.get('house__address', instance.address)
        instance.number_of_rooms = validated_data.get('flat__number_of_rooms', instance.number_of_rooms)
        instance.state = validated_data.get('flat__state', instance.state)
        return instance

    def to_representation(self, instance):
        """
        We need to check if instance attribute empty or not. Because query params cant handle 'None' value
        Also, Django`s filter lookups can take 'None' or empty string as a valid filter value.
        So, we have to return dictionary only with valid values
        :param instance:
        :return: dict
        """
        data = {'saved_filter_pk': instance.pk}
        if instance.market:
            data['living_type'] = instance.market
        if instance.payment_cond:
            data['payment_options'] = instance.payment_cond
        if instance.min_price:
            data['price__gte'] = instance.min_price
        if instance.max_price:
            data['price__lte'] = instance.max_price
        if instance.min_square:
            data['flat__square__gte'] = instance.min_square
        if instance.max_square:
            data['flat__square__lte'] = instance.max_square
        if instance.status:
            data['house__status'] = instance.status
        if instance.city:
            data['house__city'] = instance.city
        if instance.address:
            data['house__address'] = instance.address
        if instance.number_of_rooms:
            data['flatt__number_of_rooms'] = instance.number_of_rooms
        if instance.state:
            data['flat__state'] = instance.state

        return data
