from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from django.db.models import Count
from django_filters import rest_framework as filters
from django.shortcuts import get_object_or_404

from main.permissions import IsOwner, IsOwnerOrReadOnly
from main.serializers import post_serializers
from main.filters import PostFilter

from _db.models.models import Post, PostImage, UserFavorites, Complaint, Promotion


class PostViewSet(ModelViewSet):
    """ CRUD operation for user`s posts """
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = Post.objects.all().order_by('-weight', '-created')
    serializer_class = post_serializers.PostSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PostFilter

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
        if request.user.subscribed or request.user.posts.count() < Post.LIMIT:
            return super().create(request, *args, **kwargs)
        return Response({'Error': 'You have reached limit. Please, delete another post or subscribe'},
                        status=status.HTTP_400_BAD_REQUEST)


class PostViewSetPublic(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
    """ Allow all users to see publications"""
    permission_classes = (AllowAny, )
    authentication_classes = []
    queryset = Post.objects.filter(rejected=False).order_by('-weight', '-created')
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
        return self.queryset.filter(user=self.request.user, post__rejected=False)

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


class ComplaintsAdmin(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      GenericViewSet):
    """
    Admin can get list of all complaints. Filter them by user and post.
    Admin can only perform this actions: 'list', 'retrieve', 'destroy'
    """
    permission_classes = (IsAuthenticated, IsAdminUser)
    queryset = Complaint.objects.all()
    serializer_class = post_serializers.ComplaintSerializer

    def get_queryset(self):
        if self.request.data.get('user'):
            return self.queryset.filter(user__pk=self.request.data.get('user'))
        if self.request.data.get('post'):
            return self.request.filter(post__pk=self.request.data.get('post'))
        return self.queryset


class PostModerationAdmin(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    """
    Admin can get list of posts with complains
    """
    permission_classes = (IsAuthenticated, IsAdminUser)
    queryset = Post.objects.annotate(comp_count=Count('complaints')).filter(comp_count__gt=0)
    # Filter only posts with complaints
    serializer_class = post_serializers.PostSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return self.serializer_class
        if self.action in ('update', ):
            return post_serializers.RejectPostSerializer
        return self.serializer_class


class LikeAndDislikePost(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, format=None):
        post = get_object_or_404(Post, pk=pk)
        action = None
        if request.user in post.likers.all():
            action = 'like'
        if request.user in post.dislikers.all():
            action = 'dislike'
        return Response({'post': post.pk,
                         'user': request.user.pk,
                         'action': action if action else ''})

    def patch(self, request, pk, format=None):
        post = get_object_or_404(Post, pk=pk)
        action = request.data.get('action')
        if action == 'like':
            # If user disliked post before, but now he liked it - we have to remove him from dislikers list
            if request.user in post.dislikers.all():
                post.dislikers.remove(request.user)
                post.likes += 1
                post.weight += 1
            # If user liked post before, but now he wants to remove like - we have to remove him from likers list
            if request.user in post.likers.all():
                post.likers.remove(request.user)
                post.likes -= 1
                post.weight -= 1
            else:
                # Add user to likers list and increment post likes counter
                post.likers.add(request.user)
                post.likes += 1
                post.weight += 1
        else:
            # If user liked post before, but now he disliked it - we have to remove him from likers list
            if request.user in post.likers.all():
                post.likers.remove(request.user)
                post.likes -= 1
                post.weight -= 1
            # If user disliked post before, but now he wants to remove dislike - we have to remove from dislikers list
            if request.user in post.dislikers.all():
                post.dislikers.remove(request.user)
                post.likes += 1
                post.weight += 1
            else:
                # if user dislike post - add him to dislikers list and decrement likes counter
                post.dislikers.add(request.user)
                post.likes -= 1
                post.weight -= 1
        post.save()
        return Response({'post': post.pk,
                         'user': request.user.pk,
                         'action': action}, status=status.HTTP_200_OK)


class PromotionViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.DestroyModelMixin,
                       GenericViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Promotion.objects.all()
    serializer_class = post_serializers.PromotionSerializer

    def perform_destroy(self, instance):
        post = instance.post
        weight = instance.type.efficiency
        super().perform_destroy(instance)
        post.weight -= weight
        post.save()

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return post_serializers.PromotionUpdateSerializer
        else:
            return self.serializer_class
