from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()

class UserRegisterSerializer(serializers.Serializer):

    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
    password2 = serializers.CharField(max_length=255)

    def validate_email(self, email):

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Пользователь с таким email зарегистрирован!")
        return email

    def validate_password(self, email):

        if len(email) < 8:
            raise serializers.ValidationError("Минимальная длинна пароля 8 символов!")
        return email

    def validate(self, data):

        if data['password'] != data['password2']:
            raise serializers.ValidationError("Пароли не совпадают!")
        return data

    # class Meta:
    #     model = User
    #     fields = ('email', 'password', 'password2', )
    #     validators = []

    def create(self, validated_data):

        return User.objects.create(email=validated_data['email'], password=validated_data['password'])


# class UserLoginSerializer(serializers.ModelSerializer):
#
#     def validate(self):
#         if self.password != self.password2:
#             raise serializers.ValidationError("Пароли не совпадают!")
#
#     class Meta:
#         model = User
#         fields = ('email', 'password', )
