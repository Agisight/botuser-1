from django.urls import path, re_path

from .views import *

app_name = 'accounts'

urlpatterns = [
    #path('login/', login_view, name='login'),

    #path('logout/', logout_view, name='logout'),

    re_path('api/ch_pass/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', ChangePassword.as_view()),

    path('api/register/', RegisterUser.as_view(), name='register-user'),
]
