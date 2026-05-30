"""Notification sending tasks."""
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.notifications.send_notification")
def send_notification(user_id: str, notif_type: str, title: str, body: str, related_id: str = None):
    """Create an in-app notification record."""
    # Phase 2: implement notification creation
    pass
