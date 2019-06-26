from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()

class BotSerializer(serializers.ModelSerializer):
    # date_in = serializers.DatetimeField(format="%d.%m.%Y %H:%M")
    class Meta:
        model = Bot
        fields = ('name', 'is_active', 'podpiska_do', 'status', 'date_in', )
