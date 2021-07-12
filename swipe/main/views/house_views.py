from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from main.permissions import IsOwner
from main.serializers import house_serializers

from _db.models.models import House, Building, Section, Floor


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
