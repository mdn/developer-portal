import os

from django.conf import settings

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "developerportal.settings.worker")

app = Celery("developerportal.apps.ingestion", broker=settings.CELERY_BROKER_URL)

# Add the Django settings module as a configuration source for Celery
app.config_from_object("django.conf:settings")

app.autodiscover_tasks()

# We're actually registering these tasks over in `developerportal.apps.taskqueue.celery`
# because we only want to run one celerybeat scheduler (for now) to keep things simpler
# at the ops level.

# app.conf.beat_schedule = {
#     "ingest-articles-every-two-hours": {
#         "task": ("developerportal.apps.ingestion.tasks.ingest_articles"),
#         "schedule": crontab(minute=17, hour="*/2"),  # Every two hours, at 17 min past
#         "args": (),
#     },
#     "ingest-videos-every-two-hours": {
#         "task": ("developerportal.apps.ingestion.tasks.ingest_videos"),
#         "schedule": crontab(minute=37, hour="*/2"),  # Every two hours, at 37 min past
#         "args": (),
#     },
# }
app.conf.timezone = "UTC"
