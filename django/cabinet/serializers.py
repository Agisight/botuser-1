from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()

class BotListSerializer(serializers.ModelSerializer):
    # date_in = serializers.DatetimeField(format="%d.%m.%Y %H:%M")
    class Meta:
        model = Bot
        fields = ('name', 'is_active', 'podpiska_do', 'status', 'date_in', )


class BotCreateSerializer(serializers.ModelSerializer):
    # date_in = serializers.DatetimeField(format="%d.%m.%Y %H:%M")
    class Meta:
        model = Bot
        fields = ('name', )

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super(BotCreateSerializer, self).create(validated_data)
        #return User.objects.create_user(email=validated_data['email'], password=validated_data['password'])


class BotUpdateSerializer(serializers.ModelSerializer):
    # date_in = serializers.DatetimeField(format="%d.%m.%Y %H:%M")
    class Meta:
        model = Bot
        fields = ('data', )
