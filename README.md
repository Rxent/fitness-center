# Фитнес-центр — АИС

Автоматизированная информационная система для работы фитнес-центра (дипломный проект).

Стек: **Django 6**, SQLite (dev) / PostgreSQL (prod), Bootstrap 5, reportlab, openpyxl.

## Структура

```
fitness_center/
├── config/         # настройки Django, urls, wsgi/asgi
├── users/          # кастомная модель User (роли: admin/trainer/client), аутентификация
├── clients/        # клиенты
├── trainers/       # тренеры и их специализации
├── subscriptions/  # тарифы, абонементы, платежи
├── schedule/       # залы, тренировки, записи клиентов
├── reports/        # отчёты и экспорт
├── templates/      # HTML-шаблоны (Bootstrap 5)
├── requirements.txt
└── manage.py
```

## Быстрый старт

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo           # демо-данные
python manage.py createsuperuser     # опционально — свой суперюзер
python manage.py runserver
```

Откройте http://127.0.0.1:8000/.

### Демо-учётные записи

После `seed_demo` пароль у всех демо-пользователей — `demo12345`:

| Логин          | Роль          |
|----------------|---------------|
| `demo_admin`   | администратор |
| `demo_trainer1`| тренер        |
| `demo_client1` | клиент        |

Админ-панель: http://127.0.0.1:8000/admin/

## Роли и доступ

- **Администратор** — полный доступ к админ-панели, отчётам, управлению тарифами.
- **Тренер** — своё расписание, список записей клиентов.
- **Клиент** — личный кабинет, свои абонементы и записи на тренировки.

Проверка роли — декоратор `users.decorators.role_required` (`admin_required`,
`trainer_required`, `client_required`, `staff_required`).

## План разработки

- [x] Неделя 1 — модели, миграции, админ-панель, аутентификация, роли, демо-данные.
- [ ] Неделя 2 — шаблоны и формы: CRUD по клиентам/тренерам, запись на тренировки.
- [ ] Неделя 3 — отчёты (посещаемость, выручка, загрузка тренеров), экспорт PDF/Excel.
- [ ] Неделя 4 — тесты, Docker, PostgreSQL, финальная отладка.
