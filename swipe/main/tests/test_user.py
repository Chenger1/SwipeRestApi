from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from main.tests.utils import get_temporary_image
from main.tasks import check_subscription, check_and_send_notification_about_subscription_almost_ending

from _db.models.user import Contact, User, Message

import tempfile
import datetime


class TestUser(APITestCase):
    def setUp(self):
        self._test_user_email = 'user@example.com'
        self._test_user_email_two = 'test@mail.com'
        self._token = Token.objects.get(user__email=self._test_user_email)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self._token.key}'
        )
        self._user1 = User.objects.get(email=self._test_user_email)
        self._user2 = User.objects.get(email=self._test_user_email_two)
        self._url = reverse('main:users-detail', args=[self._user1.pk])

    @classmethod
    def setUpTestData(cls):
        User.objects.create(email='user@example.com', phone_number='+380638271139')
        User.objects.create(email='test@mail.com', phone_number='+380638271140')

    def test_get_user_info(self):
        """Ensure we can get user info"""
        response = self.client.get(self._url)
        self.assertEqual(response.data['pk'], self._user1.pk)

    def test_get_wrong_user(self):
        url = reverse('main:users-detail', args=['12345'])
        response = self.client.get(url)
        self.assertEqual(response.data['detail'], 'Not found.')

    def test_change_user_info(self):
        """ensure we can change user info"""
        response = self.client.patch(self._url, data={'first_name': 'User first name',
                                                      'last_name': 'User last name'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'User first name')

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_change_user_info_with_photo(self):
        """Ensure we can set profile photo"""
        file = get_temporary_image(tempfile.NamedTemporaryFile())
        response = self.client.patch(self._url, data={'first_name': 'User with photo',
                                                      'photo': file.read()})
        self.assertEqual(response.status_code, 200)

    def test_switch_notifications_to_agent(self):
        """ test that we can change notifications """
        response = self.client.patch(self._url, data={'notifications': 'AGENT'})
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email=self._test_user_email)
        self.assertEqual(user.notifications, 'AGENT')

    def test_change_user_info_with_another_user(self):
        self._token2 = Token.objects.get(user__email=self._test_user_email_two)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self._token2.key}'
        )
        response = self.client.patch(self._url, data={'first_name': 'User first name',
                                                      'last_name': 'User last name'})
        self.assertEqual(response.status_code, 403)

    def test_user_list(self):
        url = reverse('main:users-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_list_with_filter(self):
        """Ensure we can filter users by role"""
        User.objects.create(email='temp@mail.com', role='NOTARY', phone_number='+8452884781')
        url = reverse('main:users-list')
        response = self.client.get(url, data={'role': 'NOTARY'})
        self.assertEqual(response.status_code, 200)

    def test_right_choice_field_name(self):
        response = self.client.get(self._url)
        self.assertNotEqual(response.data['role_display'], 'USER')

    def test_renew_subscription(self):
        url = reverse('main:update_subscription', args=[self._user1.pk])
        response = self.client.patch(url, data={'subscribed': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['subscribed'])

    def test_cancel_subscription(self):
        url = reverse('main:update_subscription', args=[self._user1.pk])
        response = self.client.patch(url, data={'subscribed': '0'})  # if '0' - subscription has to be canceled
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['subscribed'])

    def test_contacts(self):
        """ensure we can add contact and delete it"""
        url = reverse('main:add_contact', args=[self._user1.pk])
        response = self.client.post(url, data={'contact_id': '2'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('contact_obj_id', response.data)

        url_get = reverse('main:get_user_contacts', args=['USER'])  # test getting contacts by role
        response_get = self.client.get(url_get)
        self.assertEqual(response_get.status_code, 200)
        self.assertGreater(len(response_get.data['contacts']), 0)

        url_get_without_role = reverse('main:get_user_contacts', args=['ALL'])
        response_get_without_role = self.client.get(url_get_without_role)
        self.assertEqual(response_get_without_role.status_code, 200)
        self.assertGreater(len(response_get_without_role.data['contacts']), 0)

        url_ban = reverse('main:change_banned_status', args=[response.data['contact_obj_id']])
        response_ban = self.client.patch(url_ban)
        self.assertEqual(response_ban.status_code, 200)

        url_delete = reverse('main:delete_contact', args=[response.data['contact_obj_id']])
        response_delete = self.client.delete(url_delete, data={'contact_obj_id': response.data['contact_obj_id']})
        self.assertEqual(response_delete.status_code, 200)

        contacts = Contact.objects.filter(user__pk=1)
        self.assertEqual(contacts.count(), 0)

    def test_add_message(self):
        """Ensure we can add message, edit it, get it and delete it"""

        url = reverse('main:user_messages', args=[self._user1.pk])
        response = self.client.post(url, data={'sender': self._user1.pk,
                                               'receiver': self._user2.pk,
                                               'text': 'First message'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url_edit = reverse('main:edit_message', args=[response.data[0]['pk']])
        response = self.client.patch(url_edit, data={'text': 'Edited text'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['text'], 'Edited text')

        response = self.client.delete(url_edit)
        self.assertEqual(response.status_code, 200)

        messages = Message.objects.all()
        self.assertEqual(messages.count(), 0)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_add_message_with_attachment(self):
        """Ensure we can create message with media file"""

        url = reverse('main:user_messages', args=[self._user1.pk])
        file = SimpleUploadedFile('photo.jpeg', b'file_content', content_type='image/jpeg')
        response = self.client.post(url, data={'sender': self._user1.pk,
                                               'receiver': User.objects.last().pk,
                                               'text': 'Message with image'})
        self.assertEqual(response.status_code, 200)

        url_attach = reverse('main:attachments')
        response = self.client.post(url_attach, data={'message': response.data['pk'],
                                                      'file': file})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.data['message']), Message.objects.first().attach.first().message.pk)

        # Ensure we can upload on files with available formats
        # ['.pdf', '.doc', '.docx', '.jpg', 'jpeg', '.png', '.xlxs', '.xls', '.pptx']
        file1 = SimpleUploadedFile('script.js', b'file_content', content_type='application/msword')
        response_error = self.client.post(url_attach, data={'message': response.data['pk'],
                                                            'file': file1})
        self.assertEqual(response_error.status_code, 400)

        # Ensure we can download message attachment
        url_attach_detail = reverse('main:download_attachment', args=[response.data['pk']])
        response_attach_detail = self.client.get(url_attach_detail)
        self.assertEqual(response_attach_detail.status_code, 200)
        self.assertIn('attachment; filename=', response_attach_detail.get('Content-Disposition'))

    def test_changing_ban_status(self):
        """Ensure we can change user ban status"""
        admin_user = User.objects.get(email=self._test_user_email)
        admin_user.is_staff = True
        admin_user.save()
        banned_user = User.objects.get(email=self._test_user_email_two)
        url = reverse('main:change_ban_status', args=[banned_user.pk])
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(banned_user, User.objects.filter(ban=False))

    def test_change_ban_status_by_not_admin(self):
        """Ensure non admin cant change users ban status"""
        url = reverse('main:change_ban_status', args=[self._user1.pk])
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 403)

    def test_admin_access_to_notary(self):
        """Ensure we can get, change, delete notary info from admin profile"""
        admin_user = User.objects.get(email=self._test_user_email)
        admin_user.is_staff = True
        admin_user.save()

        notary = User.objects.get(email=self._test_user_email_two)
        notary.role = 'NOTARY'
        notary.save()

        url = reverse('main:users_notary_admin-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url_change = reverse('main:users_notary_admin-detail', args=[notary.pk])
        response = self.client.patch(url_change, data={'first_name': 'Changed notary name'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.last().first_name, 'Changed notary name')

    def test_not_admin_access_to_notary(self):
        """Ensure we cant get access to notaries info without admin account"""
        url = reverse('main:users_notary_admin-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_celery_check_subscription_end_date(self):
        """ Ensure celery periodic task checks subscription status """
        user = User.objects.get(email=self._test_user_email)
        user.subscribed = True
        user.end_date = datetime.date.today()
        user.save()

        # Run celery task
        check_subscription.apply()

        # Ensure subscription state has been changed
        user = User.objects.get(email=self._test_user_email)
        self.assertFalse(user.subscribed)
        message = Message.objects.filter(receiver=user)
        self.assertTrue(message.exists())
        self.assertEqual(message.first().text, 'Your subscription has been expired')

    def test_create_user_with_role_system(self):
        """ User with role 'SYSTEM' is a account for sending notifications.
         Ensure we can create only one system account """
        url = reverse('main:users-list')
        response = self.client.post(url, data={'pk': self._user1.pk, 'role': 'SYSTEM',
                                               'email': 'swipe@mail.com',
                                               'is_staff': True,
                                               'notifications': 'OFF'})
        self.assertEqual(response.status_code, 400)

    def test_celery_task_for_notification_about_subscription_almost_ending(self):
        """ Ensure we get notification if out subscription will end in next 10 days """
        user = User.objects.get(email=self._test_user_email)
        user.subscribed = True
        user.end_date = datetime.date.today() + datetime.timedelta(days=10)
        user.save()

        # Run celery task
        check_and_send_notification_about_subscription_almost_ending.apply()

        # Ensure subscription state has been changed
        user = User.objects.get(email=self._test_user_email)
        message = Message.objects.filter(receiver=user)
        self.assertTrue(message.exists())
        self.assertEqual(message.first().text, 'Your subscription is almost expired')
