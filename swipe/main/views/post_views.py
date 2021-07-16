from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from main.permissions import IsOwner, IsOwnerOrReadOnly
from main.serializers import post_serializers

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


class PostImageViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = PostImage.objects.all()
    serializer_class = post_serializers.PostImageSerializer
