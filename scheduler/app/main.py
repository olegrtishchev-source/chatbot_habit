"""Точка входа фонового сервиса: ежедневный перенос привычек и напоминания."""

import logging

import telebot
from apscheduler.schedulers.blocking import BlockingScheduler

from app.config import settings
from app.database import session_scope
from app.services.carryover import create_missing_logs_for_today
from app.services.reminders import find_users_with_pending_habits

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(settings.telegram_bot_token)


def run_daily_carryover() -> None:
    """Создаёт записи HabitLog на новый день для всех активных привычек."""
    with session_scope() as db:
        created = create_missing_logs_for_today(db)
    logger.info("Перенос привычек: создано записей — %s", created)


def run_reminders() -> None:
    """Отправляет напоминания пользователям с невыполненными на сегодня привычками."""
    with session_scope() as db:
        pending_reminders = find_users_with_pending_habits(db)

    for reminder in pending_reminders:
        titles = "\n".join(f"• {title}" for title in reminder.habit_titles)
        text = f"⏰ Напоминание: сегодня ещё не отмечены привычки:\n{titles}"
        try:
            bot.send_message(reminder.telegram_id, text)
        except Exception:
            logger.exception(
                "Не удалось отправить напоминание пользователю %s", reminder.telegram_id
            )

    logger.info("Напоминания отправлены: %s пользователям", len(pending_reminders))


def main() -> None:
    """Запускает планировщик с задачами переноса привычек и напоминаний."""
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_daily_carryover,
        "cron",
        hour=settings.carryover_hour,
        minute=settings.carryover_minute,
    )
    scheduler.add_job(
        run_reminders,
        "cron",
        hour=settings.reminder_hour,
        minute=settings.reminder_minute,
    )
    logger.info("Планировщик запущен")
    scheduler.start()


if __name__ == "__main__":
    main()
