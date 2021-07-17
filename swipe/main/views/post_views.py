from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from django_filters import rest_framework as filters

from main.permissions import IsOwner, IsOwnerOrReadOnly
from main.serializers import post_serializers
from main.filters import PostFilter

from _db.models.models import Post, PostImage, UserFavorites, Complaint


class PostViewSet(ModelViewSet):
    """ CRUD operation for user`s posts """
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = Post.objects.all()
    serializer_class = post_serializers.PostSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PostFilter

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

    def retrieve(self, request, *args, **kwargs):
        """ Increment view counter """
        obj = self.get_object()
        obj.views += 1
        obj.save(update_fields=('views', ))
        return super().retrieve(request, *args, **kwargs)


class PostImageViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = PostImage.objects.all()
    serializer_class = post_serializers.PostImageSerializer


class UserFavoritesViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = UserFavorites.objects.all()
    serializer_class = post_serializers.UserFavoritesWritableSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """
        UserFavoritesReadableSerializer contains nested serializer 'PostSerializer' to extend info about post
        UserFavoritesWritable Serializer just a regular serializer to work with object
        :return:
        """
        if self.action in ('list', 'retrieve'):
            return post_serializers.UserFavoritesReadableSerializer
        if self.action in ('create', 'update', 'destroy'):
            return post_serializers.UserFavoritesWritableSerializer
        return post_serializers.UserFavoritesReadableSerializer


class ComplaintViewSet(ModelViewSet):
    """ CRUD operations for user`s complaints """
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = Complaint.objects.all()
    serializer_class = post_serializers.ComplaintSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
