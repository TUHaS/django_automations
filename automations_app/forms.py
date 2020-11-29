from django.contrib.auth.forms import AuthenticationForm, UsernameField, \
    UserCreationForm
from django import forms

from .models import User


class UserAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={'autofocus': True,
                                      'placeholder': 'Username'}),
        label=''
    )
    password = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password',
                                          'placeholder': 'Password'}),
    )


class UserRegistrationForm(UserCreationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={'autofocus': True,
                                      'placeholder': 'Username'}),
        label=''
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'First name'}),
        label=''
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Last name'}),
        label=''
    )
    password1 = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'placeholder': 'Password'}),
    )
    password2 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'placeholder': 'Password confirmation'}),
        strip=False,
    )
    field_order = ['username', 'first_name', 'last_name', 'password1',
                   'password2']
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user