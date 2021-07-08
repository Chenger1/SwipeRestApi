from django.urls import path, include

from main.views import user_views

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('users', user_views.UserViewSet)


app_name = 'main'


urlpatterns = [
    path('', include(router.urls)),
]
