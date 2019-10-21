from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

CELERY_BROKER_URL = "redis://redis:6379"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable production defaults that get in the way of local development
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Swap out the default use of S3 for user media to instead use local machine
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

try:
    from .local import *
except ImportError:
    pass
