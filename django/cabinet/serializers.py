from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()


class BotListSerializer(serializers.ModelSerializer):
    # date_in = serializers.DatetimeField(format="%d.%m.%Y %H:%M")
    class Meta:
        model = Bot
        fields = ('id', 'name', 'is_active', 'podpiska_do', 'data', 'status', 'date_in', )


class BotUserSerializer(serializers.ModelSerializer):
    # date_in = serializers.DatetimeField(format="%d.%m.%Y %H:%M")
    class Meta:
        model = BotUser
        fields = ('id', 'first_name', 'last_name', 'username', 'chat_id', 'date_in', )


class BotDetailSerializer(serializers.ModelSerializer):
    # date_in = serializers.DatetimeField(format="%d.%m.%Y %H:%M")
    class Meta:
        model = Bot
        fields = ('id', 'name', 'data', 'is_active', 'podpiska_do', 'status', 'date_in', )


class BotCreateSerializer(serializers.ModelSerializer):
    # date_in = serializers.DatetimeField(format="%d.%m.%Y %H:%M")
    id = serializers.ReadOnlyField()
    class Meta:
        model = Bot
        fields = ('id', 'name', )

    # def create(self, validated_data):
    #     validated_data['user'] = self.context['request'].user
    #     return super(BotCreateSerializer, self).create(validated_data)


class BotUpdateSerializer(serializers.ModelSerializer):
    # date_in = serializers.DatetimeField(format="%d.%m.%Y %H:%M")
    class Meta:
        model = Bot
        fields = ('data', 'is_active', )


class CompaignListSerializer(serializers.ModelSerializer):
    # date_in = serializers.DatetimeField(format="%d.%m.%Y %H:%M")
    status = serializers.CharField(source='get_status_display')
    class Meta:
        model = Compaign
        fields = ('id', 'text', 'photo', 'video', 'status', 'date_in', )


class CompaignCreateSerializer(serializers.ModelSerializer):
    # date_in = serializers.DatetimeField(format="%d.%m.%Y %H:%M")
    status = serializers.CharField(source='get_status_display')
    id = serializers.ReadOnlyField()
    class Meta:
        model = Compaign
        fields = ('id', 'bot', 'text', 'status', 'date_in', )
