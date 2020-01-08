from django.conf import settings


def google_analytics(request):
    DEFAULT_GA_PLACEHOLDER_VAL = "0"  # from the k8s Makefile
    output = {}
    ga_code = settings.GOOGLE_ANALYTICS
    if ga_code and ga_code != DEFAULT_GA_PLACEHOLDER_VAL:
        output.update({"GOOGLE_ANALYTICS": ga_code})
    return output


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


def pagination_constants(request):
    from developerportal.apps.common import constants

    return {"PAGINATION_QUERYSTRING_KEY": constants.PAGINATION_QUERYSTRING_KEY}


def filtering_constants(request):
    from developerportal.apps.common import constants

    return {
        "TOPIC_QUERYSTRING_KEY": constants.TOPIC_QUERYSTRING_KEY,
        "ROLE_QUERYSTRING_KEY": constants.ROLE_QUERYSTRING_KEY,
        "COUNTRY_QUERYSTRING_KEY": constants.COUNTRY_QUERYSTRING_KEY,
        "YEAR_MONTH_QUERYSTRING_KEY": constants.YEAR_MONTH_QUERYSTRING_KEY,
    }
