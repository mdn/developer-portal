import logging

from django.conf import settings
from django.test.client import RequestFactory

from wagtailbakery.views import AllPublishedPagesView

logger = logging.getLogger(__name__)


class AllPublishedPagesViewAllowingSecureRedirect(AllPublishedPagesView):
    """Extension of `AllPublishedPagesView` that detects application-level SSL
    redirection in order to avoid an issue where rendered pages end up being 0 bytes

    See https://github.com/wagtail/wagtail-bakery/issues/24 for confirmation of the
    issue and the discussion on https://github.com/wagtail/wagtail-bakery/pull/25
    that points to a custom view being the (current) workaround. Ideally we'll be
    able to replace this when that issue is resolved.

    The following code is taken from that closed PR, which adds the `secure_request`
    variable.
    """

    def build_object(self, obj):
        """
        Build wagtail page and set SERVER_NAME to retrieve corresponding site
        object.
        """
        site = obj.get_site()
        logger.debug("Building %s" % obj)
        secure_request = site.port == 443 or getattr(
            settings, "SECURE_SSL_REDIRECT", False
        )
        self.request = RequestFactory(SERVER_NAME=site.hostname).get(
            self.get_url(obj), secure=secure_request
        )
        self.set_kwargs(obj)
        path = self.get_build_path(obj)
        self.build_file(path, self.get_content(obj))
