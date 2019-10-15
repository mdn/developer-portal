import logging
import os
import shutil

from django.conf import settings
from django.core.management import call_command
from django.utils.timezone import now as tz_now

from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core.signals import page_published, page_unpublished

from developerportal.apps.staticbuild.celery import app

from .models import StaticBuild

logging.basicConfig(level=os.environ.get("LOGLEVEL", logging.INFO))
logger = logging.getLogger(__name__)


class ArticleAdmin(ModelAdmin):
    model = StaticBuild
    menu_label = "Manually trigger a static build"
    menu_icon = "doc-full"
    add_to_settings_menu = True


modeladmin_register(ArticleAdmin)


def _generate_build_path():
    """Generate a unique build path to avoid concurrent builds clashing"""
    return os.path.join(settings.BUILD_DIR, tz_now().isoformat())


@app.task
def _static_build_async(force=False, pipeline=settings.STATIC_BUILD_PIPELINE):
    """Calls each command in the static build pipeline in turn."""
    log_prefix = "Static build task"
    build_dir = None

    if settings.DEBUG is False or force:
        build_dir = _generate_build_path()
        logger.info(f"{log_prefix} Created temporary build dir {build_dir}")

    for name, command in pipeline:
        if settings.DEBUG and not force:
            logger.info(f"{log_prefix} (wagtail-bakery) command '{name}' skipped.")
        else:
            logger.info(f"{log_prefix} (wagtail-bakery) command '{name}' started.")
            # We're passing in a specific output dir so that we don't risk
            # concurrent builds clashing
            call_command(command, build_dir=build_dir)
            logger.info(f"{log_prefix} (wagtail-bakery) command '{name}' finished.")

    if build_dir:
        shutil.rmtree(build_dir)
        logger.info(f"{log_prefix} Deleted temporary build dir {build_dir}")


def static_build(**kwargs):
    """Callback for Wagtail publish and unpublish signals to spawn a
    task-queue job to do the actual build"""
    force = kwargs.get("force", False)
    _static_build_async.delay(force=force)


page_published.connect(static_build)
page_unpublished.connect(static_build)
