import logging
import os
import shutil

from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.utils.timezone import now as tz_now

from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core.signals import page_published, page_unpublished

from developerportal.apps.staticbuild.celery import (
    STATIC_BUILD_JOB_ATTEMPT_FREQUENCY,
    app,
)

from .context_managers import redis_lock
from .models import StaticBuild

logging.basicConfig(level=os.environ.get("LOGLEVEL", logging.INFO))
logger = logging.getLogger(__name__)


class ArticleAdmin(ModelAdmin):
    model = StaticBuild
    menu_label = "Manually trigger a static build"
    menu_icon = "doc-full"
    add_to_settings_menu = True


modeladmin_register(ArticleAdmin)


# === TASK QUEUE / CELERY CODE ===

# Concurrent builds, while wasteful, are possible when running Celery.
# _request_static_build tries to deal with this.

EXPECTED_BUILD_AND_SYNC_JOB_FUNC_NAME = (
    "developerportal.apps.staticbuild.wagtail_hooks._static_build_async"
)

# Evaluate this now to avoid an awkward edge cause during concurrent builds where it
# (somehow) an os.path.join()ed value involving settings.BUILD_DIR gets re-set with
# the joined value...
BUILD_ROOT_DIR = settings.BUILD_DIR

SENTINEL_KEY_TIMEOUT = (
    60 * 15
)  # 15 mins - longer than a build-and-sync should be taking
SENTINEL_KEY_NAME = "devportal-fresh-build-and-sync-needed"
SENTINEL_LOCK_NAME = "deveportal-sentinel-lock"
BUILD_LOCK_NAME = "deveportal-build-and-sync-lock"


def _generate_build_path():
    """Generate a unique build path to avoid concurrent builds clashing"""
    return os.path.join(BUILD_ROOT_DIR, tz_now().isoformat())


def _is_build_and_sync_job(job_details):
    return job_details["name"] == EXPECTED_BUILD_AND_SYNC_JOB_FUNC_NAME


def _set_build_needed_sentinel():
    """Idempotent flag that a static build should be attempted when next checked
    (which is within STATIC_BUILD_JOB_ATTEMPT_FREQUENCY seconds)"""
    with cache.lock(SENTINEL_LOCK_NAME):
        cache.set(SENTINEL_KEY_NAME, True, SENTINEL_KEY_TIMEOUT)
        print(cache.get(SENTINEL_KEY_NAME))


@app.task
def _request_static_build(**kwargs):
    log_prefix = "[Static build requester]"
    logger.info(
        f"{log_prefix} Caching a sentinel marker to request a static build "
        f"within the next {STATIC_BUILD_JOB_ATTEMPT_FREQUENCY} seconds."
    )
    _set_build_needed_sentinel()


@app.task(bind=True)
def _static_build_async(self, force=False, pipeline=settings.STATIC_BUILD_PIPELINE):
    """Schedulable task that, if it gets the appropriate flag, calls each command
    in the static build pipeline in turn.

    See setup_periodic_tasks, above.

        force (optional): Boolean - used to run a build even when DEBUG is False
        pipeline (optional): tuple of strings that map to wagtail-bakery commands
    """
    logger.info("Starting _static_build_async")
    log_prefix = "[Static build]"
    build_dir = None

    if not force:
        # Check to see if a build has been requested, and if so, wipe they key.
        with cache.lock(SENTINEL_LOCK_NAME):
            print("BEFORE cache.get(SENTINEL_KEY_NAME)", cache.get(SENTINEL_KEY_NAME))
            sentinel_val = cache.get(SENTINEL_KEY_NAME)
            cache.delete(SENTINEL_KEY_NAME)
            print("AFTER cache.get(SENTINEL_KEY_NAME)", cache.get(SENTINEL_KEY_NAME))
            if sentinel_val is not True:
                logger.info(f"{log_prefix} No static build requested.")
                return

    # If we reach here, an actual build is needed, but only if one is not
    # already in progress.
    logger.info(f"{log_prefix}Starting fresh build")
    with redis_lock(lock_id=BUILD_LOCK_NAME, oid=self.app.oid) as lock_acquired:
        if lock_acquired:

            build_dir = _generate_build_path()
            logger.info(f"{log_prefix} Created temporary build dir {build_dir}")

            for name, command in pipeline:
                if settings.DEBUG and not force:
                    logger.info(
                        f"{log_prefix} (wagtail-bakery) command '{name}' skipped."
                    )
                else:
                    logger.info(
                        f"{log_prefix} (wagtail-bakery) command '{name}' started."
                    )
                    call_command(
                        command,
                        build_dir=build_dir,
                        verbosity=0,  # Else stdout is output as logger.WARNING
                    )
                    logger.info(
                        f"{log_prefix} (wagtail-bakery) command '{name}' finished."
                    )

            if build_dir:
                shutil.rmtree(build_dir)
                logger.info(f"{log_prefix} Deleted temporary build dir {build_dir}")
        else:
            # ie, we have no lock, so we give up and set a reminder to try again
            logger.info(
                f"{log_prefix} Skipping this build attempt: another is in progress. "
                "Setting the sentinel so we'll try again later."
            )
            _set_build_needed_sentinel()


def static_build(**kwargs):
    """Callback for Wagtail publish and unpublish signals to spawn a
    task-queue job to do the actual build, if required"""
    force = kwargs.get("force", False)
    _request_static_build.delay(force=force)


page_published.connect(static_build)
page_unpublished.connect(static_build)
