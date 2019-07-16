import logging
from multiprocessing import Process
import os

from django.conf import settings
from django.core.management import call_command

from wagtail.core.signals import page_published, page_unpublished


logging.basicConfig(level=os.environ.get('LOGLEVEL', logging.INFO))
logger = logging.getLogger(__name__)


def _static_build_async(pipeline=settings.STATIC_BUILD_PIPELINE):
    """Calls each command in the static build pipeline in turn."""
    log_prefix = 'Static build task'
    for name, command in pipeline:
        if settings.DEBUG:
            logger.info(f'{log_prefix} ‘{name}’ skipped.')
        else:
            logger.info(f'{log_prefix} ‘{name}’ started.')
            call_command(command)
            logger.info(f'{log_prefix} ‘{name}’ finished.')


def static_build(**kwargs):
    """Callback for Wagtail publish and unpublish signals."""
    # Spawn a process to do the actual build.
    process = Process(target=_static_build_async)
    process.start()


page_published.connect(static_build)
page_unpublished.connect(static_build)
