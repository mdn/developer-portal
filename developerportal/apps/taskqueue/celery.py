import os

from django.conf import settings

from celery import Celery
from celery.schedules import crontab

STATIC_BUILD_JOB_ATTEMPT_FREQUENCY = 60.0 * 1  # Check each minute

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "developerportal.settings.worker")

app = Celery("developerportal.apps.taskqueue", broker=settings.CELERY_BROKER_URL)

# Add the Django settings module as a configuration source for Celery
app.config_from_object("django.conf:settings")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "run-publish-scheduled-command-every-hour": {
        "task": ("developerportal.apps.taskqueue.tasks.publish_scheduled_pages"),
        "schedule": crontab(minute=55),  # Five minutes to each hour
        "args": (),
    },
    "selectively-purge-cdn-every-night": {
        "task": "developerportal.apps.taskqueue.tasks.selectively_invalidate_cdn",
        "schedule": crontab(minute=15, hour=0),  # 15 past midnight
        "args": (),
    },
}
app.conf.timezone = "UTC"
