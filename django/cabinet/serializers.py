from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()


class BotListSerializer(serializers.ModelSerializer):
    # date_in = serializers.DatetimeField(format="%d.%m.%Y %H:%M")
    class Meta:
        model = Bot
        fields = ('id', 'name', 'is_active', 'podpiska_do', 'status', 'date_in', )


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

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super(BotCreateSerializer, self).create(validated_data)


class BotUpdateSerializer(serializers.ModelSerializer):
    # date_in = serializers.DatetimeField(format="%d.%m.%Y %H:%M")
    class Meta:
        model = Bot
        fields = ('data', 'is_active', )
