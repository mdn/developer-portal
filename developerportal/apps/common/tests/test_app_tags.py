from django.test import RequestFactory, TestCase, override_settings

from wagtail.core.models import Page

from developerportal.apps.common.constants import (
    COUNTRY_QUERYSTRING_KEY,
    DATE_PARAMS_QUERYSTRING_KEY,
    ENVIRONMENT_DEVELOPMENT,
    ENVIRONMENT_PRODUCTION,
    ENVIRONMENT_STAGING,
    PAGINATION_QUERYSTRING_KEY,
    ROLE_QUERYSTRING_KEY,
    SEARCH_QUERYSTRING_KEY,
    TOPIC_QUERYSTRING_KEY,
)
from developerportal.templatetags.app_tags import (
    filename_cachebreaker_to_querystring,
    get_favicon_path,
    has_at_least_two_filters,
    is_production_site,
    pagination_additional_filter_params,
    split_featured_items,
)


class AppTagsTestCase(TestCase):
    def test_has_at_least_two_filters(self):

        case_data = [
            # One item
            ({"foos": Page.objects.none()}, False),
            ({"foos": Page.objects.all()}, False),
            # Two items
            ({"foos": Page.objects.none(), "bars": True}, False),
            ({"foos": Page.objects.none(), "bars": False}, False),
            ({"foos": Page.objects.all(), "bars": True}, True),
            ({"foos": Page.objects.all(), "bars": False}, False),
            # Three items
            ({"foos": Page.objects.none(), "bars": True, "bams": True}, True),
            ({"foos": Page.objects.none(), "bars": False, "bams": True}, False),
            ({"foos": Page.objects.none(), "bars": False, "bams": False}, False),
            ({"foos": Page.objects.all(), "bars": True, "bams": True}, True),
            ({"foos": Page.objects.all(), "bars": False, "bams": True}, True),
            ({"foos": Page.objects.all(), "bars": False, "bams": False}, False),
        ]
        for data, expected_outcome in case_data:
            with self.subTest(data=data, expected_outcome=expected_outcome):
                self.assertEqual(has_at_least_two_filters(data), expected_outcome)

    def test_filename_cachebreaker_to_querystring(self):
        cases = [
            (
                # "expected" URL forms
                "https://example.com/static/foo.0324221c33f4.jpg",
                "https://example.com/static/foo.jpg?h=0324221c33f4",
            ),
            (
                # forms with multiple things that might match a hashh
                "/path/to/123445abc.123445def.foo.0324221c33f4.png",
                "/path/to/123445abc.123445def.foo.png?h=0324221c33f4",
            ),
            (
                # Simple filename
                "foo.0324221c33f4.jpg",
                "foo.jpg?h=0324221c33f4",
            ),
            (
                # more complex filename
                "foo-bar-baz.0324221c33f4.jpg",
                "foo-bar-baz.jpg?h=0324221c33f4",
            ),
            (
                # Full URL: CSS
                "https://example.com/static/css/21c33.example.21c33.css",
                "https://example.com/static/css/21c33.example.css?h=21c33",
            ),
            (
                # Full URL: JS
                "https://example.com/static/js/example.5434221c33f4.js",
                "https://example.com/static/js/example.js?h=5434221c33f4",
            ),
            (
                # Full URL: longer image suffix
                "https://example.com/static/img/example.55e7cbb9ba48.jpeg",
                "https://example.com/static/img/example.jpeg?h=55e7cbb9ba48",
            ),
        ]
        for input_, expected in cases:
            with self.subTest(input_=input_, expected=expected):
                self.assertEqual(filename_cachebreaker_to_querystring(input_), expected)

        no_change_cases = [
            # And a couple which are not rewritten
            ("no-filename-suffix.0324221c33f4", "no-filename-suffix.0324221c33f4"),
            ("nohash.jpg", "nohash.jpg"),
        ]
        for input_, expected in no_change_cases:
            with self.subTest(input_=input_, expected=expected):
                with self.assertLogs(
                    "developerportal.templatetags.app_tags", level="DEBUG"
                ) as cm:
                    self.assertEqual(
                        filename_cachebreaker_to_querystring(input_), expected
                    )
                    self.assertEqual(
                        cm.output,
                        [
                            (
                                f"DEBUG:developerportal.templatetags.app_tags:"
                                f"Couldn't extract hash from URL {input_}. "
                                f"Leaving unchanged."
                            )
                        ],
                    )

    def test_pagination_additional_filter_params(self):
        cases = [
            {
                # single topic only
                "input_querystring": f"?{TOPIC_QUERYSTRING_KEY}=css",
                "expected_output": f"&{TOPIC_QUERYSTRING_KEY}=css",
            },
            {
                # multiple topic
                "input_querystring": (
                    f"?{TOPIC_QUERYSTRING_KEY}=css&{TOPIC_QUERYSTRING_KEY}=javascript"
                ),
                "expected_output": (
                    f"&{TOPIC_QUERYSTRING_KEY}=css&{TOPIC_QUERYSTRING_KEY}=javascript"
                ),
            },
            {
                # single topic and page info
                "input_querystring": (
                    f"?{TOPIC_QUERYSTRING_KEY}=css&{PAGINATION_QUERYSTRING_KEY}=2"
                ),
                "expected_output": f"&{TOPIC_QUERYSTRING_KEY}=css",
            },
            {
                # multiple topic and page info
                "input_querystring": (
                    f"?{TOPIC_QUERYSTRING_KEY}=css&{TOPIC_QUERYSTRING_KEY}=javascript"
                    f"&{PAGINATION_QUERYSTRING_KEY}=2"
                ),
                "expected_output": (
                    f"&{TOPIC_QUERYSTRING_KEY}=css&{TOPIC_QUERYSTRING_KEY}=javascript"
                ),
            },
            {
                # single topic and page info
                "input_querystring": (
                    f"?{PAGINATION_QUERYSTRING_KEY}=22&{TOPIC_QUERYSTRING_KEY}=css"
                ),
                "expected_output": f"&{TOPIC_QUERYSTRING_KEY}=css",
            },
            {
                # multiple topic and page info
                "input_querystring": (
                    f"?{PAGINATION_QUERYSTRING_KEY}=3&{TOPIC_QUERYSTRING_KEY}=css"
                    f"&{TOPIC_QUERYSTRING_KEY}=javascript"
                ),
                "expected_output": (
                    f"&{TOPIC_QUERYSTRING_KEY}=css&{TOPIC_QUERYSTRING_KEY}=javascript"
                ),
            },
            {
                # multiple non-page params
                "input_querystring": (
                    f"?{TOPIC_QUERYSTRING_KEY}=css&{ROLE_QUERYSTRING_KEY}=test"
                ),
                "expected_output": (
                    f"&{TOPIC_QUERYSTRING_KEY}=css&{ROLE_QUERYSTRING_KEY}=test"
                ),
            },
            {
                # multiple params, incl pages
                "input_querystring": (
                    f"?{TOPIC_QUERYSTRING_KEY}=css&{ROLE_QUERYSTRING_KEY}=test"
                    f"&{PAGINATION_QUERYSTRING_KEY}=234"
                ),
                "expected_output": (
                    f"&{TOPIC_QUERYSTRING_KEY}=css&{ROLE_QUERYSTRING_KEY}=test"
                ),
            },
            {
                # double-multiple params, incl pages
                "input_querystring": (
                    f"?{TOPIC_QUERYSTRING_KEY}=css&{TOPIC_QUERYSTRING_KEY}=javascript"
                    f"&{COUNTRY_QUERYSTRING_KEY}=DE&{COUNTRY_QUERYSTRING_KEY}=AR"
                    f"&{ROLE_QUERYSTRING_KEY}=test&{PAGINATION_QUERYSTRING_KEY}=234"
                ),
                "expected_output": (
                    f"&{TOPIC_QUERYSTRING_KEY}=css&{TOPIC_QUERYSTRING_KEY}=javascript"
                    f"&{COUNTRY_QUERYSTRING_KEY}=DE&{COUNTRY_QUERYSTRING_KEY}=AR"
                    f"&{ROLE_QUERYSTRING_KEY}=test"
                ),
            },
            {
                # double-multiple params, incl pages, different key position
                "input_querystring": (
                    f"?{PAGINATION_QUERYSTRING_KEY}=234&{ROLE_QUERYSTRING_KEY}=test"
                    f"&{TOPIC_QUERYSTRING_KEY}=css&{TOPIC_QUERYSTRING_KEY}=javascript"
                    f"&{COUNTRY_QUERYSTRING_KEY}=DE&{COUNTRY_QUERYSTRING_KEY}=AR"
                    f"&{DATE_PARAMS_QUERYSTRING_KEY}=2020-2-20"
                ),
                "expected_output": (
                    f"&{ROLE_QUERYSTRING_KEY}=test"
                    f"&{TOPIC_QUERYSTRING_KEY}=css&{TOPIC_QUERYSTRING_KEY}=javascript"
                    f"&{COUNTRY_QUERYSTRING_KEY}=DE&{COUNTRY_QUERYSTRING_KEY}=AR"
                    f"&{DATE_PARAMS_QUERYSTRING_KEY}=2020-2-20"
                ),
            },
            {
                # Show that only whitelisted params are covered - 'evil', area'
                # and 'location' will be skipped
                "input_querystring": (
                    f"?{PAGINATION_QUERYSTRING_KEY}=234&{ROLE_QUERYSTRING_KEY}=test"
                    f"&{TOPIC_QUERYSTRING_KEY}=css&area=javascript&evil=true"
                    f"&location=DE&{COUNTRY_QUERYSTRING_KEY}=AR"
                ),
                "expected_output": (
                    f"&{ROLE_QUERYSTRING_KEY}=test"
                    f"&{TOPIC_QUERYSTRING_KEY}=css&{COUNTRY_QUERYSTRING_KEY}=AR"
                ),
            },
            {
                # multiple topic and page info AND search
                "input_querystring": (
                    f"?{TOPIC_QUERYSTRING_KEY}=css&{TOPIC_QUERYSTRING_KEY}=javascript"
                    f"&{PAGINATION_QUERYSTRING_KEY}=2"
                    f"&{SEARCH_QUERYSTRING_KEY}=test+string"
                ),
                "expected_output": (
                    f"&{TOPIC_QUERYSTRING_KEY}=css&{TOPIC_QUERYSTRING_KEY}=javascript"
                    f"&{SEARCH_QUERYSTRING_KEY}=test+string"  # note: still escaped
                ),
            },
        ]

        factory = RequestFactory()

        for case in cases:
            with self.subTest(case=case):
                request = factory.get(f"/{case['input_querystring']}")
                self.assertEqual(
                    pagination_additional_filter_params(request),
                    case["expected_output"],
                )

    def test_get_favicon_path(self):
        cases = [
            {"input": None, "output": "img/icons/favicon.ico"},
            {"input": "", "output": "img/icons/favicon.ico"},
            {"input": "production", "output": "img/icons/favicon.ico"},
            {"input": "development", "output": "img/icons/favicon_dev.ico"},
            {"input": "staging", "output": "img/icons/favicon_stage.ico"},
        ]

        for case in cases:
            with self.subTest(case=case):
                with override_settings(ACTIVE_ENVIRONMENT=case["input"]):
                    self.assertEqual(get_favicon_path(), case["output"])

    def test_is_production_site(self):

        cases = [
            {"input": ENVIRONMENT_DEVELOPMENT, "output": False},
            {"input": ENVIRONMENT_PRODUCTION, "output": True},
            {"input": ENVIRONMENT_STAGING, "output": False},
        ]

        for case in cases:
            with self.subTest(case=case):
                with override_settings(ACTIVE_ENVIRONMENT=case["input"]):
                    self.assertEqual(is_production_site(), case["output"])

    def test_split_featured_items(self):

        cases = [
            {"input": [1, 2, 3, 4, 5], "output": ([1, 2], [3, 4, 5], [])},
            {"input": [1, 2, 3, 4], "output": ([1, 2], [], [3, 4])},
            {"input": [1, 2, 3], "output": ([], [1, 2, 3], [])},
            {"input": [1, 2], "output": ([1, 2], [], [])},
            {"input": [1], "output": ([1], [], [])},
        ]

        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(split_featured_items(case["input"]), case["output"])
