from django.urls import reverse

from rest_framework.test import APITestCase

from _db.models.user import User

from main.tests.utils import get_id_token

from requests.auth import HTTPBasicAuth


class TestUser(APITestCase):
    def setUp(self):
        self._test_user_uid = '8ugeJOTWTMbeFYpKDpx2lHr0qfq1'
        self._url = reverse('main:user_detail', args=[self._test_user_uid])
        self._token = get_id_token()

    def test_get_user_info(self):
        """ensure we can get user info"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {self._token}'
        )
        response = self.client.get(self._url)
        self.assertEqual(response.data['uid'], self._test_user_uid)

    def test_get_wrong_user(self):
        url = reverse('main:user_detail', args=['12345'])
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {self._token}'
        )
        response = self.client.get(url)
        self.assertEqual(response.data['detail'], 'Not found.')
