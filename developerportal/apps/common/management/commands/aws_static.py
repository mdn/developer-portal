from django.core.management.base import BaseCommand, CommandError
from developerportal.utils import upload_file


class Command(BaseCommand):
    def handle(self, *args, **options):
        upload_file()
