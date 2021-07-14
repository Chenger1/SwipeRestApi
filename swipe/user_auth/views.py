from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from user_auth.authentication import FirebaseAuthentication


class LoginView(APIView):
    authentication_classes = [SessionAuthentication, FirebaseAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        content = {
            'user': str(request.user),
            'auth': str(request.auth)
        }
        return Response(content)
