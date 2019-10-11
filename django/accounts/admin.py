from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .forms import AccountCreationForm, AccountChangeForm

User = get_user_model()

class AccountAdmin(UserAdmin):
    # The forms to add and change user instances
    form = AccountChangeForm
    add_form = AccountCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'date_joined')
    list_filter = ()
    #list_filter = ( 'is_staff', 'is_superuser', 'is_active' )
    search_fields = ('email',)
    ordering = ('email',)

    # filter_horizontal = ('groups', 'user_permissions' )

    fieldsets = (
        #( None, {'fields': ('email', 'password')} ),
        ( None, {'fields': ('email',)} ),
        # ( 'Персональная информация', {'fields': ('first_name',)} ),
        # ( 'Permissions', {'fields': ('is_active',
        #                              'is_staff',
        #                              'is_superuser',
        #                              'groups',
        #                              'user_permissions' )} ),
        ( 'Important dates', {'fields': ('last_login',)}),
    )

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )

# Now register the new UserAdmin...
admin.site.register(User, AccountAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
# admin.site.unregister(Group)




# from django.contrib import admin
# from django.contrib.auth import get_user_model
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin
# from django.contrib.auth.models import Group as GroupBase
# from django.urls import reverse
# from django.utils.safestring import mark_safe
# from django.utils.translation import ugettext_lazy as _

# from .forms import UserChangeForm, UserCreationForm
# from .models import Profile, Group


# class ProfileInline(admin.StackedInline):
#     model = Profile
#     verbose_name_plural = 'Профиль'
#     can_delete = False


# @admin.register(get_user_model())
# class UserAdmin(BaseUserAdmin):
#     fieldsets = (
#         (None, {'fields': ('username', 'email', 'phone', 'password',)}),
#         (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
#         (_('Дополнительные парав доступа'), {'classes': ('collapse',),
#                             'fields': ('groups', 'user_permissions', )}),
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': (
#                 'username', 'email', 'phone', 'password1', 'password2',
#                 'is_active', 'is_staff', 'is_superuser'
#             ),
#         }),
#     )
#     list_display = ('full_name', 'date_joined', 'username', 'email', 'phone',
#                     'is_active', 'is_staff', 'is_superuser', 'books_link')
#     list_filter = ('is_superuser', 'groups', 'is_active', 'is_staff')

#     search_fields = ('profile__first_name', 'profile__last_name', 'email')
#     ordering = ('email',)
#     filter_horizontal = ()
#     form = UserChangeForm
#     add_form = UserCreationForm
#     inlines = [ProfileInline, ]

#     def full_name(self, object):
#         return object.full_name
#     full_name.short_description = _("ФИО")

#     def books_count(self, object):
#         return object.books.all().count()
#     books_count.short_description = _("Книги")

#     def books_link(self, obj):
#         link_tpl = '<a href="{}?authors__id__exact={}">{}</a> '
#         books_count = self.books_count(obj)
#         if books_count:
#             return mark_safe(
#                 link_tpl.format(
#                     reverse('admin:bookstore_book_changelist'),
#                     obj.id,
#                     self.books_count(obj)
#                 )
#             )
#         else:
#             return 0

#     books_link.short_description = _('Книги')
#     books_link.allow_tags = True


# @admin.register(Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     search_fields = ('first_name', 'last_name',)
#     list_display = ('user', 'first_name', 'last_name',)

#     def has_delete_permission(self, request, obj=None):
#         views = ('admin:accounts_user_changelist', 'admin:accounts_user_delete')
#         if request.resolver_match.view_name in views and request.user.is_superuser:
#             return True
#         else:
#             return False

#     def has_add_permission(self, request):
#         return False


# admin.site.unregister(GroupBase)


# @admin.register(Group)
# class GroupAdmin(GroupAdmin):
#     pass
