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
    return {"PAGINATION_QUERYSTRING_KEY": settings.PAGINATION_QUERYSTRING_KEY}
