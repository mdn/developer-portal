from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from developerportal.apps.search import views as search_views

urlpatterns = [
    url('', include('developerportal.apps.health.urls')),

    url(r'^django-admin/', admin.site.urls),

    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'^search/$', search_views.search, name='search'),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Add style guide URL
    urlpatterns += [url(r'^style-guide/', TemplateView.as_view(
        template_name='style-guide.html'))]


# For anything not caught by a more specific rule above, hand over to
# Wagtail's page serving mechanism. This should be the last pattern in
# the list:
urlpatterns += [url(r'', include(wagtail_urls))]
