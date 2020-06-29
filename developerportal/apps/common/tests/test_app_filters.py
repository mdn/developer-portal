from django.test import RequestFactory, TestCase, override_settings

from wagtail.core.models import Site

from developerportal.templatetags.app_filters import domain_from_url


class FilterTestCase(TestCase):
    @override_settings(ALLOWED_HOSTS=["developer.mozilla.com"])
    def test_domain_from_url(self):

        Site.objects.create(
            hostname="developer.mozilla.com", site_name="Test Site", root_page_id=1
        )

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
