from .settings.base import GOOGLE_ANALYTICS, MAPBOX_ACCESS_TOKEN

def google_analytics(request):
    return {'GOOGLE_ANALYTICS': GOOGLE_ANALYTICS}

def mapbox_access_token(request):
    return {'MAPBOX_ACCESS_TOKEN': MAPBOX_ACCESS_TOKEN}
