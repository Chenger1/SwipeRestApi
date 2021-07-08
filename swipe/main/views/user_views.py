from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from main.serializers import UserSerializer
from main.permissions import IsProfileOwner


User = get_user_model()


class UserViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsProfileOwner)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return get_object_or_404(User, uid=self.kwargs.get('pk'))
