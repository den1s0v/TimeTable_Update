# timetable/apps.py
from pathlib import Path
from django.apps import AppConfig
import threading
import logging

logger = logging.getLogger(__name__)

TAG_CATEGORY_MAP = {
    "education_form": "Выбрать форму обучения",
    "faculty": "Выбрать факультет",
    "course": "Выбрать курс",
}
GOOGLE_DRIVE_STORAGE_MAME = "google drive"
LOCAL_STORAGE_NAME = "local"
AVAILABLE_KEYS = {"time_update", "analyze_url", "google_json_dir", "download_storage"}


class TimetableConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "timetable"

    def ready(self):
        # Запускаем крон только в главном потоке и не в миграциях
        if threading.current_thread().name != "MainThread":
            return

        # Импортируем внутри, чтобы избежать циклических импортов
        from django.db import connection
        from timetable.cron_utils import create_update_timetable_cron_task

        # Пытаемся подключиться к БД
        try:
            connection.ensure_connection()
            if connection.is_usable():
                logger.info("База данных доступна. Запускаем крон-задачу...")
                create_update_timetable_cron_task()
            else:
                logger.warning("База данных недоступна. Крон будет запущен позже.")
        except Exception as e:
            logger.error(f"Ошибка подключения к БД при запуске крона: {e}")
