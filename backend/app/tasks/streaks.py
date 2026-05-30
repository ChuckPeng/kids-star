"""Streak checking and badge awarding tasks."""
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.streaks.check_streaks_and_badges")
def check_streaks_and_badges():
    """Check consecutive completion streaks and award badges."""
    # Phase 3: implement streak and badge logic
    pass
