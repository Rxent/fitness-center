"""Тесты приложения schedule.

Покрывают самые важные бизнес-правила:
1) нельзя записаться без действующего абонемента;
2) нельзя записаться, если зал уже заполнен;
3) нельзя записаться на прошедшую тренировку;
4) отметка «посетил» увеличивает счётчик посещений абонемента;
5) один и тот же клиент не может быть записан на тренировку дважды.

Тесты используют стандартный Django TestCase — он сам создаёт и чистит
тестовую БД, поэтому состояние одного теста не влияет на другие.
"""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from clients.models import Client
from schedule.models import Enrollment, GymRoom, TrainingClass
from schedule.views import _can_enroll
from subscriptions.models import Subscription, SubscriptionPlan
from trainers.models import Trainer

User = get_user_model()


def _create_client(username='client_test'):
    """Удобный хелпер: создаёт пользователя-клиента с профилем Client.
    Сигнал post_save создаст профиль автоматически, но get_or_create подстрахует.
    """
    user = User.objects.create_user(
        username=username, password='pwd12345', role='client',
        first_name='Тест', last_name='Клиентов',
    )
    client, _ = Client.objects.get_or_create(user=user)
    return client


def _create_trainer():
    user = User.objects.create_user(
        username='trainer_test', password='pwd12345', role='trainer',
        first_name='Тренер', last_name='Тренеров',
    )
    trainer, _ = Trainer.objects.get_or_create(user=user)
    return trainer


def _create_plan():
    return SubscriptionPlan.objects.create(
        name='Тест-тариф', plan_type='basic',
        duration_days=30, price=Decimal('1000.00'), visits_limit=10,
    )


def _create_class(trainer, *, future=True, capacity=5):
    """Создаёт тренировку либо в будущем, либо уже в прошлом."""
    now = timezone.now()
    start = now + timedelta(days=1) if future else now - timedelta(days=1)
    room = GymRoom.objects.create(name='Зал', capacity=capacity)
    return TrainingClass.objects.create(
        name='Силовая', trainer=trainer, room=room,
        start_time=start, end_time=start + timedelta(hours=1),
        max_participants=capacity, status='scheduled',
    )


class EnrollmentRulesTests(TestCase):
    """Тесты на правила функции _can_enroll."""

    def setUp(self):
        self.trainer = _create_trainer()
        self.client_obj = _create_client()
        self.plan = _create_plan()

    def _active_sub(self):
        """Создать действующий абонемент у клиента."""
        today = date.today()
        return Subscription.objects.create(
            client=self.client_obj, plan=self.plan,
            start_date=today, end_date=today + timedelta(days=30),
            status='active',
        )

    def test_cannot_enroll_without_subscription(self):
        tc = _create_class(self.trainer)
        can, reason = _can_enroll(self.client_obj, tc, None)
        self.assertFalse(can)
        self.assertIn('абонемент', reason.lower())

    def test_can_enroll_with_active_subscription(self):
        self._active_sub()
        tc = _create_class(self.trainer)
        can, reason = _can_enroll(self.client_obj, tc, None)
        self.assertTrue(can, reason)

    def test_cannot_enroll_in_past_class(self):
        self._active_sub()
        tc = _create_class(self.trainer, future=False)
        can, reason = _can_enroll(self.client_obj, tc, None)
        self.assertFalse(can)
        self.assertIn('началась', reason.lower())

    def test_cannot_enroll_when_full(self):
        self._active_sub()
        tc = _create_class(self.trainer, capacity=1)
        # Занимаем единственное место.
        other = _create_client('other')
        Enrollment.objects.create(client=other, training_class=tc)
        can, reason = _can_enroll(self.client_obj, tc, None)
        self.assertFalse(can)
        self.assertIn('свободных мест нет', reason.lower())

    def test_cannot_double_enroll(self):
        self._active_sub()
        tc = _create_class(self.trainer)
        enrollment = Enrollment.objects.create(
            client=self.client_obj, training_class=tc,
        )
        can, reason = _can_enroll(self.client_obj, tc, enrollment)
        self.assertFalse(can)
        self.assertIn('уже записаны', reason.lower())


class AttendanceIncrementsVisitsTests(TestCase):
    """Отметка «посетил» должна увеличивать visits_used активного абонемента."""

    def test_marking_attended_increments_visits(self):
        trainer = _create_trainer()
        client_obj = _create_client()
        plan = _create_plan()
        today = date.today()
        sub = Subscription.objects.create(
            client=client_obj, plan=plan,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
            status='active',
        )
        tc = _create_class(trainer)
        enrollment = Enrollment.objects.create(
            client=client_obj, training_class=tc,
        )

        # Логинимся тренером и вызываем view.
        self.client.force_login(trainer.user)
        response = self.client.post(
            f'/schedule/trainer/enrollment/{enrollment.id}/',
            {'status': 'attended'},
        )
        self.assertEqual(response.status_code, 302)

        sub.refresh_from_db()
        self.assertEqual(sub.visits_used, 1)

        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, 'attended')


class UniqueEnrollmentTests(TestCase):
    """Проверка уникальности (client, training_class) на уровне БД."""

    def test_duplicate_enrollment_raises(self):
        from django.db import IntegrityError

        trainer = _create_trainer()
        client_obj = _create_client()
        tc = _create_class(trainer)
        Enrollment.objects.create(client=client_obj, training_class=tc)
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(client=client_obj, training_class=tc)
