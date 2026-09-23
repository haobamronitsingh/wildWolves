from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'autocomplete': 'username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )


class RegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=False)
    bio = forms.CharField(max_length=500, required=False, widget=forms.Textarea)
    profile_picture = forms.ImageField(required=False)
    known_language = forms.ChoiceField(choices=UserProfile.LANGUAGE_CHOICES)
    occupation = forms.ChoiceField(choices=UserProfile.OCCUPATION_CHOICES)
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    service_area = forms.CharField(max_length=120, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            self.save_profile(user)
        return user

    def save_profile(self, user):
        return UserProfile.objects.create(
            user=user,
            phone_number=self.cleaned_data['phone_number'],
            bio=self.cleaned_data['bio'],
            profile_picture=self.cleaned_data.get('profile_picture'),
            known_language=self.cleaned_data['known_language'],
            occupation=self.cleaned_data['occupation'],
            birth_date=self.cleaned_data['birth_date'],
            service_area=self.cleaned_data['service_area'],
        )
