from rest_framework.test import APITestCase

from django.urls import reverse
from django.conf import settings
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from main.tests.utils import get_id_token

from _db.models.models import *

import os
import tempfile


class TestPost(APITestCase):
    def setUp(self):
        self._test_user_uid = '8ugeJOTWTMbeFYpKDpx2lHr0qfq1'
        self._test_user_email = 'user@example.com'
        self._test_user_uid_two = 'ifqnanQlUiOSSVBDrHHGbRvwSiw2'
        self._test_user_email_two = 'test@mail.com'
        self._url = reverse('main:user-detail', args=[self._test_user_uid])
        self._token = get_id_token()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {self._token}'
        )
        self.temp_media_image_path = os.path.join(settings.BASE_DIR, 'main/tests/test_media/test_image.png')

    def init_house_structure(self):
        url = reverse('main:houses-list')
        response = self.client.post(url, data={'name': 'House', 'address': 'Street',
                                               'tech': 'MONO1', 'territory': 'OPEN',
                                               'payment_options': 'MORTGAGE', 'role': 'FLAT',
                                               'city': 'Odessa'})
        self.assertEqual(response.status_code, 201)
        house = House.objects.first()

        building = Building.objects.create(name='One', house=house)
        section = Section.objects.create(name='One', building=building)
        floor = Floor.objects.create(name='One', section=section)
        file1 = SimpleUploadedFile('image.jpeg', b'file_content', content_type='image/jpeg')
        file2 = SimpleUploadedFile('image.jpeg', b'file_content', content_type='image/jpeg')
        flat1 = Flat.objects.create(number=1, square=100, kitchen_square=1, price_per_metre=100, price=100,
                                    number_of_rooms=2, state='BLANK', foundation_doc='OWNER', plan='FREE',
                                    balcony='YES', floor=floor, schema=file1)
        flat2 = Flat.objects.create(number=1, square=200, kitchen_square=1, price_per_metre=200, price=200,
                                    number_of_rooms=2, state='EURO', foundation_doc='OWNER', plan='FREE',
                                    balcony='YES', floor=floor, schema=file2)

        return house, building, section, floor, flat1, flat2

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_crud_operations_for_post(self):
        *_, flat = self.init_house_structure()

        url_create = reverse('main:posts-list')
        with open(self.temp_media_image_path, 'rb') as file:
            response_create = self.client.post(url_create, data={'flat': flat.pk,
                                                                 'price': 100000,
                                                                 'payment_options': 'PAYMENT',
                                                                 'main_image': file})
        self.assertEqual(response_create.status_code, 201)
        self.assertEqual(Post.objects.first().flat, flat)

        url_detail = reverse('main:posts-detail', args=[response_create.data['id']])
        response_edit = self.client.patch(url_detail, data={'price': 15000})
        self.assertEqual(response_edit.status_code, 200)
        self.assertEqual(response_edit.data['price'], 15000)
        self.assertEqual(Post.objects.first().price, 15000)

        response_detail = self.client.get(url_detail)
        self.assertEqual(response_detail.status_code, 200)
        self.assertIn('flat_info', response_detail.data.keys())

        response_delete = self.client.delete(url_detail)
        self.assertEqual(response_delete.status_code, 204)
        self.assertEqual(Post.objects.count(), 0)
