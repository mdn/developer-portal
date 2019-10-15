import os

from django.conf import settings

from celery import Celery

STATIC_BUILD_JOB_ATTEMPT_FREQUENCY = 60.0 * 1  # Check each minute

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "developerportal.settings.production")

app = Celery("developerportal.apps.staticbuild", broker=settings.CELERY_BROKER_URL)

# Add the Django settings module as a configuration source for Celery
app.config_from_object("django.conf:settings")

app.autodiscover_tasks()

# Set up a Celery Beat task to try to build the static site every minute
app.conf.beat_schedule = {
    "add-every-minute": {
        "task": "developerportal.apps.staticbuild.wagtail_hooks._static_build_async",
        "schedule": STATIC_BUILD_JOB_ATTEMPT_FREQUENCY,
        "args": (),
    }
}
app.conf.timezone = "UTC"
