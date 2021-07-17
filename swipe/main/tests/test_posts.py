from rest_framework.test import APITestCase

from django.urls import reverse
from django.conf import settings
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from main.tests.utils import get_id_token

from _db.models.models import *

import os
import tempfile
import datetime


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

    def init_post(self, house, flat):
        user = User.objects.get(uid=self._test_user_uid)
        file = SimpleUploadedFile('image.jpeg', b'file_content', content_type='image/jpeg')
        post = Post.objects.create(flat=flat, house=house, price=10000, payment_options='PAYMENT',
                                   main_image=file, user=user)
        return post

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
        post = self.init_post(house, flat)

        url_create_image = reverse('main:post_images-list')
        with open(self.temp_media_image_path, 'rb') as file:
            response_images = self.client.post(url_create_image, data={'post': post.pk,
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

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_favorites(self):
        """Ensure we can make CRUD operations with user`s favorites list"""
        house, *_, flat = self.init_house_structure()
        post = self.init_post(house, flat)

        url_add = reverse('main:favorites_posts-list')
        response_add = self.client.post(url_add, data={'post': post.pk})
        self.assertEqual(response_add.status_code, 201)
        self.assertEqual(UserFavorites.objects.count(), 1)

        url_list = reverse('main:favorites_posts-list')
        response_list = self.client.get(url_list)
        self.assertEqual(response_list.status_code, 200)
        self.assertIn('post', response_list.data[0].keys())

        url_retrieve = reverse('main:favorites_posts-detail', args=[response_add.data['id']])
        response_retrieve = self.client.get(url_retrieve)
        self.assertEqual(response_retrieve.status_code, 200)
        self.assertEqual(response_retrieve.data['post']['id'], 1)

        response_delete = self.client.delete(url_retrieve)
        self.assertEqual(response_delete.status_code, 204)
        self.assertEqual(UserFavorites.objects.count(), 0)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_increment_views_and_likes(self):
        """Ensure views counter is incremented for post"""
        house, *_, flat = self.init_house_structure()
        post = self.init_post(house, flat)

        url_get = reverse('main:posts_public-detail', args=[post.pk])
        self.client.get(url_get)
        self.client.get(url_get)
        self.client.get(url_get)
        self.assertEqual(Post.objects.first().views, 3)

        # Ensure we can like and dislike post
        url_like = reverse('main:posts-detail', args=[post.pk])
        response_increment_like = self.client.patch(url_like, data={'likes': 1})
        self.assertEqual(response_increment_like.status_code, 200)
        self.assertEqual(Post.objects.first().likes, 1)

        response_decrement_like = self.client.patch(url_like, data={'likes': -1})
        self.assertEqual(response_decrement_like.status_code, 200)
        self.assertEqual(Post.objects.first().likes, 0)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_confirm_relevance(self):
        """Ensure we can update post 'created' field """
        house, *_, flat = self.init_house_structure()
        post = self.init_post(house, flat)

        post = Post.objects.first()
        post.created = datetime.date(year=2021, month=6, day=10)
        post.save()
        self.assertEqual(Post.objects.first().created.month, 6)

        url = reverse('main:posts-detail', args=[post.pk])
        response = self.client.patch(url, data={'created': True})
        self.assertEqual(response.status_code, 200)
        post = Post.objects.first()
        self.assertEqual(post.created.month, 7)
        self.assertEqual(post.created.day, 17)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_complaints(self):
        house, *_, flat = self.init_house_structure()
        post = self.init_post(house, flat)

        url_add = reverse('main:complaints-list')
        response_create = self.client.post(url_add, data={'post': post.pk,
                                                          'type': 'PRICE'})
        self.assertEqual(response_create.status_code, 201)
        self.assertEqual(Complaint.objects.count(), 1)

        response_list = self.client.get(url_add)
        self.assertEqual(response_list.status_code, 200)
        self.assertGreater(len(response_list.data), 0)

        url_detail = reverse('main:complaints-detail', args=[response_create.data['id']])
        response_detail = self.client.get(url_detail)
        self.assertEqual(response_detail.status_code, 200)
        self.assertEqual(response_detail.data['post'], 1)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_complaints_by_admin(self):
        """Ensure admin can get complaints"""
        house, *_, flat = self.init_house_structure()
        post = self.init_post(house, flat)

        user = User.objects.get(uid=self._test_user_uid)
        user.is_staff = True
        user.save()  # Ensure test user has required permissions

        url_add = reverse('main:complaints-list')
        self.client.post(url_add, data={'post': post.pk,
                                        'type': 'PRICE'})
        self.client.post(url_add, data={'post': post.pk,
                                        'type': 'DESC'})
        self.assertEqual(Complaint.objects.count(), 2)

        url_list = reverse('main:complaints_admin-list')
        response_list = self.client.get(url_list)
        self.assertEqual(response_list.status_code, 200)
        self.assertGreater(len(response_list.data), 0)
        self.assertEqual(response_list.data[0]['post'], 1)

        url_detail = reverse('main:complaints_admin-detail', args=[Complaint.objects.first().pk])
        response_detail = self.client.get(url_detail)
        self.assertEqual(response_detail.status_code, 200)
        self.assertEqual(response_detail.data['type'], 'PRICE')

        response_filter_by_post = self.client.get(url_list, data={'post': 1})
        self.assertEqual(response_filter_by_post.status_code, 200)
        self.assertGreater(len(response_filter_by_post.data), 0)
        self.assertEqual(response_filter_by_post.data[0]['post'], 1)

        response_delete = self.client.delete(url_detail)
        self.assertEqual(response_delete.status_code, 204)
        self.assertEqual(Complaint.objects.count(), 1)


        # Ensure non admin cant get access to this view
        user.is_staff = False
        user.save()

        url_error = reverse('main:complaints_admin-list')
        response_error = self.client.get(url_error)
        self.assertEqual(response_error.status_code, 403)
