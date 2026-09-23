from django import forms

from .models import AssistanceRequest


class AssistanceRequestForm(forms.ModelForm):
    package_hours = forms.TypedChoiceField(
        choices=AssistanceRequest.PACKAGE_CHOICES,
        coerce=int,
        empty_value=None,
        label='Guide package',
    )

    class Meta:
        model = AssistanceRequest
        fields = ('area', 'tourist_count', 'package_hours', 'details')
        widgets = {
            'area': forms.TextInput(attrs={'placeholder': 'For example, Imphal West'}),
            'tourist_count': forms.NumberInput(attrs={'min': 1}),
            'details': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell the guide what help you need.',
            }),
        }

    def save(self, commit=True):
        assistance_request = super().save(commit=False)
        assistance_request.package_amount = AssistanceRequest.PACKAGE_PRICES[
            assistance_request.package_hours
        ]
        if commit:
            assistance_request.save()
        return assistance_request
