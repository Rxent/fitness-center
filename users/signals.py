from django.db.models.signals import post_save
from django.dispatch import receiver

from clients.models import Client
from trainers.models import Trainer

from .models import User


@receiver(post_save, sender=User)
def create_role_profile(sender, instance: User, created: bool, **kwargs):
    """При создании пользователя создаёт соответствующий профиль по роли."""
    if not created:
        return
    if instance.role == 'client':
        Client.objects.get_or_create(user=instance)
    elif instance.role == 'trainer':
        Trainer.objects.get_or_create(user=instance)
