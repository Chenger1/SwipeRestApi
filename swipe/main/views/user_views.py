from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from main.serializers import UserSerializer


User = get_user_model()


class UserDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uid, format=None):
        user = get_object_or_404(User, uid=uid)
        serializer = UserSerializer(user)
        return Response(serializer.data)
