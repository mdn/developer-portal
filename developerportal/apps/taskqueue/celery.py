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
        "task": "developerportal.apps.taskqueue.tasks.publish_scheduled_pages",
        "schedule": crontab(minute=55),  # Five minutes to each hour
        "args": (),
    },
    "selectively-purge-cdn-every-night": {
        "task": "developerportal.apps.taskqueue.tasks.selectively_invalidate_cdn",
        "schedule": crontab(minute=15, hour=0),  # 15 past midnight
        "args": (),
    },
    # We're registering these tasks on behalf of `developerportal.apps.ingestion`
    # because we only want to run one celerybeat scheduler (for now) to keep things
    # simpler at the ops level.
    "ingest-articles-every-two-hours": {
        "task": "developerportal.apps.ingestion.tasks.ingest_articles",
        "schedule": crontab(minute=17, hour="*/2"),  # Every two hours, at 17 min past
        "args": (),
    },
    "ingest-videos-every-two-hours": {
        "task": "developerportal.apps.ingestion.tasks.ingest_videos",
        "schedule": crontab(minute=37, hour="*/2"),  # Every two hours, at 37 min past
        "args": (),
    },
    "rebuild-search-index-weekly": {
        "task": "developerportal.apps.taskqueue.tasks.update_wagtail_search_index",
        "schedule": crontab(
            minute=30, hour=9, day_of_week="thu"
        ),  # Once a week: Thursdays at 0930 UTC (server time)
        "args": (),
    },
}
app.conf.timezone = "UTC"
