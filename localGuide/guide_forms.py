from django import forms

from .models import UserProfile


class GuideAvailabilityForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('service_area', 'is_available')
