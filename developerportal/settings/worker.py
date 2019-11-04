# Extra settings that ONLY apply to the Celery workers/schedulers

from .production import *

# GOOGLE_ANALYTICS is _only_ set in this file, because we ONLY want it
# to appear in the static site, not the live-rendered site.
GOOGLE_ANALYTICS = os.environ.get("GOOGLE_ANALYTICS")
