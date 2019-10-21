from django.test import TestCase

from developerportal import regex as regex_module


class TestRegexes(TestCase):
    def test_redis_url_regex(self):
        "Test we can spot a Redis URL that features a database component"

        pattern = regex_module.REDIS_DB_URL_PATTERN

        examples = [
            ("redis://redis:6789", False),
            ("redis://redis:6789/1", True),
            ("redis://redis:6789/22", True),
            ("redis://redis.example.com/some/resource:6789", False),
            ("redis://redis.example.com/some/resource:6789/0", True),
            ("redis://redis.example.com/some/resource:6789/22", True),
        ]

        for (input_, expect_a_hit) in examples:
            if expect_a_hit:
                self.assertTrue(pattern.match(input_))
                self.assertTrue(pattern.search(input_))
            else:
                self.assertIsNone(pattern.match(input_))
                self.assertIsNone(pattern.search(input_))
