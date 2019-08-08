from .settings.base import GOOGLE_ANALYTICS, MAPBOX_ACCESS_TOKEN

def google_analytics(request):
    return {'GOOGLE_ANALYTICS': GOOGLE_ANALYTICS}

def mapbox_access_token(request):
    return {'MAPBOX_ACCESS_TOKEN': MAPBOX_ACCESS_TOKEN}

def directory_pages(request):
    from .apps.articles.models import Articles
    from .apps.events.models import Events
    from .apps.people.models import People
    from .apps.topics.models import Topics
    return {
        'directory_pages': {
            'articles': Articles.objects.first(),
            'events': Events.objects.first(),
            'people': People.objects.first(),
            'topics': Topics.objects.first(),
        },
    }
