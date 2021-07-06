from django.urls import path

from user_auth.views import LoginView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login_view')
]
