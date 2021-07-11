from django.urls import path, include

from main.views import user_views

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('users', user_views.UserViewSet)


app_name = 'main'


urlpatterns = [
    path('', include(router.urls)),
    path('users/<str:uid>/subscription/', user_views.UpdateSubscription.as_view(), name='update_subscription'),
    path('users/<str:uid>/contact/', user_views.ContactAPI.as_view(), name='add_contact'),
    path('users/<int:pk>/delete_contact/', user_views.ContactAPI.as_view(), name='delete_contact'),
    path('users/<int:pk>/change_ban ned_status/', user_views.ContactAPI.as_view(), name='change_banned_status'),
    path('users/<str:role>/get_contacts_by_role/', user_views.ContactAPI.as_view(), name='get_user_contacts'),
]
