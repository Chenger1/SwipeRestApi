from django.urls import path, include

from main.views import user_views
from main.views import house_views

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('users/', user_views.UserViewSet)
router.register('users/notary/admin-access/', user_views.NotaryUsersApi, basename='users_notary_admin')

router.register('houses/', house_views.HouseViewSet, basename='houses')
router.register('houses/buildings/', house_views.BuildingViewSet, basename='buildings')
router.register('houses/sections/', house_views.SectionViewSet, basename='sections'),
router.register('houses/floors/', house_views.FloorViewSet, basename='floors')


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
]
