# Фитнес-центр — АИС

Дипломный проект. Веб-система для работы фитнес-центра: клиенты, тренеры, абонементы, расписание, отчёты.

Стек: Django 5, SQLite, Bootstrap 5.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Открыть http://127.0.0.1:8000/.

## Демо-учётные записи

Пароль у всех: `demo12345`

| Логин           | Роль          |
|-----------------|---------------|
| `demo_admin`    | администратор |
| `demo_trainer1` | тренер        |
| `demo_client1`  | клиент        |

Админ-панель: http://127.0.0.1:8000/admin/

## Структура

```
config/         настройки Django
users/          пользователи и роли
clients/        клиенты
trainers/       тренеры
subscriptions/  тарифы и абонементы
schedule/       залы и расписание
reports/        отчёты
templates/      HTML-шаблоны
static/         CSS и картинки
```
