import logging
import os

from django.core.management import call_command

from developerportal.apps.taskqueue.celery import app

from .utils import invalidate_cdn

logging.basicConfig(level=os.environ.get("LOGLEVEL", logging.INFO))
logger = logging.getLogger(__name__)


@app.task
def publish_scheduled_pages():
    log_prefix = "[Publish scheduled pages]"
    logger.info(f"{log_prefix} Trying to publish/unpublish scheduled pages")
    call_command("publish_scheduled_pages")


@app.task
def invalidate_entire_cdn():
    log_prefix = "[Invalidate entire CDN]"
    logger.info(f"{log_prefix} Issuing purge command")
    invalidate_cdn()
