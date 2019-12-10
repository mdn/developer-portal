from django.test import RequestFactory, TestCase

from wagtail.core.models import Page

from developerportal.templatetags.app_tags import (
    filename_cachebreaker_to_querystring,
    has_at_least_two_filters,
    pagination_additional_filter_params,
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
                "input_querystring": "?topics=css",
                "expected_output": "&topics=css",
            },
            {
                # multiple topics
                "input_querystring": "?topics=css,javascript",
                "expected_output": "&topics=css,javascript",
            },
            {
                # single topic and page info
                "input_querystring": "?topics=css&page=2",
                "expected_output": "&topics=css",
            },
            {
                # multiple topics and page info
                "input_querystring": "?topics=css,javascript&page=2",
                "expected_output": "&topics=css,javascript",
            },
            {
                # single topic and page info
                "input_querystring": "?page=22&topics=css",
                "expected_output": "&topics=css",
            },
            {
                # multiple topics and page info
                "input_querystring": "?page=3&topics=css,javascript",
                "expected_output": "&topics=css,javascript",
            },
            {
                # multiple non-page params
                "input_querystring": "?topics=css&foo=bar",
                "expected_output": "&topics=css&foo=bar",
            },
            {
                # multiple params, incl pages
                "input_querystring": "?topics=css&foo=bar&page=234",
                "expected_output": "&topics=css&foo=bar",
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
