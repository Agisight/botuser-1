from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import telebot
import json
import os, sys
from time import sleep, time
from datetime import datetime, timedelta
from . models import *
import random
import hashlib
import hmac
import requests
from django.shortcuts import get_object_or_404
from .forms import UploadFileForm
from django.shortcuts import render, redirect#, reverse
from django_hosts.resolvers import reverse
from django.contrib.auth import get_user_model

from .serializers import *

from django.contrib.auth import authenticate, login, logout
import xlwt
from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncMonth, TruncDay, TruncQuarter, ExtractWeek, ExtractDay, ExtractMonth, ExtractQuarter, ExtractYear
from django.template.defaultfilters import date as _date


import os
import sys

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view

from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.utils import six

from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes

from rest_framework_simplejwt.tokens import RefreshToken

from django.template.defaultfilters import date as _date
from django.core.paginator import Paginator
from django.db.models import Count, Min, Sum, Avg

from rest_framework import generics
from rest_framework import status

import logging
logging.basicConfig(filename="/botproject/log.txt", level=logging.ERROR)


User = get_user_model()

def is_digit(string):
    if string.isdigit():
       return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False

def isint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def random_id():
  rid = ''
  for x in range(8): rid += random.choice(string.ascii_letters + string.digits)
  return rid


# TODO
# add permission class bot contains user

#class UserBotList(generics.ListAPIView): #
class BotListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = Bot.objects.filter(user=request.user)
        serializer = BotListSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):

        self.serializer_class = BotCreateSerializer
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateBotView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Bot.objects.all()

    def get(self, request, *args, **kwargs):
        self.serializer_class = BotDetailSerializer
        queryset = Bot.objects.filter(user=request.user)
        super(RetrieveUpdateBotView, self).get(self, request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.serializer_class = BotUpdateSerializer
        queryset = Bot.objects.filter(user=request.user)
        super(RetrieveUpdateBotView, self).get(self, request, *args, **kwargs)

    # def update(self, request, id):
    #     instance = self.get_object(id)
    #     serializer = BotUpdateSerializer(instance, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetWebhookView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):

        bot = Bot.objects.get(id=id)

        # data = json.loads(request.body)

        if bot.token:

            bot = telebot.TeleBot(token=bot.token)

            try:

                res = bot.set_webhook(url=f"https://inbot24.ru/bot_webhook/{self.token}/",
                                      certificate=open('/ssl/webhook_cert.pem'))
                bot.last_log_set_webhook = json.dumps(res)

                if res:
                    bot.status = 'on'
                    bot.save()
                    return Response({"status": "OK"})

            except Exception as e:
                bot.last_log_set_webhook = str(e)

            bot.save()

        return Response({"status": "Error"}, status=status.HTTP_400_BAD_REQUEST)

# class BotList(APIView):
#
#     #permission_classes = (IsAuthenticated,)
#     http_method_names = ['post']
#
#     def post(self, request):
#
#         try:
#
#             print(request.user.is_authenticated)
#             print(request.user)
#             data = json.loads(request.body)
#
#             profile = None
#             if request.user.is_authenticated:
#                 profile = request.user.profile
#
#             print(data)
#
#             out_payment = data['haveCurrency'].lower()
#             in_payment = data['wantCurrency'].lower()
#             out_amount = float(data['have'])
#             in_amount = float(data['want'])
#             in_wallet = data['wallet']
#
#             obmen_type = f"{out_payment}_{in_payment}"
#
#             # margin = Margin.objects.get(obmen_type=obmen_type)
#
#             status, resp = validate_data(out_payment, in_payment, out_amount, in_amount, in_wallet)
#
#             if status == 400:
#                 return Response(resp, status=status)
#
#             settings = Settings.objects.all().first()
#
#             data = {"error": "some error"}
#             return Response(data, status=400)
#
#         except Exception as e:
#
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             print("sys.exc_info() : ", sys.exc_info())
#             fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#             print(exc_type, fname, exc_tb.tb_lineno)
#             print(str(e))
#             logging.error("CreateOrder {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#             data = {"error": "some error"}
#             return Response(data, status=400)




# def bots_view(request):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     return render(request, 'index_user.html', {})


#
# def get_user_activity(user):
#
#     count = MessageLog.objects.filter(bot_user=user,
#                                       in_or_out='out',
#                                       date_in__lte=user.date_in + timedelta(days=1)).count()
#
#     if count == 1:
#         return 'cold'
#     elif 1 < count < 5:
#         return 'active'
#     elif count >= 5:
#         return 'hot'
#     else:
#         return None
#
#
# def bots_view(request):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     return render(request, 'index_user.html', {})
#
#
# @csrf_exempt
# def create_bot(request):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.method != 'POST':
#         return HttpResponse(status=415)
#
#     try:
#
#         data = json.loads(request.body)
#
#         print(data)
#
#         name = data['name']
#         bot_phone = data['phone']
#
#         bot = Bot.objects.create(profile=request.user.profile,
#                                  name=name, bot_phone=bot_phone,
#                                  is_active=False, podpiska_do=datetime.today().date() - timedelta(days=1))
#
#         return JsonResponse({"id": bot.id, "name": name})
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("{} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return JsonResponse({"error": "some error"})
#
#
# @csrf_exempt
# def edit_name(request, bot_id):
#
#     if not request.user.is_authenticated:
#         return HttpResponse(status=403)
#
#     if request.method != 'POST':
#         return HttpResponse(status=415)
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         data = json.loads(request.body)
#
#         print(data)
#
#         name = data['name']
#
#         if not name:
#             return HttpResponse(status=400)
#
#         bot.name = name
#         bot.save()
#
#         return HttpResponse(status=200)
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("edit_name {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return HttpResponse(status=400)
#
#
# def get_bot_list(request):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.method != 'GET':
#         return HttpResponse(status=415)
#
#     try:
#
#         bots = Bot.objects.filter(profile=request.user.profile).order_by('-date_in')
#
#         bots_list = [] #[{"id": bot.pk, "name": bot.name} for bot in bots]
#
#         for bot in bots:
#
#             item = {}
#             item['id'] = bot.pk
#             item['name'] = bot.name
#             item['phone'] = bot.bot_phone
#             item['activity'] = bot.is_active
#             if bot.podpiska_do:
#                 podpiska_do = (bot.podpiska_do + timedelta(hours=3)).strftime('%d.%m.%Y')
#             else:
#                 podpiska_do = "-"
#             item['expired'] = podpiska_do
#
#             bots_list.append(item)
#
#         return HttpResponse(json.dumps(bots_list), content_type="application/json")
#
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("get_bot_list {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#         return JsonResponse({"error": "some error"})
#
#
# @csrf_exempt
# def bot_start_text(request, bot_id):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         if request.method == 'GET':
#
#             resp = {"text_start": bot.text_start}
#
#             return HttpResponse(json.dumps(resp), content_type="application/json")
#
#         elif request.method == 'POST':
#
#             data = json.loads(request.body)
#
#             bot.text_start = data['text_start']
#             bot.save()
#
#             return HttpResponse("OK")
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("bot_start_text {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return JsonResponse({"error": "some error"})
#
#
# @csrf_exempt
# def bot_api_data(request, bot_id):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         if request.method == 'GET':
#
#             if not bot.data:
#                 return HttpResponse('[]', content_type="application/json")
#
#             data = bot.data
#
#             return HttpResponse(json.dumps(data), content_type="application/json")
#
#         elif request.method == 'POST':
#
#             data = json.loads(request.body)
#
#             bot.data = data
#
#             bot.save()
#
#             return HttpResponse("OK")
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("bot_api_data {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return JsonResponse({"error": "some error"})
#
#
# def handle_uploaded_file(f, bot_id):
#     f_path = f"/media/upload_photos/{bot_id}/{int(time() * 100000000)}.img"
#     with open(f_path, 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)
#     return f_path
#
#
# def get_bot_users(request, bot_id, page):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.method != 'GET':
#         return HttpResponse(status=415)
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         count_on_page = 20
#
#         group = request.GET.get('group')
#
#         if group:
#             list_group = group.split(',')
#             if 'all' in list_group:
#                 users = BotUser.objects.filter(bot=bot).order_by('-date_in')
#             else:
#                 #users = BotUser.objects.filter(bot=bot, activity__in=list_group).order_by('-date_in')[(page - 1) * count_on_page: page * count_on_page]
#                 users = [user for user in BotUser.objects.filter(bot=bot).order_by('-date_in') if user.activity in list_group]
#         else:
#             users = BotUser.objects.filter(bot=bot).order_by('-date_in')
#
#         pages = len(users) // count_on_page + 1 # .count()
#
#         users_list = {"pages": pages, "data": []}
#
#         if not users:
#             return HttpResponse(json.dumps(users_list), content_type="application/json")
#
#         for user in users[(page - 1) * count_on_page: page * count_on_page]:
#
#             item = {}
#             item['name'] = user.name
#             item['phone'] = user.phone
#             item['date'] = (user.date_in + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
#             item['activity'] = [user.activity] #get_user_activity(user)
#
#             users_list["data"].append(item)
#
#         return HttpResponse(json.dumps(users_list), content_type="application/json")
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("get_bot_users {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return JsonResponse({"error": "some error"})
#
#
# def get_bot_orders(request, bot_id, page):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.method != 'GET':
#         return HttpResponse(status=415)
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         count_on_page = 20
#
#         orders = Order.objects.filter(bot=bot).order_by('-date_in')
#
#         pages = orders.count() // count_on_page + 1
#
#         orders_list = {}
#         orders_list['data'] = []
#         orders_list['pages'] = pages
#         orders_list['email'] = bot.email_notify or ''
#         orders_list['tg'] = bot.tg_notify or ''
#
#         if not orders:
#             return HttpResponse(json.dumps(orders_list), content_type="application/json")
#
#         print((page - 1) * count_on_page, page * count_on_page)
#
#         for order in orders[(page - 1) * count_on_page: page * count_on_page]:
#
#             item = {}
#             item['name'] = order.bot_user.name
#             item['phone'] = order.bot_user.phone
#             item['text'] = order.text
#             item['date'] = (order.date_in + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
#
#             orders_list['data'].append(item)
#
#         return HttpResponse(json.dumps(orders_list), content_type="application/json")
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("get_bot_orders {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return JsonResponse({"error": "some error"})


#@csrf_exempt
def upload_photo(request, bot_id):

    if not request.user.is_authenticated:
        return redirect(reverse('accounts:login', host='www'))

    if request.user.is_superuser:
        logout(request)
        return redirect(reverse('accounts:login', host='www'))

    try:

        if request.method != 'POST':
            return HttpResponse(status=415)

        f = request.FILES['image']

        image_bot_path = f"./media/upload_photos/{bot_id}"

        if not os.path.exists(image_bot_path):
            os.makedirs(image_bot_path)

        f_name = f"{int(time() * 100000000)}_{str(f)}"

        f_path = f"{image_bot_path}/{f_name}"

        with open(f_path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        response = {"url": f"https://inbot24.ru/media/upload_photos/{bot_id}/{f_name}"}

        return JsonResponse(response)

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("upload_photo {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

        return HttpResponse("some error")


#@csrf_exempt
def upload_file(request, bot_id):

    if not request.user.is_authenticated:
        return redirect(reverse('accounts:login', host='www'))

    if request.user.is_superuser:
        logout(request)
        return redirect(reverse('accounts:login', host='www'))

    try:

        if request.method != 'POST':
            return HttpResponse(status=415)

        f = request.FILES['file']

        image_bot_path = f"./media/upload_files/{bot_id}"

        if not os.path.exists(image_bot_path):
            os.makedirs(image_bot_path)

        f_name = f"{int(time() * 100000000)}_{str(f)}"

        f_path = f"{image_bot_path}/{f_name}"

        with open(f_path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        response = {"url": f"https://inbot24.ru/media/upload_files/{bot_id}/{f_name}"}

        return JsonResponse(response)

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("upload_files {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

        return HttpResponse("some error")


# def get_qr_code(request, bot_id):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.method != 'GET':
#         return HttpResponse(status=415)
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         #print(bot)
#
#         resp = {}
#
#         if not bot.api_url or not bot.api_key:
#
#             #print(bot.api_url, bot.api_key)
#
#             resp['status'] = 'init'
#             resp['desc'] = "Инициализация..."
#             resp['qrCode'] = None
#
#             return HttpResponse(json.dumps(resp), content_type="application/json")
#
#         url = f"{bot.api_url}/status?token={bot.api_key}"
#
#         r = requests.get(url)
#
#         data = json.loads(r.text)
#
#         #print(data)
#
#         if data['accountStatus'] == 'init':
#             resp['status'] = 'init'
#             resp['desc'] = "Инициализация..."
#             resp['qrCode'] = None
#         elif data['accountStatus'] == 'loading':
#             resp['status'] = 'loading'
#             resp['desc'] = "Загрузка, повторите через 30 секунд"
#             resp['qrCode'] = None
#         elif data['accountStatus'] == 'got qr code':
#             resp['status'] = 'got qr code'
#             resp['desc'] = "Eсть QR код и нужно его сфотографировать в приложении Whatsapp перейдя в Меню > WhatsApp Web > Добавить. QR код действителен в течении одной минуты."
#             resp['qrCode'] = data['qrCode']
#         elif data['accountStatus'] == 'authenticated':
#             resp['status'] = 'authenticated'
#             resp['desc'] = "Авторизация пройдена успешно"
#             resp['qrCode'] = None
#
#
#
#         #resp['qrCode'] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAYAAACtWK6eAAAMA0lEQVR4Xu2dQXIcRwwEl/9/9PqgcPhCTiomDaFHm75CBVQXUI3epSV+vd/v96v/UiAFvlXgK4M0GSnwswIZpOlIgQsFMkjjkQIZpBlIgXsKtEHu6RbqQxTIIB/S6I55T4EMck+3UB+iQAb5kEZ3zHsKZJB7uoX6EAUyyIc0umPeUyCD3NMt1IcokEE+pNEd854CGeSebqE+RIEM8iGN7pj3FMgg93QL9SEKaIN8fX391VLRX5eh80/jrfjE3+bfxpP+xC+DgEIkMA3YNJ4aTHHiT/jT46Q/8c8gGYRm5NHxDDLcPhKYbuBpvD0+8bf5t/GkP/Frg7RBaEYeHc8gw+0jgekGnsbb4xN/m38bT/oTvzZIG4Rm5NHxDDLcPhKYbuBpvD0+8bf5t/GkP/Eb3yCWIB3AxmlALH/KT/xtfcpP/KbrEz+KT/PPIPCDTjsg1EAaAFuf8hO/6frEj+LT/DNIBrmcwQwiFZh2MN0gNj7Nn/ITf9keSv8iftP1kSD8gWn+bZA2SBvkQoEMkkEySAb5WYHxFS3/b+fpJ870+e0TivDT/NsgbZA2yMkbhG4AukEoTjcw1bd44jcdt/wt3p7P1ic88VvfIDSgdACKk0BU3+KJ33Tc8rd4ez5bn/DEL4PIJxYZjBowHacBIf4Wb89n6xOe+GWQDKI+g5DBaAApTgNO9QlP9TNIBskgfUif+5qXbjC6oabjdIMSf4u357P1CU/82iBtkDZIG6QN8pMCbZDrHdIGOXyD0BNhesBtfXrCUNzWJzzVzyAZpCdWT6znPrHoBmyDXP/LnqRfG+T9vtRgesCoARSnBk/zt/XpfBS39QlP9Xti9cTqidUTqydW32LRrvg+3gZpg7RB2iBtkDZIG+RbBehD2vSH3Htt+f9QTz//NH9SuifW4U8saiDFpweMLhjiR/Fp/lQ/g2SQPoP0GeS5n0HohqP49A3cBoEOkEC2QTQAFLf1LZ74Tcctf4u357P1CU/8emL1xOqJ1ROrJ1Zf89Ku6AeF3ypw+hPxXlv/Q9ET4/TzT/MnfdefWERwOm4HhPhRfsJTnAaI8MTP5qf6Nj7NP4PIzyDUYGog4SluB5j42fzE38an+WeQDKI+pNsBt/gMYhUE/LjA8h+vpuPbG376/MTfxqf5t0HaIG2Qk7/mtTeIxY/fQG0Q26JL/Hj/3nJHTxMcVff1Gv8VZKSPPZ9s3/j57fkIT/pqfTLI8F/6b4PQjKv44w2iTn8AmG4g26DT8Qe0QFGg/lHy8Q/pROD0OAl8+oBb/qf3h/jR+QmfQUAhEjiD0Ijtxql/xC6DZBCakUfHM8hw+0jgNshwA2R66h+lb4O0QWhGHh3PIMPtI4HbIMMNkOmpf5S+DdIGoRl5dHzdII9W7wHkaUPREeyAUP6/Pa43yN8u0Pb5MshuBzLIrv5YPYOgRKN/IIOMyuuTZxCvocmQQYx6fwCbQf6AyBclMsiu/lg9g6BEo38gg4zK65NnEK+hyZBBjHp/AJtB/oDIk08s20B7fPs9P/Gn/NN4qw/h6XyEp/MTnuLEj+oTnurrDUIEiYCNawHkP9pA5yd+hLf6EJ74EX6aP/Gj+oTH803/lVsiYONagAyiWkADqpK/Xi/qL9UnPPFrg2QQmpHLOA2oSp5BrHx8w1AFajDdQNN44m/jdD7KT+cnPMWJH9UnPNVvg7RBaEbaIEYhcrDJ/TtYfUNkkN+R+cc/M91/6i/VJzwdvg2SQWhG2iBGIetgwhtuv4PVN8yyweiMpC+dn/BUfztO5yN+4xuECG43gPihgBmEJFqN6/5O/xyECGaQ3X/69PT+WHfR+Sh/G+T9Jo3UG5waRBcE4Ym8zU94qr8d1/q1QTLI1RBnEGkxEpDSE376BiJ+VJ/4U36L3+ZH9bfjpD/x64nVE0s9IWnAtuMZRHZAC9i3WLIDs3Dd3+3PILPy8G+Qovpa4OVfoGOfcKfjx/uXQa4lziDua+hpg2UQUgDi1CBKn0EyiPqekwbQDhgNMMWJH+Etf1vf8qP6dL7T8VYfwq9/i0UEbZwaTPlpgAhv61N+4kf1n463+hA+g4BCNEAocB/SLyUifcngpD/lJ3wGySCXCtCA0gBO42nAiR/hM0gGySAXCmiDoAOHnxhUn+J0w9gbkOpT/On1LX+LJ30pnkHgfzVZb5D8ST0NAMXt+bfxdD6KZ5AM8ugnFr0AyAAUzyAZJIP0GeRnBegGsk8EuqEo/vT6lr/Fk74Ub4O0QdogbZA2CN2UP8XtDb6Nv3vuf3FtkDZIG2Rzg1gHWzzdYDa/xdvPQFTf5rd4y4/w1F/ij/nt3wehAttxEnCbHzXQ8rf5LZ70pfyEJ310/gxCLZiNUwNpAIidzW/xlh/hSR/ij/kzCEk0G6cG0gAQO5vf4i0/wpM+xB/zZxCSaDZODaQBIHY2v8VbfoQnfYg/5s8gJNFsnBpIA0DsbH6Lt/wIT/oQf8yfQUii2Tg1kAaA2Nn8Fm/5EZ70If6YP4OQRLNxaiANALGz+S3e8iM86UP8Mf/fbhASwMapQZSfGmjz2/qEJ350Psq/HR//Sfr2Aafr04BQfRogm9/WJzzxo/NR/u14BpEdoAGh9DRANr+tT3jiR+ej/NvxDCI7QANC6WmAbH5bn/DEj85H+bfjGUR2gAaE0tMA2fy2PuGJH52P8m/HM4jsAA0IpacBsvltfcITPzof5d+OZxDZARoQSk8DZPPb+oQnfnQ+yr8dzyCyAzQglJ4GyOa39QlP/Oh8lH87rg1CAm0f0NbfbjDpa/nZ/BZv+zONzyCgsB1A28DpAbT5Ld7qM43PIBnkUgG6IDIIDBAJNO3w6fw0INP1SV/Lz+a3+Gn9bP42SBukDXKhQAbJIBkkg9xftPYJc7/yL+T0E8bmt3irzzS+DdIGaYNsbpDtG5humOkbcDs/nd/2h85H9W3c8qf64xtk+gB0QIpTgy3/7fx0/unzUX0bt/ypfgYZ/gU1GYRG0MUziNMP0dsDbBtM/EmA7frEj+KWP+Vvg7RBaEYu49agqvjr9cogVkHAU4NtA7bzk3zT56P6Nm75U/02SBuEZqQNYhSaviENt9/BTvPfzk8a2BuYzkf1bdzyp/rrG2RaYBKQ6hOeBJ6OT/On/HQ+0o/yT+OJfwYZfmJRA2zcDhjVp/yEnx5w4kf1iX8GySCjnzFoQO2AW3wGOfx3EFKDKD4+IHCBEL8MIm9gajA1gOLTDaL603HSj85P/Cg/4ak+5Z/GE/+eWNLgJPB03A4Y8aP8hJ8ecOJH9Yl/BskgfQa5UCCDZJAMkkF+VsCu6E/H0xPl6fE2iNwgGeTpFrjmn0EyyOWE2A+5T7dPBskgGaTPIH0G+UkB+0R8+oYg/m2QNkgbpA3SBmmD0K74Pt4GaYO0Qdogexvk3r31HJT9luv0z0BtkOEN8pxRv8c0g4Bu9gYg/L22/YeiBlJ9i7f8T8eTPsTf6k/5bbwN0gZRM5RB2iCXCtANqKbvAeAMkkEyyIUCGSSDZJAMcn+X0xODbhjC32f2C2nrW7zlfzqe9CH+1H+bn+pTfP1DOhGcjtsGnY63+tGA0vmpPuUnPNXX+d8ywzRBEsjGLf/T8VYfGg86P9Wn/ISn+jp/Bvm67AEJbBs0jacBo7g9v81PeKsf5s8gGeRqSDIIKTD8LRY5eDpub6DT8VY/Gg86P9Wn/ISn+jp/G6QN0gb5WYG+xRr+X03oBrM3IOHpBqa45W/zE57OT/wxfxukDdIGWdwg5NDT43QD0Q1G57P5Ld7yI/y0PlTfxsefWJbgNn57AGnAtvlRf4g/4el8hLfxDAIKUoOmB4Dyb/OjAST+hKfzEd7GM0gGuVTADmgGkb9gxTp8Gk8DMj0AlH+bH+lP/AlP5yO8jbdB2iBtkAsFMkgGySAZ5P6ipRU//YSg/Nv8SFniT3g6H+FtXG8QSyB8CpysQAY5uTtxW1cgg6y3IAInK5BBTu5O3NYVyCDrLYjAyQpkkJO7E7d1BTLIegsicLICGeTk7sRtXYEMst6CCJysQAY5uTtxW1cgg6y3IAInK5BBTu5O3NYVyCDrLYjAyQpkkJO7E7d1BTLIegsicLICGeTk7sRtXYF/AIBz5mymquLyAAAAAElFTkSuQmCC"
#
#         return HttpResponse(json.dumps(resp), content_type="application/json")
#
#     except Exception as e:
#         print(e)
#         return JsonResponse({"error": "some error"})
#
#
#
#
#     # user = request.user
#     #
#     # base64_str = request.POST.get('data')
#     #
#     # header, data = base64_str.split(';base64,')
#     #
#     # from base64 import b64decode
#     # image_data = b64decode(data)
#     #
#     # with open(filename, 'wb') as f:
#     #     f.write(imgdata)
#
#     # from django.core.files.base import ContentFile
#     # user.profile.photo = ContentFile(image_data, 'whatup.png')
#     # user.profile.photo_moderated = True
#     # user.profile.save()
#
#     #response = {"path": "/media/upload_photos/1.img"}
#
#     #return JsonResponse(response)
#     #HttpResponse(json.dumps(response, ensure_ascii="False"), content_type="application/json; encoding=utf-8")
#
#
# @csrf_exempt
# def compaign(request, bot_id):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.method not in ['POST']:
#         return HttpResponse(status=415)
#
#     try:
#
#         if request.method == 'POST':
#
#             bot = get_object_or_404(Bot, pk=bot_id)
#
#             if bot.profile.user != request.user:
#                 return HttpResponse(status=404)
#
#             print(request.POST)
#             print(request.FILES)
#
#             text = request.POST.get('text')
#             if not text:
#                 text = None
#
#             try:
#                 delay = int(request.POST.get('delay'))
#             except Exception as e:
#                 delay = None
#
#             activity = request.POST.get('clientType')
#
#             next_step = request.POST.get('redirect')
#             if next_step == 'none':
#                 next_step = None
#
#             try:
#                 max_mes_per_hour = int(request.POST.get('quantity'))
#             except Exception as e:
#                 max_mes_per_hour = None
#
#             try:
#                 from_date_signup = datetime.strptime(request.POST.get('fromDate'), '%Y-%m-%d')
#             except Exception as e:
#                 from_date_signup = None
#
#             try:
#                 to_date_signup = datetime.strptime(request.POST.get('toDate'), '%Y-%m-%d') + timedelta(hours=23, minutes=59, seconds=59)
#             except Exception as e:
#                 to_date_signup = None
#
#             file_url = None
#             full_file_url = None
#
#             if 'file' in request.FILES:
#
#                 f = request.FILES['file']
#
#                 image_bot_path = f"./media/upload_compaign/{bot_id}"
#
#                 if not os.path.exists(image_bot_path):
#                     os.makedirs(image_bot_path)
#
#                 f_name = f"{int(time() * 100000000)}_{str(f)}"
#
#                 f_path = f"{image_bot_path}/{f_name}"
#
#                 with open(f_path, 'wb+') as destination:
#                     for chunk in f.chunks():
#                         destination.write(chunk)
#
#                 file_url = f"/upload_compaign/{bot_id}/{f_name}"
#                 full_file_url = f"https://www.whatsbot.online/media{file_url}"
#
#             date_in = datetime.today()
#
#             compaign = Compaign.objects.create(bot=bot,
#                                                text=text,
#                                                delay=delay,
#                                                file=file_url,
#                                                status='created',
#                                                activity=activity,
#                                                next_step=next_step,
#                                                max_mes_per_hour=max_mes_per_hour,
#                                                from_date_signup=from_date_signup,
#                                                to_date_signup=to_date_signup,
#                                                date_in=date_in)
#
#             if text:
#                 if len(text) > 100:
#                     text = text[:100] + " ..."
#
#             return JsonResponse({"id": compaign.id,
#                                  "date": (date_in + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
#                                  "text": text,
#                                  "delay": delay,
#                                  "url": full_file_url,
#                                  "redirect": next_step,
#                                  "quantity": max_mes_per_hour,
#                                  "clientType": activity,
#                                  "fromDate": request.POST.get('fromDate'), #(from_date_signup + timedelta(hours=3)).strftime('%Y-%m-%d'),
#                                  "toDate": request.POST.get('toDate'), #(to_date_signup + timedelta(hours=3)).strftime('%Y-%m-%d'),
#                                  "status": "Создана"})
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("create_compaign {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return JsonResponse({"error": "some error"})
#
#
# def get_integration(request, bot_id):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.method != 'GET':
#         return HttpResponse(status=415)
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         response = {}
#         response['amo'] = {}
#         response['amo']['amo_domain'] = bot.amo_domen or ''
#         response['amo']['amo_user_email'] = bot.amo_user_email or ''
#         response['amo']['amo_user_hash'] = bot.amo_user_hash or ''
#
#         response['b24'] = {}
#         response['b24']['b24_domain'] = bot.b24_domen or ''
#         response['b24']['b24_client_id'] = bot.b24_client_id or ''
#         response['b24']['b24_client_secret'] = bot.b24_client_secret or ''
#         response['b24']['b24_access_token'] = bot.b24_access_token or ''
#         response['b24']['b24_refresh_token'] = bot.b24_refresh_token or ''
#
#         return JsonResponse(response)
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("get_integration {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return HttpResponse(status=400)
#
#
# @csrf_exempt
# def edit_amo(request, bot_id):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.method != 'POST':
#         return HttpResponse(status=415)
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         data = json.loads(request.body)
#
#         print(data)
#
#         amo_domen = data['amo_domain']
#         amo_user_email = data['amo_user_email']
#         amo_user_hash = data['amo_user_hash']
#
#         bot.amo_domen = amo_domen
#         bot.amo_user_email = amo_user_email
#         bot.amo_user_hash = amo_user_hash
#         bot.save()
#
#         return HttpResponse(status=200)
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("edit_amo {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return HttpResponse(status=400)
#
#
# @csrf_exempt
# def edit_b24(request, bot_id):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.method != 'POST':
#         return HttpResponse(status=415)
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         data = json.loads(request.body)
#
#         print(data)
#
#         b24_domen = data['b24_domain']
#         b24_client_id = data['b24_client_id']
#         b24_client_secret = data['b24_client_secret']
#         b24_access_token = data['b24_access_token']
#         b24_refresh_token = data['b24_refresh_token']
#
#         bot.b24_domen = b24_domen
#         bot.b24_client_id = b24_client_id
#         bot.b24_client_secret = b24_client_secret
#         bot.b24_access_token = b24_access_token
#         bot.b24_refresh_token = b24_refresh_token
#         bot.save()
#
#         return HttpResponse(status=200)
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("edit_b24 {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return HttpResponse(status=400)
#
#
# @csrf_exempt
# def notify(request, bot_id):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.method != 'POST':
#         return HttpResponse(status=415)
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         data = json.loads(request.body)
#
#         print(data)
#
#         email_notify = data['email']
#         tg_notify = data['tg']
#
#         bot.email_notify = email_notify
#         bot.tg_notify = tg_notify
#         bot.save()
#
#         return HttpResponse(status=200)
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("notify {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return HttpResponse(status=400)
#
#
# @csrf_exempt
# def compaign_edit(request, bot_id, compaign_id):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.method not in ['POST', 'DELETE']:
#         return HttpResponse(status=415)
#
#     bot = get_object_or_404(Bot, pk=bot_id)
#
#     if bot.profile.user != request.user:
#         return HttpResponse(status=404)
#
#     try:
#
#         if request.method == 'POST':
#
#             compaign = Compaign.objects.get(bot=bot, id=compaign_id)
#
#             print(request.POST)
#             print(request.FILES)
#
#             text = request.POST.get('text')
#             if not text:
#                 text = None
#
#             try:
#                 delay = int(request.POST.get('delay'))
#             except Exception as e:
#                 delay = None
#
#             activity = request.POST.get('clientType')
#
#             next_step = request.POST.get('redirect')
#             if next_step == 'none':
#                 next_step = None
#
#             try:
#                 max_mes_per_hour = int(request.POST.get('quantity'))
#             except Exception as e:
#                 max_mes_per_hour = None
#
#             try:
#                 from_date_signup = datetime.strptime(request.POST.get('fromDate'), '%Y-%m-%d')
#             except Exception as e:
#                 from_date_signup = None
#
#             try:
#                 to_date_signup = datetime.strptime(request.POST.get('toDate'), '%Y-%m-%d') + timedelta(hours=23, minutes=59, seconds=59)
#             except Exception as e:
#                 to_date_signup = None
#
#             file_url = compaign.file
#
#             if 'file' in request.FILES:
#
#                 f = request.FILES['file']
#
#                 image_bot_path = f"./media/upload_compaign/{bot_id}"
#
#                 if not os.path.exists(image_bot_path):
#                     os.makedirs(image_bot_path)
#
#                 f_name = f"{int(time() * 100000000)}_{str(f)}"
#
#                 f_path = f"{image_bot_path}/{f_name}"
#
#                 with open(f_path, 'wb+') as destination:
#                     for chunk in f.chunks():
#                         destination.write(chunk)
#
#                 file_url = f"/upload_compaign/{bot_id}/{f_name}"
#                 full_file_url = f"https://www.whatsbot.online/media{file_url}"
#
#             if compaign.delay and not delay:
#                 compaign.is_done = True
#                 compaign.status = 'success'
#
#             compaign.text = text
#             compaign.delay = delay
#             compaign.activity = activity
#             compaign.next_step = next_step
#             compaign.max_mes_per_hour = max_mes_per_hour
#             compaign.from_date_signup = from_date_signup
#             compaign.to_date_signup = to_date_signup
#             compaign.file = file_url
#
#             compaign.save()
#
#             response = {}
#             if file_url:
#                 response["url"] = full_file_url
#             else:
#                 response["url"] = ""
#
#             return HttpResponse(json.dumps(response), content_type="application/json")
#
#         elif request.method == 'DELETE':
#
#             Compaign.objects.get(bot=bot, id=compaign_id).delete()
#
#             return HttpResponse(status=200)
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("create_compaign {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return JsonResponse({"error": "some error"})
#
#
# def compaign_list(request, bot_id, page):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.method != 'GET':
#         return HttpResponse(status=415)
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         count_on_page = 20
#
#         compaigns = Compaign.objects.filter(bot=bot).order_by('-date_in')
#
#         pages = compaigns.count() // count_on_page + 1
#
#         compaigns_list = {"pages": pages, "data": []} #[{"id": bot.pk, "name": bot.name} for bot in bots]
#
#         for compaign in compaigns[(page - 1) * count_on_page: page * count_on_page]:
#
#             item = {}
#             item['id'] = compaign.id
#             item['delay'] = compaign.delay or ''
#             item['clientType'] = compaign.activity or ''
#             item['redirect'] = compaign.next_step or ''
#             item['quantity'] = compaign.max_mes_per_hour or ''
#             item['fromDate'] = ''
#             if compaign.from_date_signup:
#                 item['fromDate'] = compaign.from_date_signup.strftime('%Y-%m-%d')
#             item['toDate'] = ''
#             if compaign.to_date_signup:
#                 item['toDate'] = compaign.to_date_signup.strftime('%Y-%m-%d')
#
#             item['date'] = compaign.date_in.strftime('%Y-%m-%d %H:%M:%S')
#             if compaign.file:
#                 item['url'] = f"https://www.whatsbot.online/media{compaign.file}"
#             else:
#                 item['url'] = ''
#             if compaign.text:
#                 if len(compaign.text) > 100:
#                     item['text'] = compaign.text[:100] + " ..."
#                 else:
#                     item['text'] = compaign.text
#             else:
#                 item['text'] = ''
#
#             if compaign.status == "created":
#                 item['status'] = "Создана"
#             elif compaign.status == "in_progress":
#                 item['status'] = "Выполняется"
#             elif compaign.status == "success":
#                 item['status'] = "Успешно"
#             elif compaign.status == "error":
#                 item['status'] = "Ошибка"
#
#             compaigns_list["data"].append(item)
#
#             print(compaigns_list)
#
#         return HttpResponse(json.dumps(compaigns_list), content_type="application/json")
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("get_bot_list {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return JsonResponse({"error": "some error"})
#
#
# def export_users(request, bot_id):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         response = HttpResponse(content_type='application/ms-excel')
#         response['Content-Disposition'] = f'attachment; filename="users_{(datetime.today() + timedelta(hours=3)).strftime("%d_%m_%Y")}.xls"'
#
#         wb = xlwt.Workbook(encoding='utf-8')
#         ws = wb.add_sheet('Users')
#
#         # Sheet header, first row
#         row_num = 0
#
#         font_style = xlwt.XFStyle()
#         font_style.font.bold = True
#
#         columns = ['name', 'phone', 'date_added']
#
#         for col_num in range(len(columns)):
#             ws.write(row_num, col_num, columns[col_num], font_style)
#
#         # Sheet body, remaining rows
#         font_style = xlwt.XFStyle()
#
#         users = BotUser.objects.filter(bot=bot)
#
#         for user in users:
#             row_num += 1
#
#             ws.write(row_num, 0, user.name, font_style)
#             ws.write(row_num, 1, user.phone, font_style)
#             ws.write(row_num, 2, (user.date_in + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M'), font_style)
#
#         wb.save(response)
#         return response
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("export_users {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return JsonResponse({"error": "some error"})
#
#
# def export_orders(request, bot_id):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         response = HttpResponse(content_type='application/ms-excel')
#         response['Content-Disposition'] = f'attachment; filename="orders_{(datetime.today() + timedelta(hours=3)).strftime("%d_%m_%Y")}.xls"'
#
#         wb = xlwt.Workbook(encoding='utf-8')
#         ws = wb.add_sheet('Users')
#
#         # Sheet header, first row
#         row_num = 0
#
#         font_style = xlwt.XFStyle()
#         font_style.font.bold = True
#
#         columns = ['name', 'phone', 'order', 'date_added']
#
#         for col_num in range(len(columns)):
#             ws.write(row_num, col_num, columns[col_num], font_style)
#
#         # Sheet body, remaining rows
#         font_style = xlwt.XFStyle()
#
#         orders = Order.objects.filter(bot=bot)
#
#         for order in orders:
#             row_num += 1
#
#             ws.write(row_num, 0, order.bot_user.name, font_style)
#             ws.write(row_num, 1, order.bot_user.phone, font_style)
#             ws.write(row_num, 2, order.text, font_style)
#             ws.write(row_num, 3, (order.date_in + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M'), font_style)
#
#         wb.save(response)
#         return response
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("export_orders {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return JsonResponse({"error": "some error"})
#
#
# def logout_view(request):
#     logout(request)
#     return redirect(reverse('accounts:login', host='www'))
#
#
# def get_bot_statistic(request, bot_id):
#
#     if request.method != 'GET':
#         return HttpResponse(status=415)
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     try:
#
#         bot = get_object_or_404(Bot, pk=bot_id)
#
#         if bot.profile.user != request.user:
#             return HttpResponse(status=404)
#
#         print(request.GET)
#
#         #data = json.loads(request.body)
#
#         aggregate = request.GET.get('period')
#
#         #s1 = "2.2.2019"
#         #s2 = "13.4.2019"
#
#         d1 = datetime.strptime(request.GET.get('from'), '%d.%m.%Y')
#         d2 = datetime.strptime(request.GET.get('to'), '%d.%m.%Y') + timedelta(hours=23, minutes=59, seconds=59)
#
#         resp = {}
#
#         users = BotUser.objects.filter(bot=bot, date_in__range=[d1, d2])
#         orders = Order.objects.filter(bot=bot, date_in__range=[d1, d2])
#         messages = MessageLog.objects.filter(bot=bot, in_or_out='out', date_in__range=[d1, d2])
#
#         resp['orders'] = orders.count()
#         resp['clients'] = users.count()
#
#         resp['charts'] = {}
#
#         if aggregate == 'day':
#
#             users_dynamic = users.\
#                 annotate(year=ExtractYear('date_in')).\
#                 annotate(month=ExtractMonth('date_in')).\
#                 annotate(day=ExtractDay('date_in')).\
#                 values('year', 'month', 'day').\
#                 annotate(count_users=Count('id')).\
#                 values('year', 'month', 'day', 'count_users').order_by('year', 'month', 'day')
#
#             orders_dynamic = orders.\
#                 annotate(year=ExtractYear('date_in')).\
#                 annotate(month=ExtractMonth('date_in')).\
#                 annotate(day=ExtractDay('date_in')).\
#                 values('year', 'month', 'day').\
#                 annotate(count_orders=Count('id')).\
#                 values('year', 'month', 'day', 'count_orders').order_by('year', 'month', 'day')
#
#             messages_dynamic = messages.\
#                 annotate(year=ExtractYear('date_in')).\
#                 annotate(month=ExtractMonth('date_in')).\
#                 annotate(day=ExtractDay('date_in')).\
#                 values('year', 'month', 'day').\
#                 annotate(count_mes=Count('id')).\
#                 values('year', 'month', 'day', 'count_mes').order_by('year', 'month', 'day')
#
#             clients = {}
#             clients['data'] = []
#             clients['labels'] = []
#
#             if len(users_dynamic) == 1:
#
#                 clients['data'].append(None)
#                 clients['data'].append(users_dynamic[0]['count_users'])
#                 clients['data'].append(None)
#
#                 clients['labels'].append("")
#                 row = users_dynamic[0]
#                 clients['labels'].append(_date(datetime(row['year'], row['month'], row['day']), "d M"))
#                 clients['labels'].append("")
#
#             else:
#
#                 for row in users_dynamic:
#                     clients['data'].append(row['count_users'])
#                     clients['labels'].append(_date(datetime(row['year'], row['month'], row['day']), "d M"))
#
#             resp['charts']['clients'] = clients
#
#             orders = {}
#             orders['data'] = []
#             orders['labels'] = []
#
#             if len(orders_dynamic) == 1:
#
#                 orders['data'].append(None)
#                 orders['data'].append(orders_dynamic[0]['count_orders'])
#                 orders['data'].append(None)
#
#                 orders['labels'].append("")
#                 row = orders_dynamic[0]
#                 orders['labels'].append(_date(datetime(row['year'], row['month'], row['day']), "d M"))
#                 orders['labels'].append("")
#
#             else:
#
#                 for row in orders_dynamic:
#                     orders['data'].append(row['count_orders'])
#                     orders['labels'].append(_date(datetime(row['year'], row['month'], row['day']), "d M"))
#
#             resp['charts']['orders'] = orders
#
#             traffic = {}
#             traffic['data'] = []
#             traffic['labels'] = []
#
#             if len(messages_dynamic) == 1:
#
#                 traffic['data'].append(None)
#                 traffic['data'].append(messages_dynamic[0]['count_mes'])
#                 traffic['data'].append(None)
#
#                 traffic['labels'].append("")
#                 row = messages_dynamic[0]
#                 traffic['labels'].append(_date(datetime(row['year'], row['month'], row['day']), "d M"))
#                 traffic['labels'].append("")
#
#             else:
#
#                 for row in messages_dynamic:
#                     traffic['data'].append(row['count_mes'])
#                     traffic['labels'].append(_date(datetime(row['year'], row['month'], row['day']), "d M"))
#
#
#             resp['charts']['traffic'] = traffic
#
#         elif aggregate == 'week':
#
#             # https://stackoverflow.com/questions/17087314/get-date-from-week-number
#
#             users_dynamic = users.\
#                 annotate(year=ExtractYear('date_in')).\
#                 annotate(week=ExtractWeek('date_in')).\
#                 values('year', 'week').\
#                 annotate(count_users=Count('id')).\
#                 values('year', 'week', 'count_users').order_by('year', 'week')
#
#             orders_dynamic = orders.\
#                 annotate(year=ExtractYear('date_in')).\
#                 annotate(week=ExtractWeek('date_in')).\
#                 values('year', 'week').\
#                 annotate(count_orders=Count('id')).\
#                 values('year', 'week', 'count_orders').order_by('year', 'week')
#
#             messages_dynamic = messages.\
#                 annotate(year=ExtractYear('date_in')).\
#                 annotate(week=ExtractWeek('date_in')).\
#                 values('year', 'week').\
#                 annotate(count_mes=Count('id')).\
#                 values('year', 'week', 'count_mes').order_by('year', 'week')
#
#             clients = {}
#             clients['data'] = []
#             clients['labels'] = []
#
#             if len(users_dynamic) == 1:
#
#                 clients['data'].append(None)
#                 clients['data'].append(users_dynamic[0]['count_users'])
#                 clients['data'].append(None)
#
#                 clients['labels'].append("")
#                 clients['labels'].append(users_dynamic[0]['week'])
#                 clients['labels'].append("")
#
#             else:
#
#                 for row in users_dynamic:
#                     clients['data'].append(row['count_users'])
#                     clients['labels'].append(str(row['week']))
#
#             resp['charts']['clients'] = clients
#
#             orders = {}
#             orders['data'] = []
#             orders['labels'] = []
#
#             if len(orders_dynamic) == 1:
#
#                 orders['data'].append(None)
#                 orders['data'].append(orders_dynamic[0]['count_orders'])
#                 orders['data'].append(None)
#
#                 orders['labels'].append("")
#                 orders['labels'].append(orders_dynamic[0]['week'])
#                 orders['labels'].append("")
#
#             else:
#
#                 for row in orders_dynamic:
#                     orders['data'].append(row['count_orders'])
#                     orders['labels'].append(str(row['week']))
#
#             resp['charts']['orders'] = orders
#
#             traffic = {}
#             traffic['data'] = []
#             traffic['labels'] = []
#
#             if len(messages_dynamic) == 1:
#
#                 traffic['data'].append(None)
#                 traffic['data'].append(messages_dynamic[0]['count_mes'])
#                 traffic['data'].append(None)
#
#                 traffic['labels'].append("")
#                 traffic['labels'].append(messages_dynamic[0]['week'])
#                 traffic['labels'].append("")
#
#             else:
#
#                 for row in messages_dynamic:
#                     traffic['data'].append(row['count_mes'])
#                     traffic['labels'].append(str(row['week']))
#
#             resp['charts']['traffic'] = traffic
#
#         elif aggregate == 'month':
#
#             users_dynamic = users.\
#                 annotate(year=ExtractYear('date_in')).\
#                 annotate(month=ExtractMonth('date_in')).\
#                 values('year', 'month').\
#                 annotate(count_users=Count('id')).\
#                 values('year', 'month', 'count_users').order_by('year', 'month')
#
#             orders_dynamic = orders.\
#                 annotate(year=ExtractYear('date_in')).\
#                 annotate(month=ExtractMonth('date_in')).\
#                 values('year', 'month').\
#                 annotate(count_orders=Count('id')).\
#                 values('year', 'month', 'count_orders').order_by('year', 'month')
#
#             messages_dynamic = messages.\
#                 annotate(year=ExtractYear('date_in')).\
#                 annotate(month=ExtractMonth('date_in')).\
#                 values('year', 'month').\
#                 annotate(count_mes=Count('id')).\
#                 values('year', 'month', 'count_mes').order_by('year', 'month')
#
#             clients = {}
#             clients['data'] = []
#             clients['labels'] = []
#
#             if len(users_dynamic) == 1:
#
#                 clients['data'].append(None)
#                 clients['data'].append(users_dynamic[0]['count_users'])
#                 clients['data'].append(None)
#
#                 clients['labels'].append("")
#                 row = users_dynamic[0]
#                 clients['labels'].append(_date(datetime(row['year'], row['month'], 1), "M"))
#                 clients['labels'].append("")
#
#             else:
#
#                 for row in users_dynamic:
#                     clients['data'].append(row['count_users'])
#                     clients['labels'].append(_date(datetime(row['year'], row['month'], 1), "M"))
#
#             resp['charts']['clients'] = clients
#
#             orders = {}
#             orders['data'] = []
#             orders['labels'] = []
#
#             if len(orders_dynamic) == 1:
#
#                 orders['data'].append(None)
#                 orders['data'].append(orders_dynamic[0]['count_orders'])
#                 orders['data'].append(None)
#
#                 orders['labels'].append("")
#                 row = orders_dynamic[0]
#                 orders['labels'].append(_date(datetime(row['year'], row['month'], 1), "M"))
#                 orders['labels'].append("")
#
#             else:
#
#                 for row in orders_dynamic:
#                     orders['data'].append(row['count_orders'])
#                     orders['labels'].append(_date(datetime(row['year'], row['month'], 1), "M"))
#
#             resp['charts']['orders'] = orders
#
#             traffic = {}
#             traffic['data'] = []
#             traffic['labels'] = []
#
#             if len(messages_dynamic) == 1:
#
#                 traffic['data'].append(None)
#                 traffic['data'].append(messages_dynamic[0]['count_mes'])
#                 traffic['data'].append(None)
#
#                 traffic['labels'].append("")
#                 row = messages_dynamic[0]
#                 traffic['labels'].append(_date(datetime(row['year'], row['month'], 1), "M"))
#                 traffic['labels'].append("")
#
#             else:
#
#                 for row in messages_dynamic:
#                     traffic['data'].append(row['count_mes'])
#                     traffic['labels'].append(_date(datetime(row['year'], row['month'], 1), "M"))
#
#             resp['charts']['traffic'] = traffic
#
#         elif aggregate == 'quarter':
#
#             users_dynamic = users.\
#                 annotate(year=ExtractYear('date_in')).\
#                 annotate(quarter=ExtractQuarter('date_in')).\
#                 values('year', 'quarter').\
#                 annotate(count_users=Count('id')).\
#                 values('year', 'quarter', 'count_users').order_by('year', 'quarter')
#
#             orders_dynamic = orders.\
#                 annotate(year=ExtractYear('date_in')).\
#                 annotate(quarter=ExtractQuarter('date_in')).\
#                 values('year', 'quarter').\
#                 annotate(count_orders=Count('id')).\
#                 values('year', 'quarter', 'count_orders').order_by('year', 'quarter')
#
#             messages_dynamic = messages.\
#                 annotate(year=ExtractYear('date_in')).\
#                 annotate(quarter=ExtractQuarter('date_in')).\
#                 values('year', 'quarter').\
#                 annotate(count_mes=Count('id')).\
#                 values('year', 'quarter', 'count_mes').order_by('year', 'quarter')
#
#             clients = {}
#             clients['data'] = []
#             clients['labels'] = []
#
#             if len(users_dynamic) == 1:
#
#                 clients['data'].append(None)
#                 clients['data'].append(users_dynamic[0]['count_users'])
#                 clients['data'].append(None)
#
#                 clients['labels'].append("")
#                 clients['labels'].append(users_dynamic[0]['quarter'])
#                 clients['labels'].append("")
#
#             else:
#
#                 for row in users_dynamic:
#                     clients['data'].append(row['count_users'])
#                     clients['labels'].append(str(row['quarter']))
#
#             resp['charts']['clients'] = clients
#
#             orders = {}
#             orders['data'] = []
#             orders['labels'] = []
#
#             if len(orders_dynamic) == 1:
#
#                 orders['data'].append(None)
#                 orders['data'].append(orders_dynamic[0]['count_orders'])
#                 orders['data'].append(None)
#
#                 orders['labels'].append("")
#                 orders['labels'].append(orders_dynamic[0]['quarter'])
#                 orders['labels'].append("")
#
#             else:
#
#                 for row in orders_dynamic:
#                     orders['data'].append(row['count_orders'])
#                     orders['labels'].append(str(row['quarter']))
#
#             resp['charts']['orders'] = orders
#
#             traffic = {}
#             traffic['data'] = []
#             traffic['labels'] = []
#
#             if len(messages_dynamic) == 1:
#
#                 traffic['data'].append(None)
#                 traffic['data'].append(messages_dynamic[0]['count_mes'])
#                 traffic['data'].append(None)
#
#                 traffic['labels'].append("")
#                 traffic['labels'].append(messages_dynamic[0]['quarter'])
#                 traffic['labels'].append("")
#
#             else:
#
#                 for row in messages_dynamic:
#                     traffic['data'].append(row['count_mes'])
#                     traffic['labels'].append(str(row['quarter']))
#
#             resp['charts']['traffic'] = traffic
#
#         elif aggregate == 'year':
#
#             users_dynamic = users.\
#                 annotate(year=ExtractYear('date_in')).\
#                 values('year').\
#                 annotate(count_users=Count('id')).\
#                 values('year', 'count_users').order_by('year')
#
#             orders_dynamic = orders.\
#                 annotate(year=ExtractYear('date_in')).\
#                 values('year').\
#                 annotate(count_orders=Count('id')).\
#                 values('year', 'count_orders').order_by('year')
#
#             messages_dynamic = messages.\
#                 annotate(year=ExtractYear('date_in')).\
#                 values('year').\
#                 annotate(count_mes=Count('id')).\
#                 values('year', 'count_mes').order_by('year')
#
#             clients = {}
#             clients['data'] = []
#             clients['labels'] = []
#
#             if len(users_dynamic) == 1:
#
#                 clients['data'].append(None)
#                 clients['data'].append(users_dynamic[0]['count_users'])
#                 clients['data'].append(None)
#
#                 clients['labels'].append("")
#                 clients['labels'].append(users_dynamic[0]['year'])
#                 clients['labels'].append("")
#
#             else:
#
#                 for row in users_dynamic:
#                     clients['data'].append(row['count_users'])
#                     clients['labels'].append(str(row['year']))
#
#             resp['charts']['clients'] = clients
#
#             orders = {}
#             orders['data'] = []
#             orders['labels'] = []
#
#             if len(orders_dynamic) == 1:
#
#                 orders['data'].append(None)
#                 orders['data'].append(orders_dynamic[0]['count_orders'])
#                 orders['data'].append(None)
#
#                 orders['labels'].append("")
#                 orders['labels'].append(orders_dynamic[0]['year'])
#                 orders['labels'].append("")
#
#             else:
#
#                 for row in orders_dynamic:
#                     orders['data'].append(row['count_orders'])
#                     orders['labels'].append(str(row['year']))
#
#             resp['charts']['orders'] = orders
#
#             traffic = {}
#             traffic['data'] = []
#             traffic['labels'] = []
#
#             if len(messages_dynamic) == 1:
#
#                 traffic['data'].append(None)
#                 traffic['data'].append(messages_dynamic[0]['count_mes'])
#                 traffic['data'].append(None)
#
#                 traffic['labels'].append("")
#                 traffic['labels'].append(messages_dynamic[0]['year'])
#                 traffic['labels'].append("")
#
#             else:
#
#                 for row in messages_dynamic:
#                     traffic['data'].append(row['count_mes'])
#                     traffic['labels'].append(str(row['year']))
#
#             resp['charts']['traffic'] = traffic
#
#         return HttpResponse(json.dumps(resp), content_type="application/json")
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("get_bot_statistic {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return JsonResponse({"error": "some error"})
#
# @csrf_exempt
# def get_faq(request):
#
#     if not request.user.is_authenticated:
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.user.is_superuser:
#         logout(request)
#         return redirect(reverse('accounts:login', host='www'))
#
#     if request.method != 'POST':
#         return HttpResponse(status=415)
#
#     try:
#
#         print(request.POST)
#
#         #lang = request.POST.get('lang')
#
#         data = json.loads(request.body)
#         lang = data['lang']
#
#         resp = []
#
#         for fag in FAQ.objects.all().order_by('id'):
#
#             item = {}
#
#             if lang == "ru":
#                 item['question'] = fag.question_ru
#                 item['answer'] = fag.answer_ru
#             elif lang == "en":
#                 item['question'] = fag.question_en
#                 item['answer'] = fag.answer_en
#
#             resp.append(item)
#
#         return HttpResponse(json.dumps(resp), content_type="application/json")
#
#     except Exception as e:
#
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         # print("sys.exc_info() : ", sys.exc_info())
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#         logging.error("get_faq {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
#
#         return JsonResponse({"error": "some error"})
