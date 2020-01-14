from .production import *

CACHES["default"]["KEY_PREFIX"] = "test"

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
MEDIA_ROOT = "/tmp/test-media/"
