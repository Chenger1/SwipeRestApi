from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated

from main.serializers import UserSerializer

from rest_framework.viewsets import ModelViewSet


User = get_user_model()


class UserViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return get_object_or_404(User, uid=self.kwargs.get('pk'))
