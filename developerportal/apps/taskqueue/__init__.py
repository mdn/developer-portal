from .celery import app as celery_app

# Make sure Celery is always imported when Django starts
# so that @shared_task will use this app.
__all__ = ("celery_app",)
