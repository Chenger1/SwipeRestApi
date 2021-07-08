from rest_framework import serializers

from _db.models.user import User


class UserSerializer(serializers.ModelSerializer):
    uid = serializers.ReadOnlyField()
    notifications = serializers.CharField(source='get_notifications_display')
    role = serializers.CharField(source='get_role_display')

    class Meta:
        model = User
        fields = ['uid', 'first_name', 'last_name', 'email',
                  'phone_number', 'notifications', 'subscribed', 'end_date', 'role']
