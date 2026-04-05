from django.db import models
from clients.models import Client
from trainers.models import Trainer

class GymRoom(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название зала'
    )
    capacity = models.PositiveIntegerField(
        verbose_name='Вместимость'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    
    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'
    
    def __str__(self):
        return f'{self.name} (вместимость: {self.capacity})'


class TrainingClass(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Запланировано'),
        ('in_progress', 'Идёт'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name='Название тренировки'
    )
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        related_name='classes',
        verbose_name='Тренер'
    )
    room = models.ForeignKey(
        GymRoom,
        on_delete=models.SET_NULL,
        null=True,
        related_name='classes',
        verbose_name='Зал'
    )
    start_time = models.DateTimeField(
        verbose_name='Начало'
    )
    end_time = models.DateTimeField(
        verbose_name='Конец'
    )
    max_participants = models.PositiveIntegerField(
        verbose_name='Макс. участников'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='Статус'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    
    class Meta:
        verbose_name = 'Тренировка'
        verbose_name_plural = 'Тренировки'
        ordering = ['start_time']
    
    def __str__(self):
        return f'{self.name} - {self.start_time.strftime("%d.%m.%Y %H:%M")}'
    
    @property
    def available_spots(self):
        return self.max_participants - self.enrollments.count()
    
    @property
    def is_full(self):
        return self.available_spots <= 0
    
    @property
    def duration_minutes(self):
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('enrolled', 'Записан'),
        ('attended', 'Посетил'),
        ('missed', 'Пропустил'),
        ('cancelled', 'Отменил'),
    ]
    
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Клиент'
    )
    training_class = models.ForeignKey(
        TrainingClass,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Тренировка'
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата записи'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='enrolled',
        verbose_name='Статус'
    )
    
    class Meta:
        verbose_name = 'Запись на тренировку'
        verbose_name_plural = 'Записи на тренировки'
        unique_together = ['client', 'training_class']
    
    def __str__(self):
        return f'{self.client} → {self.training_class}'
# Create your models here.
