from django import forms

from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = (
            'date_of_birth', 'gender', 'address', 'emergency_contact',
            'health_notes', 'is_active',
        )
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'health_notes': forms.Textarea(attrs={'rows': 3}),
        }
