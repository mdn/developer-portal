from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.http import Http404, HttpResponseForbidden
from django.views.defaults import page_not_found, permission_denied, server_error
from django.views.generic import TemplateView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from ratelimit.exceptions import Ratelimited

from .apps.common.feed import RssFeeds
from .apps.common.views import rate_limited

urlpatterns = [
    url("", include("developerportal.apps.health.urls")),
    url(r"^django-admin/", admin.site.urls),
    url(r"^admin/", include(wagtailadmin_urls)),
    url(r"^documents/", include(wagtaildocs_urls)),
    url(r"^sitemap\.xml$", sitemap),
    url(r"^posts-feed/", RssFeeds()),
    url(r"^auth/", include("mozilla_django_oidc.urls")),
    url(r"^search/", include("developerportal.apps.search.urls")),
    url(
        r"^robots\.txt$",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
]


# Custom 403 handling, sending either a rate-limited response or a regular Forbidden
def handler403(request, exception=None):
    if isinstance(exception, Ratelimited):
        return rate_limited(request, exception)
    return permission_denied(request, exception)


if settings.DEBUG:
    urlpatterns += [
        url(r"^429/$", rate_limited, {"exception": Ratelimited()}),
        url(r"^403/$", permission_denied, {"exception": HttpResponseForbidden()}),
        url(r"^404/$", page_not_found, {"exception": Http404()}),
        url(r"^500/$", server_error),
    ]

    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    from django.views.static import serve

    # Serve media files directly.
    urlpatterns += [
        url(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})
    ]


# For anything not caught by a more specific rule above, hand over to
# Wagtail's page serving mechanism. This should be the last pattern in
# the list:
urlpatterns += [url(r"", include(wagtail_urls))]
