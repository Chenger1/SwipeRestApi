from django.urls import reverse

from rest_framework.test import APITestCase

from _db.models.models import House

from main.tests.utils import get_id_token


class TestHouse(APITestCase):
    def setUp(self):
        self._test_user_uid = '8ugeJOTWTMbeFYpKDpx2lHr0qfq1'
        self._test_user_uid_two = 'KzlTbTHMEhbkCD9pzOhNLF9Ypxa2'
        self._url = reverse('main:user-detail', args=[self._test_user_uid])
        self._token = get_id_token()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {self._token}'
        )

    def test_house_full_crud_operations(self):
        url = reverse('main:houses-list')
        response = self.client.post(url, data={'name': 'House', 'address': 'Street',
                                               'tech': 'MONO1', 'territory': 'OPEN',
                                               'payment_options': 'MORTGAGE', 'role': 'FLAT'})
        self.assertEqual(response.status_code, 201)

        url_list = reverse('main:houses-list')
        response_list = self.client.get(url_list)
        self.assertEqual(response_list.status_code, 200)
        self.assertEqual(len(response_list.data), 1)

        url_edit = reverse('main:houses-detail', args=[response.data['id']])
        response_edit = self.client.patch(url_edit, data={'name': 'Edited Name'})
        self.assertEqual(response_edit.status_code, 200)
        self.assertEqual(response_edit.data['name'], 'Edited Name')

        url_delete = reverse('main:houses-detail', args=[response.data['id']])
        response_delete = self.client.delete(url_delete)
        self.assertEqual(response_delete.status_code, 204)

    def test_house_get_list(self):
        """Ensure we can get list of houses non-creator"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {get_id_token(self._test_user_uid_two)}'
        )
        url_list = reverse('main:houses-list')
        response_list = self.client.get(url_list)
        self.assertEqual(response_list.status_code, 200)
