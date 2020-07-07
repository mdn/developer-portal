from unittest import mock

from django.conf import settings
from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings

from ratelimit.exceptions import Ratelimited

from ..middleware import rate_limiter, set_remote_addr_from_forwarded_for


@override_settings(RATELIMIT_ENABLE=True, DEVPORTAL_RATELIMIT_DEFAULT_LIMIT="2/m")
class RateLimiterMiddlewareTests(TestCase):
    def tearDown(self):
        cache.clear()

    def test_rate_limiter_middleware_is_enabled(self):
        for expected_middleware in [
            "developerportal.apps.common.middleware.rate_limiter",
            "ratelimit.middleware.RatelimitMiddleware",
        ]:
            assert expected_middleware in settings.MIDDLEWARE

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


class RemoteAddressMiddlewareTests(TestCase):
    def test_set_remote_addr_from_forwarded_for_middleware_is_enabled(self):
        assert (
            "developerportal.apps.common.middleware.set_remote_addr_from_forwarded_for"
            in settings.MIDDLEWARE
        )

    def test_set_remote_addr_from_forwarded_for_middleware(self):
        remote_addr = "172.24.24.24"
        cases = [
            {
                "x_forwarded_for_string": "172.31.255.255",
                "expected_ip": "172.31.255.255",
            },
            {
                "x_forwarded_for_string": "172.31.255.255, 172.16.1.1",
                "expected_ip": "172.31.255.255",
            },
            {
                "x_forwarded_for_string": "172.31.255.255, 172.16.1.1, 172.16.128.128",
                "expected_ip": "172.31.255.255",
            },
            {"x_forwarded_for_string": "", "expected_ip": remote_addr},
            {"x_forwarded_for_string": None, "expected_ip": remote_addr},
        ]

        factory = RequestFactory()

        mock_get_response = mock.Mock(name="get_response")
        middleware_func = set_remote_addr_from_forwarded_for(mock_get_response)

        for case in cases:
            mock_get_response.reset_mock()
            with self.subTest(label=case):

                xff = case["x_forwarded_for_string"]
                if xff is None:
                    kwargs = dict(REMOTE_ADDR=remote_addr)
                else:
                    kwargs = dict(REMOTE_ADDR=remote_addr, HTTP_X_FORWARDED_FOR=xff)
                fake_request = factory.get("/", **kwargs)
                middleware_func(fake_request)

                updated_request = mock_get_response.call_args_list[0][0][0]
                self.assertEqual(
                    updated_request.META["REMOTE_ADDR"], case["expected_ip"]
                )
