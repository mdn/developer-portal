from django.shortcuts import render
from django.views.decorators.cache import never_cache


@never_cache
def rate_limited(request, exception):
    """Render a rate-limited exception page"""
    response = render(request, "429.html", status=429)
    response["Retry-After"] = "60"
    return response
