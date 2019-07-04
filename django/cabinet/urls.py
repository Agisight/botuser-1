from django.urls import path, re_path, include

from .views import *
from accounts.views import *

from rest_framework_simplejwt import views as jwt_views

urlpatterns = [

    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),

    path('api/forgot_password/', ForgotPassword.as_view()),
    re_path('api/ch_pass/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', ChangePassword.as_view()),
    path('api/register/', RegisterUser.as_view(), name='register-user'),

    path('api/bot_list/', BotListCreateView.as_view(), name='bot-list'),

    path('api/bot_data/<int:pk>/', RetrieveUpdateBotView.as_view(), name='bot-data'),

    path('api/upload_photo/<int:bot_id>/', UploadPhoto.as_view(), name='upload-photo'),
    path('api/upload_file/<int:bot_id>/', UploadFile.as_view(), name='upload-file'),

    path('api/set_webhook/<int:bot_id>/', SetWebhookView.as_view(), name='set-webhook'),

    re_path(r'^', IndexCabinetView.as_view(), name='index-view'),

]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

