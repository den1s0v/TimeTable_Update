# timetable/cron_utils.py
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)

scheduler = None


def init_scheduler():
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")
        try:
            scheduler.start()
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}", exc_info=True)
            raise


def schedule_update_timetable():
    from timetable.management.commands.update_timetable import Command

    try:
        Command.update_timetable()
        logger.info("Timetable update task executed successfully")
    except Exception as e:
        logger.error(f"Error executing timetable update: {str(e)}", exc_info=True)


def configure_update_task():
    minutes = 180  # Значение по умолчанию

    try:
        from timetable.models import Setting

        setting = Setting.objects.get(key="time_update")
        minutes = int(setting.value)
        logger.info(f"Интервал обновления из БД: {minutes} минут")
    except ObjectDoesNotExist:
        logger.warning(
            "Настройка 'time_update' не найдена. Использую значение по умолчанию: 180 минут"
        )
    except (ValueError, TypeError):
        logger.warning(
            "Некорректное значение 'time_update'. Использую значение по умолчанию: 180 минут"
        )
    except Exception as e:
        logger.error(f"Ошибка чтения настройки time_update: {e}")

    global scheduler
    if scheduler is None:
        init_scheduler()

    # Удаляем старую задачу
    try:
        scheduler.remove_job("update_timetable")
        logger.info("Старая задача обновления удалена")
    except:
        pass

    # Добавляем новую
    scheduler.add_job(
        schedule_update_timetable,
        trigger=IntervalTrigger(minutes=minutes),
        id="update_timetable",
        max_instances=1,
        replace_existing=True,
    )
    logger.info(f"Запланировано обновление расписания каждые {minutes} минут")


def create_update_timetable_cron_task():
    """
    Безопасный запуск: не падает, если БД недоступна
    """
    try:
        init_scheduler()
        configure_update_task()
    except Exception as e:
        logger.error(f"Не удалось запустить крон: {e}")
        # Не падаем — попробуем позже
