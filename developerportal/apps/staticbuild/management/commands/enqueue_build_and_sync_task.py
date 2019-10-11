import logging

from django.core.management.base import BaseCommand

from developerportal.apps.staticbuild.wagtail_hooks import _static_build_async

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management to manually queue up a "build-and-sync-to-S3" of the
    current published state of the site"""

    def handle(self, *args, **options):
        logger.info("Adding a build-and-sync request to the task queue.")
        _static_build_async.delay()
        logger.info("Build-and-sync added to task queue.")
