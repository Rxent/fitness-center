"""Наполняет БД демо-данными для разработки и демонстрации."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from clients.models import Client
from schedule.models import Enrollment, GymRoom, TrainingClass
from subscriptions.models import Payment, Subscription, SubscriptionPlan
from trainers.models import Specialization, Trainer

User = get_user_model()


class Command(BaseCommand):
    help = 'Создаёт демо-пользователей, тарифы, залы и расписание для тестирования.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Удалить существующих демо-пользователей перед созданием.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            User.objects.filter(username__startswith='demo_').delete()
            self.stdout.write(self.style.WARNING('Удалены прежние демо-пользователи.'))

        self.stdout.write('Создание специализаций...')
        specs = {}
        for name in ['Йога', 'Силовые', 'Кардио', 'Плавание', 'Кроссфит']:
            spec, _ = Specialization.objects.get_or_create(name=name)
            specs[name] = spec

        self.stdout.write('Создание тарифов...')
        plans_data = [
            ('Базовый месяц', 'basic', 30, Decimal('2500'), 8,
             'Месячный абонемент с лимитом 8 посещений.'),
            ('Стандартный месяц', 'standard', 30, Decimal('3900'), None,
             'Безлимитный месячный абонемент.'),
            ('Премиум 3 мес.', 'premium', 90, Decimal('10500'), None,
             'Безлимит + 2 персональные тренировки в месяц.'),
        ]
        plans = {}
        for name, ptype, days, price, limit, desc in plans_data:
            plan, _ = SubscriptionPlan.objects.update_or_create(
                name=name,
                defaults={
                    'plan_type': ptype, 'duration_days': days,
                    'price': price, 'visits_limit': limit,
                    'description': desc, 'is_active': True,
                },
            )
            plans[ptype] = plan

        self.stdout.write('Создание залов...')
        rooms = {}
        for name, cap in [('Большой зал', 25), ('Зал йоги', 15), ('Кардио-зона', 20)]:
            room, _ = GymRoom.objects.get_or_create(
                name=name, defaults={'capacity': cap},
            )
            rooms[name] = room

        self.stdout.write('Создание демо-пользователей...')
        admin = self._make_user('demo_admin', 'admin', 'Анна', 'Администраторова')
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        trainer_defs = [
            ('demo_trainer1', 'Игорь', 'Силачёв', ['Силовые', 'Кроссфит'], 8, Decimal('2000')),
            ('demo_trainer2', 'Мария', 'Гибкая', ['Йога'], 5, Decimal('1800')),
            ('demo_trainer3', 'Пётр', 'Быстров', ['Кардио', 'Плавание'], 3, Decimal('1600')),
        ]
        trainers = []
        for username, first, last, spec_names, years, rate in trainer_defs:
            u = self._make_user(username, 'trainer', first, last)
            t = u.trainer_profile
            t.experience_years = years
            t.hourly_rate = rate
            t.bio = f'Тренер по направлениям: {", ".join(spec_names)}.'
            t.save()
            t.specializations.set([specs[n] for n in spec_names])
            trainers.append(t)

        client_defs = [
            ('demo_client1', 'Иван', 'Иванов', 'M'),
            ('demo_client2', 'Ольга', 'Петрова', 'F'),
            ('demo_client3', 'Сергей', 'Сидоров', 'M'),
            ('demo_client4', 'Елена', 'Кузнецова', 'F'),
        ]
        clients = []
        for username, first, last, gender in client_defs:
            u = self._make_user(username, 'client', first, last)
            c = u.client_profile
            c.gender = gender
            c.date_of_birth = timezone.now().date() - timedelta(days=365 * 25)
            c.save()
            clients.append(c)

        self.stdout.write('Создание абонементов и платежей...')
        today = timezone.now().date()
        for i, client in enumerate(clients):
            plan = list(plans.values())[i % len(plans)]
            start = today - timedelta(days=i * 5)
            end = start + timedelta(days=plan.duration_days)
            sub, _ = Subscription.objects.update_or_create(
                client=client, plan=plan, start_date=start,
                defaults={'end_date': end, 'status': 'active'},
            )
            Payment.objects.update_or_create(
                subscription=sub,
                defaults={'amount': plan.price, 'method': 'card'},
            )

        self.stdout.write('Создание тренировок...')
        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        class_defs = [
            ('Силовая тренировка', trainers[0], rooms['Большой зал'], 1, 10, 15),
            ('Йога для начинающих', trainers[1], rooms['Зал йоги'], 2, 9, 12),
            ('HIIT', trainers[2], rooms['Кардио-зона'], 3, 18, 20),
            ('Кроссфит', trainers[0], rooms['Большой зал'], 4, 19, 18),
        ]
        classes = []
        for name, trainer, room, days_ahead, hour, max_p in class_defs:
            start = now + timedelta(days=days_ahead, hours=hour - now.hour)
            tc, _ = TrainingClass.objects.update_or_create(
                name=name, trainer=trainer, start_time=start,
                defaults={
                    'room': room,
                    'end_time': start + timedelta(hours=1),
                    'max_participants': max_p,
                    'status': 'scheduled',
                },
            )
            classes.append(tc)

        self.stdout.write('Запись клиентов на тренировки...')
        for i, client in enumerate(clients):
            for tc in classes[: (i % 3) + 1]:
                Enrollment.objects.get_or_create(
                    client=client, training_class=tc,
                )

        self.stdout.write(self.style.SUCCESS('Готово! Демо-данные созданы.'))
        self.stdout.write('Учётные записи (пароль у всех: demo12345):')
        self.stdout.write('  demo_admin     — администратор (и superuser)')
        self.stdout.write('  demo_trainer1  — тренер')
        self.stdout.write('  demo_client1   — клиент')

    def _make_user(self, username: str, role: str, first: str, last: str) -> User:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'role': role,
                'first_name': first,
                'last_name': last,
                'email': f'{username}@example.com',
                'is_active': True,
            },
        )
        if created:
            user.set_password('demo12345')
            user.save()
        return user
