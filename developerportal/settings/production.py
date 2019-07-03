from urllib.parse import urlparse

from .base import *

DEBUG = False
ALLOWED_HOSTS = [urlparse(BASE_URL).hostname]

try:
    from .local import *
except ImportError:
    pass
