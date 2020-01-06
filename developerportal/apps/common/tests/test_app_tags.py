from django.test import TestCase, override_settings

from wagtail.core.models import Page

from developerportal.templatetags.app_tags import (
    filename_cachebreaker_to_querystring,
    get_favicon_path,
    has_at_least_two_filters,
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
