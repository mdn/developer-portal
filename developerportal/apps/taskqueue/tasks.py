import logging
import os

from django.core.management import call_command

from developerportal.apps.taskqueue.celery import app

logging.basicConfig(level=os.environ.get("LOGLEVEL", logging.INFO))
logger = logging.getLogger(__name__)


@app.task
def _publish_scheduled_pages():
    log_prefix = "[Publish scheduled pages]"
    logger.info(f"{log_prefix} Trying to publish/unpublish scheduled pages")
    call_command("publish_scheduled_pages")
