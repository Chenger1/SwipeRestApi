from django.urls import path, include

from main.views import user_views
from main.views import house_views
from main.views import post_views

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('users', user_views.UserViewSet, basename='users')
router.register('users/notary/admin-access', user_views.NotaryUsersApi, basename='users_notary_admin')
router.register('user_filters', user_views.UserFilterViewSet, basename='user_filters')

# HOUSE
router.register('houses', house_views.HouseViewSet, basename='houses')
router.register('buildings', house_views.BuildingViewSet, basename='buildings')
router.register('sections', house_views.SectionViewSet, basename='sections')
router.register('delete_standpipe', house_views.DeleteStandpipe, basename='delete_standpipes')
router.register('floors', house_views.FloorViewSet, basename='floors')
router.register('news', house_views.NewsItemViewSet, basename='news')
router.register('documents', house_views.DocumentViewSet, basename='documents')
router.register('flats', house_views.FlatViewSet, basename='flats')
router.register('requests', house_views.RequestToChestApi, basename='requests')

# POST
router.register('posts', post_views.PostViewSet, basename='posts')
router.register('post_images', post_views.PostImageViewSet, basename='post_images')
router.register('favorites_posts', post_views.UserFavoritesViewSet, basename='favorites_posts')
router.register('posts_moderation', post_views.PostModerationAdmin, basename='posts_moderation')
router.register('promotion', post_views.PromotionViewSet, basename='promotions')

# COMPLAINTS
router.register('complaints', post_views.ComplaintViewSet, basename='complaints')  # only for user who created them
router.register('complaints_admin', post_views.ComplaintsAdmin, basename='complaints_admin')
# Admin can see list of all complaints and filter them by post or user

# public routers
router.register('houses_public', house_views.HousePublic, basename='houses_public')
router.register('flats_public', house_views.FlatPublic, basename='flats_public')
router.register('posts_public', post_views.PostViewSetPublic, basename='posts_public')


app_name = 'main'


urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:pk>/subscription/', user_views.UpdateSubscription.as_view(), name='update_subscription'),
    path('users/<int:pk>/change_ban_status/', user_views.ChangeBanStatus.as_view(), name='change_ban_status'),

    # CONTACT
    path('users/<int:pk>/contact/', user_views.ContactAPI.as_view(), name='add_contact'),
    path('users/<int:pk>/delete_contact/', user_views.ContactAPI.as_view(), name='delete_contact'),
    path('users/<int:pk>/change_banned_status/', user_views.ContactAPI.as_view(), name='change_banned_status'),
    path('users/<str:role>/get_contacts_by_role/', user_views.ContactAPI.as_view(), name='get_user_contacts'),

    # MESSAGE
    path('users/messages/<int:pk>/', user_views.MessageApi.as_view(), name='user_messages'),
    path('users/messages/edit/<int:pk>/', user_views.MessageApi.as_view(), name='edit_message'),
    path('users/message/attachment/', user_views.AttachmentApi.as_view(), name='attachments'),
    path('users/message/attachment/<int:pk>/', user_views.AttachmentApi.as_view(), name='download_attachment'),

    # HOUSE
    path('flats/<int:pk>/booking/', house_views.BookingFlat.as_view(), name='booking_flat'),

    # POST
    path('like_dislike/<int:pk>/', post_views.LikeAndDislikePost.as_view(), name='like_dislike'),
]
