import os
import shutil

from django.conf import settings
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'Special build command that accounts for a relative path.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            default='portal',
            help=('Specify the path relative to the domain where the '
                  'developer-portal will live.'),
        )

    def handle(self, **options):
        path = options['path']
        settings.STATIC_URL = '/' + path + settings.STATIC_URL
        settings.BUILD_DIR = os.path.join(settings.BUILD_DIR, path)
        static_parent = os.path.join(settings.BUILD_DIR, path)
        shutil.rmtree(settings.BUILD_DIR, ignore_errors=True)
        os.makedirs(static_parent)
        call_command('build', '--build-dir=' + settings.BUILD_DIR,
                     '--keep-build-dir')
        shutil.move(os.path.join(static_parent, 'static'),
                    settings.BUILD_DIR)
        shutil.rmtree(static_parent)
