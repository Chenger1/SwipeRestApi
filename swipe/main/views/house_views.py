from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from django_filters import rest_framework as filters

from main.permissions import IsOwner
from main.serializers import house_serializers
from main.filters import FlatFilter

from _db.models.models import House, Building, Section, Floor, NewsItem, Document, Flat


class HouseViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = House.objects.all()
    serializer_class = house_serializers.HouseSerializer

    def get_queryset(self):
        return House.objects.filter(sales_department=self.request.user)

    def perform_create(self, serializer):
        serializer.save(sales_department=self.request.user)


class BuildingViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = Building.objects.all()
    serializer_class = house_serializers.BuildingSerializer


class SectionViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = Section.objects.all()
    serializer_class = house_serializers.SectionSerializer


class FloorViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = Floor.objects.all()
    serializer_class = house_serializers.FloorSerializer


class NewsItemViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = NewsItem.objects.all()
    serializer_class = house_serializers.NewsItemSerializer


class DocumentViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = Document.objects.all()
    serializer_class = house_serializers.DocumentSerializer


class FlatViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = Flat.objects.all()
    serializer_class = house_serializers.FlatSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = FlatFilter


class BookingFlat(APIView):
    permission_classes = (IsAuthenticated, )

    def patch(self, request, pk, format=None):
        """
        patch: If booking == '1' and not flat.client - set new one.
               If booking == '0' checks condition. Sets client as None can only either current client or house owner
               Otherwise it will return error message in response
        :param request: {'booking': '1'} or {'booking': '0'}
        :param pk: flat pk
        :param format:
        :return: Response
        """
        flat = get_object_or_404(Flat, pk=pk)
        is_house_owner = (flat.floor.section.building.house.sales_department == request.user)
        if request.data.get('booking') == '1' and not flat.client:
            flat.client = request.user
            flat.booked = True
        elif request.data.get('booking') == '0':
            if flat.client == request.user or is_house_owner:
                flat.client = None
                flat.booked = False
            else:
                return Response({'Error': 'You cannot remove current client from this flat'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Error': 'You can book this flat'}, status=status.HTTP_400_BAD_REQUEST)
        flat.save()
        return Response({'pk': flat.pk,
                         'user_uid': request.user.uid}, status=status.HTTP_200_OK)
