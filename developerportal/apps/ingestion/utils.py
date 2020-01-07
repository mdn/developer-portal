"""Helpers for feed ingestion"""
import datetime
import logging

from dateutil.parser import parse as parse_datetime

import feedparser

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
