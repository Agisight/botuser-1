from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
import json
import requests
from datetime import datetime, timedelta
import telebot

User = get_user_model()

def set_webhook(api_url, api_key, bot_id):

    url = f"{api_url}/webhook?token={api_key}"
    data = {"webhookUrl": f"https://app.whatsbot.online/bot_webhook/{bot_id}/"}

    try:
        r = requests.post(url, data=data)

        print(r.text)
        return True, json.loads(r.text)
    except Exception as e:
        return False, {"error": str(e)}


def create_instance():
    data = {"uid": "TYSCIMWbEqb0dmfaddXizq5kMdD2", "type": "whatsapp"}
    url = 'https://us-central1-app-chat-api-com.cloudfunctions.net/newInstance'

    try:
        r = requests.post(url, data=data)
        return True, json.loads(r.text)
    except Exception as e:
        return False, {"error": str(e)}

    # {"error":"not paid account already exists"}



class Bot(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)

    is_active = models.BooleanField(default=False)
    podpiska_do = models.DateField(auto_now_add=False, auto_now=False, null=True, blank=True)

    token = models.CharField(max_length=120, null=True, blank=True)
    set_webhook = models.BooleanField(default=False)
    status = models.CharField(max_length=120, null=True, blank=True, default='off', choices=(
        ('off', 'НЕ подключен'),
        ('on', 'Подключен'),
    ))
    last_log_set_webhook = models.TextField(null=True, blank=True)

    data = JSONField(null=True, blank=True)

    date_in = models.DateTimeField(auto_now_add=True, auto_now=False, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Бот'
        verbose_name_plural = 'Бот'

    def save(self, *args, **kwargs):

        if self.pk:

            self_in_db = Bot.objects.get(pk=self.pk)

            if self.set_webhook and not self_in_db.set_webhook:

                if self.token:

                    bot = telebot.TeleBot(token=self.token)
                    try:
                        res = bot.set_webhook(url=f"https://tgbot.inbot24.ru/bot_webhook/{self.token}/",
                                              certificate=open('/ssl/webhook_cert.pem'))
                        if res:
                            self.status = 'on'
                        self.last_log_set_webhook = json.dumps(res)
                    except Exception as e:
                        self.last_log_set_webhook = str(e)

                self.set_webhook = False

        super().save(*args, **kwargs)


class BotUser(models.Model):

    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)

    chat_id = models.BigIntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)

    step = models.CharField(max_length=255, null=True, blank=True)

    # variables = JSONField(null=True, blank=True)

    date_in = models.DateTimeField(auto_now_add=True, auto_now=False, null=True, blank=True)

    def __str__(self):
        return self.chat_id

    class Meta:
        verbose_name = 'TelegramBot User'
        verbose_name_plural = 'TelegramBot User'
        unique_together = ('bot', 'chat_id',)


# class Order(models.Model):
#
#     bot = models.ForeignKey(Bot, on_delete=models.CASCADE, null=True, blank=True)
#     bot_user = models.ForeignKey(BotUser, on_delete=models.CASCADE, null=True, blank=True)
#     text = models.TextField(null=True, blank=True)
#     date_in = models.DateTimeField(auto_now_add=True, auto_now=False, null=True, blank=True)
#
#     def __str__(self):
#         return 'Заказ'
#
#     class Meta:
#         verbose_name = 'Заказы'
#         verbose_name_plural = 'Заказы'


class Compaign(models.Model):

    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, null=True, blank=True)

    # compaign_type = models.CharField(max_length=120, null=True, blank=True, choices=(
    #     ('text', 'Текст'),
    #     ('photo', 'Фото'),
    #     ('photo+caption', 'Фото c подписью'),
    #     ('Файл', 'Файл')
    # ))

    text = models.TextField(null=True, blank=True)
    # photo = models.ImageField(null=True, blank=True)
    file = models.FileField(null=True, blank=True)

    status = models.CharField(max_length=120, null=True, blank=True, choices=(
        ('created', 'Создана'),
        ('in_progress', 'Выполняется'),
        ('success', 'Успешно'),
        ('error', 'Ошибка')
    ))

    date_in = models.DateTimeField(auto_now_add=True, auto_now=False, null=True, blank=True)

    is_done = models.BooleanField(default=False)

    def __str__(self):
        return 'Рассылка'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылка'


class MessageLog(models.Model):

    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, null=True, blank=True)

    bot_user = models.ForeignKey(BotUser, on_delete=models.CASCADE, null=True, blank=True)

    in_or_out = models.CharField(max_length=120, null=True, blank=True, choices=(
        ('in', 'Вебхуки'),
        ('out', 'Отправленные сообщения')
    ))

    log = models.TextField(null=True, blank=True)

    answer_out_mes_request = models.TextField(null=True, blank=True)

    date_in = models.DateTimeField(auto_now_add=True, auto_now=False, null=True, blank=True)

    def __str__(self):
        return 'Логи'

    class Meta:
        verbose_name = 'Логи'
        verbose_name_plural = 'Логи'

