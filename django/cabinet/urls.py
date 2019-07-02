from django.urls import path, re_path, include

from .views import *
from accounts.views import *

from rest_framework_simplejwt import views as jwt_views

urlpatterns = [

    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),

    re_path('api/ch_pass/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', ChangePassword.as_view()),
    path('api/register/', RegisterUser.as_view(), name='register-user'),

    path('api/bot_list/', BotListCreateView.as_view(), name='bot-list'),

    path('api/bot_data/<int:pk>/', RetrieveUpdateBotView.as_view(), name='bot-data'),

    path('api/upload_photo/<int:bot_id>/', UploadPhoto.as_view(), name='upload-photo'),
    path('api/upload_file/<int:bot_id>/', UploadFile.as_view(), name='upload-file'),

    path('api/set_webhook/<int:pk>/', SetWebhookView.as_view(), name='set-webhook'),

    re_path(r'^', IndexCabinetView.as_view, name='index-view'),

    # path('get_bot_list/', get_bot_list, name='get_bot_list'),
    #
    # path('bot/<int:bot_id>/upload_photo/', upload_photo, name='upload_photo'),
    # path('bot/<int:bot_id>/upload_file/', upload_file, name='upload_file'),
    #
    # path('api/create_bot/', create_bot, name='create_bot'),
    # path('api/edit_name/<int:bot_id>/', edit_name, name='edit_name'),
    # path('api/bots_list/', get_bot_list, name='get_bot_list'),
    # path('api/bot_data/<int:bot_id>/', bot_api_data, name='bot_api_data'),
    # path('api/bot_start_text/<int:bot_id>/', bot_start_text, name='bot_start_text'),
    # path('api/bot_data/<int:bot_id>/upload_photo', upload_photo, name='upload_photo'),
    # path('api/bot_data/<int:bot_id>/users/<int:page>', get_bot_users, name='bot_users'),
    # path('api/bot_data/<int:bot_id>/orders/<int:page>', get_bot_orders, name='bot_orders'),
    # path('api/bot_data/<int:bot_id>/get_qr_code', get_qr_code, name='get_qr_code'),
    # path('api/bot_data/<int:bot_id>/compaign', compaign, name='compaign'),
    # path('api/get_bot_statistic/<int:bot_id>/', get_bot_statistic, name='get_bot_statistic'),
    #
    # path('api/bot_data/<int:bot_id>/notify', notify, name='notify'),
    # path('api/bot_data/<int:bot_id>/integration', get_integration, name='integration'),
    # path('api/bot_data/<int:bot_id>/amo', edit_amo, name='edit_amo'),
    # path('api/bot_data/<int:bot_id>/b24', edit_b24, name='edit_b24'),
    #
    # path('api/bot_data/<int:bot_id>/compaign/<int:compaign_id>', compaign_edit, name='compaign_edit'),
    # path('api/bot_data/<int:bot_id>/compaign_list/<int:page>', compaign_list, name='compaign_list'),
    #
    # path('api/bot_data/<int:bot_id>/export_users', export_users, name='export_users'),
    # path('api/bot_data/<int:bot_id>/export_orders', export_orders, name='export_orders'),
    #
    # path('api/bot_data/faq/', get_faq, name='get_faq'),
    #
    # path('logout/', logout_view, name="logout"),
    #
    # re_path(r'^', bots_view, name='bots')
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

