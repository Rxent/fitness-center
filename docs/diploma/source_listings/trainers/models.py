from django.db import models
from users.models import User

class Specialization(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    
    class Meta:
        verbose_name = 'Специализация'
        verbose_name_plural = 'Специализации'
    
    def __str__(self):
        return self.name


class Trainer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='trainer_profile',
        verbose_name='Пользователь'
    )
    specializations = models.ManyToManyField(
        Specialization,
        related_name='trainers',
        verbose_name='Специализации'
    )
    experience_years = models.PositiveIntegerField(
        default=0,
        verbose_name='Опыт работы (лет)'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='Биография'
    )
    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name='Ставка в час (руб.)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    hired_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата найма'
    )
    
    class Meta:
        verbose_name = 'Тренер'
        verbose_name_plural = 'Тренеры'
    
    def __str__(self):
        return f'{self.user.get_full_name()}'