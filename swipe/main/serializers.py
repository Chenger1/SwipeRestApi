from rest_framework import serializers

from _db.models.user import User, Contact


class UserSerializer(serializers.ModelSerializer):
    uid = serializers.ReadOnlyField()
    notifications = serializers.CharField(source='get_notifications_display')  # to display beauty name instead of const
    role = serializers.CharField(source='get_role_display')  # to display beauty name instead of const

    class Meta:
        model = User
        fields = ['uid', 'first_name', 'last_name', 'email',
                  'phone_number', 'notifications', 'subscribed', 'end_date', 'role']


class UserContactSerializer(serializers.ModelSerializer):
    uid = serializers.ReadOnlyField()
    role = serializers.CharField(source='get_role_display')

    class Meta:
        model = User
        fields = ['uid', 'first_name', 'last_name', 'email', 'phone_number', 'role']


class ContactSerializer(serializers.ModelSerializer):
    contact = UserContactSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = ['pk', 'contact']
