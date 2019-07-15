from django.core.management.base import BaseCommand, CommandError
from developerportal.utils import upload_file


class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.info('command called upload')
        upload_file()
        help_text=('Custom admin command for aws build'))
