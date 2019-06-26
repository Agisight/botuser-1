from django.urls import path, re_path

from .views import *

urlpatterns = [

    # path('create_bot/', create_bot, name='create_bot'),
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




