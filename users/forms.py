from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class ClientRegistrationForm(UserCreationForm):
    """Регистрация клиента через публичную страницу."""

    first_name = forms.CharField(label='Имя', max_length=150, required=True)
    last_name = forms.CharField(label='Фамилия', max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)
    phone = forms.CharField(label='Телефон', max_length=15, required=False)

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'phone',
            'password1', 'password2',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone') or ''
        if commit:
            user.save()
            # Профиль клиента создаётся автоматически сигналом.
        return user


class UserProfileForm(UserChangeForm):
    """Форма редактирования собственного профиля."""

    password = None  # скрываем поле пароля из формы профиля

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'photo')
