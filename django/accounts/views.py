from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

# from math import floor
from django.contrib import messages as Messages

from django.utils.translation import ugettext as _
from django.utils.translation import activate
# from django.db.models import Count, Min, Sum, Avg

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
# Create your views here.

from .forms import *
from django.contrib.auth.forms import AuthenticationForm
from django_hosts.resolvers import reverse
from datetime import datetime, timedelta
from .models import  *
from rest_framework.response import Response

import os
import sys

import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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

from .serializers import *

import logging
logging.basicConfig(filename="./log.txt", level=logging.ERROR)


class RegisterUser(APIView):
    # permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    #@csrf_exempt
    def post(self, request):
        # {"email": "qwe@ua.fm", "password": "1111", "password2": "1112"}
        try:

            data = json.loads(request.body)

            print(data)

            serializer = UserRegisterSerializer(data=data)
            # user = UserRegisterSerializer(email="qwe@ua.fm", password="1111", password2="1112")

            if not serializer.is_valid():
                errors = []
                for error in serializer.errors:
                    for er in serializer.errors[error]:
                        errors.append(str(er))
                        print(er)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            resp = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            # return Response(serializer.data)
            return Response(resp)

        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("sys.exc_info() : ", sys.exc_info())
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(str(e))
            logging.error("RegisterUser {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
            resp = {"error": "Some error"}
            return HttpResponse(json.dumps(resp), content_type="application/json", status=400)


class ForgotPassword(APIView):
    # permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    #@csrf_exempt
    def post(self, request):

        if request.user.is_authenticated:
            return redirect('index_view')

        try:

            data = json.loads(request.body)
            email = data["email"].lower()

            try:
                user = User.objects.get(username=email)
            except Exception as e:
                user = None

            if user:
                link = 'http://inbot24.ru/change_password/' + urlsafe_base64_encode(force_bytes(user.pk)).decode("utf-8") \
                       + '/' + default_token_generator.make_token(user)

                r = requests.post("https://api.mailgun.net/v3/mail.inbot24.ru/messages",
                                  auth=("api", "e58cc2074156d23ba5af680252cfb3dc-2b778fc3-9aff387d"),
                                  data={"from": "INBOT24.RU <info@mail.inbot24.ru>", "to": [email],
                                        "subject": "Восстановление пароля", "text": "Перейдите по ссылке: %s" % link})
                print(r.text)

            data = {"status": "OK"}
            return Response(data)

            # else:
            #     data = {"error": "Пользователь с таким email не зарегистрирован."}
            #     return Response(data, status=400)


        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("sys.exc_info() : ", sys.exc_info())
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(str(e))
            logging.error("ForgotPassword {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

            data = {"status": "error"}
            return Response(data, status=400)


class ChangePassword(APIView):
    # permission_classes = (IsAuthenticated,)
    http_method_names = ['get' ,'post']

    def get(self, request, uidb64, token):

        if request.user.is_authenticated:
            return redirect('index_view')

        try:

            try:
                uid = force_text(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):

                data = {"status": "OK"}
                return Response(data)

            else:
                data = {"error": "Ссылка неправильная или ее срок действия истек."}
                return Response(data, status=400)


        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("sys.exc_info() : ", sys.exc_info())
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(str(e))
            logging.error("ChangePassword get {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

            data = {"status": "error"}
            return Response(data, status=400)

    #@csrf_exempt
    def post(self, request, uidb64, token):

        if request.user.is_authenticated:
            return redirect('index_view')

        try:

            try:
                uid = force_text(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):

                data = json.loads(request.body)
                password = data["password"]
                password2 = data["password2"]

                if password != password2:
                    resp = {"error": "Пароли не совпадают"}
                    return HttpResponse(json.dumps(resp), content_type="application/json", status=400)

                user.set_password(password)
                user.save()

                data = {"status": "OK"}
                return Response(data)

            else:
                data = {"error": "Ссылка неправильная или ее срок действия истек."}
                return Response(data, status=400)

        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("sys.exc_info() : ", sys.exc_info())
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(str(e))
            logging.error("ChangePassword post {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

            data = {"status": "error"}
            return Response(data, status=400)
