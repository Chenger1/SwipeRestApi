from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model

User = get_user_model()


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        user, created = User.objects.get_or_create(phone_number=request.query_params['phone_number'])
        token = Token.objects.get(user=user)
        content = {
            'user': str(user),
            'auth': str(token)
        }
        return Response(content)
