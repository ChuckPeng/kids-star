"""Celery app configuration for Kids-Star."""
from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "kids_star",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "check-overdue-tasks": {
            "task": "app.tasks.reminders.check_overdue_tasks",
            "schedule": 3600.0,  # every hour
        },
        "evaluate-penalty-rules": {
            "task": "app.tasks.penalties.evaluate_penalty_rules",
            "schedule": 86400.0,  # daily at midnight
        },
        "generate-repeat-tasks": {
            "task": "app.tasks.reminders.generate_repeat_tasks",
            "schedule": 86400.0,
        },
        "check-streaks": {
            "task": "app.tasks.streaks.check_streaks_and_badges",
            "schedule": 86400.0,
        },
    },
)
