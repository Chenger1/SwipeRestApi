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

        response = self.client.post(url, data={'name': 'House', 'address': 'Street',
                                               'tech': 'MONO1', 'territory': 'CLOSE',
                                               'payment_options': 'PAYMENT', 'role': 'FLAT',
                                               'city': 'Kiev'})
        self.assertEqual(response.status_code, 201)
        house2 = House.objects.last()
        house = House.objects.first()

        building = Building.objects.create(name='One', house=house)
        building2 = Building.objects.create(name='Two', house=house2)

        section = Section.objects.create(name='One', building=building)
        section2 = Section.objects.create(name='Two', building=building2)

        floor = Floor.objects.create(name='One', section=section)
        floor2 = Floor.objects.create(name='Twi', section=section2)

        file1 = SimpleUploadedFile('image.jpeg', b'file_content', content_type='image/jpeg')
        file2 = SimpleUploadedFile('image.jpeg', b'file_content', content_type='image/jpeg')
        flat1 = Flat.objects.create(number=1, square=100, kitchen_square=1, price_per_metre=100, price=100,
                                    number_of_rooms=2, state='BLANK', foundation_doc='OWNER', plan='FREE',
                                    balcony='YES', floor=floor, schema=file1)
        flat2 = Flat.objects.create(number=1, square=200, kitchen_square=1, price_per_metre=200, price=200,
                                    number_of_rooms=2, state='EURO', foundation_doc='OWNER', plan='STUDIO',
                                    balcony='YES', floor=floor2, schema=file2)

        return house, house2, building, section, floor, flat1, flat2

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_crud_operations_for_post(self):
        house, *_, flat = self.init_house_structure()

        url_create = reverse('main:posts-list')
        with open(self.temp_media_image_path, 'rb') as file:
            response_create = self.client.post(url_create, data={'flat': flat.pk,
                                                                 'house': house.pk,
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

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_crud_for_post_images(self):
        house, *_, flat = self.init_house_structure()

        url_create = reverse('main:posts-list')
        with open(self.temp_media_image_path, 'rb') as file:
            response_create = self.client.post(url_create, data={'flat': flat.pk,
                                                                 'house': house.pk,
                                                                 'price': 100000,
                                                                 'payment_options': 'PAYMENT',
                                                                 'main_image': file})
        self.assertEqual(response_create.status_code, 201)

        url_create_image = reverse('main:post_images-list')
        with open(self.temp_media_image_path, 'rb') as file:
            response_images = self.client.post(url_create_image, data={'post': response_create.data['id'],
                                                                       'image': file})
        self.assertEqual(response_images.status_code, 201)
        self.assertEqual(PostImage.objects.count(), 1)

        url_edit = reverse('main:post_images-detail', args=[PostImage.objects.first().pk])
        with open(self.temp_media_image_path, 'rb') as file:
            response_edit = self.client.patch(url_edit, data={'image': file})
        self.assertEqual(response_edit.status_code, 200)

        response_delete = self.client.delete(url_edit)
        self.assertEqual(response_delete.status_code, 204)
        self.assertEqual(PostImage.objects.count(), 0)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_filters(self):
        house, house2, *_, flat1, flat2 = self.init_house_structure()

        url_create = reverse('main:posts-list')
        with open(self.temp_media_image_path, 'rb') as file:
            response_create = self.client.post(url_create, data={'flat': flat1.pk,
                                                                 'house': house.pk,
                                                                 'price': 100000,
                                                                 'payment_options': 'PAYMENT',
                                                                 'main_image': file})
        self.assertEqual(response_create.status_code, 201)
        with open(self.temp_media_image_path, 'rb') as file:
            response_create = self.client.post(url_create, data={'flat': flat2.pk,
                                                                 'house': house2.pk,
                                                                 'price': 1000,
                                                                 'payment_options': 'PAYMENT',
                                                                 'main_image': file})
        self.assertEqual(response_create.status_code, 201)

        url = reverse('main:posts_public-list')
        response = self.client.get(url, data={'flat__square__gt': 100})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['flat_info']['square'], 200)

        response2 = self.client.get(url, data={'flat__plan': 'FREE',
                                               'price__gt': 1000})
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data[0]['price'], 100000)
        self.assertEqual(response2.data[0]['flat_info']['plan'], 'Свободная планировка')

        response3 = self.client.get(url, data={'house__city': 'Kiev',
                                               'payment_options': 'PAYMENT'})
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(response3.data[0]['flat_info']['city'], 'Kiev')
