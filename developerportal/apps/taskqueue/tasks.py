import logging
import os

from django.core.management import call_command

import requests
from developerportal.apps.taskqueue.celery import app

from ..common.utils import get_all_urls_from_sitemap
from ..events.models import Events
from ..people.models import People
from ..topics.models import Topics
from .utils import invalidate_cdn

logging.basicConfig(level=os.environ.get("LOGLEVEL", logging.INFO))
logger = logging.getLogger(__name__)


@app.task
def publish_scheduled_pages():
    log_prefix = "[Publish scheduled pages]"
    logger.info(f"{log_prefix} Trying to publish/unpublish scheduled pages")
    call_command("publish_scheduled_pages")


@app.task
def invalidate_entire_cdn():
    log_prefix = "[Invalidate entire CDN]"
    logger.info(f"{log_prefix} Issuing purge command")
    invalidate_cdn()


@app.task
def selectively_invalidate_cdn():
    """Purge certain pages which have content isn't suitable for long-term
    cacheing by the CDN.

    Scheduled to run once a day, after midnight (UTC)

    A good example of this is the Events page, which shows future and past
    events, and what counts as 'future' or 'past' depends on when the page
    is viewed, so a stale page in the CDN would be significantly out of date.
    """

    log_prefix = "[Selectively invalidate CDN]"

    events_root_path = Events.objects.first().url
    people_root_path = People.objects.first().url
    topics_root_path = Topics.objects.first().url

    selected_targets = [
        # Start with the main Events page
        f"{events_root_path}*",
        # TODO: in the future, it would be good to make these very specific,
        # by hitting the DB to work out which People and Topic pages reference
        # Events which have just gone past
        f"{people_root_path}*",
        f"{topics_root_path}*",
    ]

    logger.info(
        f"{log_prefix} Issuing purge command for "
        f"selected CDN keys: {selected_targets}"
    )
    invalidate_cdn(invalidation_targets=selected_targets)


@app.task
def warm_entire_cdn():
    """For use after blanket invalidation, this function iterates through all
    URLs listed in the sitemap.

    Note that this can be several hundreds of pages, hence it needs to happen
    in a background task.
    """
    urls = get_all_urls_from_sitemap()

    return _warm_cdn(urls)


def _warm_cdn(urls):

    total_urls = len(urls)
    logger.info(f"Warming CDN. {total_urls} URLs obtained from sitemap.")

    for i, url in enumerate(urls):
        logger.info(f"Requesting {i+1}/{total_urls}: {url}")
        response = requests.get(url)
        if response.status_code != requests.codes.ok:
            logger.exception(f"Failed to get {url} ")

    logger.info("Warming complete.")
