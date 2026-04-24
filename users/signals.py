"""
Сигналы приложения users.

Сигнал — это механизм Django, позволяющий «подписаться» на какое-то событие
и автоматически выполнить функцию при его возникновении.

Здесь используется сигнал post_save модели User: он срабатывает после
сохранения любого пользователя. Цель — автоматически создавать соответствующий
профиль (Client или Trainer) при создании пользователя с такой ролью.

Это избавляет от необходимости помнить о создании профиля вручную, когда
администратор добавляет нового пользователя через админ-панель.

Регистрация сигнала происходит в users/apps.py в методе ready().
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from clients.models import Client
from trainers.models import Trainer

from .models import User


@receiver(post_save, sender=User)
def create_role_profile(sender, instance: User, created: bool, **kwargs):
    """При создании нового пользователя создаёт профиль согласно роли."""
    # Срабатывает только при создании (created=True). Обновления игнорируем,
    # иначе каждая правка пользователя пыталась бы плодить новые профили.
    if not created:
        return

    # get_or_create возвращает уже существующий профиль или создаёт новый.
    # Это безопаснее, чем просто create, — даже если профиль каким-то образом
    # уже есть, повторного создания не произойдёт.
    if instance.role == 'client':
        Client.objects.get_or_create(user=instance)
    elif instance.role == 'trainer':
        Trainer.objects.get_or_create(user=instance)
