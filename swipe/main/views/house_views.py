from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

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
