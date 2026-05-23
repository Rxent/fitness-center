from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('trainer', 'Тренер'),
        ('client', 'Клиент'),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='client',
        verbose_name='Роль'
    )
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        verbose_name='Телефон'
    )
    photo = models.ImageField(
        upload_to='users/photos/', 
        blank=True, 
        null=True,
        verbose_name='Фото'
    )
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f'{self.get_full_name()} ({self.get_role_display()})'
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_trainer(self):
        return self.role == 'trainer'
    
    @property
    def is_client(self):
        return self.role == 'client'