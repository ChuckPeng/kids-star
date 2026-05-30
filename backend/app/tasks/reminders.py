"""Reminder and periodic check tasks."""
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.reminders.check_overdue_tasks")
def check_overdue_tasks():
    """Check for overdue required tasks and apply overtime discount."""
    # Phase 2: implement overdue check and auto-penalty
    pass


@celery_app.task(name="app.tasks.reminders.generate_repeat_tasks")
def generate_repeat_tasks():
    """Generate next day's task instances for repeating tasks."""
    # Phase 2: implement repeat task generation
    pass


@celery_app.task(name="app.tasks.reminders.send_daily_reminder")
def send_daily_reminder():
    """Send daily task reminder to children."""
    # Phase 2: implement notification sending
    pass
