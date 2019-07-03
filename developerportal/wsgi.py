"""
WSGI config for developerportal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Load dev settings by default. To override this, set either:
# - DJANGO_ENV to e.g. production, or;
# - DJANGO_SETTINGS_MODULE to e.g. developerportal.settings.production (takes precedence).
env = os.environ.setdefault("DJANGO_ENV", "dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"developerportal.settings.{env}")

application = get_wsgi_application()
