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


class IndexCabinetView(TemplateView):
    template_name = "index.html"


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
