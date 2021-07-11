from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import FileUploadParser

from main import serializers
from main.permissions import IsProfileOwner, IsOwner

from _db.models.user import Contact, Message

import datetime
from dateutil.relativedelta import relativedelta


User = get_user_model()


class UserViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsProfileOwner)
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_object(self):
        obj = get_object_or_404(User, uid=self.kwargs.get('pk'))
        self.check_object_permissions(self.request, obj)
        return obj


class UpdateSubscription(APIView):
    permission_classes = (IsAuthenticated, IsProfileOwner)

    def patch(self, request, uid, format=None):
        user = get_object_or_404(User, uid=uid)
        if bool(int(request.data['subscribed'])):
            current_date = datetime.date.today()
            user.end_date = current_date + relativedelta(month=current_date.month+1)
            user.subscribed = True
        else:
            user.end_date = datetime.date.today()
            user.subscribed = False
        user.save()
        return Response({'uid': user.uid, 'subscribed': user.subscribed,
                         'end_date': user.end_date.strftime('%Y-%m-%d')})


class ContactAPI(APIView):
    permission_classes = (IsAuthenticated, IsOwner)

    def get(self, request, role=None, format=None):
        contacts = Contact.objects.filter(user=request.user)
        if role != 'ALL':
            contacts = contacts.filter(contact__role=role)
        serializer = serializers.ContactSerializer(contacts, many=True)
        return Response({'contacts': serializer.data})

    def post(self, request, uid, format=None):
        user = get_object_or_404(User, uid=uid)
        contact = get_object_or_404(User, uid=request.data['contact_id'])
        contact_obj, _ = Contact.objects.get_or_create(user=user, contact=contact)
        return Response({'contact_obj_id': contact_obj.pk,
                         'contact_user_id': contact.uid})

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
    permission_classes = (IsAuthenticated, IsOwner)

    def get(self, request, uid=None, format=None):
        messages = Message.objects.filter(sender=request.user) | Message.objects.filter(receiver=request.user)
        messages = messages.order_by()
        serializer = serializers.ReadableMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, uid=None, format=None):
        data = {
            'sender': get_object_or_404(User, uid=request.data['sender']),
            'receiver': get_object_or_404(User, uid=request.data['receiver']),
            'text': request.data['text']
        }
        serializer = serializers.WritableMessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        message = get_object_or_404(Message, pk=pk)
        serializer = serializers.WritableMessageSerializer(instance=message, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        message = get_object_or_404(Message, pk=pk)
        message.delete()
        return Response(status=status.HTTP_200_OK)


class AttachmentApi(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk, format=None):
        serializer = serializers.AttachmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
