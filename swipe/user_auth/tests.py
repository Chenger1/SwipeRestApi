from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework import status

import firebase_admin
from firebase_admin import auth as firebase_auth

from user_auth.authentication import cred_file

from swipe.config import WEB_API_KEY

import requests

User = get_user_model()
firebase_credentials = firebase_admin.credentials.Certificate(cred_file)
firebase_app = firebase_admin.initialize_app(credential=firebase_credentials,
                                             name=__name__)


class LoginTests(APITestCase):
    def setUp(self) -> None:
        self._url = reverse('login_view')
        self._test_user_email = 'user@example.com'
        self._test_uid = '8ugeJOTWTMbeFYpKDpx2lHr0qfq1'
        User.objects.create(email=self._test_user_email,
                            uid=self._test_uid)
        self._id_token_endpoint = (
            'https://identitytoolkit.googleapis.com/v1/accounts'
            ':signInWithCustomToken?key={api_key}'
        )

    def _get_test_user_by_uid(self):
        return firebase_auth.get_user(self._test_uid)

    def _generate_custom_token(self):
        user = self._get_test_user_by_uid()
        return firebase_auth.create_custom_token(user.uid)

    def _generate_id_token(self):
        url = self._id_token_endpoint.format(
            api_key=WEB_API_KEY
        )
        data = {
            'token': self._generate_custom_token(),
            'returnSecureToken': True
        }
        res = requests.post(url, data=data)
        res.raise_for_status()
        return res.json()['idToken']

    def test_authenticated_request(self):
        """ensure we can auth with a valid id token"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {self._generate_id_token()}'
        )
        response = self.client.get(self._url)
        expected_user = self._get_test_user_by_uid()
        self.assertTrue('user' in response.data)
        self.assertEqual(response.data['auth'], expected_user.uid)

    def test_unauthenticated_request(self):
        """ensure we cant auth without id token"""
        response = self.client.get(self._url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_token_request(self):
        """ensure we cant auth with invalid id token"""
        invalid_token = self._generate_custom_token()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {invalid_token}'
        )
        response = self.client.get(self._url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
