from django.urls import path

from .views import *

app_name = 'accounts'

urlpatterns = [
    #path('login/', login_view, name='login'),

    #path('logout/', logout_view, name='logout'),

    path('api/register/', RegisterUser.as_view(), name='register-user'),
]
