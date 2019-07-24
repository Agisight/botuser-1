from django.contrib import admin
from .models import *
from solo.admin import SingletonModelAdmin

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_active', 'podpiska_do', 'token', 'status', 'date_in',)


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('bot', 'chat_id', 'first_name', 'last_name', 'username', 'step', 'date_in')


@admin.register(Compaign)
class CompaignAdmin(admin.ModelAdmin):
    list_display = ('bot', 'text', 'status', 'date_in')


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('bot', 'bot_user', 'in_or_out', 'log', 'answer_out_mes_request', 'date_in')


@admin.register(Config)
class ConfigAdmin(SingletonModelAdmin):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('bot', 'subscription_id', 'date_in')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'transaction_id', 'amount', 'date_in')


# class BotUserAdmin(admin.ModelAdmin):
#     list_display = ('bot', 'chat_id', 'step', 'name', 'phone', 'date_in')
#     list_filter = ('bot', )
# admin.site.register(BotUser, BotUserAdmin)
#
#
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('bot', 'bot_user', 'text', 'date_in')
#     list_filter = ('bot', )
# admin.site.register(Order, OrderAdmin)
#
#
# class BotAdmin(admin.ModelAdmin):
#     readonly_fields = ('status_create_instance', 'log_create_instance', 'status_webhook', 'log_set_webhook', )
#     list_display = ('name', 'bot_phone', 'profile', 'is_active', 'podpiska_do', 'is_ready_to_use', 'create_instance', 'api_instance_id', 'api_key', 'api_url',
#                     'status_create_instance', 'log_create_instance', 'set_webhook', 'status_webhook', 'log_set_webhook', 'date_in', )
#
#     #list_editable = ('is_active', 'podpiska_do', 'is_ready_to_use', )
#
#     fieldsets = (
#         ('Пользователь/Доступы', {
#             'fields': ('profile', 'is_active', 'podpiska_do', 'is_ready_to_use', ),
#         }),
#         ('Установка инстанса', {
#             'classes': ('collapse',),
#             'description': 'Шаг1. Нужно создать инстанс, должно заполнится токен, url и cтатус Успешно!',
#             'fields': ('create_instance', 'api_instance_id', 'api_key', 'api_url', 'status_create_instance', 'log_create_instance')
#         }),
#         ('Установка вебхука', {
#             'classes': ('collapse',),
#             'description': 'Шаг2. Делать после Шаг1. Нужно подключить вебхук, должно быть cтатус Успешно!',
#             'fields': ('set_webhook', 'status_webhook', 'log_set_webhook')
#         }),
#         ('Информация о боте', {
#             'classes': ('extrapretty'),
#
#             'fields': ('name', 'bot_phone', 'data', 'tg_notify', 'email_notify',
#                        'amo_domen', 'amo_user_email', 'amo_user_hash',
#                        'b24_domen', 'b24_client_id', 'b24_client_secret', 'b24_access_token', 'b24_refresh_token')
#         }),
#     )
# admin.site.register(Bot, BotAdmin)
#
#
# class MessageLogAdmin(admin.ModelAdmin):
#     list_display = ('bot', 'bot_user', 'in_or_out', 'log', 'answer_whatsapp_api', 'date_in')
#     list_filter = ('bot', 'date_in',  'in_or_out', )
#     search_fields = ('log', 'bot_user__phone', )
# admin.site.register(MessageLog, MessageLogAdmin)
#
#
# class Compaigndmin(admin.ModelAdmin):
#     list_display = ('bot', 'text',  'file', 'status', 'delay', 'is_done', 'date_in')
#     list_filter = ('bot', 'status', 'is_done', )
# admin.site.register(Compaign, Compaigndmin)
#
#
# class FAQAdmin(TranslationAdmin):
#     pass
#
# admin.site.register(FAQ, FAQAdmin)
