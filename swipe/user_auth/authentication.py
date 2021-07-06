from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.authentication import BaseAuthentication

import firebase_admin
from firebase_admin import auth

from user_auth.exceptions import NoAuthToken, InvalidAuthToken, FirebaseError

cred_file = f'{settings.BASE_DIR}\\credentials.json'

cred = firebase_admin.credentials.Certificate(cred_file)

firebase_app = firebase_admin.initialize_app(cred)


User = get_user_model()


class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            raise NoAuthToken('No auth token provided')

        id_token = auth_header.split(" ").pop()
        decoded_token = None
        try:
            decoded_token = auth.verify_id_token(id_token)
        except Exception:
            raise InvalidAuthToken('Invalid auth token')

        if not id_token or not decoded_token:
            return None

        try:
            uid = decoded_token.get('uid')
        except Exception:
            raise FirebaseError()

        try:
            user = User.objects.get(uid=uid)
            return (user, user.uid)
        except ObjectDoesNotExist:
            raise FirebaseError()
