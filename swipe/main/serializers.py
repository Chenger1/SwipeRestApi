from rest_framework import serializers

from _db.models.user import User, Contact, Message, Attachment


class UserSerializer(serializers.ModelSerializer):
    uid = serializers.ReadOnlyField()
    notifications = serializers.CharField(source='get_notifications_display')  # to display beauty name instead of const
    role = serializers.CharField(source='get_role_display')  # to display beauty name instead of const

    class Meta:
        model = User
        fields = ['uid', 'first_name', 'last_name', 'email',
                  'phone_number', 'notifications', 'subscribed', 'end_date', 'role', 'photo', 'is_staff',
                  'is_superuser']

    def update(self, instance, validated_data):
        if validated_data.get('get_notifications_display'):
            instance.notifications = validated_data.get('get_notifications_display')
        return super().update(instance, validated_data)


class UserContactSerializer(serializers.ModelSerializer):
    uid = serializers.ReadOnlyField()
    role = serializers.CharField(source='get_role_display')

    class Meta:
        model = User
        fields = ['uid', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'photo']


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
