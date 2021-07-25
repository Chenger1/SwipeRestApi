from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

User = get_user_model()


class LoginTests(APITestCase):
    def setUp(self) -> None:
        self._url = reverse('login_view')
        self._test_user_email = 'user@example.com'
        User.objects.create(email=self._test_user_email,
                            phone_number='3423423234')

    def _get_test_user_by_email(self):
        return User.objects.get(email=self._test_user_email)

    def test_authenticated_request(self):
        """ensure we can auth with a valid id token"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {Token.objects.get(user__email=self._test_user_email)}'
        )
        response = self.client.get(self._url, data={'phone_number': '3423423234'})
        self.assertTrue('user' in response.data)
        self.assertIn('auth', response.data.keys())

    def test_user_registration(self):
        response = self.client.get(self._url, data={'phone_number': '+380638271139'})
        self.assertIn('user', response.data.keys())
