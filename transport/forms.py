from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import LocalRoute, RentalInquiry, UserProfile


class StyledAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "field"


class RegisterForm(UserCreationForm):
    phone_number = forms.CharField(max_length=20, required=False, label="Phone (for ride contact)")

    class Meta:
        model = User
        fields = ("username", "email", "phone_number", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "field"

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            UserProfile.objects.update_or_create(
                user=user,
                defaults={"phone_number": self.cleaned_data.get("phone_number", "")},
            )
        return user


class LocalRouteForm(forms.ModelForm):
    class Meta:
        model = LocalRoute
        fields = (
            "mode",
            "name",
            "origin",
            "destination",
            "stops",
            "timetable",
            "fare_note",
            "notes",
            "is_active",
        )
        widgets = {
            "stops": forms.Textarea(attrs={"rows": 5, "placeholder": "One stop per line"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "field"


class RentalInquiryForm(forms.ModelForm):
    class Meta:
        model = RentalInquiry
        fields = ("days", "message")
        widgets = {"message": forms.TextInput(attrs={"placeholder": "Pickup time or notes (optional)"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "field"
