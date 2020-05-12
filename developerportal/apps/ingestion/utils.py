"""Helpers for feed ingestion"""
import datetime
import hashlib
import logging
from io import BytesIO

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.db import transaction
from django.utils.text import slugify
from django.utils.timezone import now as tz_now

from dateutil.parser import parse as parse_datetime
from wagtail.admin.mail import send_notification
from wagtail.core.models import Page
from wagtail.embeds.blocks import EmbedValue

import feedparser
import requests

from ..externalcontent import models as externalcontent_models
from ..mozimages.models import MozImage
from ..videos import models as video_models
from .constants import INGESTION_USER_USERNAME
from .models import IngestionConfiguration

FEED_TYPE_ATOM = "atom"
FEED_TYPE_RSS = "rss"

VALID_FEED_TYPES = (FEED_TYPE_ATOM, FEED_TYPE_RSS)

logger = logging.getLogger(__name__)


def _get_item_image(entry) -> str:
    if entry and hasattr(entry, "media_thumbnail") and entry.media_thumbnail[0]:
        # Gets YT thumbnail
        return entry.media_thumbnail[0]["url"]

    elif (
        entry
        and hasattr(entry, "media_content")
        and entry.media_content[0]["medium"] == "image"
    ):
        # Gets RSS image
        return entry.media_content[0]["url"]

    return ""


def fetch_external_data(feed_url: str, last_synced: datetime.datetime) -> list:
    """For the given feed_url, fetch all entries that are timestamped since
    last_synced and return them as a list of 0...n standardised dictionaries
    in the format:

    [
        {
            "title": <str> - title of the entry
            "authors": [<str>] - 0...n author names,
            "url": <str> - URL of the thing we want to link to as external content,
            "image_url": <str> - URL of any accompanying image,
            "timestamp: <datetime.datetime> - item's own timestamp
        },
        ...
    ]
    """

    output = []
    parsed_data = feedparser.parse(feed_url)

    # DANGER: we can't do this next check with feeds that lack an <updated> node:
    if "updated" in parsed_data.feed.keys():
        # Check we have something that's worth parsing
        feed_last_updated = parse_datetime(parsed_data.feed.updated)
        if feed_last_updated <= last_synced:
            logger.info(
                f"Feed's last updated date ({feed_last_updated}) "
                f"was not after last_synced ({last_synced})"
            )
            return output

    for entry in parsed_data.entries:
        timestamp = parse_datetime(entry.published)
        if timestamp <= last_synced:
            # no point continuing
            break

        output.append(
            dict(
                title=entry.title,
                authors=[x["name"] for x in entry.authors],
                url=entry.link,
                image_url=_get_item_image(entry),
                timestamp=timestamp,
            )
        )

    return output


def _get_factory_func(model_name):
    """Get an appropriate helper function generate the desired ingestion target.
    That func will be passed into generate_draft_from_external_data"""
    if model_name == "Video":
        func = _make_video_page
    elif model_name == "ExternalArticle":
        func = _make_external_article_page
    else:
        raise NotImplementedError(
            f"This is not intended to be used on the {model_name} class "
            "without further development."
        )

    return func


def ingest_content(type_: str):
    """For the given type_:
    * fetch the relevant data from the configured sources
    * for each item of source data:
        * create an appropriate ExternalContent page subclass, as a draft
    * update the last_sync timestamp for each configured source
    * submit all just-created draft pages for moderation
    """

    _now = tz_now()
    model_name = type_

    configs = IngestionConfiguration.objects.filter(integration_type=type_)

    factory_func = _get_factory_func(model_name)

    ingestion_user = User.objects.get(username=INGESTION_USER_USERNAME)

    for config in configs:
        draft_page_revision_buffer = []

        with transaction.atomic():
            data_from_source = fetch_external_data(
                feed_url=config.source_url, last_synced=config.last_sync
            )
            config.last_sync = _now
            config.save()

            for data in data_from_source:
                data.update(owner=ingestion_user)
                try:
                    draft_page = generate_draft_from_external_data(
                        factory_func=factory_func, data=data
                    )
                except ValidationError as ve:
                    logger.warning("Problem ingesting article from %s: %s", data, ve)
                else:
                    draft_page.owner = ingestion_user
                    draft_page.save()
                    revision = draft_page.save_revision(
                        submitted_for_moderation=True, user=ingestion_user
                    )
                    draft_page_revision_buffer.append(revision)

        # If the transaction completes, we send the notification emails. If the
        # notifications don't send even tho the data is now set in the DB, it's
        # not the end of the world: the main CMS admin page will still
        # show the items needing approval.
        if settings.NOTIFY_AFTER_INGESTING_CONTENT:
            for revision in draft_page_revision_buffer:
                notification_success = send_notification(
                    page_revision_id=revision.id,
                    notification="submitted",
                    excluded_user_id=ingestion_user.id,
                )
                if not notification_success:
                    logger.warning(
                        "Failed to send notification that %s was created.",
                        revision.page,
                    )


def _store_external_image(image_url: str) -> MozImage:
    """Download an image from the given URL and store it as a Wagtail image"""
    response = requests.get(image_url)
    filename = image_url.split("/")[-1]
    image = MozImage(
        title=filename, file=ImageFile(BytesIO(response.content), name=filename)
    )
    image.save()
    return image


def _get_slug(data):
    """Return a slug for the Page being imported, making it unique (enough) by
    adding a 12-char truncated hash of the whole data payload at the end
    eg "the-mozilla-story-a1b2c3d4e5f6"

    """
    MAX_SLUG_LENGTH = (
        242
    )  # Slugfield's max is 255, minus 12 for trucated hash (below), minus one for dash

    hash_ = hashlib.sha1(str(data).encode("utf-8")).hexdigest()[:12]
    slug = slugify(data["title"])[:MAX_SLUG_LENGTH]
    return f"{slug}-{hash_}"


def _make_external_article_page(data, extra_kwargs):
    "Callable that takes care of making ExternalArticles"
    instance_data = dict(
        title=data["title"],
        draft_title=data["title"],
        slug=_get_slug(data),
        date=data["timestamp"].date(),
        live=False,  # Needs to be set because default is True
        has_unpublished_changes=True,  # again, overriding a default
        owner=extra_kwargs.get("owner"),
        external_url=data["url"],
    )

    page = externalcontent_models.ExternalArticle(**instance_data)
    # These get added to the root page
    parent_page = Page.objects.filter(slug="root").first().specific
    parent_page.add_child(instance=page)  # Takes care of saving

    return page


def _make_video_page(data, extra_kwargs):

    _video_url = data.get("url")

    instance_data = dict(
        title=data["title"],
        draft_title=data["title"],
        slug=_get_slug(data),
        date=data["timestamp"].date(),
        live=False,  # Needs to be set because default is True
        has_unpublished_changes=True,  # again, overriding a default
        owner=extra_kwargs.get("owner"),
    )

    page = video_models.Video(**instance_data)
    page.video_url = [("embed", EmbedValue(_video_url))]
    parent_page = Page.objects.filter(slug="videos").first().specific
    parent_page.add_child(instance=page)  # Takes care of saving

    return page


@transaction.atomic()
def generate_draft_from_external_data(factory_func, data, **kwargs):
    """Create a draft page of the appropriate `model` (eg: ExternalArticle,
    Video) from the given `factory_func` and `data`, including any associated
    thumbnail (which is saved down as a Wagtail image on the card_image field).
    """
    logger.info(
        f"Generating a new draft using {factory_func.__name__} from {str(data)}"
    )

    page = factory_func(data=data, extra_kwargs=kwargs)

    # If there's an image to be associated, do that.
    if data.get("image_url"):
        image = _store_external_image(data["image_url"])
        page.card_image = image
        page.save()
    return page
