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
from rest_framework.pagination import PageNumberPagination

from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.utils import six

from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes

from rest_framework_simplejwt.tokens import RefreshToken

from django.template.defaultfilters import date as _date
from django.core.paginator import Paginator
from django.db.models import Count, Min, Sum, Avg

from django.views.generic.base import TemplateView

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


class StandartPagination(PageNumberPagination):
    page_size = 20


class IndexCabinetView(TemplateView):
    template_name = "index.html"

class TestView(TemplateView):
    template_name = "testpay.html"


class CloudpaymentsStatusView(APIView):

    # permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    def post(self, request):

        try:

            print(request.body)
            print(request.POST)

            data = json.loads(request.body)

            print(data)

            return Response({"status": "OK"})

        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("sys.exc_info() : ", sys.exc_info())
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(str(e))
            logging.error("UpdateKurs {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

            data = {"status": "error",
                    "description": "some error, pls contact support"}
            return Response(data)

# <QueryDict: {'TransactionId': ['174538442'], 'Amount': ['1.00'], 'Currency': ['RUB'], 'PaymentAmount': ['1.00'],
# 'PaymentCurrency': ['RUB'], 'OperationType': ['Payment'], 'InvoiceId': ['1234567'], 'AccountId': ['user@example.com'],
# 'SubscriptionId': ['sc_dc8c6cad671ab111b2dc28aa926a8'], 'Name': ['MOMENTUM R'], 'Email': ['orlan_mh94@mail.ru'],
# 'DateTime': ['2019-07-20 11:33:45'], 'IpAddress': ['162.243.37.65'], 'IpCountry': ['US'], 'IpCity': ['New York'],
# 'IpRegion': ['New York'], 'IpDistrict': ['New York'], 'IpLatitude': ['40.7143'], 'IpLongitude': ['-74.006'],
# 'CardFirstSix': ['533669'], 'CardLastFour': ['7481'], 'CardType': ['MasterCard'], 'CardExpDate': ['08/21'],
# 'Issuer': ['SBERBANK OF RUSSIA'], 'IssuerBankCountry': ['RU'], 'Description': ['Подписка на ежемесячный доступ к сайту example.com'],
# 'AuthCode': ['210686'], 'Token': ['537155323'], 'TestMode': ['0'], 'Status': ['Completed'], 'GatewayName': ['Tinkoff'],
# 'Data': ['{"cloudPayments":{"recurrent":{"interval":"Month","period":1,"customerReceipt":{"Items":[{"label":"Наименование товара 3",
# "price":300,"quantity":3,"amount":900,"vat":20,"method":0,"object":0}],"taxationSystem":0,"email":"user@example.com",
# "phone":"","isBso":false,"amounts":{"electronic":900,"advancePayment":0,"credit":0,"provision":0}}}}}'],
# 'TotalFee': ['0.04'], 'CardProduct': ['MCS']}>


class BotListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = Bot.objects.filter(user=request.user).order_by('id')
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

    def get(self, request, *args, **kwargs):
        self.serializer_class = BotDetailSerializer
        self.queryset = Bot.objects.filter(user=request.user)

        return super(RetrieveUpdateBotView, self).get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self.serializer_class = BotUpdateSerializer
        self.queryset = Bot.objects.filter(user=request.user)

        return super(RetrieveUpdateBotView, self).put(request, *args, **kwargs)


class SetWebhookView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, bot_id):

        try:

            bot = Bot.objects.get(id=bot_id)

            if bot.user.id != request.user.id:
                return Response(status=400)

            data = json.loads(request.body)
            token = data['token']

            tg_bot = telebot.TeleBot(token=token)

            res = tg_bot.set_webhook(url=f"https://tgbot.inbot24.ru/bot_webhook/{token}/",
                                     certificate=open('/ssl/webhook_cert.pem'))
            bot.last_log_set_webhook = json.dumps(res)

            if res:
                bot.status = 'on'
                bot.token = token
                bot.save()
                return Response({"status": "OK"})

        except Exception as e:
            bot.last_log_set_webhook = str(e)

        bot.save()

        return Response({"status": "Error"}, status=status.HTTP_400_BAD_REQUEST)


class UploadPhoto(APIView):
    # permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    def post(self, request, bot_id):

        try:

            bot = Bot.objects.get(id=bot_id)
            if bot.user.id != request.user.id:
                return Response(status=400)

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

            return Response(response)

        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("sys.exc_info() : ", sys.exc_info())
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("UploadPhoto {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
            data = {"status": "error"}
            return Response(data)


class UploadFile(APIView):
    # permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    def post(self, request, bot_id):

        try:

            bot = Bot.objects.get(id=bot_id)
            if bot.user.id != request.user.id:
                return Response(status=400)

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

            return Response(response)

        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("sys.exc_info() : ", sys.exc_info())
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error("UploadFile {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
            data = {"status": "error"}
            return Response(data)


class BotUserView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = StandartPagination

    def list(self, request, bot_id):
        try:

            bot = Bot.objects.get(id=bot_id)

            if bot.user.id != request.user.id:
                return Response({"status": "Error"}, status=status.HTTP_400_BAD_REQUEST)

            if not bot.podpiska_do:
                return Response(None)

            self.queryset = BotUser.objects.filter(bot=bot).order_by('id')
            self.serializer_class = BotUserSerializer

            return super().list(self, request)

        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("sys.exc_info() : ", sys.exc_info())
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(str(e))
            logging.error("BotUserView {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
            data = {"status": "error"}
            return Response(data)


class AnalyticsView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def get(self, request, bot_id):

        try:

            bot = Bot.objects.get(id=bot_id)

            if bot.user.id != request.user.id:
                return Response({"status": "Error"}, status=status.HTTP_400_BAD_REQUEST)

            if not bot.podpiska_do:
                return Response(None)

            all_users_count = BotUser.objects.filter(bot=bot).count()
            d = datetime.today()
            from_today_date = datetime(d.year, d.month, d.day)
            today_users_count = BotUser.objects.filter(bot=bot, date_in__gt=from_today_date).count()
            unsubscribe_users_count = BotUser.objects.filter(bot=bot, otpiska=True).count()

            resp = {"all_users_count": all_users_count,
                    "today_users_count": today_users_count,
                    "unsubscribe_users_count": unsubscribe_users_count}

            return Response(resp)

        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("sys.exc_info() : ", sys.exc_info())
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(str(e))
            logging.error("AnalyticsView {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
            data = {"status": "error"}
            return Response(data)


class CompaignListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = StandartPagination

    def list(self, request, bot_id):

        bot = Bot.objects.get(id=bot_id)

        if bot.user.id != request.user.id:
            return Response({"status": "Error"}, status=status.HTTP_400_BAD_REQUEST)

        if not bot.podpiska_do:
            return Response(None)

        # Note the use of `get_queryset()` instead of `self.queryset`
        self.queryset = Compaign.objects.filter(bot=bot).order_by('id')
        self.serializer_class = CompaignListSerializer

        return super().list(self, request)

    def create(self, request, bot_id):

        bot = Bot.objects.get(id=bot_id)

        if bot.user.id != request.user.id:
            return Response({"status": "Error"}, status=status.HTTP_400_BAD_REQUEST)

        if not bot.podpiska_do:
            return Response(None)

        self.serializer_class = CompaignCreateSerializer
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            serializer.save({"bot": bot})
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#
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
