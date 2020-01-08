import logging
import os
import shutil

from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.utils.timezone import now as tz_now

from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core.signals import page_published, page_unpublished

from developerportal.apps.taskqueue.celery import (
    STATIC_BUILD_JOB_ATTEMPT_FREQUENCY,
    app,
)

from .context_managers import redis_lock
from .models import StaticBuild

logging.basicConfig(level=os.environ.get("LOGLEVEL", logging.INFO))
logger = logging.getLogger(__name__)


class ArticleAdmin(ModelAdmin):
    model = StaticBuild
    menu_label = "Manually request a static build"
    menu_icon = "doc-full"
    add_to_settings_menu = True


modeladmin_register(ArticleAdmin)


# === TASK QUEUE / CELERY CODE ===

# A note on the approach here:
#
# We run the build-and-sync process async so that it doesn't block Wagtail
# when a page is published. We also process the entire site each time, to avoid
# the risk of some pages remaining stale but containing data from pages that
# have since been updated (eg an Article that's also shown on a Topic page).
# Full-replacement is the safest approach and doesn't need to be optimised yet.
#
# However, if we just added build tasks directly to the task queue, it'd be very
# easy to end up with concurrent build-and-sync processes taking place, but with
# noguarantee about the order in which they will complete, which risks the
# "wrong" expected state being the one that ends up remaining published.
# Also, it's worth avoiding unnecessary CPU and I/O costs for concurrent builds
# that we don't need
#
# To this end, the approach we're taking is:
#
# * When a Page is published (which means we want a static build-and-sync), it
#   spawns a Celery task which, when processed, simply sets a flag to say a
#   "build is needed".
#
# * A separate periodic Celerybeat task checks for that flag and, if it finds
#   it, takes down the flag and starts a static build
#
# * The static build runs within a simple distributed lock, so if a build it
#   still running when the periodic task runs and finds a new build has been
#   requestd, we don't allow a concurrent build, but we do preserve/re-instate
#   the flag ready for the next attempt by the periodic task. This means we only
#   ever have one build in progress, but we can immediately follow a build with
#   a new one if there's still an unsatisfied request for a build.

EXPECTED_BUILD_AND_SYNC_JOB_FUNC_NAME = (
    "developerportal.apps.staticbuild.wagtail_hooks._static_build_async"
)

SENTINEL_KEY_TIMEOUT = (
    60 * 15
)  # 15 mins - longer than a build-and-sync should be taking
SENTINEL_KEY_NAME = "devportal-fresh-build-and-sync-needed"
SENTINEL_LOCK_NAME = "deveportal-sentinel-lock"
BUILD_LOCK_NAME = "deveportal-build-and-sync-lock"

# Evaluate this now to avoid an awkward edge case during the former concurrent
# builds where it (somehow) an os.path.join()ed value involving
# settings.BUILD_DIR gets re-set with the joined value...
BUILD_ROOT_DIR = settings.BUILD_DIR


def _generate_build_path():
    """Generate a unique build path to avoid concurrent builds clashing"""
    return os.path.join(BUILD_ROOT_DIR, tz_now().isoformat())


def _is_build_and_sync_job(job_details):
    return job_details["name"] == EXPECTED_BUILD_AND_SYNC_JOB_FUNC_NAME


def _set_build_needed_sentinel(oid):
    """Idempotent flag that a static build should be attempted when next checked
    (which is within STATIC_BUILD_JOB_ATTEMPT_FREQUENCY seconds)"""
    with redis_lock(SENTINEL_LOCK_NAME, oid=oid):
        cache.set(SENTINEL_KEY_NAME, True, SENTINEL_KEY_TIMEOUT)


def _get_build_needed_sentinel(oid):
    # Check to see if a build has been requested, and if so, wipe the key.
    with redis_lock(SENTINEL_LOCK_NAME, oid=oid):
        sentinel_val = cache.get(SENTINEL_KEY_NAME)
        cache.delete(SENTINEL_KEY_NAME)
    return sentinel_val


@app.task(bind=True)
def _request_static_build(self):
    log_prefix = "[Static-build-and-sync requester]"
    logger.info(
        f"{log_prefix} Caching a sentinel marker to request a static build "
        f"within the next {STATIC_BUILD_JOB_ATTEMPT_FREQUENCY} seconds."
    )
    _set_build_needed_sentinel(oid=self.app.oid)


@app.task(bind=True)
def _static_build_async(self, pipeline=settings.STATIC_BUILD_PIPELINE):
    """Schedulable task that, if it gets the appropriate flag as a sign to proceed,
    calls each command in the static build pipeline in turn.

    See setup_periodic_tasks, above.
        pipeline (optional): tuple of strings that map to wagtail-bakery commands
    """
    logger.debug("Entering _static_build_async")
    log_prefix = "[Static-build-and-sync]"
    build_dir = None

    sentinel_val = _get_build_needed_sentinel(oid=self.app.oid)
    if sentinel_val is not True:
        logger.info(f"{log_prefix} No fresh static build requested.")
        return

    # If we reach here, an actual build is needed, but only if one is not
    # already in progress.
    logger.info(f"{log_prefix} Attempting fresh build")
    with redis_lock(lock_id=BUILD_LOCK_NAME, oid=self.app.oid) as lock_acquired:
        if lock_acquired:

            if not settings.DEBUG:
                build_dir = _generate_build_path()
                logger.info(f"{log_prefix} Created temporary build dir {build_dir}")

            for name, command in pipeline:
                if not settings.DEBUG:
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
                else:
                    logger.info(
                        (
                            f"{log_prefix} (wagtail-bakery) command '{name}' "
                            "skipped because DEBUG=True."
                        )
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
            _set_build_needed_sentinel(oid=self.app.oid)


def static_build(**kwargs):
    """Callback for Wagtail publish and unpublish signals to spawn a
    task-queue job to do the actual build, if required"""
    _request_static_build.delay()


page_published.connect(static_build)
page_unpublished.connect(static_build)
