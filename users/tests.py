"""Тесты приложения users.

Проверяют, что:
1) сигнал post_save автоматически создаёт профиль Client/Trainer при создании пользователя;
2) декораторы ролей действительно блокируют доступ «не-своим» ролям.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clients.models import Client
from trainers.models import Trainer

User = get_user_model()


class SignalCreatesProfileTests(TestCase):
    def test_client_profile_created(self):
        user = User.objects.create_user(
            username='signal_client', password='pwd12345', role='client',
        )
        self.assertTrue(Client.objects.filter(user=user).exists())

    def test_trainer_profile_created(self):
        user = User.objects.create_user(
            username='signal_trainer', password='pwd12345', role='trainer',
        )
        self.assertTrue(Trainer.objects.filter(user=user).exists())

    def test_admin_does_not_create_client_or_trainer(self):
        user = User.objects.create_user(
            username='signal_admin', password='pwd12345', role='admin',
        )
        self.assertFalse(Client.objects.filter(user=user).exists())
        self.assertFalse(Trainer.objects.filter(user=user).exists())


class RoleDecoratorTests(TestCase):
    def test_client_cannot_open_reports(self):
        user = User.objects.create_user(
            username='no_reports', password='pwd12345', role='client',
        )
        self.client.force_login(user)
        response = self.client.get(reverse('reports:index'))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_open_reports(self):
        user = User.objects.create_user(
            username='yes_reports', password='pwd12345', role='admin',
        )
        self.client.force_login(user)
        response = self.client.get(reverse('reports:index'))
        self.assertEqual(response.status_code, 200)
