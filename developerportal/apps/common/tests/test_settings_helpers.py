from unittest import mock

from django.test import TestCase

from developerportal.apps.common.settings_helpers import _get_redis_url_for_cache

REDIS_CACHE_DB_NUMBER = 15


class TestHelpers(TestCase):
    def test__get_redis_url_for_cache(self):

        examples = [
            ("redis://redis:6789", f"redis://redis:6789/{REDIS_CACHE_DB_NUMBER}"),
            (
                "redis://redis.example.com/path/to/thing:6789",
                f"redis://redis.example.com/path/to/thing:6789/{REDIS_CACHE_DB_NUMBER}",
            ),
        ]
        for input_, expected in examples:
            with mock.patch(
                "developerportal.apps.common.settings_helpers.os.environ.get"
            ) as mock_environ_get:
                mock_environ_get.return_value = input_
                self.assertEqual(
                    _get_redis_url_for_cache(REDIS_CACHE_DB_NUMBER), expected
                )
