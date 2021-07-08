from django.urls import reverse

from rest_framework.test import APITestCase

from main.tests.utils import get_id_token


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

    def test_change_user_info(self):
        """ensure we can change user info"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {self._token}'
        )
        response = self.client.patch(self._url, data={'first_name': 'User first name',
                                                      'last_name': 'User last name',
                                                      'uid': self._test_user_uid})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'User first name')

    def test_change_user_info_with_wrong_uid(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {self._token}'
        )
        response = self.client.patch(self._url, data={'first_name': 'User first name',
                                                      'last_name': 'User last name',
                                                      'uid': '123'})
        self.assertEqual(response.status_code, 403)
