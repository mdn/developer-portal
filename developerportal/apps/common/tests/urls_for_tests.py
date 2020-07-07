from django.conf.urls import url

from developerportal.urls import urlpatterns as real_urlpatterns
from ratelimit.exceptions import Ratelimited

from ..views import rate_limited

# custom URL patterns for this test module so we can access rate_limted when DEBUG=False
urlpatterns = real_urlpatterns + [
    url(r"^test-rate-limited/$", rate_limited, {"exception": Ratelimited()})
]
