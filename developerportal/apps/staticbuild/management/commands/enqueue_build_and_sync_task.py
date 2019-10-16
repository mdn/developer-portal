import logging

from django.core.management.base import BaseCommand

from developerportal.apps.staticbuild.wagtail_hooks import static_build

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management to manually enqueue a request for a "build-and-sync-to-S3" of the
    current/latest published state of the site."""

    def handle(self, *args, **options):
        logger.info("Adding a request for a build-and-sync request to the task queue.")
        static_build()
        logger.info("Build-and-sync request added to task queue.")
