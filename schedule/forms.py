from django import forms

from .models import TrainingClass


class TrainingClassForm(forms.ModelForm):
    class Meta:
        model = TrainingClass
        fields = (
            'name', 'trainer', 'room', 'start_time', 'end_time',
            'max_participants', 'status', 'description',
        )
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
