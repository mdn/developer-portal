from unittest import mock

from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings

from ratelimit.exceptions import Ratelimited

from ..middleware import rate_limiter


@override_settings(RATELIMIT_ENABLE=True, DEVPORTAL_RATELIMIT_DEFAULT_LIMIT="2/m")
class RateLimiterMiddlewareTests(TestCase):
    def tearDown(self):
        cache.clear()

    def test_rate_limiter__works_for_all_http_methods(self):

        factory = RequestFactory()

        for method in ["get", "post", "put", "delete", "head", "options"]:
            with self.subTest(label=method):

                # django-ratelimit uses the default cache. Invalidating it between
                # attempts means subtests will not interfere with each other
                cache.clear()

                mock_get_response = mock.Mock(name="get_response")
                fake_request = getattr(factory, method)("/", REMOTE_ADDR="127.0.0.1")
                middleware_func = rate_limiter(mock_get_response)

                # First time, no problem
                middleware_func(fake_request)
                assert mock_get_response.call_count == 1

                # Second time, no problem
                middleware_func(fake_request)
                assert mock_get_response.call_count == 2

                # Third time: rate-limited problem
                with self.assertRaises(Ratelimited):
                    middleware_func(fake_request)
                assert mock_get_response.call_count == 2  # ie, didn't get called again

    @override_settings(DEVPORTAL_RATELIMIT_DEFAULT_LIMIT="3/m")  # 3 per min max
    def test_rate_limiter__definitely_separates_by_ip(self):

        factory = RequestFactory()

        mock_get_response = mock.Mock(name="get_response")
        middleware_func = rate_limiter(mock_get_response)

        # Four calls from different IPs: all fine
        cache.clear()  # reset any previous rate limiting
        for i, ip in enumerate(["127.0.0.1", "127.0.0.2", "127.0.0.3", "127.0.0.4"]):
            fake_request = factory.get("/", REMOTE_ADDR=ip)
            middleware_func(fake_request)
            assert mock_get_response.call_count == 1 + i

        # Four calls from SAME IP: fourth will be limited
        cache.clear()  # reset any previous rate limiting

        assert fake_request.META["REMOTE_ADDR"] == "127.0.0.4"

        middleware_func(fake_request)
        middleware_func(fake_request)
        middleware_func(fake_request)
        with self.assertRaises(Ratelimited):
            middleware_func(fake_request)
