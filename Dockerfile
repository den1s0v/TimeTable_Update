FROM python:3.13-slim

# УСТАНАВЛИВАЕМ git ПЕРВЫМ!
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Создаём папки
RUN mkdir -p staticfiles logs temp

EXPOSE 8000

CMD python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py collectstatic --noinput --clear && \
    gunicorn timetable_project.wsgi:application --bind 0.0.0.0:8000
