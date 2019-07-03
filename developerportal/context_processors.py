from .settings.base import GOOGLE_ANALYTICS

def google_analytics(request):
    return {'GOOGLE_ANALYTICS': GOOGLE_ANALYTICS}
