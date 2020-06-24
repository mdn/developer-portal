from django.test import RequestFactory, TestCase

from developerportal.apps.articles import models as articles_models
from developerportal.apps.content import models as content_models
from developerportal.apps.events import models as events_models
from developerportal.apps.externalcontent import models as externalcontent_models
from developerportal.apps.people import models as people_models
from developerportal.apps.topics import models as topics_models
from developerportal.apps.videos import models as videos_models
from developerportal.templatetags.app_filters import domain_from_url, page_type_label


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

    def test_page_type_label(self):

        cases = [
            {"input": (articles_models.Article()), "output": "Post"},
            {"input": (articles_models.Articles()), "output": None},
            {"input": (videos_models.Video()), "output": "Post"},
            {"input": (videos_models.Videos()), "output": None},
            {"input": (events_models.Event()), "output": "Event"},
            {"input": (events_models.Events()), "output": None},
            {"input": (externalcontent_models.ExternalArticle()), "output": "Post"},
            {"input": (externalcontent_models.ExternalVideo()), "output": "Post"},
            {"input": (externalcontent_models.ExternalEvent()), "output": "Event"},
            {"input": (topics_models.Topic()), "output": "Products & Technologies"},
            {"input": (topics_models.Topics()), "output": None},
            {"input": (content_models.ContentPage()), "output": None},
            {"input": (people_models.Person()), "output": "Person"},
            {"input": (people_models.People()), "output": None},
        ]

        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(page_type_label(case["input"]), case["output"])
