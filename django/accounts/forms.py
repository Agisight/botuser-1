from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountCreationForm(forms.ModelForm):
    ''' Форма регистрации пользователей, наследованная от нативной без поля username '''

    def __init__( self, *args, **kwargs ) :
        super( AccountCreationForm, self ).__init__( *args, **kwargs )
        for field in self.fields :
           self.fields[field].widget.attrs['class'] = 'form-control'

    password1 = forms.CharField( label = 'Password', widget = forms.PasswordInput )
    password2 = forms.CharField( label = 'Password confirmation', widget = forms.PasswordInput )

    class Meta :
        model = User
        fields = ('email',)

    def clean_password2 ( self ) :
        # Check that the two password entries match
        password1 = self.cleaned_data.get( "password1" )
        password2 = self.cleaned_data.get( "password2" )
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError( "Пароли не совпадают" )
        return password2

    def save(self, commit = True) :
        # Save the provided password in hashed format
        user = super( AccountCreationForm, self ).save( commit = False )
        user.set_password( self.cleaned_data[ "password1" ] )
        if commit:
            user.save()
        return user



class AccountChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"{}\">this form</a>."
        ),
    )

    class Meta:
        model = User
        fields = ( 'email', 'password', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].help_text = self.fields['password'].help_text.format('../password/')
        f = self.fields.get('user_permissions')
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password ( self ) :
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial[ "password" ]
