"""Penalty rule evaluation tasks."""
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.penalties.evaluate_penalty_rules")
def evaluate_penalty_rules():
    """Evaluate family penalty rules and apply penalties."""
    # Phase 2: implement penalty rule evaluation
    pass
