from datetime import date

from django.db import models

from users.models import User

class Client(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='client_profile',
        verbose_name='Пользователь'
    )
    date_of_birth = models.DateField(
        blank=True, 
        null=True,
        verbose_name='Дата рождения'
    )
    gender = models.CharField(
        max_length=1, 
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name='Пол'
    )
    address = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Адрес'
    )
    emergency_contact = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Контакт для экстренной связи'
    )
    health_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Заметки о здоровье'
    )
    registration_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
    
    def __str__(self):
        return f'{self.user.get_full_name()}'
    
    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        years = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1
        return years
