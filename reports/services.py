"""Сбор данных для отчётов.

Каждая функция возвращает словарь с тремя ключами:
- title   — заголовок отчёта (строка, идёт в PDF/Excel/HTML);
- headers — список названий колонок для таблицы;
- rows    — список списков (значения ячеек по строкам);
- totals  — (опц.) словарь с итоговыми числами (общая сумма, итого посещений).

Единый формат позволяет в views использовать одну и ту же функцию экспорта
для любого отчёта.
"""
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Count, Q, Sum

from schedule.models import Enrollment, TrainingClass
from subscriptions.models import Payment


# Если пользователь не указал дату «с» — возьмём 30 дней назад.
# Если не указал «по» — возьмём сегодняшний день.
def _normalize_range(date_from: date | None, date_to: date | None) -> tuple[date, date]:
    today = date.today()
    if not date_to:
        date_to = today
    if not date_from:
        date_from = date_to - timedelta(days=30)
    if date_from > date_to:
        date_from, date_to = date_to, date_from
    return date_from, date_to


def attendance_report(date_from, date_to, trainer=None) -> dict[str, Any]:
    """Отчёт по посещаемости за период.

    Строки — тренировки. Колонки: дата, название, тренер, зал,
    записано / посетило / пропустило, % посещаемости.
    """
    date_from, date_to = _normalize_range(date_from, date_to)
    qs = (
        TrainingClass.objects
        .filter(start_time__date__gte=date_from, start_time__date__lte=date_to)
        .select_related('trainer__user', 'room')
        .annotate(
            total=Count('enrollments', filter=~Q(enrollments__status='cancelled')),
            attended=Count('enrollments', filter=Q(enrollments__status='attended')),
            missed=Count('enrollments', filter=Q(enrollments__status='missed')),
        )
        .order_by('start_time')
    )
    if trainer:
        qs = qs.filter(trainer=trainer)

    rows = []
    total_attended = 0
    total_missed = 0
    total_enrolled = 0
    for tc in qs:
        pct = f'{(tc.attended / tc.total * 100):.0f}%' if tc.total else '—'
        trainer_name = tc.trainer.user.get_full_name() if tc.trainer else '—'
        room = tc.room.name if tc.room else '—'
        rows.append([
            tc.start_time.strftime('%d.%m.%Y %H:%M'),
            tc.name,
            trainer_name,
            room,
            tc.total,
            tc.attended,
            tc.missed,
            pct,
        ])
        total_enrolled += tc.total
        total_attended += tc.attended
        total_missed += tc.missed

    avg_pct = (
        f'{(total_attended / total_enrolled * 100):.0f}%'
        if total_enrolled else '—'
    )

    return {
        'title': f'Посещаемость тренировок за {date_from:%d.%m.%Y}—{date_to:%d.%m.%Y}',
        'headers': [
            'Дата и время', 'Тренировка', 'Тренер', 'Зал',
            'Записано', 'Посетило', 'Пропустило', '% посещаемости',
        ],
        'rows': rows,
        'totals': {
            'Всего записей': total_enrolled,
            'Всего посетило': total_attended,
            'Всего пропусков': total_missed,
            'Средняя посещаемость': avg_pct,
        },
        'meta': {'date_from': date_from, 'date_to': date_to},
    }


def revenue_report(date_from, date_to, plan=None) -> dict[str, Any]:
    """Отчёт по выручке за период.

    Строки — абонементы с оплатой. Колонки: дата оплаты, клиент, тариф,
    способ, сумма.
    """
    date_from, date_to = _normalize_range(date_from, date_to)
    qs = (
        Payment.objects
        .filter(paid_at__date__gte=date_from, paid_at__date__lte=date_to)
        .select_related('subscription__client__user', 'subscription__plan')
        .order_by('paid_at')
    )
    if plan:
        qs = qs.filter(subscription__plan=plan)

    rows = []
    total_amount = Decimal('0')
    by_plan: dict[str, Decimal] = {}
    by_method: dict[str, Decimal] = {}
    for p in qs:
        client = p.subscription.client.user.get_full_name()
        plan_name = p.subscription.plan.name
        method = p.get_method_display()
        amount = p.amount
        rows.append([
            p.paid_at.strftime('%d.%m.%Y %H:%M'),
            client,
            plan_name,
            method,
            f'{amount:.2f}',
        ])
        total_amount += amount
        by_plan[plan_name] = by_plan.get(plan_name, Decimal('0')) + amount
        by_method[method] = by_method.get(method, Decimal('0')) + amount

    totals = {'Всего платежей': len(rows), 'Общая сумма, руб.': f'{total_amount:.2f}'}
    # Разбивка по тарифам и способам — отдельно, чтобы было нагляднее.
    for name, amt in by_plan.items():
        totals[f'  Тариф «{name}», руб.'] = f'{amt:.2f}'
    for name, amt in by_method.items():
        totals[f'  Способ «{name}», руб.'] = f'{amt:.2f}'

    return {
        'title': f'Выручка за {date_from:%d.%m.%Y}—{date_to:%d.%m.%Y}',
        'headers': ['Дата оплаты', 'Клиент', 'Тариф', 'Способ', 'Сумма, руб.'],
        'rows': rows,
        'totals': totals,
        'meta': {'date_from': date_from, 'date_to': date_to},
    }


def trainer_load_report(date_from, date_to) -> dict[str, Any]:
    """Загрузка тренеров за период.

    Строки — тренеры. Колонки: тренер, тренировок всего, проведено,
    отменено, посетило клиентов, среднее число посетивших на тренировку.
    """
    date_from, date_to = _normalize_range(date_from, date_to)
    tcs = (
        TrainingClass.objects
        .filter(start_time__date__gte=date_from, start_time__date__lte=date_to)
        .select_related('trainer__user')
    )

    stats: dict[int, dict[str, Any]] = {}
    for tc in tcs:
        if not tc.trainer_id:
            continue
        bucket = stats.setdefault(tc.trainer_id, {
            'trainer': tc.trainer,
            'total': 0, 'completed': 0, 'cancelled': 0, 'attended': 0,
        })
        bucket['total'] += 1
        if tc.status == 'completed':
            bucket['completed'] += 1
        if tc.status == 'cancelled':
            bucket['cancelled'] += 1

    # Посетившие клиенты — отдельным запросом, чтобы не плодить N+1.
    attended_rows = (
        Enrollment.objects
        .filter(
            status='attended',
            training_class__start_time__date__gte=date_from,
            training_class__start_time__date__lte=date_to,
        )
        .values('training_class__trainer_id')
        .annotate(total_attended=Count('id'))
    )
    for r in attended_rows:
        tid = r['training_class__trainer_id']
        if tid in stats:
            stats[tid]['attended'] = r['total_attended']

    rows = []
    total_classes = 0
    total_attended = 0
    for b in sorted(stats.values(), key=lambda x: -x['total']):
        avg = (b['attended'] / b['total']) if b['total'] else 0
        rows.append([
            b['trainer'].user.get_full_name() or b['trainer'].user.username,
            b['total'],
            b['completed'],
            b['cancelled'],
            b['attended'],
            f'{avg:.1f}',
        ])
        total_classes += b['total']
        total_attended += b['attended']

    return {
        'title': f'Загрузка тренеров за {date_from:%d.%m.%Y}—{date_to:%d.%m.%Y}',
        'headers': [
            'Тренер', 'Тренировок всего', 'Проведено',
            'Отменено', 'Посетило клиентов', 'Среднее на тренировку',
        ],
        'rows': rows,
        'totals': {
            'Всего тренировок': total_classes,
            'Всего посещений': total_attended,
        },
        'meta': {'date_from': date_from, 'date_to': date_to},
    }
