from django.contrib.auth import get_user_model
from django.contrib.auth.models import (
    Group as GroupBase, AbstractBaseUser, BaseUserManager, PermissionsMixin, User
)
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):

        if not email:
            raise ValueError('Не указан email адрес')

        user = self.model(email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        '''  '''
        user = self.create_user(email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length = 255, unique = True)
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    is_staff = models.BooleanField(default=False, verbose_name="Сотрудник")
    date_joined = models.DateTimeField(auto_now_add=True, auto_now=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__ ( self ) :
        return self.email

    def get_full_name(self):
        return self.email

    @property
    def full_name(self):
        return self.get_full_name()


# class Group(GroupBase):
#     class Meta:
#         proxy = True
#         verbose_name = _('group')
#         verbose_name_plural = _('groups')


# class Profile(models.Model):
#     user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, verbose_name=_('username'))
#     first_name = models.CharField(_('first name'), max_length=100, blank=True, null=True)
#     last_name = models.CharField(_('last name'), max_length=100, blank=True, null=True)
#     vk = models.CharField(_('страница в ВК'), max_length=100, blank=True, null=True)
#     instagram = models.CharField(_('instagram'), max_length=100, blank=True, null=True)
#     personal_site = models.CharField(_('Персональный сайт'), max_length=100, blank=True, null=True)
#     avatar = models.ImageField(_('avatar'), upload_to='profile/%Y/%m/', blank=True, null=True)

#     @property
#     def full_name(self):
#         return "".join([self.first_name or "", " ", self.last_name or ""])

#     class Meta:
#         verbose_name = _('профиль')
#         verbose_name_plural = _('профили')

#     def __str__(self):
#         return str(self.user)

#     def has_avatar(self):
#         return bool(self.avatar)

#     def get_avatar(self):
#         return self.avatar.url if self.has_avatar() else static('img/user_default.png')


