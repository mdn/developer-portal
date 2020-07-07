from django.conf.urls import url
from django.test import TestCase, override_settings
from django.urls import reverse

from developerportal.urls import urlpatterns as real_urlpatterns
from ratelimit.exceptions import Ratelimited

from ..views import rate_limited

# Make the rate_limited view available to this test only without needing DEBUG=True.
# We prepend our test url(), else wagtail's catch-all at the bottom of
# real_urlpatterns will stop it being reached
urlpatterns = [
    url(
        r"^test-rate-limited/$",
        rate_limited,
        {"exception": Ratelimited()},
        name="test-rl-view",
    )
] + real_urlpatterns


@override_settings(ROOT_URLCONF=__name__)
class RateLimitViewTests(TestCase):
    def test_rate_limited__does_not_get_cached_at_cdn(self):
        resp = self.client.get(reverse("test-rl-view"))
        self.assertEqual(
            resp["Cache-Control"], "max-age=0, no-cache, no-store, must-revalidate"
        )
