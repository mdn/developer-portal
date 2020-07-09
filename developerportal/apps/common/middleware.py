"""Custom middleware for Developer Portal"""

from django.conf import settings

from ratelimit import ALL
from ratelimit.core import is_ratelimited
from ratelimit.exceptions import Ratelimited


def rate_limiter(get_response):
    """Enforces rate-limiting on all views.

    Custom wrapper for django-ratelimit so we can use it with Wagtail.

    Why are we rate-limiting ALL views and not just those that the CDN won't
    be cacheing? Here's the logic:

    * Most production traffic spikes will be handled by the CDN. The most likely pages
    to be CDN cache misses are search ones, because the GET params can contain anything
    * Rate-limiting Search is the real goal here, but we have challenges to overcome.
    * Search appears on three pages - one is a vanilla Django view 'search:site-search'
    two are Wagtail pages which are served by 'wagtail.core.views.serve', and those
    pages handle GET-based search queries themselves -- they don't hand off to the
    `search:site-search` view
    * We can't decorate the Wagtail view with django-ratelimit, but we can use
    middleware to do perform rate-limiting checks, using django-ratelimit's core helpers
    * However, django-ratelimit's API/helpers need a request object because they
    rate-limit based on a view func, not a path from the URL, so we can't easily target
    specific Wagtail-served pages for rate limiting.

    So: given that non-search pages will be cached by the CDN, we rate-limit ALL the
    pages served by the site. In the wild, once the CDN is warm, the majority of
    uncached requests will be search ones, so we'll effectively be only rate-limiting
    them.

    The limit set will be one which should not impair real-world content curation via
    /admin/ either.

    """
    # One-time configuration and initialization here

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # Set an arbitrary catch-all group name, because we need to provide
        # a group because we don't have the view func available here.
        group = "all_requests"

        old_limited = getattr(request, "limited", False)
        ratelimited = is_ratelimited(
            request=request,
            group=group,
            key="ip",
            rate=settings.DEVPORTAL_RATELIMIT_DEFAULT_LIMIT,
            increment=True,
            method=ALL,  #  ie include GET, not just ratelimit.UNSAFE methods
        )
        request.limited = ratelimited or old_limited
        if ratelimited:
            raise Ratelimited()

        response = get_response(request)
        return response

    return middleware


def set_remote_addr_from_forwarded_for(get_response):
    """
    Middleware that sets REMOTE_ADDR based on HTTP_X_FORWARDED_FOR, if the
    latter is set. This is useful if you're sitting behind a reverse proxy
    """

    def middleware(request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs.
            # The client's claimed IP will be the first in the list, as CDN etc
            # append to the end.
            forwarded_for = forwarded_for.split(",")[0].strip()
            request.META["REMOTE_ADDR"] = forwarded_for

        response = get_response(request)
        return response

    return middleware
