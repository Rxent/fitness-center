from django.db import models
from django.utils import timezone
from clients.models import Client

class SubscriptionPlan(models.Model):
    TYPE_CHOICES = [
        ('basic', 'Базовый'),
        ('standard', 'Стандартный'),
        ('premium', 'Премиум'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    plan_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Тип'
    )
    duration_days = models.PositiveIntegerField(
        verbose_name='Длительность (дней)'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена (руб.)'
    )
    visits_limit = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Лимит посещений (null = безлимит)'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    
    class Meta:
        verbose_name = 'Тарифный план'
        verbose_name_plural = 'Тарифные планы'
    
    def __str__(self):
        return f'{self.name} - {self.price} руб.'


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('expired', 'Истёк'),
        ('frozen', 'Заморожен'),
        ('cancelled', 'Отменён'),
    ]
    
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Клиент'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name='Тарифный план'
    )
    start_date = models.DateField(
        verbose_name='Дата начала'
    )
    end_date = models.DateField(
        verbose_name='Дата окончания'
    )
    visits_used = models.PositiveIntegerField(
        default=0,
        verbose_name='Посещений использовано'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Абонемент'
        verbose_name_plural = 'Абонементы'
    
    def __str__(self):
        return f'{self.client} - {self.plan.name}'
    
    @property
    def is_valid(self):
        return (
            self.status == 'active' and 
            self.end_date >= timezone.now().date()
        )
    
    @property
    def days_left(self):
        if self.end_date >= timezone.now().date():
            return (self.end_date - timezone.now().date()).days
        return 0
    
    def save(self, *args, **kwargs):
        # Автоматически вычисляем дату окончания
        if not self.end_date:
            from datetime import timedelta
            self.end_date = self.start_date + timedelta(
                days=self.plan.duration_days
            )
        super().save(*args, **kwargs)


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
        ('online', 'Онлайн'),
    ]
    
    subscription = models.OneToOneField(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name='Абонемент'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма (руб.)'
    )
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        verbose_name='Способ оплаты'
    )
    paid_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата оплаты'
    )
    
    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
    
    def __str__(self):
        return f'Платёж {self.amount} руб. от {self.paid_at.date()}'
# Create your models here.
