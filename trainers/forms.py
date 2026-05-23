from django import forms

from .models import Trainer


class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ('specializations', 'experience_years', 'bio', 'hourly_rate', 'is_active')
        widgets = {
            'specializations': forms.CheckboxSelectMultiple,
            'bio': forms.Textarea(attrs={'rows': 3}),
        }
