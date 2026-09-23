from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import TouristProfile


class TouristLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))


class TouristRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            TouristProfile.objects.create(user=user, phone_number=self.cleaned_data['phone_number'])
        return user
