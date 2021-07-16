from django.urls import path, include

from main.views import user_views
from main.views import house_views
from main.views import post_views

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('users', user_views.UserViewSet)
router.register('users/notary/admin-access', user_views.NotaryUsersApi, basename='users_notary_admin')

# HOUSE
router.register('houses', house_views.HouseViewSet, basename='houses')
router.register('buildings', house_views.BuildingViewSet, basename='buildings')
router.register('sections', house_views.SectionViewSet, basename='sections')
router.register('floors', house_views.FloorViewSet, basename='floors')
router.register('news', house_views.NewsItemViewSet, basename='news')
router.register('documents', house_views.DocumentViewSet, basename='documents')
router.register('flats', house_views.FlatViewSet, basename='flats')
router.register('requests', house_views.RequestToChestApi, basename='requests')

# POST
router.register('posts', post_views.PostViewSet, basename='posts')

# public routers
router.register('houses_public', house_views.HousePublic, basename='houses_public')
router.register('flats_public', house_views.FlatPublic, basename='flats_public')


app_name = 'main'


urlpatterns = [
    path('', include(router.urls)),
    path('users/<str:uid>/subscription/', user_views.UpdateSubscription.as_view(), name='update_subscription'),
    path('users/<str:uid>/change_ban_status/', user_views.ChangeBanStatus.as_view(), name='change_ban_status'),

    # CONTACT
    path('users/<str:uid>/contact/', user_views.ContactAPI.as_view(), name='add_contact'),
    path('users/<int:pk>/delete_contact/', user_views.ContactAPI.as_view(), name='delete_contact'),
    path('users/<int:pk>/change_banned_status/', user_views.ContactAPI.as_view(), name='change_banned_status'),
    path('users/<str:role>/get_contacts_by_role/', user_views.ContactAPI.as_view(), name='get_user_contacts'),

    # MESSAGE
    path('users/messages/<str:uid>/', user_views.MessageApi.as_view(), name='user_messages'),
    path('users/messages/edit/<int:pk>/', user_views.MessageApi.as_view(), name='edit_message'),
    path('users/message/attachment/', user_views.AttachmentApi.as_view(), name='attachments'),

    # HOUSE
    path('flats/<int:pk>/booking/', house_views.BookingFlat.as_view(), name='booking_flat'),
]
