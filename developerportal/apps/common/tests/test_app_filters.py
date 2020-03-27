from django.test import RequestFactory, TestCase

from developerportal.templatetags.app_filters import domain_from_url


class FilterTestCase(TestCase):
    def test_domain_from_url(self):

        request = RequestFactory().get("/", HTTP_HOST="developer.mozilla.com")

        assert request.META["HTTP_HOST"] == "developer.mozilla.com"

        cases = [
            {"input": ("https://example.com", request), "output": "example.com"},
            {
                "input": ("https://example.com/path/here", request),
                "output": "example.com",
            },
            {"input": ("http://example.com", request), "output": "example.com"},
            {"input": ("https://www.example.com", request), "output": "example.com"},
            {
                "input": ("https://subdomain.example.com", request),
                "output": "example.com",
            },
            {
                "input": ("https://subsub.sub.example.net", request),
                "output": "example.net",
            },
            {"input": ("https://example.net", request), "output": "example.net"},
            {"input": ("/path/only", request), "output": "developer.mozilla.com"},
            {"input": ("path/only", request), "output": "developer.mozilla.com"},
            {"input": ("", request), "output": "developer.mozilla.com"},
            # And a worst-case fallback
            {"input": ("https://badbadbad", request), "output": "badbadbad"},
        ]

        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(
                    domain_from_url(url=case["input"][0], request=case["input"][1]),
                    case["output"],
                )
