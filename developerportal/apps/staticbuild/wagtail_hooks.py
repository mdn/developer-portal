import logging
from multiprocessing import Process
import os

from django.conf import settings
from django.core.management import call_command

from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core.signals import page_published, page_unpublished

from .models import StaticBuild


logging.basicConfig(level=os.environ.get('LOGLEVEL', logging.INFO))
logger = logging.getLogger(__name__)


class ArticleAdmin(ModelAdmin):
    model = StaticBuild
    menu_icon = 'doc-full'
    add_to_settings_menu = True


modeladmin_register(ArticleAdmin)


def _static_build_async(force=False, pipeline=settings.STATIC_BUILD_PIPELINE, **kwargs):
    """Calls each command in the static build pipeline in turn."""
    log_prefix = 'Static build task'
    for name, command in pipeline:
        if settings.DEBUG and not force:
            logger.info(f'{log_prefix} ‘{name}’ skipped.')
        else:
            logger.info(f'{log_prefix} ‘{name}’ started.')
            call_command(command)
            logger.info(f'{log_prefix} ‘{name}’ finished.')


def static_build(**kwargs):
    """Callback for Wagtail publish and unpublish signals."""
    # Spawn a process to do the actual build.
    process = Process(target=_static_build_async, kwargs=kwargs)
    process.start()


page_published.connect(static_build)
page_unpublished.connect(static_build)
