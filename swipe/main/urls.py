from django.urls import path

from main.views import user_views


app_name = 'main'


urlpatterns = [
    path('user/<str:uid>/', user_views.UserDetail.as_view(), name='user_detail')
]
