from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from django.urls import reverse
from django.conf import settings
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from main.tasks import check_promotion, check_and_send_notification_about_promotion_time_almost_ending

from _db.models.models import *
from _db.models.user import UserFilter, Message

import os
import tempfile
import datetime
import pytz
from dateutil.relativedelta import relativedelta


class TestPost(APITestCase):
    def setUp(self):
        self._test_user_email = 'user@example.com'
        self._test_user_email_two = 'test@mail.com'
        self._user1 = User.objects.create(email='user@example.com', phone_number='+380638271139')
        self._user2 = User.objects.create(email='test@mail.com', phone_number='+380638271140')
        self._token = Token.objects.get(user__email=self._test_user_email)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self._token}'
        )
        self.temp_media_image_path = os.path.join(settings.BASE_DIR, 'main/tests/test_media/test_image.png')
        self._url = reverse('main:users-detail', args=[self._user1.pk])

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
    def init_post(self, house, flat):
        user = User.objects.get(email=self._test_user_email)
        file = SimpleUploadedFile('image.jpeg', b'file_content', content_type='image/jpeg')
        post = Post.objects.create(flat=flat, house=house, price=10000, payment_options='PAYMENT',
                                   main_image=file, user=user, number=1)
        post2 = Post.objects.create(flat=flat, house=house, price=1000, payment_options='MORTGAGE',
                                    main_image=file, user=user, number=2)
        post3 = Post.objects.create(flat=flat, house=house, price=5000, payment_options='MORTGAGE',
                                    main_image=file, user=user, number=3)
        return post, post2, post3

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
        post = Post.objects.first()
        self.assertEqual(post.flat, flat)
        self.assertEqual(post.number, 1)

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
        post, *_ = self.init_post(house, flat)

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
        response = self.client.get(url, data={'flat__square__gte': 101})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['flat_info']['square'], 200)

        response2 = self.client.get(url, data={'flat__plan': 'FREE',
                                               'price__gte': 1000})
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
        post, *_ = self.init_post(house, flat)

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
        post, *_ = self.init_post(house, flat)
        user = User.objects.get(email=self._test_user_email)

        url_get = reverse('main:posts_public-detail', args=[post.pk])
        self.client.get(url_get)
        self.client.get(url_get)
        self.client.get(url_get)
        self.assertEqual(Post.objects.first().views, 3)

        # Ensure we can like and dislike post
        url_like = reverse('main:like_dislike', args=[post.pk])
        response_increment_like = self.client.patch(url_like, data={'action': 'like'})
        self.assertEqual(response_increment_like.status_code, 200)
        self.assertEqual(Post.objects.first().likes, 1)
        self.assertIn(user, Post.objects.first().likers.all())

        response_decrement_like = self.client.patch(url_like, data={'action': 'dislike'})
        self.assertEqual(response_decrement_like.status_code, 200)
        self.assertEqual(Post.objects.first().likes, -1)
        self.assertIn(user, Post.objects.first().dislikers.all())
        self.assertNotIn(user, Post.objects.first().likers.all())

        # Remove dislike if user 'tap' buttons twice
        response_remove_dislike = self.client.patch(url_like, data={'action': 'dislike'})
        self.assertEqual(response_remove_dislike.status_code, 200)
        self.assertEqual(Post.objects.first().likes, 0)
        self.assertNotIn(user, Post.objects.first().dislikers.all())

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_confirm_relevance_with_old_date(self):
        """Ensure we can update post 'created' field if old 'created' date is more than 31 days old"""
        house, *_, flat = self.init_house_structure()
        post, *_ = self.init_post(house, flat)

        post = Post.objects.first()
        post.created = datetime.datetime(2021, 6, 10, tzinfo=pytz.UTC)
        post.save()
        self.assertEqual(Post.objects.first().created.month, 6)

        url = reverse('main:posts-detail', args=[post.pk])
        response = self.client.patch(url, data={'created': True})
        self.assertEqual(response.status_code, 200)
        post = Post.objects.first()
        self.assertEqual(post.created.month, datetime.date.today().month)
        self.assertEqual(post.created.day, datetime.date.today().day)

    def test_post_confirm_relevance_with_new_date(self):
        """ Ensure we cant update post if it`s 'created' date is not 30 days old"""
        house, *_, flat = self.init_house_structure()
        post, *_ = self.init_post(house, flat)

        url = reverse('main:posts-detail', args=[post.pk])
        response = self.client.patch(url, data={'created': True})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['created'][0], 'You can confirm relevance every 31 days')

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_complaints(self):
        house, *_, flat = self.init_house_structure()
        post, *_ = self.init_post(house, flat)

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
        post, post1, *_ = self.init_post(house, flat)

        user = User.objects.get(email=self._test_user_email)
        user.is_staff = True
        user.save()  # Ensure test user has required permissions

        url_add = reverse('main:complaints-list')
        self.client.post(url_add, data={'post': post.pk,
                                        'type': 'PRICE'})
        self.client.post(url_add, data={'post': post1.pk,
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

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_moderation_by_admin(self):
        """Ensure admin can moderate posts"""
        house, *_, flat = self.init_house_structure()
        post, *_ = self.init_post(house, flat)

        user = User.objects.get(email=self._test_user_email)
        user.is_staff = True
        user.save()  # Ensure test user has required permissions

        url_list = reverse('main:posts_moderation-list')
        response_list_empty = self.client.get(url_list)
        self.assertEqual(response_list_empty.status_code, 200)
        self.assertEqual(len(response_list_empty.data), 0)

        # Add complaint
        url_add = reverse('main:complaints-list')
        self.client.post(url_add, data={'post': post.pk,
                                        'type': 'PRICE'})

        # Ensure we can filter posts by complaints
        response_list = self.client.get(url_list)
        self.assertEqual(response_list.status_code, 200)
        self.assertGreater(len(response_list.data), 0)

        url_detail = reverse('main:posts_moderation-detail', args=[post.pk])
        response_reject = self.client.patch(url_detail, data={'rejected': True,
                                                              'reject_message': 'PRICE'})
        self.assertEqual(response_reject.status_code, 200)
        self.assertTrue(Post.objects.first().rejected)

        user.is_staff = False
        user.save()

        # Ensure rejected post wont be displaying in public list
        url_public_list = reverse('main:posts_public-list')
        response_public = self.client.get(url_public_list)
        self.assertEqual(response_public.status_code, 200)
        self.assertEqual(len(response_public.data), 2)

        # Ensure non admin cant get access to this view
        url_list = reverse('main:posts_moderation-list')
        response_list_empty = self.client.get(url_list)
        self.assertEqual(response_list_empty.status_code, 403)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_saving_filters(self):
        """ Ensure we can save and get user`s saved filters """
        house, *_, flat = self.init_house_structure()
        post, *_ = self.init_post(house, flat)

        filter_data = {
            'price__gt': 5000,
            'payment_options': 'PAYMENT'
        }
        # Ensure we can filter posts
        url_filter = reverse('main:posts-list')
        response_filter = self.client.get(url_filter, data=filter_data)
        self.assertEqual(response_filter.status_code, 200)
        self.assertGreater(len(response_filter.data), 0)
        self.assertEqual(response_filter.data[0]['price'], 10000)

        # Save current filter set
        url_list = reverse('main:user_filters-list')
        response_add = self.client.post(url_list, data=filter_data)
        self.assertEqual(response_add.status_code, 201)
        self.assertEqual(UserFilter.objects.count(), 1)
        self.assertEqual(UserFilter.objects.first().min_price, 5000)

        # Get saved filter set
        url_detail = reverse('main:user_filters-detail', args=[response_add.data['saved_filter_pk']])
        response_detail = self.client.get(url_detail)
        self.assertEqual(response_detail.status_code, 200)
        self.assertEqual(response_detail.data['price__gt'], 5000)

        # Ensure we can filter by saved filters
        response_filter_by_saved_filter = self.client.get(url_filter, data=response_detail.data)
        self.assertEqual(response_filter_by_saved_filter.status_code, 200)
        self.assertGreater(len(response_filter_by_saved_filter.data), 0)
        self.assertEqual(response_filter_by_saved_filter.data[0]['price'], 10000)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_subscription_limitations(self):
        """ Ensure unsubscribed users have restrictions
            And subscribed users do not have
         """
        house, *_, flat = self.init_house_structure()

        # WARNING: For test purposes limitations are reduced
        UserFilter.set_limit(2)
        Post.set_limit(2)

        user = User.objects.get(email=self._test_user_email)
        self.assertFalse(user.subscribed)  # Ensure user is not subscribed

        # Check filter limitations
        filter_data = {
            'price__gte': 5000,
            'payment_options': 'PAYMENT'
        }
        url_list = reverse('main:user_filters-list')
        response_add = self.client.post(url_list, data=filter_data)
        self.assertEqual(response_add.status_code, 201)
        response_add2 = self.client.post(url_list, data=filter_data)
        self.assertEqual(response_add2.status_code, 201)
        self.assertEqual(UserFilter.objects.count(), 2)
        # Max available filter - 2
        # Check limit
        response_add3 = self.client.post(url_list, data=filter_data)
        self.assertEqual(response_add3.status_code, 400)
        self.assertEqual(response_add3.data['Error'],
                         'You have reached limit. Please, delete another filter or subscribe')
        self.assertEqual(UserFilter.objects.count(), 2)

        # Check post limitations
        post_data = {'flat': flat.pk,
                     'house': house.pk,
                     'price': 100000,
                     'payment_options': 'PAYMENT'}

        url_create = reverse('main:posts-list')

        with open(self.temp_media_image_path, 'rb') as file:
            post_data['main_image'] = file
            response_create1 = self.client.post(url_create, data=post_data)
        self.assertEqual(response_create1.status_code, 201)

        with open(self.temp_media_image_path, 'rb') as file:
            post_data['main_image'] = file
            response_create2 = self.client.post(url_create, data=post_data)
        self.assertEqual(response_create2.status_code, 201)
        self.assertEqual(Post.objects.count(), 2)
        # Max available posts - 2
        # Check limit
        with open(self.temp_media_image_path, 'rb') as file:
            post_data['main_image'] = file
            response_create3 = self.client.post(url_create, data=post_data)
        self.assertEqual(response_create3.status_code, 400)
        self.assertEqual(response_create3.data['Error'],
                         'You have reached limit. Please, delete another post or subscribe')
        self.assertEqual(Post.objects.count(), 2)

        # Set subscription
        user.subscribed = True
        user.save()
        self.assertTrue(user.subscribed)

        # Check that we can add new filter
        response_add3 = self.client.post(url_list, data=filter_data)
        self.assertEqual(response_add3.status_code, 201)
        self.assertEqual(UserFilter.objects.count(), 3)

        # Check that we can add new post
        with open(self.temp_media_image_path, 'rb') as file:
            post_data['main_image'] = file
            response_create3 = self.client.post(url_create, data=post_data)
        self.assertEqual(response_create3.status_code, 201)
        self.assertEqual(Post.objects.count(), 3)

        # Unset subscription
        user.subscribed = False
        user.save()
        self.assertFalse(user.subscribed)

        # Ensure we cant add new filter or post
        response_add4 = self.client.post(url_list, data=filter_data)
        self.assertEqual(response_add4.status_code, 400)
        self.assertEqual(response_add4.data['Error'],
                         'You have reached limit. Please, delete another filter or subscribe')
        self.assertEqual(UserFilter.objects.count(), 3)

        # Delete two filters
        filter_one = UserFilter.objects.filter(user__email=self._test_user_email).first()
        filter_two = UserFilter.objects.filter(user__email=self._test_user_email).last()
        url_filter_detail_one = reverse('main:user_filters-detail', args=[filter_one.pk])
        response_delete_one = self.client.delete(url_filter_detail_one)
        url_filter_detail_two = reverse('main:user_filters-detail', args=[filter_two.pk])
        response_delete_two = self.client.delete(url_filter_detail_two)
        self.assertEqual(response_delete_one.status_code, 204)
        self.assertEqual(response_delete_two.status_code, 204)
        self.assertEqual(UserFilter.objects.count(), 1)

        # Ensure we can add filter because filter amount ==  1
        response_add5 = self.client.post(url_list, data=filter_data)
        self.assertEqual(response_add5.status_code, 201)
        self.assertEqual(UserFilter.objects.count(), 2)

    def test_promotion(self):
        """ Ensure we can create\\get\\delete promotion
            Also, test that ensure type efficiency make effect on posts order
         """
        house, *_, flat = self.init_house_structure()
        post, post2, post3 = self.init_post(house, flat)

        url_post_list = reverse('main:posts-list')
        response_post_list = self.client.get(url_post_list)
        self.assertEqual(response_post_list.status_code, 200)
        self.assertEqual(response_post_list.data[0]['weight'], 0)
        self.assertEqual(response_post_list.data[1]['weight'], 0)
        self.assertEqual(response_post_list.data[2]['weight'], 0)

        # Add promotion for first post
        low = PromotionType.objects.get(efficiency=50)
        average = PromotionType.objects.get(efficiency=75)
        high = PromotionType.objects.get(efficiency=100)

        url_promotion = reverse('main:promotions-list')
        response_add1 = self.client.post(url_promotion, data={'post': post.pk,
                                                              'phrase': 'TRADE',
                                                              'color': 'GREEN',
                                                              'type': low.pk})
        self.assertEqual(response_add1.status_code, 201)
        self.assertEqual(Post.objects.get(pk=post.pk).weight, 50)

        # Add promotion to second post
        response_add2 = self.client.post(url_promotion, data={'post': post2.pk,
                                                              'phrase': 'SEA',
                                                              'color': 'PINK',
                                                              'type': average.pk})
        self.assertEqual(response_add2.status_code, 201)
        self.assertEqual(Post.objects.get(pk=post2.pk).weight, 75)

        # Add promotion to third post
        response_add3 = self.client.post(url_promotion, data={'post': post3.pk,
                                                              'phrase': 'PRICE',
                                                              'color': 'GREEN',
                                                              'type': high.pk})
        self.assertEqual(response_add3.status_code, 201)
        self.assertEqual(Post.objects.get(pk=post3.pk).weight, 100)

        # Test ordering
        # It should be next: post3, post2, post1
        # Because their weight right now are: 100, 75, 50
        response_post_list_by_ordering = self.client.get(url_post_list)
        self.assertEqual(response_post_list_by_ordering.status_code, 200)
        self.assertEqual(response_post_list_by_ordering.data[0]['weight'], 100)
        self.assertEqual(response_post_list_by_ordering.data[1]['weight'], 75)
        self.assertEqual(response_post_list_by_ordering.data[2]['weight'], 50)

        # Test public views
        url_post_public = reverse('main:posts_public-list')
        response_post_public = self.client.get(url_post_public)
        self.assertEqual(response_post_public.status_code, 200)
        self.assertEqual(response_post_public.data[0]['weight'], 100)
        self.assertEqual(response_post_public.data[1]['weight'], 75)
        self.assertEqual(response_post_public.data[2]['weight'], 50)

        # Assert that price has been changed
        self.assertGreater(Promotion.objects.get(post=post).price, 0)
        self.assertGreater(Promotion.objects.get(post=post2).price, 0)
        self.assertGreater(Promotion.objects.get(post=post3).price, 0)

        # Ensure we cant add more that one promotion for post
        response_add4 = self.client.post(url_promotion, data={'post': post.pk,
                                                              'phrase': 'TRADE',
                                                              'color': 'GREEN',
                                                              'type': low.pk})
        self.assertEqual(response_add4.status_code, 400)

        # Test deleting promotion for post
        url_promotion_detail = reverse('main:promotions-detail', args=[response_add3.data['id']])
        response_promotion_delete = self.client.delete(url_promotion_detail)
        self.assertEqual(response_promotion_delete.status_code, 204)

        # Ensure post ordering has been changed. It should be now: post2, post1, post3
        response_posts_list_with_new_ordering = self.client.get(url_post_list)
        self.assertEqual(response_posts_list_with_new_ordering.status_code, 200)
        self.assertEqual(response_posts_list_with_new_ordering.data[0]['weight'], 75)
        self.assertEqual(response_posts_list_with_new_ordering.data[1]['weight'], 50)
        self.assertEqual(response_posts_list_with_new_ordering.data[2]['weight'], 0)

        response_post_public = self.client.get(url_post_public)
        self.assertEqual(response_post_public.status_code, 200)
        self.assertEqual(response_post_public.data[0]['weight'], 75)
        self.assertEqual(response_post_public.data[1]['weight'], 50)
        self.assertEqual(response_post_public.data[2]['weight'], 0)

    def test_promotion_info_in_post_serializer(self):
        """ Ensure we will get info about current promotion for post """
        house, *_, flat = self.init_house_structure()
        post, post2, *_ = self.init_post(house, flat)

        high = PromotionType.objects.get(efficiency=100)

        url_promotion = reverse('main:promotions-list')
        response_add1 = self.client.post(url_promotion, data={'post': post.pk,
                                                              'phrase': 'TRADE',
                                                              'color': 'GREEN',
                                                              'type': high.pk})
        self.assertEqual(response_add1.status_code, 201)
        promo = Promotion.objects.get(pk=response_add1.data['id'])
        current_date = datetime.date.today()
        next_month = current_date + relativedelta(month=current_date.month + 1)
        self.assertEqual(promo.end_date, next_month)

        url_post_detail = reverse('main:posts-detail', args=[post.pk])
        response_post_detail = self.client.get(url_post_detail)
        self.assertEqual(response_post_detail.status_code, 200)
        self.assertEqual(response_post_detail.data['promotion']['color'], 'GREEN')
        self.assertEqual(response_post_detail.data['promotion']['phrase'], 'Возможен торг')

        # Ensure we still can get post without promotions
        url_post_detail2 = reverse('main:posts-detail', args=[post2.pk])
        response_post_detail2 = self.client.get(url_post_detail2)
        self.assertEqual(response_post_detail2.status_code, 200)
        self.assertEqual(response_post_detail2.data['promotion'], None)

    def test_like_dislike_weight_effect(self):
        """ Ensure like/dislike has effect on post weight """
        house, *_, flat = self.init_house_structure()
        post, post2, post3 = self.init_post(house, flat)

        url_post_list = reverse('main:posts-list')
        response_post_list = self.client.get(url_post_list)
        self.assertEqual(response_post_list.status_code, 200)
        self.assertEqual(response_post_list.data[0]['weight'], 0)
        self.assertEqual(response_post_list.data[1]['weight'], 0)
        self.assertEqual(response_post_list.data[2]['weight'], 0)

        url_like = reverse('main:like_dislike', args=[post2.pk])
        response_increment_like = self.client.patch(url_like, data={'action': 'like'})
        self.assertEqual(response_increment_like.status_code, 200)
        self.assertEqual(Post.objects.get(pk=post2.pk).likes, 1)

        response_post_after_like = self.client.get(url_post_list)
        self.assertEqual(response_post_after_like.status_code, 200)
        self.assertEqual(response_post_after_like.data[0]['id'], post2.pk)
        self.assertEqual(response_post_after_like.data[0]['weight'], 1)

        response_decrement_like = self.client.patch(url_like, data={'action': 'dislike'})
        self.assertEqual(response_decrement_like.status_code, 200)
        self.assertEqual(Post.objects.get(pk=post2.pk).likes, -1)

        response_post_after_dislike = self.client.get(url_post_list)
        self.assertEqual(response_post_after_dislike.data[-1]['weight'], -1)

        # Remove dislike if user 'tap' buttons twice
        response_remove_dislike = self.client.patch(url_like, data={'action': 'dislike'})
        self.assertEqual(response_remove_dislike.status_code, 200)
        self.assertEqual(Post.objects.first().likes, 0)

        response_post_after_remove_dislike = self.client.get(url_post_list)
        self.assertEqual(response_post_after_remove_dislike.data[1]['weight'], 0)

    def test_add_promotion_without_pay(self):
        """ Ensure unpaid promotion will have no effect on post
            Also, test that change status from 'unpaid' to 'paid' will have effect on post
         """
        house, *_, flat = self.init_house_structure()
        post, post2, post3 = self.init_post(house, flat)

        high = PromotionType.objects.get(efficiency=100)

        url_promotion = reverse('main:promotions-list')
        response_add1 = self.client.post(url_promotion, data={'post': post.pk,
                                                              'phrase': 'TRADE',
                                                              'color': 'GREEN',
                                                              'type': high.pk,
                                                              'paid': False})
        self.assertEqual(response_add1.status_code, 201)
        post = Post.objects.get(pk=post.pk)
        promotion = post.promotion
        self.assertEqual(post.weight, 0)
        self.assertFalse(promotion.paid)

        # Ensure post wont contain promotion if it is not paid
        url_post_detail = reverse('main:posts-detail', args=[post.pk])
        response_post_detail = self.client.get(url_post_detail)
        self.assertEqual(response_post_detail.status_code, 200)
        self.assertIsNone(response_post_detail.data['promotion'])

        promotion_detail = reverse('main:promotions-detail', args=[promotion.pk])
        response_paid_promotion = self.client.patch(promotion_detail, data={'paid': True})
        self.assertEqual(response_paid_promotion.status_code, 200)
        post = Post.objects.get(pk=post.pk)
        promotion = post.promotion
        self.assertEqual(post.weight, 100)
        self.assertTrue(promotion.paid)

        response_post_detail_success = self.client.get(url_post_detail)
        self.assertEqual(response_post_detail_success.status_code, 200)
        self.assertIsNotNone(response_post_detail_success.data['promotion'])

        url_post_list = reverse('main:posts-list')
        response_list = self.client.get(url_post_list)
        self.assertEqual(response_list.status_code, 200)
        self.assertEqual(response_list.data[0]['id'], post.pk)
        self.assertEqual(response_list.data[0]['weight'], post.weight)

    def test_celery_check_promotion_end_date(self):
        """ Ensure celery will delete expiring promotions """
        house, *_, flat = self.init_house_structure()
        post, post2, post3 = self.init_post(house, flat)

        # Ensure all post`s weights are the same
        url_post_list = reverse('main:posts-list')
        response_post_list = self.client.get(url_post_list)
        self.assertEqual(response_post_list.status_code, 200)
        self.assertEqual(response_post_list.data[0]['weight'], 0)
        self.assertEqual(response_post_list.data[1]['weight'], 0)
        self.assertEqual(response_post_list.data[2]['weight'], 0)

        # Add promotion for first post
        low = PromotionType.objects.get(efficiency=50)

        url_promotion = reverse('main:promotions-list')
        response_add1 = self.client.post(url_promotion, data={'post': post.pk,
                                                              'phrase': 'TRADE',
                                                              'color': 'GREEN',
                                                              'type': low.pk})
        self.assertEqual(response_add1.status_code, 201)
        post = Post.objects.get(pk=post.pk)
        self.assertEqual(post.weight, 50)
        promo = post.promotion
        promo.end_date = datetime.date.today()
        promo.save()

        # Ensure first post has bigger weight that others
        response_post_list = self.client.get(url_post_list)
        self.assertEqual(response_post_list.status_code, 200)
        self.assertEqual(response_post_list.data[0]['weight'], 50)
        self.assertEqual(response_post_list.data[1]['weight'], 0)
        self.assertEqual(response_post_list.data[2]['weight'], 0)

        # Run celery task
        check_promotion.apply()
        post = Post.objects.get(pk=post.pk)
        self.assertFalse(hasattr(post, 'promotion'))
        self.assertEqual(post.weight, 0)
        message = Message.objects.filter(receiver=post.user)
        self.assertTrue(message.exists())
        self.assertEqual(message.first().text, 'Your promotion plan has been expired')

        # Ensure all post`s weights are the same
        url_post_list = reverse('main:posts-list')
        response_post_list = self.client.get(url_post_list)
        self.assertEqual(response_post_list.status_code, 200)
        self.assertEqual(response_post_list.data[0]['weight'], 0)
        self.assertEqual(response_post_list.data[1]['weight'], 0)
        self.assertEqual(response_post_list.data[2]['weight'], 0)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_celery_check_filters_matching(self):
        """ Ensure that after we create post that matches one of the user`s filter - user will receiver
         message notification """

        # Save user filter
        filter_data = {
                    'price__gt': 10000,
                    'payment_options': 'PAYMENT'
                }
        url_list = reverse('main:user_filters-list')
        response_add = self.client.post(url_list, data=filter_data)
        self.assertEqual(response_add.status_code, 201)
        self.assertEqual(UserFilter.objects.count(), 1)
        self.assertEqual(UserFilter.objects.first().min_price, 10000)

        # Create new post
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {Token.objects.get(user__email=self._test_user_email_two)}'
        )
        house, *_, flat = self.init_house_structure()
        url_create = reverse('main:posts-list')
        with open(self.temp_media_image_path, 'rb') as file:
            response_create = self.client.post(url_create, data={'flat': flat.pk,
                                                                 'house': house.pk,
                                                                 'price': 100000,
                                                                 'payment_options': 'PAYMENT',
                                                                 'main_image': file})
        self.assertEqual(response_create.status_code, 201)

        # Ensure we get notification from system
        messages = Message.objects.filter(receiver__email=self._test_user_email)
        self.assertGreater(messages.count(), 0)
        self.assertEqual(messages.first().sender.role, 'SYSTEM')

    def test_celery_check_notification_about_promotion_almost_ending(self):
        """ Ensure we get notification if out promotion plan will end in next 10 days """
        house, *_, flat = self.init_house_structure()
        post, *_ = self.init_post(house, flat)

        # Add promotion for first post
        low = PromotionType.objects.get(efficiency=50)

        url_promotion = reverse('main:promotions-list')
        response_add1 = self.client.post(url_promotion, data={'post': post.pk,
                                                              'phrase': 'TRADE',
                                                              'color': 'GREEN',
                                                              'type': low.pk})
        self.assertEqual(response_add1.status_code, 201)
        post = Post.objects.get(pk=post.pk)
        promo = post.promotion
        promo.end_date = datetime.date.today() + datetime.timedelta(days=10)
        promo.save()

        # Run celery task
        check_and_send_notification_about_promotion_time_almost_ending.apply()
        message = Message.objects.filter(receiver=post.user)
        self.assertTrue(message.exists())
        self.assertEqual(message.first().text, 'Your promotion plan is almost expired')

