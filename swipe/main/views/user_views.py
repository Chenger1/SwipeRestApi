from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response

from main.serializers import UserSerializer
from main.permissions import IsProfileOwner

import datetime
from dateutil.relativedelta import relativedelta


User = get_user_model()


class UserViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsProfileOwner)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return get_object_or_404(User, uid=self.kwargs.get('pk'))


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
