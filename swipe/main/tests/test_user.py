from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from rest_framework.test import APITestCase

from main.tests.utils import get_id_token, get_temporary_image

from _db.models.user import Contact, User, Message

import tempfile


class TestUser(APITestCase):
    def setUp(self):
        self._test_user_uid = '8ugeJOTWTMbeFYpKDpx2lHr0qfq1'
        self._test_user_uid_two = '6vO5mBRld2evvoEzDzZoMquRyIn1'
        self._test_user_email = 'user@example.com'
        self._test_user_email_two = 'test@mail.com'
        self._url = reverse('main:user-detail', args=[self._test_user_uid])
        self._token = get_id_token()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {self._token}'
        )

    @classmethod
    def setUpTestData(cls):
        cls._test_user_uid = '8ugeJOTWTMbeFYpKDpx2lHr0qfq1'
        cls._test_user_uid_two = '6vO5mBRld2evvoEzDzZoMquRyIn1'
        User.objects.create(uid=cls._test_user_uid, email='user@example.com')
        User.objects.create(uid=cls._test_user_uid_two, email='test@mail.com')

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
        user = User.objects.get(uid=self._test_user_uid)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.notifications, 'AGENT')

    def test_change_user_info_with_another_user_uid(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {get_id_token(self._test_user_email_two)}'  # test email
        )
        response = self.client.patch(self._url, data={'first_name': 'User first name',
                                                      'last_name': 'User last name'})
        self.assertEqual(response.status_code, 403)

    def test_uid_is_read_only_field(self):
        """ ensure we cant change uid. Because this is key field with firebase integration """
        response = self.client.patch(self._url, data={'uid': '123'})
        self.assertEqual(response.data['uid'], '8ugeJOTWTMbeFYpKDpx2lHr0qfq1')

    def test_user_list(self):
        url = reverse('main:user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_list_with_filter(self):
        """Ensure we can filter users by role"""
        User.objects.create(uid=123, email='temp@mail.com', role='NOTARY')
        url = reverse('main:user-list')
        response = self.client.get(url, data={'role': 'NOTARY'})
        self.assertEqual(response.status_code, 200)

    def test_right_choice_field_name(self):
        response = self.client.get(self._url)
        self.assertNotEqual(response.data['role'], 'USER')

    def test_renew_subscription(self):
        url = reverse('main:update_subscription', args=[self._test_user_uid])
        response = self.client.patch(url, data={'subscribed': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['subscribed'])

    def test_cancel_subscription(self):
        url = reverse('main:update_subscription', args=[self._test_user_uid])
        response = self.client.patch(url, data={'subscribed': '0'})  # if '0' - subscription has to be canceled
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['subscribed'])

    def test_contacts(self):
        """ensure we can add contact and delete it"""
        url = reverse('main:add_contact', args=[self._test_user_uid])
        response = self.client.post(url, data={'contact_id': '6vO5mBRld2evvoEzDzZoMquRyIn1'})
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

        contacts = Contact.objects.filter(user__uid=self._test_user_uid)
        self.assertEqual(contacts.count(), 0)

    def test_add_message(self):
        """Ensure we can add message, edit it, get it and delete it"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {self._token}'
        )

        url = reverse('main:user_messages', args=[self._test_user_uid])
        response = self.client.post(url, data={'sender': self._test_user_uid,
                                               'receiver': self._test_user_uid_two,
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
        self.client.credentials(
            HTTP_AUTHORIZATION=f'JWT {self._token}'
        )

        url = reverse('main:user_messages', args=[self._test_user_uid])
        file = SimpleUploadedFile('photo.jpeg', b'file_content', content_type='image/jpeg')
        response = self.client.post(url, data={'sender': self._test_user_uid,
                                               'receiver': self._test_user_uid_two,
                                               'text': 'Message with image'})
        self.assertEqual(response.status_code, 200)

        url_attach = reverse('main:attachments')
        response = self.client.post(url_attach, data={'message': response.data['pk'],
                                                      'file': file})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.data['message']), Message.objects.first().attach.first().message.pk)

    def test_changing_ban_status(self):
        """Ensure we can change user ban status"""
        admin_user = User.objects.get(uid=self._test_user_uid)
        admin_user.is_staff = True
        admin_user.save()
        banned_user = User.objects.get(uid=self._test_user_uid_two)
        url = reverse('main:change_ban_status', args=[self._test_user_uid_two])
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(banned_user, User.objects.filter(ban=False))

    def test_change_ban_status_by_not_admin(self):
        """Ensure non admin cant change users ban status"""
        url = reverse('main:change_ban_status', args=[self._test_user_uid])
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 403)

    def test_admin_access_to_notary(self):
        """Ensure we can get, change, delete notary info from admin profile"""
        admin_user = User.objects.get(uid=self._test_user_uid)
        admin_user.is_staff = True
        admin_user.save()

        notary = User.objects.get(uid=self._test_user_uid_two)
        notary.role = 'NOTARY'
        notary.save()

        url = reverse('main:users_notary_admin-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url_change = reverse('main:users_notary_admin-detail', args=[notary.uid])
        response = self.client.patch(url_change, data={'first_name': 'Changed notary name'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(uid=self._test_user_uid_two).first_name, 'Changed notary name')

    def test_not_admin_access_to_notary(self):
        """Ensure we cant get access to notaries info without admin account"""
        url = reverse('main:users_notary_admin-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
