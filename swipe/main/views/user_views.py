from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from main.serializers import user_serializers
from main.permissions import IsProfileOwner, IsMessageSenderOrReceiver, IsOwnerOrReadOnly, IsOwner
from main.services import generate_http_response_to_download

from _db.models.user import Contact, Message, UserFilter, Attachment, AdminToken

import datetime
from dateutil.relativedelta import relativedelta

User = get_user_model()


class UserViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsProfileOwner)
    queryset = User.objects.all().order_by('-id')
    serializer_class = user_serializers.UserSerializer
    view_tags = ['User']

    def get_object(self):
        obj = get_object_or_404(User, pk=self.kwargs.get('pk'))
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        return User.objects.filter(ban=False).order_by('-id')  # banned users not passed

    def list(self, request, *args, **kwargs):
        """
        Use 'GET' without params to get all users in system.
        Set query param 'role' in request 'GET' to filter users by role.
        :param request: query_params['role']
        :param args:
        :param kwargs:
        :return: queryset -> serialize -> json
        """
        queryset = self.filter_queryset(self.get_queryset())
        if request.query_params.get('role'):
            queryset = queryset.filter(role=request.query_params.get('role'))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        If user wants to change his admin status, he has to provide special admin token
        """

        if request.data.get('is_staff') or request.data.get('is_superuser'):
            if not request.data.get('admin_token'):
                return Response({'Token': 'No admin token is provided'}, status=status.HTTP_400_BAD_REQUEST)
            token = request.data.pop('admin_token')
            if AdminToken.objects.filter(token=token).exists():
                return super().update(request, *args, **kwargs)
            else:
                return Response({'Token': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super().update(request, *args, **kwargs)


class UpdateSubscription(APIView):
    permission_classes = (IsAuthenticated, IsProfileOwner)
    view_tags = ['User']

    def patch(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        if bool(int(request.data['subscribed'])):
            current_date = datetime.date.today()  # set new subscription end date in next month
            user.end_date = current_date + relativedelta(month=current_date.month+1)
            user.subscribed = True
        else:
            user.end_date = datetime.date.today()
            user.subscribed = False
        user.save()
        return Response({'pk': user.pk, 'subscribed': user.subscribed,
                         'end_date': user.end_date.strftime('%Y-%m-%d')})


class ChangeBanStatus(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    view_tags = ['Admin']

    def patch(self, request, pk, format=None):
        """
        Change user ban status to opposite
        :param request:
        :param pk:
        :param format:
        :return: Response
        """
        user = get_object_or_404(User, pk=pk)
        user.ban = not user.ban
        user.save()
        return Response({'pk': user.pk,
                         'ban': user.ban}, status=status.HTTP_200_OK)


class ContactAPI(APIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    view_tags = ['User']

    def get(self, request, role=None, format=None):
        """
        If role is 'ALL' - return all contacts.
        Otherwise, filter queryset by role.
        :param request:
        :param role: string: 'USER', 'AGENT', 'NOTARY', 'DEPART', 'ALL'
        :param format:
        :return: queryset -> serialize -> json
        """
        contacts = Contact.objects.filter(user=request.user, user__ban=False)
        if role != 'ALL':
            contacts = contacts.filter(contact__role=role)
        serializer = user_serializers.ContactSerializer(contacts, many=True)
        return Response({'contacts': serializer.data})

    def post(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        contact = get_object_or_404(User, pk=request.data['contact_id'])
        contact_obj, _ = Contact.objects.get_or_create(user=user, contact=contact)
        return Response({'contact_obj_id': contact_obj.pk,
                         'contact_user_id': contact.pk})

    def patch(self, request, pk, format=None):
        """
        Uses patch for change contact banned status.
        If it is True - sets False. Otherwise - True.
        :param request:
        :param pk:
        :param format:
        :return: response
        """
        contact = get_object_or_404(Contact, pk=pk)
        contact.ban = not contact.ban  # reverse current banned status
        contact.save()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        get_object_or_404(Contact, pk=pk).delete()
        return Response(status=status.HTTP_200_OK)


class MessageApi(APIView):
    permission_classes = (IsAuthenticated, IsMessageSenderOrReceiver)
    view_tags = ['User']

    def get(self, request, pk=None, format=None):
        if request.user.pk != pk:
            return Response({'Error': 'You can`t access this messages'})
        messages = Message.objects.filter(sender__pk=pk) | Message.objects.filter(receiver__pk=pk)
        messages = messages.order_by()
        serializer = user_serializers.ReadableMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, pk=None, format=None):
        if request.user.pk != int(request.data.get('sender')):
            #  User can send message only from himself
            return Response({'Error': 'You try send message from another person'}, status=status.HTTP_400_BAD_REQUEST)
        data = {
            'sender': get_object_or_404(User, pk=request.data['sender']),
            'receiver': get_object_or_404(User, pk=request.data['receiver']),
            'text': request.data['text']
        }
        serializer = user_serializers.WritableMessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        message = get_object_or_404(Message, pk=pk)
        self.check_object_permissions(request, message)
        serializer = user_serializers.WritableMessageSerializer(instance=message, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        message = get_object_or_404(Message, pk=pk)
        self.check_object_permissions(request, message)
        message.delete()
        return Response(status=status.HTTP_200_OK)


class AttachmentApi(APIView):
    permission_classes = (IsAuthenticated, )
    view_tags = ['User']

    def post(self, request, format=None):
        serializer = user_serializers.AttachmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, format=None):
        attach = get_object_or_404(Attachment, pk=pk)
        return generate_http_response_to_download(attach)


class NotaryUsersApi(ModelViewSet):
    """
    Api for work with users role 'Notary'. Get, edit, delete
    NOTE: THIS API USES FOR ADMIN USER WITH 'is_staff' privileges.
    If you want to get users with role 'Notary' for common users - use 'UserViewSet' with query params
    """
    permission_classes = (IsAuthenticated, IsAdminUser)
    serializer_class = user_serializers.UserSerializer
    queryset = User.objects.filter(role='NOTARY').order_by('-id')
    view_tags = ['Admin']


class UserFilterViewSet(ModelViewSet):
    """
     User can save 'Post' filters and get them from db
     """
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = user_serializers.UserFilterSerializer
    queryset = UserFilter.objects.all().order_by('-id')
    view_tags = ['User']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        If user is subscribed - he doesnt have any restrictions
        If he doens`t - check for reaching limit.
        :param request:
        :param args:
        :param kwargs:
        :return: Response
        """
        if request.user.subscribed or request.user.filters.count() < UserFilter.LIMIT:
            return super().create(request, *args, **kwargs)
        return Response({'Error': 'You have reached limit. Please, delete another filter or subscribe'},
                        status=status.HTTP_400_BAD_REQUEST)
