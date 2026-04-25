"""Тесты приложения subscriptions.

Проверяют, что:
1) при сохранении Subscription без end_date она вычисляется по duration_days;
2) property is_valid возвращает True только у активного не просроченного абонемента;
3) через view покупки абонемента нельзя оформить второй активный на того же клиента.
"""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from clients.models import Client
from subscriptions.models import Subscription, SubscriptionPlan

User = get_user_model()


def _client():
    u = User.objects.create_user(
        username='c1', password='pwd12345', role='client',
    )
    obj, _ = Client.objects.get_or_create(user=u)
    return obj


def _plan(days=30):
    return SubscriptionPlan.objects.create(
        name='Тариф', plan_type='basic',
        duration_days=days, price=Decimal('500.00'), visits_limit=8,
    )


class SubscriptionModelTests(TestCase):
    def test_end_date_autocalculated(self):
        plan = _plan(30)
        client_obj = _client()
        sub = Subscription.objects.create(
            client=client_obj, plan=plan, start_date=date(2026, 1, 1),
        )
        # Сохраняли без end_date — save() должен подставить.
        self.assertEqual(sub.end_date, date(2026, 1, 31))

    def test_is_valid_true_for_active_not_expired(self):
        plan = _plan(30)
        client_obj = _client()
        today = date.today()
        sub = Subscription.objects.create(
            client=client_obj, plan=plan,
            start_date=today, end_date=today + timedelta(days=10),
            status='active',
        )
        self.assertTrue(sub.is_valid)

    def test_is_valid_false_when_expired(self):
        plan = _plan(30)
        client_obj = _client()
        today = date.today()
        sub = Subscription.objects.create(
            client=client_obj, plan=plan,
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=30),
            status='active',
        )
        self.assertFalse(sub.is_valid)


class PurchasePlanViewTests(TestCase):
    def test_cannot_purchase_second_active_plan(self):
        plan = _plan(30)
        client_obj = _client()
        today = date.today()
        # У клиента уже есть активный абонемент.
        Subscription.objects.create(
            client=client_obj, plan=plan,
            start_date=today, end_date=today + timedelta(days=10),
            status='active',
        )
        self.client.force_login(client_obj.user)
        response = self.client.post(
            f'/subscriptions/{plan.id}/purchase/', {'method': 'card'},
        )
        # Страница делает редирект обратно с сообщением об ошибке,
        # второго активного абонемента в БД не появляется.
        self.assertEqual(Subscription.objects.filter(
            client=client_obj, status='active',
        ).count(), 1)
