from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from django_filters import rest_framework as filters

from main.permissions import IsOwner, IsOwnerOrReadOnly
from main.serializers import post_serializers
from main.filters import PostFilter

from _db.models.models import Post, PostImage


class PostViewSet(ModelViewSet):
    """ CRUD operation for user`s posts """
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = Post.objects.all()
    serializer_class = post_serializers.PostSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostViewSetPublic(ListModelMixin,
                        RetrieveModelMixin,
                        GenericViewSet):
    """ Allow all users to see publications"""
    permission_classes = (AllowAny, )
    authentication_classes = []
    queryset = Post.objects.all()
    serializer_class = post_serializers.PostSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PostFilter


class PostImageViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = PostImage.objects.all()
    serializer_class = post_serializers.PostImageSerializer
