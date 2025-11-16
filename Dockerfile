FROM python:3.11-slim

# Принимаем токен
ARG GITHUB_TOKEN

# УСТАНАВЛИВАЕМ git ПЕРВЫМ!
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

# ТЕПЕРЬ настраиваем git с токеном
RUN git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"

WORKDIR /app

# Клонируем репозиторий
RUN git clone https://github.com/VladTeslenkov/TimeTable_Update.git . && \
    rm -rf .git

# Убираем токен (безопасность)
RUN git config --global --unset url."https://${GITHUB_TOKEN}@github.com/".insteadOf || true

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir mysql-connector-python

# Создаём папки
RUN mkdir -p staticfiles logs temp

EXPOSE 8000

CMD python wait-for-db.py && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput --clear && \
    gunicorn timetable_project.wsgi:application --bind 0.0.0.0:8000
