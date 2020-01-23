from urllib.parse import urlparse

from .base import *  # noqa

DEBUG = False
DEBUG_PROPAGATE_EXCEPTIONS = True

ALLOWED_HOSTS = []

if BASE_URL:
    # This is the URL that Wagtail's CMS runs on.
    ALLOWED_HOSTS.append(urlparse(BASE_URL).hostname)

if EXPORTED_SITE_URL:
    # This is the URL the CDNed site will be served from.
    # It is different from the BASE_URL (where Wagtail is running).
    ALLOWED_HOSTS.append(urlparse(EXPORTED_SITE_URL).hostname)

try:
    from .local import *  # noqa
except ImportError:
    pass
