from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.conf import settings

from rest_framework.test import APITestCase

from main.tests.utils import get_id_token

from _db.models.models import House, NewsItem, Flat, Building, Section, Floor

import tempfile
import os


class TestHouse(APITestCase):
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
                                               'payment_options': 'MORTGAGE', 'role': 'FLAT'})
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
            HTTP_AUTHORIZATION=f'JWT {get_id_token(self._test_user_email_two)}'
        )
        url_list = reverse('main:houses-list')
        response_list = self.client.get(url_list)
        self.assertEqual(response_list.status_code, 200)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_house_building_section_floors_flat(self):
        #  Test creating house
        url = reverse('main:houses-list')
        response = self.client.post(url, data={'name': 'House', 'address': 'Street',
                                               'tech': 'MONO1', 'territory': 'OPEN',
                                               'payment_options': 'MORTGAGE', 'role': 'FLAT'})
        self.assertEqual(response.status_code, 201)

        # Test editing house
        url_edit = reverse('main:houses-detail', args=[response.data['id']])
        response_edit = self.client.patch(url_edit, data={'name': 'Edited House'})
        self.assertEqual(response_edit.status_code, 200)
        self.assertEqual(response_edit.data['name'], 'Edited House')

        # Test creating building
        url_building = reverse('main:buildings-list')
        response_building = self.client.post(url_building, data={'name': 'One',
                                                                 'house': response.data['id']})
        self.assertEqual(response_building.status_code, 201)

        url_building_edit = reverse('main:buildings-detail', args=[response_building.data['id']])
        response_building_edit = self.client.patch(url_building_edit, data={'name': 'Two'})
        self.assertEqual(response_building_edit.status_code, 200)

        # Test create section
        url_section = reverse('main:sections-list')
        #  Test that we can add section and standpipes to it
        response_section = self.client.post(url_section, data={'name': 'One',
                                                               'building': response_building.data['id'],
                                                               'pipes': [
                                                                   {'name': 'PipeOne'},
                                                                   {'name': 'PipeTwo'}
                                                               ]
                                                               }, format='json')

        self.assertEqual(response_section.status_code, 201)

        url_section_edit = reverse('main:sections-detail', args=[response_section.data['id']])
        response_section_edit = self.client.patch(url_section_edit, data={'name': 'Two'})
        self.assertEqual(response_section_edit.status_code, 200)

        # Test creating floors
        url_floor = reverse('main:floors-list')
        response_floor = self.client.post(url_floor, data={'name': 'One',
                                                           'section': response_section.data['id']})
        self.assertEqual(response_floor.status_code, 201)

        url_floor_edit = reverse('main:floors-detail', args=[response_floor.data['id']])
        response_floor_edit = self.client.patch(url_floor_edit, data={'name': 'Two'})
        self.assertEqual(response_floor_edit.status_code, 200)

        # Test creating flats
        url_flat = reverse('main:flats-list')
        with open(self.temp_media_image_path, 'rb') as file:
            response_flat = self.client.post(url_flat, data={'number': 1, 'square': 1,
                                                             'kitchen_square': 1, 'price_per_metre': 1,
                                                             'price': 1, 'number_of_rooms': 2, 'state': 'BLANK',
                                                             'foundation_doc': 'OWNER', 'plan': 'FREE',
                                                             'balcony': 'YES', 'floor': response_floor.data['id'],
                                                             'schema': file})
        self.assertEqual(response_flat.status_code, 201)
        self.assertTrue(Flat.objects.exists())

        url_flat_edit = reverse('main:flats-detail', args=[response_flat.data['id']])
        response_flat_edit = self.client.patch(url_flat_edit, data={'number': 2})
        self.assertEqual(response_flat_edit.status_code, 200)
        self.assertEqual(response_flat_edit.data['number'], 2)
        self.assertEqual(Flat.objects.first().number, 2)

        url_flat_delete = reverse('main:flats-detail', args=[response_flat.data['id']])
        response_flat_delete = self.client.delete(url_flat_delete)
        self.assertEqual(response_flat_delete.status_code, 204)

    def test_news_item(self):
        url = reverse('main:houses-list')
        response = self.client.post(url, data={'name': 'House', 'address': 'Street',
                                               'tech': 'MONO1', 'territory': 'OPEN',
                                               'payment_options': 'MORTGAGE', 'role': 'FLAT'})
        self.assertEqual(response.status_code, 201)

        url_news = reverse('main:news-list')
        response_news = self.client.post(url_news, data={'title': 'News Title', 'text': 'Text',
                                                         'house': response.data['id']})
        self.assertEqual(response.status_code, 201)
        self.assertIn(NewsItem.objects.get(pk=response_news.data['id']),
                      House.objects.get(id=response.data['id']).news.all())

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_documents_in_house(self):
        url = reverse('main:houses-list')
        file = SimpleUploadedFile('doc.docx', b'file_content', content_type='application/msword')
        response = self.client.post(url, data={'name': 'House', 'address': 'Street',
                                               'tech': 'MONO1', 'territory': 'OPEN',
                                               'payment_options': 'MORTGAGE', 'role': 'FLAT'})
        self.assertEqual(response.status_code, 201)

        url_doc = reverse('main:documents-list')
        response_doc = self.client.post(url_doc, data={'name': 'documment',
                                                       'file': file,
                                                       'house': response.data['id']})
        self.assertEqual(response_doc.status_code, 201)
        self.assertTrue(House.objects.first().documents.exists())

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_flat_filters(self):
        _ = self.init_house_structure()

        url_filter_price = reverse('main:flats-list')
        response = self.client.get(url_filter_price, data={'price__gt': 101})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['price'], 200)

        url_filter_square = reverse('main:flats-list')
        response_square = self.client.get(url_filter_square, data={'square__lt': 200})
        self.assertEqual(response_square.status_code, 200)
        self.assertEqual(response_square.data[0]['square'], 100)

        url_filter_state = reverse('main:flats-list')
        response_state = self.client.get(url_filter_state, data={'state': 'BLANK'})
        self.assertEqual(response_state.status_code, 200)
        self.assertEqual(response_state.data[0]['state'], 'BLANK')

        url_filter_both = reverse('main:flats-list')
        response_both = self.client.get(url_filter_both, data={'price__lt': 201,
                                                               'price__gt': 99})
        self.assertEqual(response_both.status_code, 200)
        self.assertEqual(len(response_both.data), 2)

    def test_booking_flat(self):
        """ Ensure we can change flat booked status """
        *_, flat = self.init_house_structure()

        url = reverse('main:booking_flat', args=[flat.pk])
        response = self.client.patch(url, data={'booking': '1'})
        self.assertEqual(response.status_code, 200)
        updated_flat = Flat.objects.get(pk=flat.pk)
        self.assertEqual(updated_flat.client.email, self._test_user_email)

        # Ensure we can change booking status from another person (If this person is not a house owner)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {get_id_token(self._test_user_email_two)}'
        )
        response_errors = self.client.patch(url, data={'booking': '0'})
        self.assertEqual(response_errors.status_code, 400)
        self.assertEqual(response_errors.data.get('Error'), 'You cannot remove current client from this flat')
        updated_flat = Flat.objects.get(pk=flat.pk)
        self.assertNotEqual(updated_flat.client, None)

        # Ensure we can set flat client as None if we either house owner or current client
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {self._token}'
        )
        response_success = self.client.patch(url, data={'booking': '0'})
        self.assertEqual(response_success.status_code, 200)
        updated_flat = Flat.objects.get(pk=flat.pk)
        self.assertEqual(updated_flat.client, None)

    def test_all_houses(self):
        """Ensure we can get all house"""
        self.init_house_structure()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {get_id_token(self._test_user_email_two)}'
        )

        url = reverse('main:all_houses_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response_404 = self.client.post(url)
        self.assertEqual(response_404.status_code, 405)
