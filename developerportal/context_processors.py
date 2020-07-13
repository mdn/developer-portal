import logging

from django.conf import settings
from django.core.cache import cache

from wagtail.contrib.redirects.models import Redirect

logger = logging.getLogger(__name__)


def google_analytics(request):
    DEFAULT_GA_PLACEHOLDER_VAL = "0"  # from the k8s Makefile
    output = {}
    ga_code = settings.GOOGLE_ANALYTICS
    if ga_code and ga_code != DEFAULT_GA_PLACEHOLDER_VAL:
        output.update({"GOOGLE_ANALYTICS": ga_code})
    return output


def blog_link(request):

    blog_link = (
        Redirect.objects.filter(redirect_link="https://hacks.mozilla.org")
        .values_list("old_path", flat=True)
        .first()
    )  # Returns a string or None

    return {"BLOG_LINK": blog_link}


def mapbox_access_token(request):
    return {"MAPBOX_ACCESS_TOKEN": settings.MAPBOX_ACCESS_TOKEN}


def directory_pages(request):
    from .apps.articles.models import Articles
    from .apps.events.models import Events
    from .apps.people.models import People
    from .apps.topics.models import Topics

    return {
        "directory_pages": {
            "articles": Articles.published_objects.first(),
            "events": Events.published_objects.first(),
            "people": People.published_objects.first(),
            "topics": Topics.published_objects.first(),
        }
    }


def topics_title(request):
    """Get a name to use for the section formerly known as "Topics", based on
    whatever the Topics page is currently called.

    NB: this assumes the Topics page's title is a plural."""
    from .apps.topics.models import Topics

    _key = Topics.CACHE_KEY_TOPICS_TITLE

    title = cache.get(_key)
    if not title:
        topics_page = Topics.published_objects.first()
        if not topics_page:
            # Something is very wrong here, but temporarily fall back regardless
            # without caching
            return {"TOPICS_TITLE_LABEL": "Topics"}

        title = topics_page.title
        cache.set(_key, title, settings.CACHE_TIME_VERY_LONG)

    return {"TOPICS_TITLE_LABEL": title}


def pagination_constants(request):
    from developerportal.apps.common import constants

    return {"PAGINATION_QUERYSTRING_KEY": constants.PAGINATION_QUERYSTRING_KEY}


def filtering_constants(request):
    from developerportal.apps.common import constants

    return {
        "TOPIC_QUERYSTRING_KEY": constants.TOPIC_QUERYSTRING_KEY,
        "ROLE_QUERYSTRING_KEY": constants.ROLE_QUERYSTRING_KEY,
        "LOCATION_QUERYSTRING_KEY": constants.LOCATION_QUERYSTRING_KEY,
        "DATE_PARAMS_QUERYSTRING_KEY": constants.DATE_PARAMS_QUERYSTRING_KEY,
        "PAST_EVENTS_QUERYSTRING_VALUE": constants.PAST_EVENTS_QUERYSTRING_VALUE,
        "DEFAULT_EVENTS_LOOKAHEAD_WINDOW_MONTHS": constants.DEFAULT_EVENTS_LOOKAHEAD_WINDOW_MONTHS,  # noqa E501
        "SEARCH_QUERYSTRING_KEY": constants.SEARCH_QUERYSTRING_KEY,
    }
