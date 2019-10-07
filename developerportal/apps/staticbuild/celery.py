import os

from django.conf import settings

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "developerportal.settings.production")

app = Celery("developerportal.apps.staticbuild", broker=settings.CELERY_BROKER_URL)

# Add the Django settings module as a configuration source for Celery
app.config_from_object("django.conf:settings")

app.autodiscover_tasks()
