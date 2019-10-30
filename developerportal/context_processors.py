from django.conf import settings


def google_analytics(request):
    return {"GOOGLE_ANALYTICS": settings.GOOGLE_ANALYTICS}


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
