import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from developerportal.apps.staticbuild.utils import S3Uploader


logging.basicConfig(level=os.environ.get('LOGLEVEL', logging.INFO))
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Upload the ‘build’ directory to Amazon S3.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--build-dir',
            default=settings.BUILD_DIR,
            help=('Specify the path of the build directory. Will use '
                  'settings.BUILD_DIR by default.'),
            nargs='?',
            type=str,
        )
        parser.add_argument(
            '--bucket',
            default=settings.S3_BUCKET,
            help='The Amazon S3 bucket to upload files to.',
            nargs='?',
            type=str,
        )

    def handle(self, bucket=None, build_dir=None, **options):
        logger.info('S3 upload started')

        if not bucket:
            logger.info('S3 upload aborted, no bucket specified')
            return

        uploader = S3Uploader(bucket=bucket)
        uploader.upload_directory(build_dir)
        logger.info('S3 upload finished')
