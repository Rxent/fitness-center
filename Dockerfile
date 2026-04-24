# Dockerfile для приложения фитнес-центра.
# Собирается единый образ, в котором запускается Django через gunicorn.
FROM python:3.12-slim

# Чтобы Python не создавал .pyc и сразу писал логи без буферизации.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Устанавливаем системные зависимости:
# - libpq-dev и gcc нужны для сборки драйвера psycopg2 к PostgreSQL;
# - fonts-dejavu-core нужен для корректной кириллицы в PDF-отчётах.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала копируем только requirements.txt, чтобы Docker кэшировал слой
# с установкой зависимостей, пока файл не меняется.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Теперь копируем остальной код.
COPY . .

# Собираем статику (один раз на сборку образа).
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# По умолчанию запускаем gunicorn. Перед стартом применяем миграции,
# чтобы контейнер был самодостаточным.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
