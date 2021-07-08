from django.urls import reverse

from rest_framework.test import APITestCase

from main.tests.utils import get_id_token


class TestUser(APITestCase):
    def setUp(self):
        self._test_user_uid = '8ugeJOTWTMbeFYpKDpx2lHr0qfq1'
        self._url = reverse('main:user-detail', args=[self._test_user_uid])
        self._token = get_id_token()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {self._token}'
        )

    def test_get_user_info(self):
        """ensure we can get user info"""
        response = self.client.get(self._url)
        self.assertEqual(response.data['uid'], self._test_user_uid)

    def test_get_wrong_user(self):
        url = reverse('main:user-detail', args=['12345'])
        response = self.client.get(url)
        self.assertEqual(response.data['detail'], 'Not found.')

    def test_change_user_info(self):
        """ensure we can change user info"""
        response = self.client.patch(self._url, data={'first_name': 'User first name',
                                                      'last_name': 'User last name',
                                                      'uid': self._test_user_uid})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'User first name')

    def test_change_user_info_with_another_user_uid(self):
        """ ensure user can access to only his info """
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {get_id_token("A07YwJEGeKORDzveFn27fn5k8BT2")}'  # test uid
        )
        response = self.client.patch(self._url, data={'first_name': 'User first name',
                                                      'last_name': 'User last name'})
        self.assertEqual(response.status_code, 404)

    def test_uid_is_read_only_field(self):
        """ ensure we cant change uid. Because this is key field with firebase integration """
        response = self.client.patch(self._url, data={'uid': '123'})
        self.assertEqual(response.data['uid'], '8ugeJOTWTMbeFYpKDpx2lHr0qfq1')

    def test_user_list(self):
        url = reverse('main:user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
